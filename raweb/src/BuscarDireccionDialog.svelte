<script>
  import { createEventDispatcher } from 'svelte';

  const dispatch = createEventDispatcher();

  let direccionInput = '';

  function handleBuscar() {
    if (direccionInput.trim() === '') {
      alert('Por favor, ingrese una dirección.');
      return;
    }
    dispatch('buscar', { direccion: direccionInput.trim() });
  }

  function handleCancelar() {
    dispatch('close');
  }

  // Permitir submit con Enter en el input
  function handleKeydown(event) {
    if (event.key === 'Enter') {
      handleBuscar();
    }
  }
</script>

<div class="modal-backdrop"> <!-- Eliminado on:click={handleCancelar} -->
  <div class="modal-content" on:click|stopPropagation>
    <button class="close-button" on:click={handleCancelar}>&times;</button>
    <h2>Buscar Dirección</h2>
    <input
      type="text"
      bind:value={direccionInput}
      placeholder="Ej: SARMIENTO 550"
      on:keydown={handleKeydown}
      autofocus
    />
    <div class="modal-actions">
      <button on:click={handleBuscar}>Buscar</button>
      <button on:click={handleCancelar}>Cancelar</button>
    </div>
  </div>
</div>

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
    z-index: 1001; /* Encima del navbar */
  }

  .modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    min-width: 300px;
    max-width: 500px;
    position: relative; /* Para posicionar el botón de cierre absoluto */
  }

  .close-button {
    position: absolute;
    top: 10px;
    right: 10px;
    background: transparent;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0;
    line-height: 1;
  }

  .modal-content h2 {
    margin-top: 0;
  }

  .modal-content input[type="text"] {
    width: calc(100% - 20px); /* Ajustar por padding del input */
    padding: 10px;
    margin-bottom: 15px;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  .modal-actions {
    text-align: right;
  }

  .modal-actions button {
    margin-left: 10px;
    padding: 8px 15px;
    cursor: pointer;
    border: 1px solid #ccc;
    border-radius: 4px;
  }

  .modal-actions button:first-child {
    background-color: #007bff; /* Azul para el botón principal */
    color: white;
    border-color: #007bff;
  }
  .modal-actions button:first-child:hover {
    background-color: #0056b3;
  }
</style>
