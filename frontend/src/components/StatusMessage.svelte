<script lang="ts">
  interface Props {
    message: string
  }

  let { message }: Props = $props()
</script>

{#if message}
  <div class="status-message" role="status" aria-live="polite">
    <span class="spinner" aria-hidden="true"></span>
    <span>{message}</span>
  </div>
{/if}

<style>
  .status-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8125rem;
    color: var(--color-sage);
    font-style: italic;
    padding: 0.2rem 0.25rem;
    margin-bottom: 0.25rem;
  }

  .spinner {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 2px solid var(--color-sage-light);
    border-top-color: var(--color-sage);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    flex-shrink: 0;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
