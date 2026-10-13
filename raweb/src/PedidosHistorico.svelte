<script>
  import { API_BASE_URL } from './config.js';
  import { createEventDispatcher } from 'svelte';
  import DialogHeader from './design-system/DialogHeader.svelte';
  import Icon from './design-system/Icon.svelte';
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

  function alCambiarDesde(event) {
    fechaHasta = event.currentTarget.value;
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

  let eliminandoId = null;
  let pedidoAEliminar = null;

  function pedirEliminar(pedido) {
    if (eliminandoId !== null) return;
    pedidoAEliminar = pedido;
  }

  function cancelarEliminar() {
    if (eliminandoId !== null) return;
    pedidoAEliminar = null;
  }

  async function eliminar_pedido() {
    const pedido = pedidoAEliminar;
    if (!pedido || eliminandoId !== null) return;

    eliminandoId = pedido.id;
    errorMessage = "";
    try {
      const response = await fetch(`${API_BASE_URL}/api/pedidos/eliminar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_pedido: pedido.id })
      });
      const body = await response.json().catch(() => ({ error: "Error desconocido" }));
      if (!response.ok) {
        throw new Error(body.error || `Error ${response.status}: ${response.statusText}`);
      }
      pedidos = pedidos.filter((item) => item.id !== pedido.id);
      calcularEstadisticas();
      if (pedidos.length === 0) {
        errorMessage = "No se encontraron pedidos para las fechas indicadas.";
      }
      dispatch('refreshPedidosLayer');
      dispatch('showGlobalNotification', {
        message: body.mensaje || 'Pedido eliminado correctamente.',
        type: 'success'
      });
      pedidoAEliminar = null;
    } catch (err) {
      errorMessage = err.message;
      console.error("Error al eliminar pedido:", err);
    } finally {
      eliminandoId = null;
    }
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
    box-shadow: var(--ds-shadow-dialog);
    width: 100%;
    max-width: 1100px;
    max-height: 95vh;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
  }

  .modal-header {
    box-shadow: inset 0 -1px var(--ds-divider);
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
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
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
    margin: 0 0 0.85rem 0;
    font-size: var(--ds-type-section);
    font-weight: 600;
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
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
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
    outline: 2px solid var(--ds-focus);
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
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
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

  .eliminar-btn {
    color: var(--ds-text-muted);
  }

  .eliminar-btn:hover:not(:disabled) {
    color: var(--ds-error);
  }

  .confirm-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1102;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    box-sizing: border-box;
    background-color: rgba(0, 0, 0, 0.45);
  }

  .confirm-dialog {
    width: 100%;
    max-width: 26rem;
    background-color: var(--ds-surface);
    color: var(--ds-text);
    border-radius: 12px;
    box-shadow: var(--ds-shadow-dialog);
    overflow: hidden;
  }

  .confirm-body {
    padding: 1rem 1.25rem 1.25rem;
  }

  .confirm-body p {
    margin: 0;
    line-height: 1.45;
  }

  .confirm-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 1.25rem;
  }

  .confirm-actions button {
    font: inherit;
    font-weight: 600;
    border-radius: 6px;
    padding: 0.45rem 0.9rem;
    cursor: pointer;
    width: auto;
  }

  .confirm-cancelar {
    color: var(--ds-text);
    background: transparent;
    border: 1px solid var(--ds-divider);
  }

  .confirm-eliminar {
    color: var(--ds-error);
    background: var(--ds-error-surface);
    border: 1px solid var(--ds-error);
  }

  .confirm-actions button:disabled {
    cursor: default;
    opacity: 0.7;
  }
</style>

<div class="modal-backdrop"
     on:click={() => !pedidoAEliminar && dispatch('close')}
     on:keydown={(e) => e.key === 'Escape' && !pedidoAEliminar && dispatch('close')}
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
        <Icon name="history" size={18} />
        Pedidos histórico
        <svelte:fragment slot="close">
          <button type="button" class="close-button ds-button ds-button--icon ds-focus" on:click={() => dispatch('close')} aria-label="Cerrar"><Icon name="close" size={16} /></button>
        </svelte:fragment>
      </DialogHeader>
    </div>

    <div class="modal-body">
      <form class="filtros-fecha" on:submit|preventDefault={buscar}>
        <label>
          Desde
          <input type="date" bind:value={fechaDesde} on:change={alCambiarDesde} />
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
                  <th></th>
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
                    <td>
                      <button
                        type="button"
                        class="eliminar-btn ds-button ds-button--icon ds-focus"
                        aria-label="Eliminar pedido"
                        disabled={eliminandoId === pedido.id}
                        on:click|stopPropagation={() => pedirEliminar(pedido)}
                      >
                        <Icon name="trash" size={16} />
                      </button>
                    </td>
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

{#if pedidoAEliminar}
  <div class="confirm-backdrop"
       on:click={cancelarEliminar}
       on:keydown={(e) => e.key === 'Escape' && cancelarEliminar()}
       role="presentation">
    <div class="confirm-dialog"
         on:click|stopPropagation
         on:keydown|stopPropagation={(e) => e.key === 'Escape' && cancelarEliminar()}
         use:dialogFocus
         role="dialog"
         aria-modal="true"
         aria-labelledby="eliminar-pedido-title">
      <div class="modal-header">
        <DialogHeader titleId="eliminar-pedido-title">
          <Icon name="trash" size={18} />
          Eliminar pedido
          <svelte:fragment slot="close">
            <button type="button" class="close-button ds-button ds-button--icon ds-focus" on:click={cancelarEliminar} aria-label="Cerrar" disabled={eliminandoId !== null}><Icon name="close" size={16} /></button>
          </svelte:fragment>
        </DialogHeader>
      </div>
      <div class="confirm-body">
        <p>¿Eliminar el pedido de {pedidoAEliminar.nombre || `pedido ${pedidoAEliminar.id}`}? El cliente quedará sin pedido activo.</p>
        <div class="confirm-actions">
          <button type="button" class="confirm-cancelar ds-focus" data-dialog-initial-focus on:click={cancelarEliminar} disabled={eliminandoId !== null}>Cancelar</button>
          <button type="button" class="confirm-eliminar ds-focus" on:click={eliminar_pedido} disabled={eliminandoId !== null}>Eliminar</button>
        </div>
      </div>
    </div>
  </div>
{/if}
