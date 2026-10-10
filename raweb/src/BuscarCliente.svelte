<script>
  import { API_BASE_URL } from './config.js';
  import { createEventDispatcher, tick } from 'svelte'; // Importar dispatcher y tick
  import DialogHeader from './design-system/DialogHeader.svelte';
  import { dialogFocus } from './design-system/dialog-focus.mjs';
  import { shouldActivateRow } from './design-system/keyboard.mjs';
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
      if (results.length === 0) {
        errorMessage = "No se encontraron clientes con ese nombre.";
      } else {
        // Scroll hacia la grilla de resultados
        await scrollToResults();
      }
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
      if (results.length === 0) {
        errorMessage = "No se encontraron clientes con esa dirección.";
      } else {
        // Scroll hacia la grilla de resultados
        await scrollToResults();
      }
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
      if (results.length === 0) {
        errorMessage = "No se encontraron clientes con esa calle/altura.";
      } else {
        // Scroll hacia la grilla de resultados
        await scrollToResults();
      }
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

  async function scrollToResults() {
    // Esperar a que el DOM se actualice con los nuevos resultados
    await tick();
    const resultsSection = document.getElementById("search-results-section");
    if (resultsSection) {
      resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }

  function handleResultRowKeydown(event, client) {
    if (!shouldActivateRow(event.key, event.repeat, event.target === event.currentTarget)) return;
    if (event.key === ' ') event.preventDefault();
    selectClient(client);
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
      
      // Ir a la ubicación del cliente usando su dirección para geocodificación
      if (selectedClient && selectedClient.direccion) {
        dispatch('buscarDireccionCliente', { 
          direccion: selectedClient.direccion
        });
      }
      
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
    background-color: var(--ds-surface);
    color: var(--ds-text);
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
    box-shadow: inset 0 -1px var(--ds-border);
    flex-shrink: 0;
    background-color: var(--ds-surface);
    color: var(--ds-text);
  }

  .modal-header :global(.close-button) {
    min-height: 32px;
  }

  .modal-header :global(.ds-dialog-header) {
    padding-block: 0;
  }

  .modal-body {
    overflow-y: auto;
    flex-grow: 1;
    padding: 1rem 1.5rem 1.5rem 1.5rem;
  }

  .close-button {
    box-sizing: border-box;
    min-height: 32px;
    margin: 0;
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

  h3 {
    color: var(--ds-text);
    margin: 0 0 1rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    border-bottom: 2px solid var(--ds-border);
    padding-bottom: 0.5rem;
  }

  .search-section, .selected-client-section {
    margin-bottom: 2rem;
    background-color: var(--ds-surface);
    color: var(--ds-text);
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid var(--ds-border);
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
    color: var(--ds-text);
    font-size: 0.9rem;
  }

  input[type="text"], input[type="number"], textarea {
    width: 100%;
    padding: 0.75rem;
    border: 2px solid var(--ds-border);
    border-radius: 6px;
    font-size: 1rem;
    box-sizing: border-box;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    background-color: var(--ds-surface);
    color: var(--ds-text);
    margin-bottom: 0;
  }

  input[type="number"].narrow-number {
    max-width: 120px;
  }

  input[type="text"]:focus, input[type="number"]:focus, textarea:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
    border-color: var(--ds-focus);
    box-shadow: none;
  }

  input[readonly] {
    background-color: var(--ds-background);
    color: var(--ds-text-muted);
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
    border: 1px solid var(--ds-border);
    border-radius: 6px;
    background-color: var(--ds-secondary);
    color: var(--ds-on-secondary);
    font-size: 0.9rem;
    font-weight: 500;
    transition: all 0.2s ease;
    min-height: 44px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  button:hover {
    background-color: var(--ds-secondary-hover);
    border-color: var(--ds-border);
    transform: translateY(-1px);
  }

  button:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
    border-color: var(--ds-focus);
    box-shadow: none;
  }

  .input-group button.ds-button:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
    border-color: var(--ds-focus);
    box-shadow: none;
  }

  button.primary,
  .input-group button.ds-button--primary,
  .selected-client-section button {
    background-color: var(--ds-primary);
    color: var(--ds-on-primary);
    border-color: var(--ds-primary);
  }

  button.primary:hover,
  .input-group button.ds-button--primary:hover,
  .selected-client-section button:hover {
    background-color: var(--ds-primary-hover);
    border-color: var(--ds-primary-hover);
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

  .results-hint {
    font-size: 0.8rem;
    color: var(--ds-text-muted);
    margin-top: 0.5rem;
    text-align: center;
  }

  .table-container {
    max-height: 300px;
    overflow: auto;
    border: 1px solid var(--ds-border);
    border-radius: 8px;
    margin-top: 1rem;
    background-color: var(--ds-surface);
    color: var(--ds-text);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    min-width: 600px; /* Ancho mínimo para scroll horizontal */
  }

  th, td {
    border-bottom: 1px solid var(--ds-border);
    padding: 0.75rem;
    text-align: left;
    vertical-align: middle;
  }

  th {
    background-color: var(--ds-background);
    font-weight: 600;
    color: var(--ds-text);
    position: sticky;
    top: 0;
    z-index: 10;
  }

  tbody tr {
    transition: background-color 0.15s ease;
  }

  tbody tr:hover {
    background-color: var(--ds-secondary-hover);
    cursor: pointer;
  }

  tbody tr.selected {
    background-color: var(--ds-selected);
    color: var(--ds-on-selected);
    box-shadow: inset 3px 0 var(--ds-on-selected);
  }

  tbody tr:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: -3px;
  }

  .checkbox-group {
    display: flex;
    align-items: center;
    margin-bottom: 0.75rem;
    padding: 0.5rem;
    border-radius: 6px;
    background-color: var(--ds-background);
    color: var(--ds-text);
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
    background-color: var(--ds-error-surface);
    color: var(--ds-error);
    border: 1px solid var(--ds-error);
  }

  .loading-indicator {
    text-align: center;
    padding: 2rem;
    font-style: italic;
    color: var(--ds-text-muted);
    background-color: var(--ds-background);
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
      padding: 0;
      min-height: 0;
    }

    .modal-body {
      padding: 0.75rem 1rem 1rem 1rem;
    }

    .search-section, .selected-client-section {
      padding: 1rem;
      margin-bottom: 1.5rem;
    }

    .modal-header :global(h2) {
      font-size: 1.125rem;
    }

    .modal-header :global(.close-button) {
      width: 36px;
      height: 36px;
      font-size: 1rem;
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

    .modal-body {
      padding: 0.625rem 0.875rem 0.875rem 0.875rem;
    }

    .search-section, .selected-client-section {
      padding: 0.75rem;
      margin-bottom: 1rem;
    }

    .modal-header :global(h2) {
      font-size: 1rem;
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

</style>

<div class="modal-backdrop" 
     on:click={() => dispatch('close')}
     on:keydown={(e) => e.key === 'Escape' && dispatch('close')}
     role="button"
     tabindex="0"
     aria-label="Cerrar modal">
  <div class="modal-content" 
       use:dialogFocus
       on:click|stopPropagation
       on:keydown|stopPropagation
       role="dialog"
       aria-labelledby="modal-title">
    <div class="modal-header">
      <DialogHeader titleId="modal-title">
        👤 Buscar Cliente
        <button slot="close" type="button" class="close-button ds-focus" on:click={() => dispatch('close')} aria-label="Cerrar">&times;</button>
      </DialogHeader>
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
            <input type="text" class="ds-field" id="search-cliente" data-dialog-initial-focus bind:value={searchTermCliente} placeholder="Nombre del cliente">
            <button type="button" class="ds-button ds-button--primary" on:click={searchByName}>Buscar</button>
          </div>
        </div>

        <div class="form-group centered-search">
          <label for="search-direccion">Buscar por dirección:</label>
          <div class="input-group">
            <input type="text" class="ds-field" id="search-direccion" bind:value={searchTermDireccion} placeholder="Parte de la dirección">
            <button type="button" class="ds-button ds-button--primary" on:click={searchByAddress}>Buscar</button>
          </div>
        </div>

        <div class="form-group centered-search">
          <label for="searchTermCalle">Buscar por calle y altura:</label>
          <div class="input-group">
            <input id="searchTermCalle" type="text" class="ds-field" bind:value={searchTermCalle} placeholder="Nombre de la calle" aria-label="Nombre de la calle">
            <input type="text" class="ds-field" bind:value={searchTermAltura} placeholder="Altura" aria-label="Altura de la calle">
            <button type="button" class="ds-button ds-button--primary" on:click={searchByStreetHeight}>Buscar</button>
          </div>
        </div>
      </div>

      {#if searchResults.length > 0}
        <div class="results-grid search-section" id="search-results-section">
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
                  <tr tabindex="0" on:click={() => selectClient(client)} on:keydown={(event) => handleResultRowKeydown(event, client)} class:selected={selectedClient && selectedClient.id === client.id}>
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
          <p class="results-hint">
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
                <input type="text" class="ds-field" id="selected-client-id" value={selectedClient.id} readonly>
              </div>
            </div>
            <div class="form-column">
              <div class="form-group">
                <label for="selected-client-nombre">Nombre:</label>
                <input type="text" class="ds-field" id="selected-client-nombre" value={selectedClient.nombre} readonly>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-column">
              <div class="form-group">
                <label for="docenas">Docenas (Cantidad):</label>
                <input type="number" class="ds-field narrow-number" id="docenas" bind:value={editableFields.docenas} placeholder="Ej: 1.5" step="0.5">
              </div>
            </div>
            <div class="form-column">
              <div class="form-group">
                <label for="nro_pao">Nro. PaO:</label>
                <input type="number" class="ds-field narrow-number" id="nro_pao" bind:value={editableFields.nro_pao} placeholder="Ej: 123">
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-column">
               <div class="form-group">
                <label for="horario">Horario (HH:MM:SS):</label>
                <input type="text" class="ds-field" id="horario" bind:value={editableFields.horario} placeholder="Ej: 14:30:00">
              </div>
            </div>
             <div class="form-column">
                <div class="checkbox-group">
                  <input type="checkbox" class="ds-choice" id="tiene_pedido" bind:checked={editableFields.tiene_pedido}>
                  <label for="tiene_pedido">Tiene Pedido</label>
                </div>
                <div class="checkbox-group">
                  <input type="checkbox" class="ds-choice" id="es_regalo" bind:checked={editableFields.es_regalo}>
                  <label for="es_regalo">Es Regalo</label>
                </div>
            </div>
          </div>

          <div class="form-group">
            <label for="observaciones">Observaciones:</label>
            <textarea class="ds-field" id="observaciones" bind:value={editableFields.observaciones} placeholder="Ingrese observaciones adicionales..."></textarea>
          </div>

          <div class="form-actions">
            <button type="button" class="ds-button ds-button--primary primary" on:click={saveChanges}>💾 Guardar Cambios</button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
