"""Tests for Fase 4 — Agente LangGraph con streaming."""

import asyncio
import base64
import io
import json
import struct
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

# Pre-import so patch() can resolve modules in Python 3.13+
import backend.agent        # noqa: F401
import backend.agent_tools  # noqa: F401
import backend.main         # noqa: F401

from backend.agent import _ThinkStreamFilter, strip_thinking_tokens
from backend.main import app


# ---------------------------------------------------------------------------
# Unit tests — strip_thinking_tokens
# ---------------------------------------------------------------------------


def test_strip_thinking_removes_complete_block():
    """A complete <think>...</think> block is fully removed."""
    result = strip_thinking_tokens("<think>razonamiento interno</think> texto visible")
    assert result == " texto visible"


def test_strip_thinking_no_block_unchanged():
    """Text without any <think> tags is returned unchanged."""
    text = "texto sin think"
    assert strip_thinking_tokens(text) == text


def test_strip_thinking_multiline_block():
    """Multiline content inside <think>...</think> is removed."""
    text = "<think>\nlinea 1\nlinea 2\n</think>respuesta"
    assert strip_thinking_tokens(text) == "respuesta"


def test_strip_thinking_incomplete_block():
    """An incomplete <think> without closing tag is removed up to end of text."""
    text = "inicio<think>razonamiento sin cerrar"
    result = strip_thinking_tokens(text)
    assert "<think>" not in result
    assert "inicio" in result


def test_strip_thinking_empty_string():
    """Empty string input returns empty string."""
    assert strip_thinking_tokens("") == ""


# ---------------------------------------------------------------------------
# Unit tests — _ThinkStreamFilter (streaming-safe filter)
# ---------------------------------------------------------------------------


def test_think_stream_filter_complete_block_single_chunk():
    f = _ThinkStreamFilter()
    result = f.feed("<think>skip</think>visible")
    assert result == "visible"


def test_think_stream_filter_split_across_chunks():
    """<think> block split across multiple chunks is handled correctly."""
    f = _ThinkStreamFilter()
    r1 = f.feed("<thi")
    r2 = f.feed("nk>hidden</think>shown")
    assert r1 == ""
    assert r2 == "shown"


def test_think_stream_filter_no_think():
    f = _ThinkStreamFilter()
    assert f.feed("hello ") == "hello "
    assert f.feed("world") == "world"


def test_think_stream_filter_open_never_closed():
    """Think block that opens but never closes produces no output after it."""
    f = _ThinkStreamFilter()
    r1 = f.feed("before <think>hidden")
    r2 = f.feed(" more hidden")
    assert r1 == "before "
    assert r2 == ""


# ---------------------------------------------------------------------------
# Helpers — minimal valid JPEG in base64
# ---------------------------------------------------------------------------


def _minimal_jpeg_b64() -> str:
    """Return a tiny but valid JPEG (1×1 white pixel) as base64."""
    # Minimal JPEG bytes (SOI + APP0 JFIF + SOF0 + ... + EOI)
    jpeg_bytes = bytes(
        [
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00,
            0xFF, 0xDB, 0x00, 0x43, 0x00,
            *([0x08] * 64),
            0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x11, 0x00,
            0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00, 0x01, 0x05, 0x01, 0x01, 0x01, 0x01,
            0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02,
            0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B,
            0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01, 0x00, 0x00, 0x3F, 0x00, 0xF5, 0x4A,
            0xFF, 0xD9,
        ]
    )
    return base64.b64encode(jpeg_bytes).decode()


# ---------------------------------------------------------------------------
# Integration test — POST /chat
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_endpoint_streams_status_and_token():
    """POST /chat with a real-looking JPEG must stream status and token events."""

    # We mock build_agent to avoid real API calls
    async def fake_astream_events(inputs, version, config):
        # Simulate: analyze tool start, search tool start, LLM model start, token
        yield {"event": "on_tool_start", "name": "analyze_image_tool", "data": {}}
        yield {"event": "on_tool_start", "name": "search_recipes_tool", "data": {}}
        yield {"event": "on_chat_model_start", "name": "ChatQwen", "data": {}}
        chunk = MagicMock()
        chunk.content = "## Tortilla\n"
        chunk.additional_kwargs = {}
        yield {"event": "on_chat_model_stream", "data": {"chunk": chunk}}

    mock_agent = MagicMock()
    mock_agent.astream_events = fake_astream_events

    jpeg_b64 = _minimal_jpeg_b64()
    jpeg_bytes = base64.b64decode(jpeg_b64)

    with patch("backend.main.build_agent", return_value=mock_agent), \
         patch("backend.main.make_analyze_image_tool", return_value=MagicMock()):

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/chat",
                files={"image": ("fridge.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
                data={"message": "", "session_id": "test-session"},
            )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]

    # Parse SSE events
    event_types = []
    for line in response.text.splitlines():
        if line.startswith("event:"):
            event_types.append(line.split(":", 1)[1].strip())

    assert "status" in event_types, "Must emit at least one status event"
    assert "token" in event_types, "Must emit at least one token event"
    assert "done" in event_types, "Must end with a done event"


@pytest.mark.asyncio
async def test_chat_endpoint_rejects_invalid_format():
    """POST /chat with a non-image file must return 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/chat",
            files={"image": ("file.txt", io.BytesIO(b"not an image"), "text/plain")},
            data={"message": "", "session_id": ""},
        )
    assert response.status_code == 422
