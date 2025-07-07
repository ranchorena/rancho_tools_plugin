<script>
  import { API_BASE_URL } from './config.js';
  import { createEventDispatcher, tick } from 'svelte'; // Importar dispatcher y tick
  const dispatch = createEventDispatcher(); // Inicializar dispatcher

  // Variables de estado para los campos de búsqueda
  let searchTermCliente = "";
  let searchTermDireccion = "";
  let searchTermCalle = "";
  let searchTermAltura = "";

  // Resultados de la búsqueda
  let searchResults = []; // Array de objetos cliente: { id, nombre, direccion, calle, altura }

  // Cliente seleccionado de la grilla
  let selectedClient = null; // Objeto cliente seleccionado

  // Campos editables para el cliente seleccionado
  let editableFields = {
    docenas: null,
    nro_pao: null,
    tiene_pedido: false,
    es_regalo: false,
    observaciones: "",
    horario: "" // HH:MM:SS
  };

  let isLoading = false;
  let errorMessage = "";
  // let successMessage = ""; // Eliminada, se usará notificación global

  async function fetchData(url, options) {
    isLoading = true;
    errorMessage = "";
    // successMessage = ""; // Eliminada
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

  async function searchByName() {
    if (!searchTermCliente.trim()) {
      errorMessage = "Por favor, ingrese un nombre de cliente.";
      return;
    }
    const payload = {
      criterio: "nombre",
      nombre_cliente: searchTermCliente
    };
    const results = await fetchData(`${API_BASE_URL}/api/clientes/buscar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (results) {
      searchResults = results;
      if (results.length === 0) errorMessage = "No se encontraron clientes con ese nombre.";
    }
  }

  async function searchByAddress() {
    if (!searchTermDireccion.trim()) {
      errorMessage = "Por favor, ingrese una dirección.";
      return;
    }
    const payload = {
      criterio: "direccion",
      direccion: searchTermDireccion
    };
    const results = await fetchData(`${API_BASE_URL}/api/clientes/buscar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (results) {
      searchResults = results;
      if (results.length === 0) errorMessage = "No se encontraron clientes con esa dirección.";
    }
  }

  async function searchByStreetHeight() {
    if (!searchTermCalle.trim()) {
      errorMessage = "Por favor, ingrese una calle.";
      return;
    }
    const payload = {
      criterio: "calle_altura",
      calle: searchTermCalle,
      altura: searchTermAltura.trim() || null // Enviar null si la altura está vacía
    };
    const results = await fetchData(`${API_BASE_URL}/api/clientes/buscar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (results) {
      searchResults = results;
       if (results.length === 0) errorMessage = "No se encontraron clientes con esa calle/altura.";
    }
  }

  async function selectClient(client) {
    selectedClient = client;
    editableFields = {
      // Si client.cantidad es undefined o null, default a 1. Sino, usar client.cantidad.
      docenas: (client.cantidad !== undefined && client.cantidad !== null) ? client.cantidad : 1,
      nro_pao: (client.nro_pao !== undefined && client.nro_pao !== null) ? client.nro_pao : null,
      // Si client.tiene_pedido es undefined (no existe el campo), default a true. Si existe, usar su valor booleano.
      tiene_pedido: client.tiene_pedido !== undefined ? Boolean(client.tiene_pedido) : true,
      es_regalo: client.es_regalo !== undefined ? Boolean(client.es_regalo) : false,
      observaciones: client.observacion || "",
      horario: client.horario || ""
    };
    // successMessage = ""; // Eliminado para evitar ReferenceError
    errorMessage = "";

    if (client) {
      await tick();
      const selectedClientSection = document.getElementById("selected-client-details");
      if (selectedClientSection) {
        selectedClientSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }
  }

  function isValidTimeFormat(timeStr) {
    if (!timeStr) return true;
    return /^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$/.test(timeStr);
  }

  async function saveChanges() {
    if (!selectedClient) {
      errorMessage = "No hay un cliente seleccionado para guardar.";
      return;
    }
    if (editableFields.horario && !isValidTimeFormat(editableFields.horario)) {
      errorMessage = "Formato de horario inválido. Use HH:MM:SS.";
      return;
    }

    const payload = {
      docenas: editableFields.docenas !== null ? parseFloat(editableFields.docenas) : null,
      nro_pao: editableFields.nro_pao !== null ? parseInt(editableFields.nro_pao) : null,
      tiene_pedido: editableFields.tiene_pedido,
      es_regalo: editableFields.es_regalo,
      observaciones: editableFields.observaciones,
      horario: editableFields.horario || null
    };

    const result = await fetchData(`${API_BASE_URL}/api/clientes/actualizar/${selectedClient.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (result && result.mensaje) {
      // successMessage = result.mensaje; // Ya no se usa localmente
      dispatch('showGlobalNotification', { message: result.mensaje || 'Cliente actualizado correctamente.', type: 'success' });
      dispatch('refreshPedidosLayer');
      dispatch('close'); // Cerrar el formulario
    }
  }
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
    max-width: 800px;
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
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    flex-shrink: 0;
    background-color: #f8f9fa;
  }

  .modal-body {
    overflow-y: auto;
    flex-grow: 1;
    padding: 1rem 1.5rem 1.5rem 1.5rem;
  }

  .close-button {
    background: transparent;
    border: none;
    font-size: 1.75rem;
    cursor: pointer;
    padding: 0.25rem;
    line-height: 1;
    color: #6b7280;
    font-weight: normal;
    border-radius: 50%;
    width: 36px;
    height: 36px;
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
    font-size: 1.25rem;
    font-weight: 600;
  }

  h3 {
    color: #374151;
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 0.5rem;
  }

  .search-section, .selected-client-section {
    margin-bottom: 2rem;
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
  }

  .search-section:last-child, .selected-client-section:last-child {
    margin-bottom: 0;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group.centered-search {
    max-width: 100%;
    margin: 0 auto 1.5rem auto;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #374151;
    font-size: 0.9rem;
  }

  input[type="text"], input[type="number"], textarea {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid #d1d5db;
    border-radius: 6px;
    font-size: 1rem;
    box-sizing: border-box;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    background-color: #fff;
    margin-bottom: 0;
  }

  input[type="number"].narrow-number {
    max-width: 120px;
  }

  input[type="text"]:focus, input[type="number"]:focus, textarea:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  input[readonly] {
    background-color: #f3f4f6;
    color: #6b7280;
    cursor: not-allowed;
  }

  textarea {
    min-height: 100px;
    resize: vertical;
    font-family: inherit;
    line-height: 1.4;
  }

  .input-group {
    display: flex;
    gap: 0.75rem;
    align-items: flex-end;
    flex-wrap: wrap;
  }

  .input-group input[type="text"] {
    flex: 1;
    min-width: 150px;
  }

  .input-group input[type="text"][placeholder="Altura"] {
    max-width: 100px;
    flex: 0 0 100px;
  }

  .input-group button {
    white-space: nowrap;
    flex-shrink: 0;
    margin: 0;
  }

  button {
    padding: 0.75rem 1.25rem;
    cursor: pointer;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    background-color: #fff;
    color: #374151;
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.2s ease;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  button:hover {
    background-color: #f9fafb;
    border-color: #9ca3af;
    transform: translateY(-1px);
  }

  button:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  button.primary,
  .input-group button,
  .selected-client-section button {
    background-color: #3b82f6;
    color: #fff;
    border-color: #3b82f6;
  }

  button.primary:hover,
  .input-group button:hover,
  .selected-client-section button:hover {
    background-color: #2563eb;
    border-color: #2563eb;
    transform: translateY(-1px);
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1.5rem;
    gap: 0.75rem;
  }

  .results-grid {
    margin-top: 1rem;
  }

  .table-container {
    max-height: 300px;
    overflow: auto;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    margin-top: 1rem;
    background-color: #fff;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    min-width: 600px; /* Ancho mínimo para scroll horizontal */
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

  tbody tr.selected {
    background-color: #dbeafe;
  }

  .checkbox-group {
    display: flex;
    align-items: center;
    margin-bottom: 0.75rem;
    padding: 0.5rem;
    border-radius: 6px;
    background-color: #f3f4f6;
  }

  .checkbox-group input[type="checkbox"] {
    margin-right: 0.75rem;
    width: auto;
    transform: scale(1.1);
  }

  .checkbox-group label {
    margin-bottom: 0;
    font-weight: 500;
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

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 1rem;
  }

  .form-column {
    min-width: 0; /* Importante para que funcione el grid */
  }

  /* Responsive breakpoints */
  
  /* Tablet y móvil grande */
  @media (max-width: 768px) {
    .modal-backdrop {
      padding: 0.5rem;
      align-items: flex-start;
      padding-top: 1rem;
    }

    .modal-content {
      max-width: 100%;
      max-height: calc(100vh - 2rem);
      border-radius: 8px;
    }

    .modal-header {
      padding: 0.5rem 1rem;
    }

    .modal-body {
      padding: 0.75rem 1rem 1rem 1rem;
    }

    .search-section, .selected-client-section {
      padding: 1rem;
      margin-bottom: 1.5rem;
    }

    h2 {
      font-size: 1.125rem;
    }

    h3 {
      font-size: 1rem;
    }

    .form-group.centered-search {
      max-width: 100%;
    }

    .input-group {
      flex-direction: column;
      align-items: stretch;
      gap: 0.5rem;
    }

    .input-group input[type="text"] {
      min-width: auto;
    }

    .input-group input[type="text"][placeholder="Altura"] {
      max-width: none;
      flex: 1;
    }

    .input-group button {
      width: 100%;
      margin-top: 0.5rem;
    }

    .form-row {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    .form-actions {
      flex-direction: column-reverse;
      gap: 0.5rem;
    }

    .form-actions button {
      width: 100%;
    }

    button {
      padding: 1rem;
      font-size: 1rem;
      min-height: 48px;
    }

    input[type="text"], input[type="number"], textarea {
      padding: 1rem;
      font-size: 16px; /* Evita zoom en iOS */
    }

    input[type="number"].narrow-number {
      max-width: none;
    }

    .table-container {
      border-radius: 6px;
    }

    table {
      font-size: 0.9rem;
    }

    th, td {
      padding: 0.5rem;
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
      padding: 0.5rem 0.875rem;
    }

    .modal-body {
      padding: 0.625rem 0.875rem 0.875rem 0.875rem;
    }

    .search-section, .selected-client-section {
      padding: 0.75rem;
      margin-bottom: 1rem;
    }

    h2 {
      font-size: 1rem;
    }

    h3 {
      font-size: 0.95rem;
      margin-bottom: 0.75rem;
    }

    .close-button {
      width: 32px;
      height: 32px;
      font-size: 1.5rem;
    }

    button {
      padding: 0.875rem;
    }

    .checkbox-group {
      padding: 0.375rem;
    }

    table {
      font-size: 0.8rem;
      min-width: 500px;
    }

    th, td {
      padding: 0.375rem;
    }
  }

  /* Landscape móvil */
  @media (max-width: 768px) and (orientation: landscape) {
    .modal-backdrop {
      align-items: center;
      padding-top: 0.5rem;
    }

    .modal-content {
      max-height: calc(100vh - 1rem);
    }

    .form-row {
      grid-template-columns: 1fr 1fr;
    }

    .form-actions {
      flex-direction: row;
      justify-content: flex-end;
    }

    .form-actions button {
      width: auto;
      min-width: 120px;
    }
  }

  /* Tablet */
  @media (min-width: 769px) and (max-width: 1024px) {
    .modal-content {
      max-width: 90%;
    }

    .form-group.centered-search {
      max-width: 80%;
    }
  }

  /* Ajustes para pantallas de alta densidad */
  @media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 2dppx) {
    button, input, textarea {
      -webkit-font-smoothing: antialiased;
    }
  }

  /* Reducir animaciones para usuarios que las prefieren deshabilitadas */
  @media (prefers-reduced-motion: reduce) {
    .modal-content {
      animation: none;
    }
    
    * {
      transition: none !important;
    }
  }

  /* Modo oscuro (preparado para futuro) */
  @media (prefers-color-scheme: dark) {
    .modal-content {
      background-color: #1f2937;
      color: #f9fafb;
    }

    .search-section, .selected-client-section {
      background-color: #374151;
      border-color: #4b5563;
    }

    h2, h3 {
      color: #f9fafb;
    }

    input[type="text"], input[type="number"], textarea {
      background-color: #374151;
      border-color: #4b5563;
      color: #f9fafb;
    }

    input[readonly] {
      background-color: #4b5563;
      color: #9ca3af;
    }

    .checkbox-group {
      background-color: #4b5563;
    }

    th {
      background-color: #374151;
      color: #f9fafb;
    }

    .table-container {
      border-color: #4b5563;
      background-color: #1f2937;
    }
  }
</style>

<div class="modal-backdrop" on:click={() => dispatch('close')}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <h2>👤 Buscar Cliente</h2>
      <button class="close-button" on:click={() => dispatch('close')} aria-label="Cerrar">&times;</button>
    </div>

    <div class="modal-body">
      {#if errorMessage}
      <div class="message error-message">{errorMessage}</div>
      {/if}
      {#if isLoading}
        <div class="loading-indicator">🔄 Cargando...</div>
      {/if}

      <div class="search-section">
        <h3>🔍 Criterios de Búsqueda</h3>
        
        <div class="form-group centered-search">
          <label for="search-cliente">Buscar por nombre:</label>
          <div class="input-group">
            <input type="text" id="search-cliente" bind:value={searchTermCliente} placeholder="Nombre del cliente">
            <button on:click={searchByName}>Buscar</button>
          </div>
        </div>

        <div class="form-group centered-search">
          <label for="search-direccion">Buscar por dirección:</label>
          <div class="input-group">
            <input type="text" id="search-direccion" bind:value={searchTermDireccion} placeholder="Parte de la dirección">
            <button on:click={searchByAddress}>Buscar</button>
          </div>
        </div>

        <div class="form-group centered-search">
          <label>Buscar por calle y altura:</label>
          <div class="input-group">
            <input type="text" bind:value={searchTermCalle} placeholder="Nombre de la calle">
            <input type="text" bind:value={searchTermAltura} placeholder="Altura">
            <button on:click={searchByStreetHeight}>Buscar</button>
          </div>
        </div>
      </div>

      {#if searchResults.length > 0}
        <div class="results-grid search-section">
          <h3>📋 Resultados de Búsqueda</h3>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Dirección</th>
                  <th>Calle</th>
                  <th>Altura</th>
                </tr>
              </thead>
              <tbody>
                {#each searchResults as client (client.id)}
                  <tr on:click={() => selectClient(client)} class:selected={selectedClient && selectedClient.id === client.id}>
                    <td>{client.id}</td>
                    <td>{client.nombre}</td>
                    <td>{client.direccion}</td>
                    <td>{client.calle}</td>
                    <td>{client.altura}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
          <p style="font-size: 0.8rem; color: #6b7280; margin-top: 0.5rem; text-align: center;">
            💡 Desliza horizontalmente para ver todas las columnas
          </p>
        </div>
      {/if}

      {#if selectedClient}
        <div class="selected-client-section" id="selected-client-details">
          <h3>✏️ Editar Cliente Seleccionado</h3>

          <div class="form-row">
            <div class="form-column">
              <div class="form-group">
                <label for="selected-client-id">ID Cliente:</label>
                <input type="text" id="selected-client-id" value={selectedClient.id} readonly>
              </div>
            </div>
            <div class="form-column">
              <div class="form-group">
                <label for="selected-client-nombre">Nombre:</label>
                <input type="text" id="selected-client-nombre" value={selectedClient.nombre} readonly>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-column">
              <div class="form-group">
                <label for="docenas">Docenas (Cantidad):</label>
                <input type="number" class="narrow-number" id="docenas" bind:value={editableFields.docenas} placeholder="Ej: 1.5" step="0.5">
              </div>
            </div>
            <div class="form-column">
              <div class="form-group">
                <label for="nro_pao">Nro. PaO:</label>
                <input type="number" class="narrow-number" id="nro_pao" bind:value={editableFields.nro_pao} placeholder="Ej: 123">
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-column">
               <div class="form-group">
                <label for="horario">Horario (HH:MM:SS):</label>
                <input type="text" id="horario" bind:value={editableFields.horario} placeholder="Ej: 14:30:00">
              </div>
            </div>
             <div class="form-column">
                <div class="checkbox-group">
                  <input type="checkbox" id="tiene_pedido" bind:checked={editableFields.tiene_pedido}>
                  <label for="tiene_pedido">Tiene Pedido</label>
                </div>
                <div class="checkbox-group">
                  <input type="checkbox" id="es_regalo" bind:checked={editableFields.es_regalo}>
                  <label for="es_regalo">Es Regalo</label>
                </div>
            </div>
          </div>

          <div class="form-group">
            <label for="observaciones">Observaciones:</label>
            <textarea id="observaciones" bind:value={editableFields.observaciones} placeholder="Ingrese observaciones adicionales..."></textarea>
          </div>

          <div class="form-actions">
            <button class="primary" on:click={saveChanges}>💾 Guardar Cambios</button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
