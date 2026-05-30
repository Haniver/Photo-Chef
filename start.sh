#!/usr/bin/env bash
set -e

# Build the frontend
cd frontend
npm install
npm run build

# Start the backend (serves frontend/dist/ as static files)
cd ..
exec uv run uvicorn backend.main:app --port 8005
