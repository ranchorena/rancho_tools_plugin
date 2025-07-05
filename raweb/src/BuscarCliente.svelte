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

    // Scroll automático a la sección del cliente seleccionado
    if (client) {
      await tick(); // Esperar a que el DOM se actualice
      const selectedClientSection = document.getElementById("selected-client-details");
      if (selectedClientSection) {
        selectedClientSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    }
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

  /* Estilos para el modal */
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
    z-index: 1001; /* Encima del navbar, igual que BuscarDireccionDialog */
  }

  .modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    width: 90%; /* Ancho relativo a la ventana */
    max-width: 700px; /* Reducido de 1000px a 700px para hacerlo más angosto */
    max-height: 90vh; /* Alto máximo para permitir scroll */
    display: flex; /* Usar flexbox para la estructura interna */
    flex-direction: column; /* Dirección de los elementos internos */
    position: relative; /* Para el botón de cierre interno */
  }

  .modal-header {
    /* Contenedor para el título y el botón de cierre, no se desplaza */
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 10px; /* Espacio antes del contenido desplazable */
    border-bottom: 1px solid #e5e7eb; /* Separador visual */
    margin-bottom: 10px;
  }

  .modal-body {
    /* Contenedor para el contenido que sí se desplaza */
    overflow-y: auto;
    flex-grow: 1; /* Ocupa el espacio restante */
    padding-right: 15px; /* Espacio para la barra de scroll si aparece */
    margin-right: -15px; /* Compensar el padding-right para alinear contenido */
  }

  /* Estilo para el botón de cierre, para que coincida con BuscarDireccionDialog */
  .close-button {
    background: transparent;
    border: none;
    font-size: 1.5rem; /* Coincide con BuscarDireccionDialog */
    cursor: pointer;
    padding: 0;
    line-height: 1;
    color: #333; /* Mantener un color visible */
    font-weight: normal; /* Quitar bold si no está en el original */
  }
  .close-button:hover {
    color: #000;
  }

  h2 {
    color: #1f2937;
    margin-top: 0;
    margin-bottom: 0; /* Ajustado porque está en el modal-header */
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
    max-width: 50%; /* Reducir a la mitad */
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

  /* Estilo base para botones */
  button {
    padding: 8px 15px; /* BuscarDireccionDialog */
    cursor: pointer;
    border: 1px solid #ccc; /* global.css / BuscarDireccionDialog */
    border-radius: 4px; /* BuscarDireccionDialog */
    background-color: #f4f4f4; /* global.css */
    color: #333; /* global.css */
    font-size: inherit; /* global.css */
    transition: background-color 0.2s, border-color 0.2s;
    margin-left: 5px; /* Pequeño margen entre botones si están juntos */
  }
  button:first-of-type { /* Para grupos de botones como en .input-group o .modal-actions */
      /* margin-left: 0; No, porque el botón Guardar Cambios es único en su línea a veces */
  }


  button:hover {
    background-color: #e9e9e9; /* Un hover genérico */
    border-color: #bbb;
  }

  button:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
  }

  /* Estilo para botones primarios (equivalente al "Buscar" de BuscarDireccionDialog) */
  button.primary,
  .input-group button, /* Los botones de búsqueda en input-group serán primarios */
  .selected-client-section button /* El botón "Guardar Cambios" */ {
    background-color: #007bff; /* Azul primario */
    color: white;
    border-color: #007bff;
  }

  button.primary:hover,
  .input-group button:hover,
  .selected-client-section button:hover {
    background-color: #0056b3; /* Azul más oscuro */
    border-color: #0056b3;
  }

  /* Si se necesita un botón secundario explícito diferente al base */
  /* button.secondary { ... } */

  .results-grid {
    margin-top: 20px;
    overflow-x: auto; /* Para tablas anchas en pantallas pequeñas */
  }

  .results-grid table { /* Aplicar al contenedor de la tabla para el scroll */
    width: 100%;
    border-collapse: collapse;
  }

  .table-container { /* Contenedor para el scroll vertical */
    max-height: 18em;
    overflow-y: auto;
    border: 1px solid #ccc; /* Borde unificado */
    border-radius: 4px; /* Consistente con otros elementos */
    margin-top: 10px; /* Espacio antes de la tabla */
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th, td {
    border: 1px solid #ccc; /* Borde unificado */
    padding: 8px; /* Un poco menos padding */
    text-align: left;
  }

  th {
    background-color: #f4f4f4; /* Mismo color que fondo de botón base (global.css) */
    font-weight: bold; /* Estándar para cabeceras */
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

<!-- Estructura del Modal -->
<div class="modal-backdrop" on:click={() => dispatch('close')}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <h2>Buscar Cliente</h2>
      <button class="close-button" on:click={() => dispatch('close')}>&times;</button> {/* Clase cambiada */}
    </div>

    <div class="modal-body">
      <!-- Contenido Original del Componente -->
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
    <div class="selected-client-section" id="selected-client-details"> {/* ID añadido */}
      <h3>Cliente Seleccionado: {selectedClient.nombre} (ID: {selectedClient.id})</h3>

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

      <button on:click={saveChanges}>Guardar Cambios</button>
    </div>
  {/if}
    </div> <!-- Fin modal-body -->
  </div> <!-- Fin modal-content -->
</div> <!-- Fin modal-backdrop -->
