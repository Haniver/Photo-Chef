<script lang="ts">
  import ImageUpload from './components/ImageUpload.svelte'
  import ChatWindow from './components/ChatWindow.svelte'
  import { sendMessage } from './lib/api.ts'
  import type { Message } from './lib/types.ts'

  const sessionId = crypto.randomUUID()

  let messages = $state<Message[]>([])
  let imageFile = $state<File | null>(null)
  let imageLocked = $state(false)
  let isStreaming = $state(false)
  let inputText = $state('')
  let imageError = $state('')

  function handleImageSelect(file: File) {
    imageFile = file
    imageError = ''
  }

  function handleImageError(msg: string) {
    imageError = msg
    imageFile = null
  }

  function canSend(): boolean {
    if (isStreaming) return false
    if (!imageLocked) {
      // First message: an image is required (text is optional)
      return imageFile !== null
    }
    // Follow-up: text is required
    return inputText.trim().length > 0
  }

  async function handleSend() {
    if (!canSend()) return

    const isFirstMessage = !imageLocked
    const fileToSend = isFirstMessage ? imageFile : null
    const text = inputText.trim()

    inputText = ''
    imageLocked = true
    isStreaming = true

    // Add user bubble
    const userContent = text || '📷 ¿Qué puedo preparar con esto?'
    messages.push({
      id: crypto.randomUUID(),
      role: 'user',
      content: userContent,
      isStreaming: false,
      statusText: ''
    })

    // Add agent placeholder bubble
    const agentIdx = messages.length
    messages.push({
      id: crypto.randomUUID(),
      role: 'agent',
      content: '',
      isStreaming: true,
      statusText: ''
    })

    await sendMessage(
      sessionId,
      text,
      {
        onStatus(msg) {
          messages[agentIdx].statusText = msg
        },
        onToken(token) {
          messages[agentIdx].content += token
        },
        onDone() {
          messages[agentIdx].isStreaming = false
          messages[agentIdx].statusText = ''
          isStreaming = false
        },
        onError(detail) {
          messages[agentIdx] = {
            ...messages[agentIdx],
            role: 'error',
            content: `⚠️ ${detail}`,
            isStreaming: false,
            statusText: ''
          }
          isStreaming = false
        }
      },
      fileToSend ?? undefined
    )
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  let inputPlaceholder = $derived(
    !imageLocked
      ? imageFile
        ? 'Mensaje opcional — la foto es suficiente para empezar…'
        : 'Primero selecciona una foto…'
      : 'Pregunta sobre la receta…'
  )
</script>

<div class="app">
  <header class="header">
    <span class="header-logo" aria-hidden="true">🍳</span>
    <h1 class="header-title">Photo-Chef</h1>
  </header>

  <div class="upload-section">
    <ImageUpload
      locked={imageLocked}
      error={imageError}
      onSelect={handleImageSelect}
      onError={handleImageError}
    />
  </div>

  <div class="chat-section">
    <ChatWindow {messages} />

    <div class="input-row">
      <textarea
        bind:value={inputText}
        onkeydown={handleKeydown}
        disabled={isStreaming || (!imageLocked && imageFile === null)}
        placeholder={inputPlaceholder}
        rows={2}
        class="text-input"
        aria-label="Mensaje al agente"
      ></textarea>
      <button
        onclick={handleSend}
        disabled={!canSend()}
        class="send-btn"
        aria-label="Enviar mensaje"
      >
        Enviar
      </button>
    </div>
  </div>
</div>

<style>
  .app {
    display: flex;
    flex-direction: column;
    height: 100%;
    max-width: var(--max-width);
    margin: 0 auto;
    background: var(--color-bg);
    border-left: 1px solid var(--color-border);
    border-right: 1px solid var(--color-border);
  }

  .header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    background: white;
    border-bottom: 2px solid var(--color-accent);
    flex-shrink: 0;
  }

  .header-logo {
    font-size: 1.4rem;
  }

  .header-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--color-accent);
    letter-spacing: -0.01em;
  }

  .upload-section {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--color-border);
    background: var(--color-surface);
    flex-shrink: 0;
  }

  .chat-section {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
  }

  .input-row {
    display: flex;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--color-border);
    background: white;
    align-items: flex-end;
    flex-shrink: 0;
  }

  .text-input {
    flex: 1;
    padding: 0.625rem 0.875rem;
    border: 1px solid var(--color-border);
    border-radius: 0.625rem;
    font-family: inherit;
    font-size: 0.9375rem;
    resize: none;
    background: var(--color-bg);
    color: var(--color-text);
    outline: none;
    transition: border-color 0.2s;
    line-height: 1.5;
  }

  .text-input:focus {
    border-color: var(--color-accent);
  }

  .text-input:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .text-input::placeholder {
    color: var(--color-text-muted);
  }

  .send-btn {
    padding: 0.625rem 1.25rem;
    background: var(--color-accent);
    color: white;
    border: none;
    border-radius: 0.625rem;
    font-family: inherit;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition:
      background 0.2s,
      opacity 0.2s;
    white-space: nowrap;
    line-height: 1.5;
    height: fit-content;
  }

  .send-btn:hover:not(:disabled) {
    background: var(--color-accent-hover);
  }

  .send-btn:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
</style>
