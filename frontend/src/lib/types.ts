export interface Message {
  id: string
  role: 'user' | 'agent' | 'error'
  content: string
  isStreaming: boolean
  statusText: string
}
