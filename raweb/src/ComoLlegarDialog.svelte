<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { API_BASE_URL } from './config.js';
  import { authorizedFetch } from './auth/session.mjs';
  import DialogHeader from './design-system/DialogHeader.svelte';
  import Icon from './design-system/Icon.svelte';
  import { dialogFocus } from './design-system/dialog-focus.mjs';
  import { buildRoutePayload, formatCoordinates, swapPoints } from './route-planner.mjs';

  export let ubicacionActiva = false;
  export let ubicacionActual = null;
  export let puntoSeleccionado = null; // { rol: 'origen' | 'destino', lat, lon }
  export let seleccionando = false;
  export let puntosIniciales = null; // { origen, destino } del último recorrido

  const dispatch = createEventDispatcher();
  const MI_UBICACION = 'Mi ubicación';

  let origen = puntosIniciales?.origen ?? null;
  let destino = puntosIniciales?.destino ?? null;
  let origenTexto = origen?.label ?? '';
  let destinoTexto = destino?.label ?? '';
  let buscando = null;
  let calculando = false;
  let mensajeError = '';
  let ultimoPuntoAplicado = puntoSeleccionado;

  $: hayUbicacion = ubicacionActiva && Boolean(ubicacionActual);

  // El origen «Mi ubicación» sigue a la posición del móvil y se vacía si se apaga.
  $: if (origen?.actual) {
    if (hayUbicacion) {
      if (origen.lat !== ubicacionActual.lat || origen.lon !== ubicacionActual.lon) {
        origen = { ...origen, lat: ubicacionActual.lat, lon: ubicacionActual.lon };
      }
    } else {
      origen = null;
      origenTexto = '';
    }
  }

  $: if (puntoSeleccionado && puntoSeleccionado !== ultimoPuntoAplicado) {
    ultimoPuntoAplicado = puntoSeleccionado;
    const { rol, lat, lon } = puntoSeleccionado;
    fijarPunto(rol, { lat, lon, label: formatCoordinates({ lat, lon }) });
  }

  onMount(() => {
    if (!origen && hayUbicacion) usarMiUbicacion();
  });

  function fijarPunto(rol, punto) {
    mensajeError = '';
    if (rol === 'origen') {
      origen = punto;
      origenTexto = punto?.label ?? '';
    } else {
      destino = punto;
      destinoTexto = punto?.label ?? '';
    }
  }

  function usarMiUbicacion() {
    if (!hayUbicacion) return;
    fijarPunto('origen', {
      lat: ubicacionActual.lat,
      lon: ubicacionActual.lon,
      label: MI_UBICACION,
      actual: true
    });
  }

  function editarTexto(rol) {
    const punto = rol === 'origen' ? origen : destino;
    const texto = rol === 'origen' ? origenTexto : destinoTexto;
    if (punto && texto !== punto.label) {
      if (rol === 'origen') origen = null;
      else destino = null;
    }
  }

  async function buscarDireccion(rol) {
    const direccion = (rol === 'origen' ? origenTexto : destinoTexto).trim();
    if (!direccion) {
      mensajeError = `Ingresá una dirección para el ${rol}.`;
      return;
    }
    buscando = rol;
    mensajeError = '';
    try {
      const response = await authorizedFetch(`${API_BASE_URL}/api/direcciones/buscar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direccion })
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !Number.isFinite(data.latitud) || !Number.isFinite(data.longitud)) {
        mensajeError = data.error || 'No se pudo encontrar la dirección.';
        return;
      }
      fijarPunto(rol, { lat: data.latitud, lon: data.longitud, label: direccion });
    } catch (error) {
      console.error('Error al buscar dirección:', error);
      mensajeError = 'No se pudo buscar la dirección.';
    } finally {
      buscando = null;
    }
  }

  function elegirEnMapa(rol) {
    mensajeError = '';
    dispatch('seleccionarPunto', { rol });
  }

  function intercambiar() {
    const swapped = swapPoints(origen, destino);
    origen = swapped.origin;
    destino = swapped.destination ? { ...swapped.destination, actual: false } : null;
    [origenTexto, destinoTexto] = [destinoTexto, origenTexto];
  }

  async function verRecorrido() {
    const request = buildRoutePayload(origen, destino);
    if (!request.ok) {
      mensajeError = request.message;
      return;
    }
    calculando = true;
    mensajeError = '';
    try {
      const response = await authorizedFetch(`${API_BASE_URL}/api/rutas/calcular`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request.payload)
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.geometria) {
        mensajeError = data.error || 'No se pudo calcular el recorrido.';
        return;
      }
      dispatch('mostrarRuta', { ruta: data, origen, destino });
    } catch (error) {
      console.error('Error al calcular el recorrido:', error);
      mensajeError = 'No se pudo calcular el recorrido.';
    } finally {
      calculando = false;
    }
  }

  function handleKeydown(event, rol) {
    if (event.key === 'Enter') {
      event.preventDefault();
      buscarDireccion(rol);
    }
    if (event.key === 'Escape') handleCancelar();
  }

  function handleCancelar() {
    dispatch('close');
  }
</script>

<div class="modal-backdrop"
     class:seleccionando-punto={seleccionando}
     on:click={handleCancelar}
     on:keydown={(e) => e.key === 'Escape' && handleCancelar()}
     role="button"
     tabindex="0"
     aria-label="Cerrar modal">
  <div class="modal-content"
       use:dialogFocus
       on:click|stopPropagation
       on:keydown|stopPropagation
       role="dialog"
       aria-labelledby="como-llegar-title">
    <div class="modal-header">
      <DialogHeader titleId="como-llegar-title">
        <Icon name="route" size={18} />
        Cómo llegar
        <button slot="close" type="button" class="close-button ds-button ds-button--icon ds-focus" on:click={handleCancelar} aria-label="Cerrar">
          <Icon name="close" size={16} />
        </button>
      </DialogHeader>
    </div>

    <div class="modal-body">
      <div class="route-grid">
        <div class="route-points">
          <div class="point-row">
            <label for="origen-input" class="point-label">Origen</label>
            <div class="point-field">
              <input
                id="origen-input"
                data-dialog-initial-focus
                class="ds-field"
                type="text"
                bind:value={origenTexto}
                on:input={() => editarTexto('origen')}
                on:keydown={(e) => handleKeydown(e, 'origen')}
                placeholder="Dirección, ej: SARMIENTO 550"
                autocomplete="off"
              />
              <button type="button" class="icon-btn ds-button" on:click={() => buscarDireccion('origen')}
                      disabled={buscando === 'origen'} title="Buscar dirección de origen" aria-label="Buscar dirección de origen">
                <Icon name="search" size={16} />
              </button>
              <button type="button" class="icon-btn ds-button" on:click={() => elegirEnMapa('origen')}
                      title="Elegir origen en el mapa" aria-label="Elegir origen en el mapa">
                <Icon name="pin" size={16} />
              </button>
              <button type="button" class="icon-btn ds-button" class:ds-button--location={origen?.actual}
                      on:click={usarMiUbicacion} disabled={!hayUbicacion}
                      title={hayUbicacion ? 'Usar mi ubicación como origen' : 'Activá la posición del móvil para usarla como origen'}
                      aria-label="Usar mi ubicación como origen" aria-pressed={Boolean(origen?.actual)}>
                <Icon name="locate" size={16} />
              </button>
            </div>
          </div>

          <div class="point-row">
            <label for="destino-input" class="point-label">Destino</label>
            <div class="point-field">
              <input
                id="destino-input"
                class="ds-field"
                type="text"
                bind:value={destinoTexto}
                on:input={() => editarTexto('destino')}
                on:keydown={(e) => handleKeydown(e, 'destino')}
                placeholder="Dirección, ej: ITALIA 50"
                autocomplete="off"
              />
              <button type="button" class="icon-btn ds-button" on:click={() => buscarDireccion('destino')}
                      disabled={buscando === 'destino'} title="Buscar dirección de destino" aria-label="Buscar dirección de destino">
                <Icon name="search" size={16} />
              </button>
              <button type="button" class="icon-btn ds-button" on:click={() => elegirEnMapa('destino')}
                      title="Elegir destino en el mapa" aria-label="Elegir destino en el mapa">
                <Icon name="pin" size={16} />
              </button>
            </div>
          </div>
        </div>

        <button type="button" class="swap-btn ds-button ds-button--icon ds-focus" on:click={intercambiar}
                title="Intercambiar origen y destino" aria-label="Intercambiar origen y destino">
          <Icon name="swap" size={18} />
        </button>
      </div>

      {#if !hayUbicacion}
        <p class="hint">Para usar tu ubicación como origen, activá la posición del móvil en el mapa.</p>
      {/if}
      {#if mensajeError}
        <p class="error" role="alert">{mensajeError}</p>
      {/if}
    </div>

    <div class="modal-footer">
      <button type="button" class="btn-primary ds-button ds-button--primary" on:click={verRecorrido}
              disabled={!buildRoutePayload(origen, destino).ok || calculando || Boolean(buscando)}>
        <Icon name="route" size={16} />
        {calculando ? 'Calculando…' : 'Ver recorrido'}
      </button>
    </div>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1001;
    padding: 1rem;
    box-sizing: border-box;
    backdrop-filter: blur(2px);
  }

  /* Al elegir un punto, el clic tiene que llegar al viewport de OpenLayers. */
  .modal-backdrop.seleccionando-punto {
    pointer-events: none;
    background: transparent;
    backdrop-filter: none;
  }

  .modal-backdrop.seleccionando-punto .modal-content {
    visibility: hidden;
  }

  .modal-content {
    background-color: var(--ds-surface);
    color: var(--ds-text);
    border-radius: 12px;
    box-shadow: var(--ds-shadow-dialog);
    width: 100%;
    max-width: 520px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    animation: modalSlideIn 0.3s ease-out;
  }

  @keyframes modalSlideIn {
    from {
      opacity: 0;
      transform: scale(0.9) translateY(-20px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
  }

  .modal-header {
    box-shadow: inset 0 -1px var(--ds-divider);
    flex-shrink: 0;
    color: var(--ds-text);
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
    transition: all 0.2s ease;
  }

  .close-button:hover {
    color: var(--ds-on-secondary);
    background-color: var(--ds-secondary-hover);
  }

  .modal-body {
    padding: 1rem 1.5rem;
    flex-grow: 1;
    overflow-y: auto;
  }

  .route-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    align-items: center;
    gap: 0.5rem;
  }

  .route-points {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    min-width: 0;
  }

  .point-row {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
  }

  .point-label {
    font-weight: 600;
    color: var(--ds-text);
    font-size: var(--ds-type-label);
  }

  .point-field {
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }

  .point-field input[type="text"] {
    flex: 1 1 auto;
    min-width: 0;
    min-height: 2.625rem;
    padding: 0.55rem 0.75rem;
    border: 1px solid var(--ds-border);
    border-radius: 999px;
    font-size: var(--ds-type-body);
    background: var(--ds-background);
    color: var(--ds-text);
    box-sizing: border-box;
    margin: 0;
  }

  .point-field input[type="text"]:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
    border-color: var(--ds-focus);
    box-shadow: none;
  }

  .icon-btn {
    flex: 0 0 auto;
    width: 2.5rem;
    height: 2.5rem;
    min-height: 2.5rem;
    margin: 0;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-round);
    cursor: pointer;
  }

  .icon-btn:disabled {
    cursor: not-allowed;
  }

  .swap-btn {
    width: 2.5rem;
    height: 2.5rem;
    margin: 1.2rem 0 0;
    padding: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--ds-radius-round);
    cursor: pointer;
  }

  .hint {
    margin: 0.75rem 0 0;
    color: var(--ds-text-muted);
    font-size: 0.8125rem;
  }

  .error {
    margin: 0.75rem 0 0;
    color: var(--ds-error);
    font-size: 0.875rem;
    font-weight: 600;
  }

  .modal-footer {
    display: flex;
    justify-content: stretch;
    gap: 0.75rem;
    padding: 0.85rem 1.25rem 1.1rem;
    background: var(--ds-background);
    box-shadow: inset 0 1px var(--ds-divider);
    flex-shrink: 0;
  }

  .btn-primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    width: 100%;
    padding: 0.55rem 1rem;
    border-radius: var(--ds-radius-small);
    font-weight: 600;
    cursor: pointer;
    font-size: var(--ds-type-nav);
    min-height: 2.625rem;
  }

  .btn-primary:disabled {
    color: var(--ds-on-disabled);
    background: var(--ds-disabled);
    border-color: var(--ds-border);
    opacity: 1;
    cursor: not-allowed;
  }

  @media (max-width: 768px) {
    .modal-backdrop {
      padding: 0.5rem;
      align-items: flex-start;
      padding-top: 2rem;
    }

    .modal-content {
      max-width: 100%;
      border-radius: 8px;
      max-height: calc(100vh - 3rem);
    }

    .close-button {
      width: 36px;
      height: 36px;
    }

    .modal-body {
      padding: 0.75rem 1rem;
    }

    .modal-footer {
      padding: 0.75rem 1rem 1rem;
    }

    .point-field input[type="text"] {
      font-size: 16px; /* Evita zoom en iOS */
    }
  }

  @media (max-width: 400px) {
    .point-field {
      gap: 0.25rem;
    }

    .icon-btn,
    .swap-btn {
      width: 2.25rem;
      height: 2.25rem;
      min-height: 2.25rem;
    }
  }

  @media (prefers-reduced-motion: reduce) {
    .modal-content {
      animation: none;
    }
  }
</style>
