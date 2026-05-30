<script lang="ts">
  import { marked } from 'marked'
  import DOMPurify from 'dompurify'
  import StatusMessage from './StatusMessage.svelte'
  import TypingIndicator from './TypingIndicator.svelte'

  interface Props {
    role: 'user' | 'agent' | 'error'
    content: string
    isStreaming?: boolean
    statusText?: string
  }

  let { role, content, isStreaming = false, statusText = '' }: Props = $props()

  // Render agent/error content as sanitized Markdown HTML
  let renderedHtml = $derived(
    role !== 'user'
      ? DOMPurify.sanitize(marked.parse(content) as string, {
          // Allow standard HTML tags produced by marked
          ALLOWED_TAGS: [
            'p', 'br', 'strong', 'em', 'b', 'i', 'ul', 'ol', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote',
            'code', 'pre', 'hr', 'a', 'span'
          ],
          ALLOWED_ATTR: ['href', 'class'],
          FORCE_BODY: true
        })
      : ''
  )
</script>

<div class="bubble-wrapper" class:user={role === 'user'} class:agent={role !== 'user'}>
  {#if role !== 'user'}
    <div class="sender-name">Photo-Chef</div>
  {/if}
  {#if statusText}
    <StatusMessage message={statusText} />
  {/if}
  <div
    class="bubble"
    class:bubble-user={role === 'user'}
    class:bubble-agent={role === 'agent'}
    class:bubble-error={role === 'error'}
  >
    {#if role === 'user'}
      {content}
    {:else}
      {#if content}
        <!-- eslint-disable-next-line svelte/no-at-html-tags -->
        {@html renderedHtml}
      {/if}
      {#if isStreaming}
        <TypingIndicator />
      {/if}
    {/if}
  </div>
</div>

<style>
  .bubble-wrapper {
    display: flex;
    flex-direction: column;
    max-width: 85%;
  }

  .bubble-wrapper.user {
    align-self: flex-end;
    align-items: flex-end;
  }

  .bubble-wrapper.agent {
    align-self: flex-start;
    align-items: flex-start;
  }

  .sender-name {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--color-text-muted);
    margin-bottom: 0.25rem;
    padding-left: 0.25rem;
  }

  .bubble {
    padding: 0.75rem 1rem;
    border-radius: 1rem;
    font-size: 0.9375rem;
    line-height: 1.6;
    word-break: break-word;
  }

  .bubble-user {
    background: var(--color-accent);
    color: white;
    border-bottom-right-radius: 0.25rem;
  }

  .bubble-agent {
    background: var(--color-surface);
    border: 1px solid var(--color-border);
    border-bottom-left-radius: 0.25rem;
    min-width: 2.5rem;
    min-height: 2.5rem;
  }

  .bubble-error {
    background: #fff3f0;
    border: 1px solid #f5c6bc;
    color: #8b2500;
    border-bottom-left-radius: 0.25rem;
  }

  /* Markdown styles scoped via :global inside agent bubble */
  .bubble-agent :global(h1),
  .bubble-agent :global(h2),
  .bubble-agent :global(h3),
  .bubble-agent :global(h4) {
    font-size: 1rem;
    font-weight: 700;
    margin-top: 0.875rem;
    margin-bottom: 0.25rem;
    color: var(--color-accent);
  }

  .bubble-agent :global(h2) {
    font-size: 1.0625rem;
  }

  .bubble-agent :global(h3) {
    font-size: 1rem;
    color: var(--color-sage);
  }

  .bubble-agent :global(ul),
  .bubble-agent :global(ol) {
    padding-left: 1.375rem;
    margin: 0.4rem 0;
  }

  .bubble-agent :global(li) {
    margin: 0.25rem 0;
  }

  .bubble-agent :global(strong) {
    font-weight: 600;
  }

  .bubble-agent :global(em) {
    font-style: italic;
  }

  .bubble-agent :global(p) {
    margin: 0.4rem 0;
  }

  .bubble-agent :global(p:first-child) {
    margin-top: 0;
  }

  .bubble-agent :global(p:last-child) {
    margin-bottom: 0;
  }

  .bubble-agent :global(code) {
    background: var(--color-bg);
    padding: 0.1em 0.35em;
    border-radius: 0.25em;
    font-size: 0.875em;
    font-family: ui-monospace, monospace;
  }

  .bubble-agent :global(pre) {
    background: var(--color-bg);
    padding: 0.75rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 0.5rem 0;
  }

  .bubble-agent :global(pre code) {
    background: none;
    padding: 0;
  }

  .bubble-agent :global(blockquote) {
    border-left: 3px solid var(--color-accent-light);
    padding-left: 0.75rem;
    color: var(--color-text-muted);
    margin: 0.5rem 0;
  }

  .bubble-agent :global(hr) {
    border: none;
    border-top: 1px solid var(--color-border);
    margin: 0.75rem 0;
  }
</style>
