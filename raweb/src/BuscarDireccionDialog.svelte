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
    if (event.key === 'Escape') {
      handleCancelar();
    }
  }
</script>

<div class="modal-backdrop" on:click={handleCancelar}>
  <div class="modal-content" on:click|stopPropagation>
    <div class="modal-header">
      <h2>📍 Buscar Dirección</h2>
      <button class="close-button" on:click={handleCancelar} aria-label="Cerrar">
        &times;
      </button>
    </div>

    <div class="modal-body">
      <div class="input-group">
        <label for="direccion-input">Ingrese la dirección a buscar:</label>
        <input
          id="direccion-input"
          type="text"
          bind:value={direccionInput}
          placeholder="Ej: SARMIENTO 550"
          on:keydown={handleKeydown}
          autofocus
        />
      </div>
    </div>

    <div class="modal-footer">
      <button class="btn-primary" on:click={handleBuscar}>
        🔍 Buscar
      </button>
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
    max-width: 500px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow: hidden;
    animation: modalSlideIn 0.3s ease-out;
  }

  @keyframes modalSlideIn {
    from {
      opacity: 0;
      transform: scale(0.9) translateY(-20px);
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
    padding: 0.5rem 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    flex-shrink: 0;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #1f2937;
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
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }

  .close-button:hover {
    color: #374151;
    background-color: #f3f4f6;
  }

  .modal-body {
    padding: 1rem 1.5rem;
    flex-grow: 1;
    overflow-y: auto;
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  label {
    font-weight: 500;
    color: #374151;
    font-size: 0.9rem;
  }

  input[type="text"] {
    width: 100%;
    padding: 0.875rem 1rem;
    border: 2px solid #d1d5db;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-sizing: border-box;
    margin: 0;
  }

  input[type="text"]:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .modal-footer {
    display: flex;
    justify-content: center;
    gap: 0.75rem;
    padding: 1rem 1.5rem 1.5rem 1.5rem;
    border-top: 1px solid #e5e7eb;
    flex-shrink: 0;
  }

  .btn-primary {
    padding: 0.625rem 1.25rem;
    border: 1px solid #3b82f6;
    border-radius: 6px;
    background-color: #3b82f6;
    color: #fff;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.9rem;
    min-height: 44px;
  }

  .btn-primary:hover {
    background-color: #2563eb;
    border-color: #2563eb;
  }

  .btn-primary:focus {
    outline: none;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  /* Responsive breakpoints */
  @media (max-width: 768px) {
    .modal-backdrop {
      padding: 0.5rem;
      align-items: flex-start;
      padding-top: 2rem;
    }

    .modal-content {
      max-width: 100%;
      border-radius: 8px;
      max-height: calc(100vh - 3rem);
    }

    .modal-header {
      padding: 0.375rem 1rem;
    }

    .modal-header h2 {
      font-size: 1.125rem;
    }

    .close-button {
      font-size: 1.5rem;
      width: 36px;
      height: 36px;
    }

    .modal-body {
      padding: 0.75rem 1rem;
    }

    .modal-footer {
      padding: 0.75rem 1rem 1rem 1rem;
      justify-content: center;
    }

    .btn-primary {
      width: 100%;
      padding: 0.875rem 1rem;
      font-size: 1rem;
      min-height: 48px;
      max-width: 300px;
    }

    input[type="text"] {
      padding: 1rem;
      font-size: 16px; /* Evita zoom en iOS */
    }
  }

  /* Pantallas muy pequeñas */
  @media (max-width: 480px) {
    .modal-backdrop {
      padding: 0.25rem;
      padding-top: 1rem;
    }

    .modal-content {
      border-radius: 6px;
      max-height: calc(100vh - 1.5rem);
    }

    .modal-header {
      padding: 0.375rem 0.875rem;
    }

    .modal-body {
      padding: 0.625rem 0.875rem;
    }

    .modal-footer {
      padding: 0.625rem 0.875rem 0.875rem 0.875rem;
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

    .modal-footer {
      justify-content: center;
    }

    .btn-primary {
      width: auto;
      min-width: 140px;
      max-width: none;
    }
  }

  /* Tablet */
  @media (min-width: 769px) and (max-width: 1024px) {
    .modal-content {
      max-width: 400px;
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
