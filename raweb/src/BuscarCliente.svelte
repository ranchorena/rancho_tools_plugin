<script>
  import { API_BASE_URL } from './config.js';

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
  let successMessage = "";

  async function fetchData(url, options) {
    isLoading = true;
    errorMessage = "";
    successMessage = "";
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

  function selectClient(client) {
    selectedClient = client;
    // Poblar campos editables. Usar valores del cliente o defaults.
    // Los nombres de campo en `client` son id, nombre, direccion, calle, altura.
    // Los campos editables son docenas, nro_pao, tiene_pedido, es_regalo, observaciones, horario.
    // Estos campos no vienen en la búsqueda inicial, así que se inicializan o se podrían buscar por separado.
    // Por ahora, los inicializamos. El backend los tiene como nullable o con defaults.
    // La tarea implica que estos campos se cargan de alguna manera, pero la búsqueda solo devuelve Id, Nombre, Dirección, Calle, Altura.
    // Para una mejor UX, se debería hacer un GET /api/clientes/{id} para obtener todos los detalles.
    // Como no está definido ese endpoint, se inicializan.
    editableFields = {
      docenas: client.cantidad !== undefined ? client.cantidad : null, // Asumiendo que 'cantidad' es 'docenas'
      nro_pao: client.nro_pao !== undefined ? client.nro_pao : null,
      tiene_pedido: client.tiene_pedido ? true : false, // Asumiendo 0/1 en BBDD
      es_regalo: client.es_regalo ? true : false, // Asumiendo 0/1 en BBDD
      observaciones: client.observacion || "", // Asumiendo 'observacion' es 'observaciones'
      horario: client.horario || "" // Formato HH:MM:SS
    };
    successMessage = "";
    errorMessage = "";
  }

  function isValidTimeFormat(timeStr) {
    if (!timeStr) return true; // Vacío es válido (se enviará null o string vacío)
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
      tiene_pedido: editableFields.tiene_pedido, // Svelte envía true/false
      es_regalo: editableFields.es_regalo,     // Svelte envía true/false
      observaciones: editableFields.observaciones,
      horario: editableFields.horario || null // Enviar null si está vacío
    };

    const result = await fetchData(`${API_BASE_URL}/api/clientes/actualizar/${selectedClient.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (result && result.mensaje) {
      successMessage = result.mensaje;
      // Opcional: Refrescar datos en la grilla. Podríamos volver a buscar o actualizar localmente.
      // Por simplicidad, el usuario puede volver a buscar si necesita ver el cambio en la grilla inmediatamente.
      // O, actualizar el item en searchResults si existe:
      const index = searchResults.findIndex(c => c.id === selectedClient.id);
      if (index !== -1) {
        searchResults[index] = {
            ...searchResults[index], // Mantener id, nombre, direccion, calle, altura
            // Actualizar los campos que podrían estar en la grilla si se añadieran, o que son relevantes
            // Esta parte es compleja si la grilla no muestra estos campos.
            // Por ahora, no actualizamos la grilla localmente tras guardar, solo mostramos mensaje.
        };
        searchResults = [...searchResults]; // Forzar reactividad
      }
    }
    // `errorMessage` ya se maneja en `fetchData`
  }

</script>

<style>
  .container {
    font-family: "Inter", sans-serif; /* Intentar usar Inter */
    padding: 20px;
    max-width: 1000px;
    margin: auto; /* Esto centra el contenedor si es más estrecho que la ventana */
    background-color: #f9fafb; /* Similar a Tailwind bg-gray-50 */
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    position: relative; /* Necesario para el posicionamiento absoluto del botón de cierre */
    /* Para hacerlo más tipo "dialogo grande" sobre el mapa, necesitaríamos: */
    /* position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 1002; */
    /* max-height: 90vh; overflow-y: auto; */
    /* Sin embargo, esto cambiaría significativamente su comportamiento actual. */
    /* Por ahora, solo se asegura que el botón de cierre esté bien posicionado. */
  }

  h2 {
    color: #1f2937; /* Similar a Tailwind text-gray-800 */
    margin-bottom: 16px;
  }

  .search-section, .selected-client-section {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    border: 1px solid #e5e7eb; /* Tailwind border-gray-200 */
  }

  .form-group {
    margin-bottom: 15px;
  }

  label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: #374151; /* Tailwind text-gray-700 */
  }

  input[type="text"], input[type="number"], textarea {
    width: calc(100% - 22px); /* Ajustar por padding y borde */
    padding: 10px;
    border: 1px solid #d1d5db; /* Tailwind border-gray-300 */
    border-radius: 6px; /* Tailwind rounded-md */
    font-size: 1rem;
  }

  input[type="text"]:focus, input[type="number"]:focus, textarea:focus {
    outline: none;
    border-color: #2563eb; /* Tailwind focus:border-blue-500 */
    box-shadow: 0 0 0 2px #bfdbfe; /* Tailwind focus:ring-blue-200 */
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
  .input-group button {
    white-space: nowrap; /* Evitar que el texto del botón se divida */
  }

  button {
    padding: 10px 15px;
    background-color: #2563eb; /* Tailwind bg-blue-600 */
    color: white;
    border: none;
    border-radius: 6px; /* Tailwind rounded-md */
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.2s;
  }

  button:hover {
    background-color: #1d4ed8; /* Tailwind bg-blue-700 */
  }

  button.secondary {
    background-color: #4b5563; /* Tailwind bg-gray-600 */
  }
  button.secondary:hover {
    background-color: #374151; /* Tailwind bg-gray-700 */
  }

  .results-grid {
    margin-top: 20px;
    overflow-x: auto; /* Para tablas anchas en pantallas pequeñas */
  }

  .results-grid table { /* Aplicar al contenedor de la tabla para el scroll */
    width: 100%;
    border-collapse: collapse;
  }

  .table-container { /* Nuevo contenedor para el scroll vertical */
    max-height: 18em; /* Altura aproximada para 5 filas (5 * ~3em/fila + ajsutes) */
    overflow-y: auto;
    border: 1px solid #e5e7eb; /* Tailwind border-gray-200 */
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th, td {
    border: 1px solid #e5e7eb; /* Tailwind border-gray-200 */
    padding: 10px;
    text-align: left;
  }

  th {
    background-color: #f3f4f6; /* Tailwind bg-gray-100 */
    font-weight: 600;
  }

  tbody tr:hover {
    background-color: #f0f9ff; /* Tailwind hover:bg-blue-50 (aproximado) */
    cursor: pointer;
  }

  tbody tr.selected {
    background-color: #dbeafe; /* Tailwind bg-blue-200 (aproximado) */
  }

  .checkbox-group {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
  }
  .checkbox-group input[type="checkbox"] {
    margin-right: 8px;
    width: auto; /* Reset width for checkbox */
  }
  .checkbox-group label {
    margin-bottom: 0; /* Reset margin for label in checkbox group */
    font-weight: normal;
  }

  .message {
    padding: 10px;
    margin: 10px 0;
    border-radius: 6px;
    text-align: center;
  }
  .error-message {
    background-color: #fee2e2; /* Tailwind bg-red-100 */
    color: #b91c1c; /* Tailwind text-red-700 */
    border: 1px solid #fecaca; /* Tailwind border-red-300 */
  }
  .success-message {
    background-color: #dcfce7; /* Tailwind bg-green-100 */
    color: #15803d; /* Tailwind text-green-700 */
    border: 1px solid #bbf7d0; /* Tailwind border-green-300 */
  }

  .loading-indicator {
    text-align: center;
    padding: 15px;
    font-style: italic;
    color: #4b5563; /* Tailwind text-gray-600 */
  }

  .form-row {
    display: flex;
    gap: 20px; /* Espacio entre columnas */
    margin-bottom: 15px;
  }

  .form-column {
    flex: 1; /* Cada columna toma el mismo espacio */
    min-width: 200px; /* Ancho mínimo para evitar que se encojan demasiado */
  }

  /* Estilo para el botón de cierre del contenedor principal de BuscarCliente */
  .main-close-button {
    position: absolute; /* O fixed si el contenedor no es el body */
    top: 20px; /* Ajustar según la posición del contenedor principal */
    right: 20px; /* Ajustar según la posición del contenedor principal */
    background-color: #f44336; /* Rojo */
    color: white;
    border: none;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    z-index: 1005; /* Asegurar que esté sobre otros elementos del diálogo */
  }
  .main-close-button:hover {
    background-color: #d32f2f; /* Rojo más oscuro */
  }

</style>

<div class="container"> <!-- Este es el contenedor principal del componente -->
  <button class="main-close-button" on:click={() => dispatch('close')}>&times;</button>
  <h2>Buscar Cliente</h2>

  {#if errorMessage}
    <div class="message error-message">{errorMessage}</div>
  {/if}
  {#if successMessage}
    <div class="message success-message">{successMessage}</div>
  {/if}
  {#if isLoading}
    <div class="loading-indicator">Cargando...</div>
  {/if}

  <!-- Sección de Búsqueda de Clientes -->
  <div class="search-section">
    <h3>Criterios de Búsqueda</h3>
    <div class="form-group">
      <label for="search-cliente">Cliente:</label>
      <div class="input-group">
        <input type="text" id="search-cliente" bind:value={searchTermCliente} placeholder="Nombre del cliente">
        <button on:click={searchByName}>Buscar</button>
      </div>
    </div>

    <div class="form-group">
      <label for="search-direccion">Dirección (texto libre):</label>
      <div class="input-group">
        <input type="text" id="search-direccion" bind:value={searchTermDireccion} placeholder="Parte de la dirección">
        <button on:click={searchByAddress}>Por Dirección</button>
      </div>
    </div>

    <div class="form-group">
      <label>Calle y Altura:</label>
      <div class="input-group">
        <input type="text" bind:value={searchTermCalle} placeholder="Nombre de la calle">
        <input type="text" style="max-width: 100px;" bind:value={searchTermAltura} placeholder="Altura">
        <button on:click={searchByStreetHeight}>Buscar</button>
      </div>
    </div>
  </div>

  <!-- Grilla de Resultados -->
  {#if searchResults.length > 0}
    <div class="results-grid search-section">
      <h3>Resultados de Búsqueda</h3>
      <div class="table-container"> <!-- Contenedor para el scroll -->
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
      </div> <!-- Fin de table-container -->
    </div>
  {/if}

  <!-- Sección de Cliente Seleccionado -->
  {#if selectedClient}
    <div class="selected-client-section">
      <h3>Cliente Seleccionado: {selectedClient.nombre} (ID: {selectedClient.id})</h3>

      <div class="form-row">
        <div class="form-column">
          <div class="form-group">
            <label for="docenas">Docenas (Cantidad):</label>
            <input type="number" id="docenas" bind:value={editableFields.docenas} placeholder="Ej: 1.5">
          </div>
        </div>
        <div class="form-column">
          <div class="form-group">
            <label for="nro_pao">Nro. PaO:</label>
            <input type="number" id="nro_pao" bind:value={editableFields.nro_pao} placeholder="Ej: 123">
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

      <button on:click={saveChanges}>Guardar Cambios</button>
    </div>
  {/if}

</div>
