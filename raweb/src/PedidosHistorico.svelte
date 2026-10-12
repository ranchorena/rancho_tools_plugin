<script>
  import { API_BASE_URL } from './config.js';
  import { createEventDispatcher } from 'svelte';
  import DialogHeader from './design-system/DialogHeader.svelte';
  import { dialogFocus } from './design-system/dialog-focus.mjs';
  import { shouldActivateRow } from './design-system/keyboard.mjs';
  const dispatch = createEventDispatcher();

  let pedidos = [];
  let isLoading = false;
  let errorMessage = "";
  let fechaDesde = "";
  let fechaHasta = "";

  let cantidadTotal = 0;
  let cantidadVendidas = 0;
  let valorTotal = 0;

  async function fetchData(url) {
    isLoading = true;
    errorMessage = "";
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: { "Content-Type": "application/json" }
      });
      const body = await response.json().catch(() => ({ error: "Error desconocido" }));
      if (!response.ok) {
        throw new Error(body.error || `Error ${response.status}: ${response.statusText}`);
      }
      return body;
    } catch (err) {
      errorMessage = err.message;
      console.error("Fetch error:", err);
      return null;
    } finally {
      isLoading = false;
    }
  }

  function aplicarResultado(results) {
    fechaDesde = results.fecha_desde || "";
    fechaHasta = results.fecha_hasta || "";
    pedidos = results.pedidos || [];
    calcularEstadisticas();
    if (!fechaDesde) {
      errorMessage = "No hay pedidos registrados.";
    } else if (pedidos.length === 0) {
      errorMessage = "No se encontraron pedidos para las fechas indicadas.";
    }
  }

  async function loadInicial() {
    const results = await fetchData(`${API_BASE_URL}/api/pedidos/historico`);
    if (results) aplicarResultado(results);
  }

  async function buscar() {
    if (!fechaDesde || !fechaHasta) {
      errorMessage = "Indicá la fecha desde y la fecha hasta.";
      pedidos = [];
      calcularEstadisticas();
      return;
    }
    const params = new URLSearchParams({ desde: fechaDesde, hasta: fechaHasta });
    const results = await fetchData(`${API_BASE_URL}/api/pedidos/historico?${params}`);
    if (results) aplicarResultado(results);
  }

  function calcularEstadisticas() {
    cantidadTotal = 0;
    cantidadVendidas = 0;
    valorTotal = 0;

    pedidos.forEach(pedido => {
      const cantidad = parseFloat(pedido.cantidad) || 0;
      const esRegalo = pedido.es_regalo === 1;
      const precio = parseFloat(pedido.precio_unitario) || 0;
      cantidadTotal += cantidad;
      if (!esRegalo) {
        cantidadVendidas += cantidad;
        valorTotal += cantidad * precio;
      }
    });
  }

  function formatearPrecio(valor) {
    if (valor === null || valor === undefined || valor === "") return "N/A";
    const numero = Number(valor);
    return Number.isFinite(numero) ? numero.toFixed(2) : "N/A";
  }

  function onPedidoClick(pedido) {
    if (pedido.longitud && pedido.latitud) {
      dispatch('zoomToLocation', {
        longitude: pedido.longitud,
        latitude: pedido.latitud
      });
      dispatch('close');
    }
  }

  function verEnMapa() {
    dispatch('verEnMapa', { pedidos });
    dispatch('close');
  }

  function handlePedidoRowKeydown(event, pedido) {
    if (!shouldActivateRow(event.key, event.repeat, event.target === event.currentTarget)) return;
    event.preventDefault();
    onPedidoClick(pedido);
  }

  loadInicial();
</script>

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

  .modal-content {
    background-color: var(--ds-surface);
    color: var(--ds-text);
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    width: 100%;
    max-width: 1100px;
    max-height: 95vh;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }

  .modal-header {
    border-bottom: 1px solid var(--ds-border);
    flex-shrink: 0;
    background-color: var(--ds-surface);
    min-height: 40px;
  }

  .modal-body {
    overflow-y: auto;
    flex-grow: 1;
    padding: 1rem 1.5rem 1.5rem 1.5rem;
  }

  .close-button {
    box-sizing: border-box;
    margin: 0;
    min-height: 32px;
    background: transparent;
    border: none;
    font-size: 1rem;
    cursor: pointer;
    padding: 0.25rem;
    line-height: 1;
    color: var(--ds-text-muted);
    font-weight: normal;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close-button:hover {
    color: var(--ds-on-secondary);
    background-color: var(--ds-secondary-hover);
  }

  .close-button:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
  }

  .modal-header :global(h2) {
    color: var(--ds-text);
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.2;
  }

  h3 {
    color: var(--ds-text);
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    border-bottom: 2px solid var(--ds-border);
    padding-bottom: 0.5rem;
  }

  .filtros-fecha {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    align-items: flex-end;
    margin-bottom: 1rem;
  }

  .filtros-fecha label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    color: var(--ds-text);
    font-size: 0.85rem;
    font-weight: 600;
  }

  .filtros-fecha input {
    font: inherit;
    color: var(--ds-text);
    background: var(--ds-surface);
    border: 1px solid var(--ds-border);
    border-radius: 6px;
    padding: 0.4rem 0.5rem;
  }

  .filtros-fecha button {
    font: inherit;
    font-weight: 600;
    color: var(--ds-on-primary);
    background: var(--ds-primary);
    border: none;
    border-radius: 6px;
    padding: 0.45rem 0.9rem;
    cursor: pointer;
    width: auto;
    align-self: flex-end;
  }

  .filtros-fecha button:focus,
  .filtros-fecha input:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
  }

  .pedidos-section,
  .estadisticas-section {
    margin-bottom: 2rem;
    background-color: var(--ds-surface);
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--ds-border);
  }

  .table-container {
    max-height: 400px;
    overflow: auto;
    border: 1px solid var(--ds-border);
    border-radius: 8px;
    margin-top: 1rem;
    background-color: var(--ds-surface);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    min-width: 900px;
  }

  th, td {
    border-bottom: 1px solid var(--ds-border);
    padding: 0.75rem;
    text-align: left;
    vertical-align: middle;
    color: var(--ds-text);
  }

  th {
    background-color: var(--ds-surface);
    font-weight: 600;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  tbody tr {
    cursor: pointer;
  }

  tbody tr:focus-visible {
    outline: 3px solid var(--ds-focus);
    outline-offset: -3px;
  }

  .message {
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    text-align: center;
    font-weight: 500;
  }

  .error-message {
    background-color: var(--ds-error-surface);
    color: var(--ds-error);
    border: 1px solid var(--ds-error);
  }

  .loading-indicator {
    text-align: center;
    padding: 2rem;
    font-style: italic;
    color: var(--ds-text-muted);
  }

  .estadisticas-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .estadistica-item {
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid var(--ds-border);
    text-align: center;
  }

  .estadistica-label {
    font-size: 0.9rem;
    color: var(--ds-text-muted);
    margin-bottom: 0.5rem;
  }

  .estadistica-valor {
    font-size: 1.5rem;
    font-weight: 600;
  }

  .valor-monetario {
    color: var(--ds-success);
  }

  .ver-mapa-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.75rem;
  }

  .ver-mapa-btn {
    font: inherit;
    font-weight: 600;
    color: var(--ds-on-primary);
    background: var(--ds-primary);
    border: none;
    border-radius: 6px;
    padding: 0.45rem 0.9rem;
    cursor: pointer;
    width: auto;
  }

  .ver-mapa-btn:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
  }

  .pedido-regalo {
    background-color: var(--ds-warning-surface) !important;
  }

  .pedido-regalo td,
  .pedido-regalo:hover td {
    color: var(--ds-warning);
  }

  .pedido-normal:hover {
    background-color: var(--ds-selected) !important;
  }
</style>

<div class="modal-backdrop"
     on:click={() => dispatch('close')}
     on:keydown={(e) => e.key === 'Escape' && dispatch('close')}
     role="button"
     tabindex="0"
     aria-label="Cerrar modal">
  <div class="modal-content"
       on:click|stopPropagation
       on:keydown|stopPropagation
       use:dialogFocus
       role="dialog"
       aria-labelledby="pedidos-historico-title">
    <div class="modal-header">
      <DialogHeader titleId="pedidos-historico-title">
        Pedidos Histórico
        <svelte:fragment slot="close">
          <button type="button" class="close-button ds-focus" on:click={() => dispatch('close')} aria-label="Cerrar">&times;</button>
        </svelte:fragment>
      </DialogHeader>
    </div>

    <div class="modal-body">
      <form class="filtros-fecha" on:submit|preventDefault={buscar}>
        <label>
          Desde
          <input type="date" bind:value={fechaDesde} />
        </label>
        <label>
          Hasta
          <input type="date" bind:value={fechaHasta} />
        </label>
        <button type="submit">Buscar</button>
      </form>

      {#if errorMessage}
        <div class="message error-message">{errorMessage}</div>
      {/if}

      {#if isLoading}
        <div class="loading-indicator">Cargando pedidos...</div>
      {/if}

      <div class="pedidos-section">
        <h3>Pedidos</h3>

        {#if pedidos.length > 0}
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Dirección</th>
                  <th>Cantidad</th>
                  <th>Teléfono</th>
                  <th>Horario</th>
                  <th>Nro. PaO</th>
                  <th>Regalo</th>
                  <th>Precio unitario</th>
                  <th>Observaciones</th>
                </tr>
              </thead>
              <tbody>
                {#each pedidos as pedido (pedido.id)}
                  <tr
                    tabindex="0"
                    on:keydown={(event) => handlePedidoRowKeydown(event, pedido)}
                    on:click={() => onPedidoClick(pedido)}
                    class:pedido-regalo={pedido.es_regalo === 1}
                    class:pedido-normal={pedido.es_regalo !== 1}
                  >
                    <td>{pedido.id}</td>
                    <td>{pedido.nombre || 'N/A'}</td>
                    <td>{pedido.direccion || 'N/A'}</td>
                    <td>{pedido.cantidad || 0}</td>
                    <td>{pedido.telefono || 'N/A'}</td>
                    <td>{pedido.horario || 'N/A'}</td>
                    <td>{pedido.nro_pao || 'N/A'}</td>
                    <td>{pedido.es_regalo === 1 ? 'Sí' : 'No'}</td>
                    <td>{formatearPrecio(pedido.precio_unitario)}</td>
                    <td>{pedido.observacion || 'N/A'}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
          <p style="font-size: 0.8rem; color: var(--ds-text-muted); margin-top: 0.5rem; text-align: center;">
            Haz click en una fila para hacer zoom en el mapa | Pedidos regalo marcados en amarillo
          </p>
          <div class="ver-mapa-row">
            <button type="button" class="ver-mapa-btn" on:click={verEnMapa}>Ver en Mapa</button>
          </div>
        {/if}
      </div>

      {#if pedidos.length > 0}
        <div class="estadisticas-section">
          <h3>Estadísticas</h3>
          <div class="estadisticas-grid">
            <div class="estadistica-item">
              <div class="estadistica-label">Cantidad Total</div>
              <div class="estadistica-valor">{cantidadTotal.toFixed(1)}</div>
            </div>
            <div class="estadistica-item">
              <div class="estadistica-label">Cantidad Vendidas</div>
              <div class="estadistica-valor">{cantidadVendidas.toFixed(1)}</div>
            </div>
            <div class="estadistica-item">
              <div class="estadistica-label">Valor Total</div>
              <div class="estadistica-valor valor-monetario">$ {valorTotal.toFixed(2)}</div>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
