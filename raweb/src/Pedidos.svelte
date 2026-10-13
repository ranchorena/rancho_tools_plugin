<script>
  import { API_BASE_URL } from './config.js';
  import { createEventDispatcher } from 'svelte';
  import DialogHeader from './design-system/DialogHeader.svelte';
  import Icon from './design-system/Icon.svelte';
  import { dialogFocus } from './design-system/dialog-focus.mjs';
  import { shouldActivateRow } from './design-system/keyboard.mjs';
  const dispatch = createEventDispatcher();

  // Variables de estado
  let pedidos = []; // Array de clientes con pedidos
  let isLoading = false;
  let errorMessage = "";

  // Variables para estadísticas
  let cantidadTotal = 0;
  let cantidadVendidas = 0;
  let valorTotal = 0;
  const PRECIO_DOCENA = 500; // Obtenido del archivo rancho_tools_plugin.ini

  async function fetchData(url, options) {
    isLoading = true;
    errorMessage = "";
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: "Error desconocido" }));
        throw new Error(errorData.error || `Error ${response.status}: ${response.statusText}`);
      }
      return await response.json();
    } catch (err) {
      errorMessage = err.message;
      console.error("Fetch error:", err);
      return null;
    } finally {
      isLoading = false;
    }
  }

  async function loadPedidos() {
    const results = await fetchData(`${API_BASE_URL}/api/clientes/pedidos`, {
      method: "GET",
      headers: { "Content-Type": "application/json" }
    });
    
    if (results) {
      pedidos = Array.isArray(results) ? results : [];
      calcularEstadisticas();
      if (pedidos.length === 0) {
        errorMessage = "No se encontraron clientes con pedidos.";
      }
    }
  }

  function calcularEstadisticas() {
    cantidadTotal = 0;
    cantidadVendidas = 0;
    valorTotal = 0;

    pedidos.forEach(pedido => {
      const cantidad = parseFloat(pedido.cantidad) || 0;
      const esRegalo = pedido.es_regalo === 1;
      
      cantidadTotal += cantidad;
      if (!esRegalo) {
        cantidadVendidas += cantidad;
      }
      valorTotal += cantidad * PRECIO_DOCENA;
    });
  }

  function onPedidoClick(pedido) {
    // Hacer zoom al cliente en el mapa
    if (pedido.longitud && pedido.latitud) {
      dispatch('zoomToLocation', {
        longitude: pedido.longitud,
        latitude: pedido.latitud
      });
      // Cerrar el formulario para permitir visualizar el mapa
      dispatch('close');
    }
  }

  function handlePedidoRowKeydown(event, pedido) {
    if (!shouldActivateRow(event.key, event.repeat, event.target === event.currentTarget)) return;
    event.preventDefault();
    onPedidoClick(pedido);
  }

  let confirmarInicio = false;
  let iniciando = false;

  function cancelarInicio() {
    if (iniciando) return;
    confirmarInicio = false;
  }

  async function iniciar_pedidos() {
    if (iniciando) return;
    iniciando = true;
    errorMessage = "";
    try {
      const response = await fetch(`${API_BASE_URL}/api/pedidos/iniciar`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      const body = await response.json().catch(() => ({ error: "Error desconocido" }));
      if (!response.ok) {
        throw new Error(body.error || `Error ${response.status}: ${response.statusText}`);
      }
      confirmarInicio = false;
      dispatch('refreshPedidosLayer');
      dispatch('showGlobalNotification', {
        message: body.mensaje || 'Pedidos iniciados.',
        type: 'success'
      });
      await loadPedidos();
    } catch (err) {
      errorMessage = err.message;
      console.error("Error al iniciar pedidos:", err);
      confirmarInicio = false;
    } finally {
      iniciando = false;
    }
  }

  // Cargar pedidos al montar el componente
  loadPedidos();
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
    max-width: 1000px;
    max-height: 95vh;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    animation: modalSlideIn 0.3s ease-out;
  }

  @keyframes modalSlideIn {
    from {
      opacity: 0;
      transform: scale(0.95) translateY(-10px);
    }
    to {
      opacity: 1;
      transform: scale(1) translateY(0);
    }
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
    transition: all 0.2s ease;
  }

  .close-button:hover {
    color: var(--ds-on-secondary);
    background-color: var(--ds-secondary-hover);
  }

  .close-button:active {
    color: var(--ds-on-secondary);
    background-color: var(--ds-secondary-hover);
  }

  .close-button:focus {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
    border-color: var(--ds-focus);
    box-shadow: none;
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

  .pedidos-section {
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
    min-width: 800px;
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
    color: var(--ds-text);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  tbody tr {
    transition: background-color 0.15s ease;
    cursor: pointer;
  }

  tbody tr:hover {
    background-color: var(--ds-selected);
  }

  tbody tr:hover td {
    color: var(--ds-on-selected);
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
    background-color: var(--ds-surface);
    border-radius: 8px;
    margin: 1rem 0;
  }

  .estadisticas-section {
    color: var(--ds-text);
    background-color: var(--ds-surface);
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--ds-border);
  }

  .estadisticas-section h3 {
    color: var(--ds-text);
    border-bottom-color: var(--ds-border);
  }

  .estadisticas-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .estadistica-item {
    color: var(--ds-text);
    background-color: var(--ds-surface);
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
    color: var(--ds-text);
  }

  .valor-monetario {
    color: var(--ds-success);
  }

  /* Responsive */
  @media (max-width: 768px) {
    .modal-backdrop {
      padding: 0.5rem;
      align-items: flex-start;
      padding-top: 1rem;
    }

    .modal-content {
      max-width: 100%;
      max-height: calc(100vh - 2rem);
    }

    .modal-header {
      min-height: 36px;
    }

    .modal-header :global(.close-button) {
      width: 36px;
      height: 36px;
      font-size: 1rem;
    }

    .modal-body {
      padding: 0.75rem 1rem 1rem 1rem;
    }

    .pedidos-section, .estadisticas-section {
      padding: 1rem;
      margin-bottom: 1.5rem;
    }

    table {
      font-size: 0.9rem;
    }

    th, td {
      padding: 0.5rem;
    }

    .estadisticas-grid {
      grid-template-columns: 1fr;
    }
  }

  /* Móvil pequeño */
  @media (max-width: 480px) {
    .modal-backdrop {
      padding: 0.25rem;
      padding-top: 0.5rem;
    }

    .modal-content {
      max-height: calc(100vh - 1rem);
      border-radius: 6px;
    }

    .modal-header {
      min-height: 32px;
    }

    .modal-body {
      padding: 0.625rem 0.875rem 0.875rem 0.875rem;
    }

    .pedidos-section, .estadisticas-section {
      padding: 0.75rem;
      margin-bottom: 1rem;
    }

    .modal-header :global(h2) {
      font-size: 0.9rem;
    }

    h3 {
      font-size: 0.95rem;
      margin-bottom: 0.75rem;
    }

    .close-button {
      width: 36px;
      height: 36px;
      font-size: 1rem;
    }

    table {
      font-size: 0.8rem;
      min-width: 600px;
    }

    th, td {
      padding: 0.375rem;
    }
  }

  /* Indicadores visuales para diferentes tipos */
  .pedido-regalo {
    background-color: var(--ds-warning-surface) !important;
  }

  .pedido-regalo td, .pedido-regalo:hover td {
    color: var(--ds-warning);
  }

  .pedido-normal:hover {
    background-color: var(--ds-selected) !important;
  }

  .pedidos-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 0.85rem;
  }

  .pedidos-section-header h3 {
    margin: 0;
  }

  .iniciar-pedidos-btn {
    width: auto;
    min-height: 32px;
    margin: 0;
    padding: 0.35rem 0.75rem;
    border: none;
    border-radius: 6px;
    background: var(--ds-primary);
    color: var(--ds-on-primary);
    font: inherit;
    font-size: 0.8125rem;
    font-weight: 600;
    line-height: 1.2;
    white-space: nowrap;
    cursor: pointer;
  }

  .iniciar-pedidos-btn:disabled {
    cursor: default;
    opacity: 0.7;
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

  .confirm-iniciar {
    color: var(--ds-on-primary);
    background: var(--ds-primary);
    border: none;
  }

  .confirm-actions button:disabled {
    cursor: default;
    opacity: 0.7;
  }
</style>

<div class="modal-backdrop" 
     on:click={() => !confirmarInicio && dispatch('close')}
     on:keydown={(e) => e.key === 'Escape' && !confirmarInicio && dispatch('close')}
     role="button"
     tabindex="0"
     aria-label="Cerrar modal">
  <div class="modal-content" 
       on:click|stopPropagation
       on:keydown|stopPropagation
       use:dialogFocus
       role="dialog"
       aria-labelledby="pedidos-title">
    <div class="modal-header">
      <DialogHeader titleId="pedidos-title">
        <Icon name="box" size={18} />
        Pedidos
        <svelte:fragment slot="close">
          <button type="button" class="close-button ds-button ds-button--icon ds-focus" on:click={() => dispatch('close')} aria-label="Cerrar" data-dialog-initial-focus><Icon name="close" size={16} /></button>
        </svelte:fragment>
      </DialogHeader>
    </div>

    <div class="modal-body">
      {#if errorMessage}
        <div class="message error-message">{errorMessage}</div>
      {/if}
      
      {#if isLoading}
        <div class="loading-indicator">Cargando pedidos...</div>
      {/if}

      <div class="pedidos-section">
        <div class="pedidos-section-header">
          <h3>Todos los pedidos</h3>
          <button type="button" class="iniciar-pedidos-btn ds-focus" on:click={() => confirmarInicio = true} disabled={iniciando}>Iniciar Pedidos</button>
        </div>
        
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
                    <td>{pedido.observacion || 'N/A'}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
          <p style="font-size: 0.8rem; color: var(--ds-text-muted); margin-top: 0.5rem; text-align: center;">
            💡 Haz click en una fila para hacer zoom en el mapa | Pedidos regalo marcados en amarillo
          </p>
        {/if}
      </div>

      {#if pedidos.length > 0}
        <div class="estadisticas-section">
          <h3>📊 Estadísticas</h3>
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

{#if confirmarInicio}
  <div class="confirm-backdrop"
       on:click={cancelarInicio}
       on:keydown={(e) => e.key === 'Escape' && cancelarInicio()}
       role="presentation">
    <div class="confirm-dialog"
         on:click|stopPropagation
         on:keydown|stopPropagation={(e) => e.key === 'Escape' && cancelarInicio()}
         use:dialogFocus
         role="dialog"
         aria-modal="true"
         aria-labelledby="iniciar-pedidos-title">
      <div class="modal-header">
        <DialogHeader titleId="iniciar-pedidos-title">
          Iniciar pedidos
          <svelte:fragment slot="close">
            <button type="button" class="close-button ds-button ds-button--icon ds-focus" on:click={cancelarInicio} aria-label="Cerrar" disabled={iniciando}><Icon name="close" size={16} /></button>
          </svelte:fragment>
        </DialogHeader>
      </div>
      <div class="confirm-body">
        <p>Los clientes que tienen un pedido activo quedarán sin pedido, con cantidad 1, sin horario, sin número de PaO y sin marca de regalo.</p>
        <div class="confirm-actions">
          <button type="button" class="confirm-cancelar ds-focus" data-dialog-initial-focus on:click={cancelarInicio} disabled={iniciando}>Cancelar</button>
          <button type="button" class="confirm-iniciar ds-focus" on:click={iniciar_pedidos} disabled={iniciando}>Iniciar Pedidos</button>
        </div>
      </div>
    </div>
  </div>
{/if}
