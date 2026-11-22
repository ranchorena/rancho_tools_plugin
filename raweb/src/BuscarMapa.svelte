<script>
  import { onDestroy, onMount, tick } from 'svelte';
  import { API_BASE_URL } from './config.js';
  import { authorizedFetch } from './auth/session.mjs';
  import { mapSearchPath, SEARCH_DEBOUNCE_MS } from './map-search.mjs';
  import UiIcon from './design-system/Icon.svelte';
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let barraVisible = true;
  let campo;
  let texto = '';
  let pedidos = [];
  let clientes = [];
  let abierta = false;
  let buscando = false;
  let sinResultados = false;
  let error = '';
  let indice = -1;
  let timer;
  let controlador;
  let raiz;
  let secuencia = 0;

  function filas() {
    return [
      ...pedidos.map((item) => ({ ...item, grupo: 'pedido' })),
      ...clientes.map((item) => ({ ...item, grupo: 'cliente' }))
    ];
  }

  function cancelarConsulta() {
    clearTimeout(timer);
    if (controlador) {
      controlador.abort();
      controlador = null;
    }
  }

  function cerrarLista() {
    abierta = false;
    indice = -1;
  }

  function programar() {
    cancelarConsulta();
    const ruta = mapSearchPath(texto);
    if (!ruta) {
      pedidos = [];
      clientes = [];
      sinResultados = false;
      error = '';
      buscando = false;
      cerrarLista();
      return;
    }
    timer = setTimeout(() => consultar(ruta), SEARCH_DEBOUNCE_MS);
  }

  async function consultar(ruta) {
    const actual = ++secuencia;
    if (controlador) controlador.abort();
    controlador = new AbortController();
    const signal = controlador.signal;
    buscando = true;
    error = '';
    if (pedidos.length === 0 && clientes.length === 0) abierta = true;
    try {
      const response = await authorizedFetch(`${API_BASE_URL}${ruta}`, { signal });
      if (actual !== secuencia) return;
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        error = data.error || 'No se pudo buscar.';
        pedidos = [];
        clientes = [];
        sinResultados = false;
        indice = -1;
        abierta = true;
        return;
      }
      pedidos = Array.isArray(data.pedidos) ? data.pedidos : [];
      clientes = Array.isArray(data.clientes) ? data.clientes : [];
      sinResultados = pedidos.length === 0 && clientes.length === 0;
      error = '';
      indice = filas().length > 0 ? 0 : -1;
      abierta = true;
    } catch (causa) {
      if (causa && causa.name === 'AbortError') return;
      if (actual !== secuencia) return;
      error = 'No se pudo buscar.';
      pedidos = [];
      clientes = [];
      sinResultados = false;
      indice = -1;
      abierta = true;
    } finally {
      if (actual === secuencia) buscando = false;
    }
  }

  function elegir(item) {
    const longitud = Number(item.longitud);
    const latitud = Number(item.latitud);
    if (!Number.isFinite(longitud) || !Number.isFinite(latitud)) return;
    secuencia += 1;
    cancelarConsulta();
    buscando = false;
    texto = item.nombre || texto;
    cerrarLista();
    dispatch('zoom', { longitude: longitud, latitude: latitud, marker: 'medialuna' });
  }

  async function alternarBarra() {
    if (barraVisible) {
      secuencia += 1;
      cancelarConsulta();
      buscando = false;
      cerrarLista();
      barraVisible = false;
      return;
    }
    barraVisible = true;
    await tick();
    campo?.focus();
  }

  function limpiar() {
    secuencia += 1;
    cancelarConsulta();
    texto = '';
    pedidos = [];
    clientes = [];
    sinResultados = false;
    error = '';
    buscando = false;
    cerrarLista();
  }

  function alTeclado(event) {
    if (event.key === 'Escape') {
      if (!abierta) return;
      event.preventDefault();
      cerrarLista();
      return;
    }
    const opciones = filas();
    if (!abierta || opciones.length === 0) return;
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      indice = indice < opciones.length - 1 ? indice + 1 : 0;
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      indice = indice > 0 ? indice - 1 : opciones.length - 1;
    } else if (event.key === 'Enter' && indice >= 0) {
      event.preventDefault();
      elegir(opciones[indice]);
    }
  }

  function clicFuera(event) {
    if (!abierta || !raiz || raiz.contains(event.target)) return;
    cerrarLista();
  }

  onMount(() => {
    window.addEventListener('pointerdown', clicFuera);
  });

  onDestroy(() => {
    window.removeEventListener('pointerdown', clicFuera);
    secuencia += 1;
    cancelarConsulta();
  });
</script>

<div class="mapa-buscar" class:colapsada={!barraVisible} bind:this={raiz}>
  <div class="mapa-buscar-caja">
    <button
      type="button"
      class="mapa-buscar-lupa"
      aria-label={barraVisible ? 'Ocultar búsqueda' : 'Buscar cliente o pedido'}
      aria-expanded={barraVisible}
      on:click={alternarBarra}
    >
      <UiIcon name="search" size={18} />
    </button>
    {#if barraVisible}
    <input
      type="text"
      class="mapa-buscar-input"
      placeholder="Buscar cliente o pedido"
      aria-label="Buscar cliente o pedido"
      role="combobox"
      aria-autocomplete="list"
      aria-expanded={abierta}
      aria-controls="mapa-buscar-lista"
      aria-activedescendant={abierta && indice >= 0 ? `mapa-opcion-${indice}` : undefined}
      bind:this={campo}
      bind:value={texto}
      on:input={programar}
      on:keydown={alTeclado}
    />
    {/if}
    {#if barraVisible && texto}
      <button type="button" class="mapa-buscar-limpiar" aria-label="Limpiar búsqueda" on:click={limpiar}>
        <UiIcon name="close" size={16} />
      </button>
    {/if}
  </div>

  {#if barraVisible && abierta}
    <div class="mapa-buscar-lista" id="mapa-buscar-lista" role="listbox" aria-label="Resultados">
      {#if error}
        <p class="mapa-buscar-aviso">{error}</p>
      {:else if sinResultados}
        <p class="mapa-buscar-aviso">Sin resultados</p>
      {:else}
        {#if buscando && pedidos.length === 0 && clientes.length === 0}
          <p class="mapa-buscar-aviso">Buscando…</p>
        {/if}
        {#if pedidos.length > 0}
          <div class="mapa-buscar-grupo">Pedidos</div>
          {#each pedidos as item, i (item.id)}
            <button
              type="button"
              class="mapa-buscar-fila"
              class:activa={indice === i}
              id="mapa-opcion-{i}"
              role="option"
              aria-selected={indice === i}
              on:click={() => elegir(item)}
              on:mouseenter={() => indice = i}
            >
              <span class="mapa-buscar-marca" aria-hidden="true"><UiIcon name="box" size={16} /></span>
              <span class="mapa-buscar-texto">
                <span class="mapa-buscar-nombre">{item.nombre || 'Sin nombre'}</span>
                {#if item.direccion}<span class="mapa-buscar-direccion">{item.direccion}</span>{/if}
              </span>
            </button>
          {/each}
        {/if}
        {#if clientes.length > 0}
          <div class="mapa-buscar-grupo">Clientes</div>
          {#each clientes as item, i (item.id)}
            <button
              type="button"
              class="mapa-buscar-fila"
              class:activa={indice === pedidos.length + i}
              id="mapa-opcion-{pedidos.length + i}"
              role="option"
              aria-selected={indice === pedidos.length + i}
              on:click={() => elegir(item)}
              on:mouseenter={() => indice = pedidos.length + i}
            >
              <span class="mapa-buscar-marca" aria-hidden="true"><UiIcon name="user" size={16} /></span>
              <span class="mapa-buscar-texto">
                <span class="mapa-buscar-nombre">{item.nombre || 'Sin nombre'}</span>
                {#if item.direccion}<span class="mapa-buscar-direccion">{item.direccion}</span>{/if}
              </span>
            </button>
          {/each}
        {/if}
      {/if}
    </div>
  {/if}
</div>

<style>
  .mapa-buscar {
    position: absolute;
    z-index: 1100;
    top: 0.75rem;
    /* Zoom: 0.75rem + 30px de botón + 2px de borde, y un hueco de 0.75rem. */
    left: calc(0.75rem + 32px + 0.75rem);
    width: min(24rem, calc(100% - 3rem - 76px));
    pointer-events: auto;
  }

  .mapa-buscar-caja {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    min-height: 44px;
    padding: 0 0.85rem;
    background: var(--ds-surface);
    color: var(--ds-text);
    border: 1px solid var(--ds-border);
    border-radius: 999px;
    box-shadow: var(--ds-shadow-panel);
  }

  .mapa-buscar-caja:focus-within {
    border-color: var(--ds-focus);
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
  }

  .mapa-buscar.colapsada {
    width: auto;
  }

  .mapa-buscar.colapsada .mapa-buscar-caja {
    width: 44px;
    height: 44px;
    min-height: 44px;
    padding: 0;
    justify-content: center;
    gap: 0;
  }

  .mapa-buscar-lupa {
    display: flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    width: 28px;
    min-width: 28px;
    height: 28px;
    min-height: 28px;
    margin: 0;
    padding: 0;
    border: 0;
    border-radius: 999px;
    background: transparent;
    color: var(--ds-text-muted);
  }

  .mapa-buscar-lupa:hover:not(:disabled) {
    background: var(--ds-secondary-hover);
    color: var(--ds-text);
  }

  .mapa-buscar.colapsada .mapa-buscar-lupa {
    width: 44px;
    height: 44px;
    min-width: 44px;
    min-height: 44px;
    color: var(--ds-text);
  }

  .mapa-buscar-lupa:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
  }

  .mapa-buscar-input {
    flex: 1 1 auto;
    width: auto;
    min-width: 0;
    min-height: 0;
    margin: 0;
    padding: 0;
    border: 0;
    border-radius: 0;
    background: transparent;
    box-shadow: none;
    color: var(--ds-text);
    font-size: 1rem;
  }

  .mapa-buscar-input:focus-visible {
    outline: none;
    border: 0;
    box-shadow: none;
  }

  .mapa-buscar-limpiar {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    min-width: 28px;
    height: 28px;
    min-height: 28px;
    margin: 0;
    padding: 0;
    border: 0;
    border-radius: 999px;
    background: transparent;
    color: var(--ds-text-muted);
  }

  .mapa-buscar-limpiar:hover:not(:disabled) {
    background: var(--ds-secondary-hover);
    color: var(--ds-text);
  }

  .mapa-buscar-lista {
    margin-top: 0.4rem;
    max-height: min(24rem, 50dvh);
    overflow: auto;
    background: var(--ds-surface);
    color: var(--ds-text);
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-medium);
    box-shadow: var(--ds-shadow-panel);
    padding: 0.35rem 0;
  }

  .mapa-buscar-grupo {
    padding: 0.45rem 0.9rem 0.2rem;
    color: var(--ds-text-muted);
    font-size: 0.75rem;
    font-weight: 600;
  }

  .mapa-buscar-fila {
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    width: 100%;
    min-height: 44px;
    margin: 0;
    padding: 0.45rem 0.9rem;
    border: 0;
    border-radius: 0;
    background: transparent;
    color: var(--ds-text);
    text-align: left;
    font-weight: 500;
  }

  .mapa-buscar-fila:hover:not(:disabled),
  .mapa-buscar-fila.activa {
    background: var(--ds-secondary-hover);
  }

  .mapa-buscar-fila:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: -2px;
  }

  .mapa-buscar-marca {
    display: flex;
    flex: 0 0 auto;
    margin-top: 0.15rem;
    color: var(--ds-text-muted);
  }

  .mapa-buscar-texto {
    display: flex;
    flex-direction: column;
    min-width: 0;
  }

  .mapa-buscar-nombre,
  .mapa-buscar-direccion {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .mapa-buscar-direccion {
    color: var(--ds-text-muted);
    font-size: 0.8125rem;
    font-weight: 400;
  }

  .mapa-buscar-aviso {
    margin: 0;
    padding: 0.7rem 0.9rem;
    color: var(--ds-text-muted);
  }

  @media (max-width: 768px) {
    .mapa-buscar {
      top: 0.25rem;
      left: calc(0.25rem + 30px + 0.65rem);
      width: min(24rem, calc(100% - 0.25rem - 30px - 0.65rem - 44px - 1rem));
    }

    .mapa-buscar-input {
      margin: 0;
      padding: 0;
      font-size: 16px;
    }

    .mapa-buscar-lupa,
    .mapa-buscar-limpiar,
    .mapa-buscar-fila {
      margin: 0;
      padding: 0;
    }
  }
</style>
