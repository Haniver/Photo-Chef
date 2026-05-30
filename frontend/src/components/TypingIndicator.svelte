<script lang="ts">
  // No props — purely presentational
</script>

<span class="typing-indicator" aria-label="Escribiendo..." role="status">
  <span></span>
  <span></span>
  <span></span>
</span>

<style>
  .typing-indicator {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    padding: 4px 2px 0;
    vertical-align: middle;
  }

  .typing-indicator span {
    width: 6px;
    height: 6px;
    background-color: var(--color-text-muted);
    border-radius: 50%;
    animation: bounce 1.2s infinite ease-in-out;
  }

  .typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
  }

  .typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
  }

  @keyframes bounce {
    0%,
    80%,
    100% {
      transform: scale(0.6);
      opacity: 0.4;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }
</style>
