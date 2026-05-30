export interface SSECallbacks {
  onStatus: (msg: string) => void
  onToken: (text: string) => void
  onDone: () => void
  onError: (detail: string) => void
}

/**
 * Sends a message to the Photo-Chef agent and streams the response via SSE.
 * On the first message, pass the image File; subsequent messages send text only.
 */
export async function sendMessage(
  sessionId: string,
  message: string,
  callbacks: SSECallbacks,
  imageFile?: File
): Promise<void> {
  const formData = new FormData()
  formData.append('session_id', sessionId)
  formData.append('message', message)
  if (imageFile) {
    formData.append('image', imageFile)
  }

  let response: Response
  try {
    response = await fetch('/api/chat', {
      method: 'POST',
      body: formData
    })
  } catch {
    callbacks.onError(
      'No se pudo conectar al servidor. Verifica tu conexión e inténtalo de nuevo.'
    )
    return
  }

  if (!response.ok) {
    let detail = `Error del servidor (${response.status})`
    try {
      const body = await response.json()
      if (typeof body?.detail === 'string') detail = body.detail
    } catch {
      // ignore
    }
    callbacks.onError(detail)
    return
  }

  const reader = response.body?.getReader()
  if (!reader) {
    callbacks.onError('No se pudo leer la respuesta del servidor.')
    return
  }

  const decoder = new TextDecoder()
  let buffer = ''
  let terminated = false

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // SSE messages are delimited by double newlines
      const parts = buffer.split('\n\n')
      buffer = parts.pop() ?? ''

      for (const part of parts) {
        if (!part.trim()) continue

        const lines = part.trim().split('\n')
        let eventType = 'message'
        let dataStr = ''

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim()
          } else if (line.startsWith('data: ')) {
            dataStr = line.slice(6)
          }
        }

        if (!dataStr) continue

        try {
          const data = JSON.parse(dataStr)
          if (eventType === 'status') {
            callbacks.onStatus(data.message ?? '')
          } else if (eventType === 'token') {
            callbacks.onToken(data.text ?? '')
          } else if (eventType === 'done') {
            callbacks.onDone()
            terminated = true
            return
          } else if (eventType === 'error') {
            callbacks.onError(data.detail ?? 'Error desconocido del agente.')
            terminated = true
            return
          }
        } catch {
          // ignore malformed SSE data
        }
      }
    }
  } catch {
    if (!terminated) {
      callbacks.onError('Se interrumpió la conexión. Recarga la página e inténtalo de nuevo.')
      terminated = true
    }
  } finally {
    reader.releaseLock()
  }

  if (!terminated) {
    callbacks.onDone()
  }
}
