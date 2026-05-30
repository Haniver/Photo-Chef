<script lang="ts">
  interface Props {
    locked: boolean
    error: string
    onSelect: (file: File) => void
    onError: (msg: string) => void
  }

  const ACCEPTED_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])

  let { locked, error, onSelect, onError }: Props = $props()

  let previewUrl = $state<string | null>(null)

  function handleFileChange(e: Event) {
    const input = e.target as HTMLInputElement
    const file = input.files?.[0]
    if (!file) return

    if (!ACCEPTED_TYPES.has(file.type)) {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl)
        previewUrl = null
      }
      input.value = ''
      onError(
        `Formato no soportado (${file.name.split('.').pop()?.toUpperCase() ?? 'desconocido'}). ` +
          'Por favor sube una imagen JPEG, PNG o WEBP.'
      )
      return
    }

    if (previewUrl) URL.revokeObjectURL(previewUrl)
    previewUrl = URL.createObjectURL(file)
    onSelect(file)
  }
</script>

<div class="image-upload">
  {#if previewUrl}
    <div class="preview-container" class:locked>
      <img src={previewUrl} alt="Vista previa del refrigerador" class="preview-img" />
      {#if locked}
        <div class="locked-overlay" aria-label="Foto enviada">
          <span>📷 Foto enviada</span>
        </div>
      {/if}
    </div>
  {:else if !locked}
    <label class="upload-label" for="image-input">
      <span class="upload-icon" aria-hidden="true">📷</span>
      <span class="upload-text">Sube una foto de tu refrigerador</span>
      <span class="upload-hint">JPEG · PNG · WEBP</span>
    </label>
  {/if}

  <input
    id="image-input"
    type="file"
    accept="image/jpeg,image/png,image/webp"
    onchange={handleFileChange}
    disabled={locked}
    class="file-input"
    aria-label="Seleccionar imagen"
  />

  {#if error}
    <p class="error-msg" role="alert">{error}</p>
  {/if}
</div>

<style>
  .image-upload {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    width: 100%;
  }

  .upload-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.4rem;
    cursor: pointer;
    padding: 1.25rem 2rem;
    border: 2px dashed var(--color-border);
    border-radius: 0.75rem;
    background: white;
    color: var(--color-text-muted);
    font-size: 0.9rem;
    transition:
      border-color 0.2s,
      background 0.2s;
    width: 100%;
    text-align: center;
  }

  .upload-label:hover {
    border-color: var(--color-accent);
    background: var(--color-accent-light);
  }

  .upload-icon {
    font-size: 2rem;
  }

  .upload-text {
    font-weight: 500;
    color: var(--color-text);
  }

  .upload-hint {
    font-size: 0.75rem;
    color: var(--color-border);
  }

  .file-input {
    display: none;
  }

  .preview-container {
    position: relative;
    width: 100%;
    max-width: 260px;
  }

  .preview-img {
    width: 100%;
    border-radius: 0.625rem;
    display: block;
    object-fit: cover;
    max-height: 160px;
  }

  .locked-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    border-radius: 0.625rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 0.875rem;
    font-weight: 500;
  }

  .error-msg {
    color: #b91c1c;
    font-size: 0.8125rem;
    text-align: center;
    padding: 0 0.5rem;
  }
</style>
