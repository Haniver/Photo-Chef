<script lang="ts">
  import { tick } from 'svelte'
  import ChatBubble from './ChatBubble.svelte'
  import type { Message } from '../lib/types.ts'

  interface Props {
    messages: Message[]
  }

  let { messages }: Props = $props()

  let container = $state<HTMLDivElement | undefined>(undefined)

  $effect(() => {
    // Re-run whenever messages length or last message content changes
    void messages.length
    void (messages[messages.length - 1]?.content ?? '')
    tick().then(() => {
      if (container) {
        container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' })
      }
    })
  })
</script>

<div class="chat-window" bind:this={container}>
  {#if messages.length === 0}
    <div class="empty-state">
      <p>🍽️ Sube una foto de tu refrigerador y Photo-Chef te sugerirá una receta.</p>
    </div>
  {/if}
  {#each messages as msg (msg.id)}
    <ChatBubble
      role={msg.role}
      content={msg.content}
      isStreaming={msg.isStreaming}
      statusText={msg.statusText}
    />
  {/each}
</div>

<style>
  .chat-window {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    scroll-behavior: smooth;
  }

  .empty-state {
    text-align: center;
    color: var(--color-text-muted);
    padding: 3rem 1rem;
    font-size: 0.9375rem;
    line-height: 1.6;
  }
</style>
