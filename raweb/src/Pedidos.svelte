<script>
  import { API_BASE_URL } from './config.js';
  import { createEventDispatcher } from 'svelte';
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
      pedidos = results;
      calcularEstadisticas();
      if (results.length === 0) {
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
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
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
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.375rem 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    flex-shrink: 0;
    background-color: #f8f9fa;
    min-height: 40px;
  }

  .modal-body {
    overflow-y: auto;
    flex-grow: 1;
    padding: 1rem 1.5rem 1.5rem 1.5rem;
  }

  .close-button {
    background: transparent;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
    padding: 0.25rem;
    line-height: 1;
    color: #6b7280;
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
    color: #374151;
    background-color: #e5e7eb;
  }

  h2 {
    color: #1f2937;
    margin: 0;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.2;
  }

  h3 {
    color: #374151;
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5rem;
  }

  .pedidos-section {
    margin-bottom: 2rem;
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
  }

  .table-container {
    max-height: 400px;
    overflow: auto;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    margin-top: 1rem;
    background-color: #fff;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    min-width: 800px;
  }

  th, td {
    border-bottom: 1px solid #e5e7eb;
    padding: 0.75rem;
    text-align: left;
    vertical-align: middle;
  }

  th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #374151;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  tbody tr {
    transition: background-color 0.15s ease;
  }

  tbody tr:hover {
    background-color: #f0f9ff;
    cursor: pointer;
  }

  .message {
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 8px;
    text-align: center;
    font-weight: 500;
  }

  .error-message {
    background-color: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
  }

  .loading-indicator {
    text-align: center;
    padding: 2rem;
    font-style: italic;
    color: #6b7280;
    background-color: #f9fafb;
    border-radius: 8px;
    margin: 1rem 0;
  }

  .estadisticas-section {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
  }

  .estadisticas-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .estadistica-item {
    background-color: #fff;
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid #d1d5db;
    text-align: center;
  }

  .estadistica-label {
    font-size: 0.9rem;
    color: #6b7280;
    margin-bottom: 0.5rem;
  }

  .estadistica-valor {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1f2937;
  }

  .valor-monetario {
    color: #059669;
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
      padding: 0.25rem 1rem;
      min-height: 36px;
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
      padding: 0.25rem 0.875rem;
      min-height: 32px;
    }

    .modal-body {
      padding: 0.625rem 0.875rem 0.875rem 0.875rem;
    }

    .pedidos-section, .estadisticas-section {
      padding: 0.75rem;
      margin-bottom: 1rem;
    }

    h2 {
      font-size: 0.9rem;
    }

    h3 {
      font-size: 0.95rem;
      margin-bottom: 0.75rem;
    }

    .close-button {
      width: 24px;
      height: 24px;
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
    background-color: #fef3c7 !important;
  }

  .pedido-normal:hover {
    background-color: #dbeafe !important;
  }
</style>

<div class="modal-backdrop" on:click={() => dispatch('close')}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <h2>📦 Pedidos</h2>
      <button class="close-button" on:click={() => dispatch('close')} aria-label="Cerrar">&times;</button>
    </div>

    <div class="modal-body">
      {#if errorMessage}
        <div class="message error-message">{errorMessage}</div>
      {/if}
      
      {#if isLoading}
        <div class="loading-indicator">🔄 Cargando pedidos...</div>
      {/if}

      <div class="pedidos-section">
        <h3>📋 Todos los Pedidos</h3>
        
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
          <p style="font-size: 0.8rem; color: #6b7280; margin-top: 0.5rem; text-align: center;">
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