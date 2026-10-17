<script>
  import { API_BASE_URL } from './config.js';
  import { authorizedFetch } from './auth/session.mjs';
  import { createEventDispatcher, tick } from 'svelte'; // Importar dispatcher y tick
  import DialogHeader from './design-system/DialogHeader.svelte';
  import Icon from './design-system/Icon.svelte';
  import { dialogFocus } from './design-system/dialog-focus.mjs';
  import { shouldActivateRow } from './design-system/keyboard.mjs';
  import { resolveClientSearch } from './client-search.mjs';
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
      const response = await authorizedFetch(url, options);
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

  async function search() {
    const decision = resolveClientSearch({
      nombre: searchTermCliente,
      direccion: searchTermDireccion,
      calle: searchTermCalle,
      altura: searchTermAltura
    });
    if (!decision.ok) {
      errorMessage = decision.message;
      return;
    }

    const results = await fetchData(`${API_BASE_URL}/api/clientes/buscar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(decision.payload)
    });
    if (results) {
      searchResults = results;
      selectedClient = null;
      if (results.length === 0) {
        errorMessage = decision.emptyMessage;
      } else {
        await scrollToResults();
      }
    }
  }

  function handleSearchKeydown(event) {
    if (event.key !== "Enter") return;
    event.preventDefault();
    search();
  }

  function openAgregarCliente() {
    dispatch("agregarCliente", {
      nombre: searchTermCliente.trim(),
      direccion: searchTermDireccion.trim(),
      calle: searchTermCalle.trim(),
      altura: searchTermAltura.trim()
    });
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
    box-shadow: var(--ds-shadow-dialog);
    width: min(720px, calc(100vw - 2rem));
    max-width: 720px;
    max-height: min(85dvh, 95vh);
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    animation: modalSlideIn var(--ds-motion) ease-out;
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
    padding: 0.75rem 1.25rem 1.25rem;
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
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--ds-text);
    margin: 0 0 0.85rem 0;
    font-size: var(--ds-type-section);
    font-weight: 600;
    padding-bottom: 0;
  }

  .search-section {
    margin-bottom: 1.25rem;
    background-color: transparent;
    color: var(--ds-text);
    padding: 0;
    border: none;
  }

  .selected-client-section,
  .results-grid.search-section {
    margin-bottom: 1.25rem;
    background-color: var(--ds-background);
    color: var(--ds-text);
    padding: 0.9rem;
    border-radius: var(--ds-radius-medium);
    border: 1px solid var(--ds-border);
  }

  .search-section:last-child, .selected-client-section:last-child {
    margin-bottom: 0;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group.centered-search {
    max-width: none;
    margin: 0 0 0.85rem 0;
  }

  label {
    display: block;
    margin-bottom: 0.3rem;
    font-weight: 600;
    color: var(--ds-text);
    font-size: var(--ds-type-label);
  }

  input[type="text"], input[type="number"], textarea {
    width: 100%;
    min-height: 2.625rem;
    padding: 0.5rem 0.7rem;
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-small);
    background-color: var(--ds-background);
    font-size: var(--ds-type-body);
    box-sizing: border-box;
    transition: border-color var(--ds-motion) ease;
    color: var(--ds-text);
    margin-bottom: 0;
  }

  input[type="number"].narrow-number {
    max-width: 120px;
  }

  input[type="text"]:hover, input[type="number"]:hover, textarea:hover {
    border-color: var(--ds-text-muted);
  }

  input[type="text"]:focus-visible, input[type="number"]:focus-visible, textarea:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
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
    max-width: 7rem;
    flex: 0 0 7rem;
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

  button:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
    border-color: var(--ds-focus);
    box-shadow: none;
  }

  .search-actions .ds-button--ghost {
    background: transparent;
    border-color: var(--ds-divider);
    color: var(--ds-text);
  }

  .search-actions .ds-button--ghost:hover {
    background: var(--ds-secondary-hover);
    border-color: var(--ds-divider);
    transform: none;
  }

  .search-actions .ds-button--primary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    min-width: 8rem;
  }

  button.primary,
  .search-actions button.ds-button--primary,
  .selected-client-section button {
    background-color: var(--ds-primary);
    color: var(--ds-on-primary);
    border-color: var(--ds-primary);
  }

  button.primary:hover,
  .search-actions button.ds-button--primary:hover,
  .selected-client-section button:hover {
    background-color: var(--ds-primary-hover);
    border-color: var(--ds-primary-hover);
    transform: translateY(-1px);
  }

  .form-actions,
  .search-actions {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    margin-top: 0.5rem;
    gap: 0.5rem;
  }

  .search-actions button,
  .form-actions button {
    width: auto;
    margin-bottom: 0;
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
    outline: 2px solid var(--ds-focus);
    outline-offset: -2px;
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

    .search-section {
      padding: 0;
      margin-bottom: 1rem;
    }

    .selected-client-section,
    .results-grid.search-section {
      padding: 0.75rem;
      margin-bottom: 1rem;
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

    .form-row {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    .form-actions,
    .search-actions {
      flex-direction: column-reverse;
      gap: 0.5rem;
    }

    .form-actions button,
    .search-actions button {
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

    .search-section {
      padding: 0;
    }

    .selected-client-section,
    .results-grid.search-section {
      padding: 0.65rem;
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

    .form-actions,
    .search-actions {
      flex-direction: row;
      justify-content: flex-end;
    }

    .form-actions button,
    .search-actions button {
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
        <Icon name="user" size={18} />
        Buscar cliente
        <button slot="close" type="button" class="close-button ds-button ds-button--icon ds-focus" on:click={() => dispatch('close')} aria-label="Cerrar"><Icon name="close" size={16} /></button>
      </DialogHeader>
    </div>

    <div class="modal-body">
      {#if errorMessage}
      <div class="message error-message">{errorMessage}</div>
      {/if}
      {#if isLoading}
        <div class="loading-indicator">Cargando...</div>
      {/if}

      <div class="search-section">
        <h3><Icon name="search" size={16} /> Criterios de búsqueda</h3>
        
        <div class="form-group centered-search">
          <label for="search-cliente">Buscar por nombre:</label>
          <div class="input-group">
            <input type="text" class="ds-field" id="search-cliente" data-dialog-initial-focus bind:value={searchTermCliente} placeholder="Nombre del cliente" on:keydown={handleSearchKeydown}>
          </div>
        </div>

        <div class="form-group centered-search">
          <label for="search-direccion">Buscar por dirección:</label>
          <div class="input-group">
            <input type="text" class="ds-field" id="search-direccion" bind:value={searchTermDireccion} placeholder="Parte de la dirección" on:keydown={handleSearchKeydown}>
          </div>
        </div>

        <div class="form-group centered-search">
          <label for="searchTermCalle">Buscar por calle y altura:</label>
          <div class="input-group">
            <input id="searchTermCalle" type="text" class="ds-field" bind:value={searchTermCalle} placeholder="Nombre de la calle" aria-label="Nombre de la calle" on:keydown={handleSearchKeydown}>
            <input type="text" class="ds-field" bind:value={searchTermAltura} placeholder="Altura" aria-label="Altura de la calle" on:keydown={handleSearchKeydown}>
          </div>
        </div>

        <div class="search-actions">
          <button type="button" class="ds-button ds-button--ghost" on:click={openAgregarCliente}>Agregar cliente</button>
          <button type="button" class="ds-button ds-button--primary primary" on:click={search}><Icon name="search" size={16} /> Buscar</button>
        </div>
      </div>

      {#if searchResults.length > 0}
        <div class="results-grid search-section" id="search-results-section">
          <h3>Resultados de búsqueda</h3>
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
            <button type="button" class="ds-button ds-button--primary primary" on:click={saveChanges}>Guardar cambios</button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
