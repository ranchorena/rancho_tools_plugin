<script>
  import { createEventDispatcher, onDestroy, onMount } from 'svelte';
  import { GOOGLE_MAPS_API_KEY } from './config.js';
  import DialogHeader from './design-system/DialogHeader.svelte';
  import Icon from './design-system/Icon.svelte';
  import { dialogFocus } from './design-system/dialog-focus.mjs';
  import { STREET_VIEW_RADIUS_METERS, streetViewEmbedUrl } from './street-view.mjs';
  import { loadGoogleMaps, queryNearestPanorama } from './street-view-client.mjs';

  export let lat;
  export let lon;

  const dispatch = createEventDispatcher();

  let state = 'loading';
  let embedUrl = '';
  let alive = true;

  onDestroy(() => {
    alive = false;
  });

  onMount(async () => {
    try {
      const maps = await loadGoogleMaps(GOOGLE_MAPS_API_KEY);
      if (!alive) return;
      const result = await queryNearestPanorama(maps, { lat, lon });
      if (!alive) return;
      if (result.state === 'ready') {
        embedUrl = streetViewEmbedUrl({
          apiKey: GOOGLE_MAPS_API_KEY,
          panoId: result.panorama.panoId
        });
        state = 'ready';
      } else if (result.state === 'missing') {
        state = 'missing';
      } else {
        state = 'error';
      }
    } catch {
      if (alive) state = 'error';
    }
  });

  function closeDialog() {
    dispatch('close');
  }
</script>

<div
  class="modal-backdrop"
  on:click={closeDialog}
  on:keydown={(event) => event.key === 'Escape' && closeDialog()}
  role="button"
  tabindex="0"
  aria-label="Cerrar Street View"
>
  <div
    class="modal-content"
    use:dialogFocus
    on:click|stopPropagation
    on:keydown|stopPropagation
    role="dialog"
    aria-labelledby="street-view-title"
    aria-busy={state === 'loading'}
  >
    <div class="modal-header">
      <DialogHeader titleId="street-view-title">
        <Icon name="person" size={18} />
        Calle
        <button slot="close" type="button" class="close-button ds-button ds-button--icon ds-focus" on:click={closeDialog} aria-label="Cerrar">
          <Icon name="close" size={16} />
        </button>
      </DialogHeader>
    </div>

    <div class="modal-body">
      {#if state === 'ready'}
        <iframe
          title="Foto de la calle"
          src={embedUrl}
          loading="lazy"
          referrerpolicy="strict-origin-when-cross-origin"
          allowfullscreen
        ></iframe>
      {:else}
        <p class="status" role="status">
          {#if state === 'loading'}
            Buscando la foto de esta calle…
          {:else if state === 'missing'}
            Google no tiene foto de esta calle. Probá un punto sobre la calzada, a menos de {STREET_VIEW_RADIUS_METERS} metros.
          {:else}
            No se pudo consultar Street View. Revisá la conexión y la clave de Google.
          {/if}
        </p>
      {/if}
    </div>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1100;
    padding: 1rem;
    box-sizing: border-box;
  }

  .modal-content {
    background-color: var(--ds-surface);
    color: var(--ds-text);
    border-radius: 12px;
    box-shadow: var(--ds-shadow-dialog);
    width: 100%;
    max-width: 920px;
    height: min(78vh, 640px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .modal-header {
    box-shadow: inset 0 -1px var(--ds-divider);
    flex-shrink: 0;
  }

  .close-button {
    box-sizing: border-box;
    min-height: 32px;
    margin: 0;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    line-height: 1;
    color: var(--ds-text-muted);
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close-button:hover {
    color: var(--ds-on-secondary);
    background-color: var(--ds-secondary-hover);
  }

  .modal-body {
    flex: 1;
    min-height: 0;
    display: flex;
  }

  iframe {
    flex: 1;
    width: 100%;
    border: 0;
    background: var(--ds-background);
  }

  .status {
    margin: auto;
    max-width: 36rem;
    padding: 1.5rem;
    text-align: left;
    line-height: 1.45;
  }

  @media (max-width: 768px) {
    .modal-backdrop {
      padding: 0.5rem;
    }

    .modal-content {
      height: min(88vh, 720px);
    }

    .close-button {
      min-width: 44px;
      min-height: 44px;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .modal-content {
      animation: none;
    }
  }
</style>
