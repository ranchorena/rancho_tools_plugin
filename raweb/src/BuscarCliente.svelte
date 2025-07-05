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

      // La actualización local de searchResults ya no es tan crítica si el formulario se cierra,
      // pero se puede mantener si se desea por consistencia si se reabre inmediatamente.
      // const index = searchResults.findIndex(c => c.id === selectedClient.id);
      // if (index !== -1) {
      //   searchResults[index] = {
      //       ...searchResults[index],
      //   };
      //   searchResults = [...searchResults];
      // }
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
  }

  .modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    width: 90%;
    max-width: 700px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    position: relative;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 10px;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 10px;
  }

  .modal-body {
    overflow-y: auto;
    flex-grow: 1;
    padding-right: 15px;
    margin-right: -15px;
  }

  .close-button {
    background: transparent;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    line-height: 1;
    color: #333;
    font-weight: normal;
  }
  .close-button:hover {
    color: #000;
  }

  h2 {
    color: #1f2937;
    margin-top: 0;
    margin-bottom: 0;
  }

  .search-section, .selected-client-section {
    padding: 10px 0;
    margin-bottom: 20px;
  }
  .search-section:last-child, .selected-client-section:last-child {
    margin-bottom: 0;
  }

  .form-group {
    margin-bottom: 15px;
  }

  .form-group.centered-search {
    max-width: 50%;
    margin-left: auto;
    margin-right: auto;
  }

  label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: #374151;
  }

  input[type="text"], input[type="number"], textarea {
    width: calc(100% - 1.6em);
    padding: 0.6em;
    margin-bottom: 10px;
    border: 1px solid #ccc;
    border-radius: 4px;
    font-size: inherit;
    box-sizing: border-box;
  }

  input[type="number"].narrow-number {
    max-width: 100px;
  }

  input[type="text"]:focus, input[type="number"]:focus, textarea:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  }

  textarea {
    min-height: 80px;
    resize: vertical;
  }

  .input-group {
    display: flex;
    gap: 10px;
    align-items: flex-end;
  }

  .input-group input[type="text"] {
     flex-grow: 1;
  }

  .input-group input[type="text"][placeholder="Altura"] {
    max-width: 100px;
    flex-grow: 0;
  }

  .input-group button {
    white-space: nowrap;
  }

  button {
    padding: 8px 15px;
    cursor: pointer;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #f4f4f4;
    color: #333;
    font-size: inherit;
    transition: background-color 0.2s, border-color 0.2s;
    margin-left: 5px;
  }

  button:hover {
    background-color: #e9e9e9;
    border-color: #bbb;
  }

  button:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
  }

  button.primary,
  .input-group button,
  .selected-client-section button {
    background-color: #007bff;
    color: white;
    border-color: #007bff;
  }

  button.primary:hover,
  .input-group button:hover,
  .selected-client-section button:hover {
    background-color: #0056b3;
    border-color: #0056b3;
  }

  .form-actions {
    text-align: right; /* Alinea el contenido (el botón) a la derecha */
    margin-top: 20px; /* Espacio por encima del botón */
  }

  .results-grid {
    margin-top: 20px;
    overflow-x: auto;
  }

  .results-grid table {
    width: 100%;
    border-collapse: collapse;
  }

  .table-container {
    max-height: 18em;
    overflow-y: auto;
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-top: 10px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th, td {
    border: 1px solid #ccc;
    padding: 8px;
    text-align: left;
  }

  th {
    background-color: #f4f4f4;
    font-weight: bold;
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
    margin-bottom: 10px;
  }
  .checkbox-group input[type="checkbox"] {
    margin-right: 8px;
    width: auto;
  }
  .checkbox-group label {
    margin-bottom: 0;
    font-weight: normal;
  }

  .message {
    padding: 10px;
    margin: 10px 0;
    border-radius: 6px;
    text-align: center;
  }
  .error-message {
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fecaca;
  }
  .success-message {
    background-color: #dcfce7;
    color: #15803d;
    border: 1px solid #bbf7d0;
  }

  .loading-indicator {
    text-align: center;
    padding: 15px;
    font-style: italic;
    color: #4b5563;
  }

  .form-row {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
  }

  .form-column {
    flex: 1;
    min-width: 200px;
  }
</style>

<div class="modal-backdrop"> <!-- Eliminado on:click={() => dispatch('close')} -->
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <h2>Buscar Cliente</h2>
      <button class="close-button" on:click={() => dispatch('close')}>&times;</button>
    </div>

    <div class="modal-body">
      {#if errorMessage}
      <div class="message error-message">{errorMessage}</div>
      {/if}
      <!-- Bloque de successMessage eliminado -->
      {#if isLoading}
        <div class="loading-indicator">Cargando...</div>
      {/if}

      <div class="search-section">
        <h3>Criterios de Búsqueda</h3>
        <div class="form-group centered-search">
          <label for="search-cliente">Cliente:</label>
          <div class="input-group">
            <input type="text" id="search-cliente" bind:value={searchTermCliente} placeholder="Nombre del cliente">
            <button on:click={searchByName}>Buscar</button>
          </div>
        </div>

        <div class="form-group centered-search">
          <label for="search-direccion">Dirección (texto libre):</label>
          <div class="input-group">
            <input type="text" id="search-direccion" bind:value={searchTermDireccion} placeholder="Parte de la dirección">
            <button on:click={searchByAddress}>Por Dirección</button>
          </div>
        </div>

        <div class="form-group centered-search">
          <label>Calle y Altura:</label>
          <div class="input-group">
            <input type="text" bind:value={searchTermCalle} placeholder="Nombre de la calle">
            <input type="text" bind:value={searchTermAltura} placeholder="Altura">
            <button on:click={searchByStreetHeight}>Buscar</button>
          </div>
        </div>
      </div>

      {#if searchResults.length > 0}
        <div class="results-grid search-section">
          <h3>Resultados de Búsqueda</h3>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Id</th>
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
        </div>
      {/if}

      {#if selectedClient}
        <div class="selected-client-section" id="selected-client-details">
      <h3>Cliente Seleccionado</h3>

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
                <input type="number" class="narrow-number" id="docenas" bind:value={editableFields.docenas} placeholder="Ej: 1.5">
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
            <textarea id="observaciones" bind:value={editableFields.observaciones}></textarea>
          </div>

          <div class="form-actions">
            <button on:click={saveChanges}>Guardar Cambios</button>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
