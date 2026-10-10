<script>
  import { createEventDispatcher } from 'svelte';
  import { API_BASE_URL } from './config.js';
  import DialogHeader from './design-system/DialogHeader.svelte';
  import { dialogFocus } from './design-system/dialog-focus.mjs';

  const dispatch = createEventDispatcher();

  // Props
  export let coordenadas = null; // { lat, lon } - coordenadas seleccionadas en el mapa
  export let seleccionandoUbicacion = false;

  // Estado del formulario
  let formData = {
    nombre: '',
    direccion: '',
    calle: '',
    altura: '',
    telefono: '',
    tiene_pedido: false,
    cantidad: '',
    horario: '',
    nro_pao: '',
    observacion: '',
    es_regalo: false
  };

  // Estado de la interfaz
  let isLoading = false;
  let errorMessage = '';
  let successMessage = '';

  // Reactivamente mostrar las coordenadas
  $: coordenadasTexto = coordenadas ? 
    `Lat: ${coordenadas.lat.toFixed(6)}, Lon: ${coordenadas.lon.toFixed(6)}` : 
    'No seleccionadas';

  async function handleSubmit() {
    // Validaciones básicas
    if (!formData.nombre.trim()) {
      errorMessage = 'El nombre del cliente es requerido.';
      return;
    }

    if (!formData.direccion.trim()) {
      errorMessage = 'La dirección del cliente es requerida.';
      return;
    }

    if (!coordenadas) {
      errorMessage = 'Debe seleccionar una ubicación en el mapa.';
      return;
    }

    isLoading = true;
    errorMessage = '';
    successMessage = '';

    try {
      // Preparar datos para envío
      const clienteData = {
        nombre: formData.nombre.trim(),
        direccion: formData.direccion.trim(),
        calle: formData.calle.trim() || undefined,
        altura: formData.altura ? parseInt(formData.altura) : undefined,
        telefono: formData.telefono.trim() || undefined,
        tiene_pedido: formData.tiene_pedido,
        cantidad: formData.cantidad ? parseFloat(formData.cantidad) : undefined,
        horario: formData.horario || undefined,
        nro_pao: formData.nro_pao ? parseInt(formData.nro_pao) : undefined,
        observacion: formData.observacion.trim() || undefined,
        es_regalo: formData.es_regalo,
        latitud: coordenadas.lat,
        longitud: coordenadas.lon
      };

      const response = await fetch(`${API_BASE_URL}/api/clientes/agregar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(clienteData)
      });

      const result = await response.json();

      if (response.ok) {
        successMessage = result.mensaje || 'Cliente agregado correctamente.';
        
        // Notificar éxito al componente padre
        dispatch('clienteAgregado', {
          cliente: result.cliente,
          message: successMessage
        });

        // Limpiar formulario después del éxito
        setTimeout(() => {
          dispatch('close');
        }, 2000);

      } else {
        errorMessage = result.error || 'Error al agregar el cliente.';
      }
    } catch (error) {
      console.error('Error al agregar cliente:', error);
      errorMessage = 'Error de conexión. Verifique su conexión a internet.';
    } finally {
      isLoading = false;
    }
  }

  function handleCancel() {
    dispatch('close');
  }

  function handleSeleccionarUbicacion() {
    dispatch('seleccionarUbicacion');
  }
</script>

<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    backdrop-filter: blur(2px);
  }

  .modal-content {
    background: var(--ds-surface);
    color: var(--ds-text);
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .modal-header {
    background: var(--ds-surface);
    color: var(--ds-text);
    box-shadow: inset 0 -1px var(--ds-border);
    padding: 0;
  }

  .modal-header :global(.ds-dialog-header) {
    padding-top: 0;
    padding-bottom: 0;
  }

  .close-button {
    box-sizing: border-box;
    min-height: 32px;
    margin: 0;
    background: none;
    border: none;
    color: var(--ds-text-muted);
    font-size: 1rem;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 50%;
    transition: background-color 0.2s;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close-button:hover {
    background: var(--ds-secondary-hover);
    color: var(--ds-on-secondary);
  }

  .close-button:active {
    background: var(--ds-secondary-hover);
    color: var(--ds-on-secondary);
  }

  @media (max-width: 768px) {
    .close-button {
      width: 36px;
      height: 36px;
      font-size: 1rem;
    }
  }

  .modal-body {
    padding: 2rem;
    overflow-y: auto;
    flex: 1;
  }

  .form-section {
    margin-bottom: 2rem;
  }

  .section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--ds-text);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--ds-border);
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
  }

  .form-group.full-width {
    grid-column: 1 / -1;
  }

  .form-group label {
    font-weight: 500;
    color: var(--ds-text);
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }

  .form-group input,
  .form-group textarea {
    padding: 0.75rem;
    border: 2px solid var(--ds-border);
    border-radius: 8px;
    font-size: 0.9rem;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .form-group input.ds-field,
  .form-group textarea.ds-field {
    color: var(--ds-text);
    background-color: var(--ds-surface);
    border-color: var(--ds-border);
  }
  /* Mantener el anillo compartido en controles y observación. */
  .form-group input:focus,
  .form-group textarea:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
    border-color: var(--ds-focus);
    box-shadow: none;
  }

  .form-group input.ds-field:focus,
  .form-group textarea.ds-field:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
    border-color: var(--ds-focus);
    box-shadow: none;
  }

  .form-group textarea {
    min-height: 80px;
    resize: vertical;
  }

  .checkbox-group {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }

  .checkbox-group input[type="checkbox"] {
    width: auto;
    margin: 0;
    outline: 1px solid var(--ds-border);
    outline-offset: 0;
  }

  .coordenadas-section {
    background: var(--ds-surface);
    border: 2px dashed var(--ds-border);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
  }

  .coordenadas-info {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    color: var(--ds-text-muted);
    margin-bottom: 1rem;
  }

  .btn-seleccionar {
    background: var(--ds-location);
    color: var(--ds-on-location);
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .btn-seleccionar:hover {
    background: var(--ds-location-hover);
    transform: translateY(-1px);
    box-shadow: var(--ds-shadow-panel);
  }

  .btn-seleccionar:active {
    background: var(--ds-location-active);
  }

  .btn-seleccionar:focus,
  .close-button:focus,
  .checkbox-group input[type="checkbox"]:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
  }

  .alert {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-weight: 500;
  }

  .alert-error {
    background-color: var(--ds-error-surface);
    color: var(--ds-error);
    border: 1px solid var(--ds-error);
  }

  .alert-success {
    background-color: var(--ds-success-surface);
    color: var(--ds-success);
    border: 1px solid var(--ds-success);
  }

  .modal-footer {
    padding: 1.5rem 2rem;
    background: var(--ds-surface);
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    border-top: 1px solid var(--ds-border);
  }

  .btn {
    min-width: 0;
    overflow-wrap: anywhere;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
    font-size: 0.9rem;
  }

  .btn-secondary {
    background: var(--ds-secondary);
    color: var(--ds-on-secondary);
    border: 1px solid var(--ds-border);
  }

  .btn-secondary:hover {
    background: var(--ds-secondary-hover);
    color: var(--ds-on-secondary);
  }

  .btn-primary {
    background: var(--ds-primary);
    color: var(--ds-on-primary);
    border: 1px solid var(--ds-primary);
  }

  .btn-primary:hover:not(:disabled) {
    background: var(--ds-primary-hover);
    border-color: var(--ds-primary-hover);
    transform: translateY(-1px);
  }

  .btn-primary:active:not(:disabled) {
    background: var(--ds-primary-active);
    border-color: var(--ds-primary-active);
  }

  .btn-secondary.ds-button {
    color: var(--ds-on-secondary);
    background: var(--ds-secondary);
    border: 1px solid var(--ds-border);
  }

  .btn-secondary.ds-button:hover:not(:disabled) {
    background: var(--ds-secondary-hover);
    color: var(--ds-on-secondary);
  }

  .btn-secondary.ds-button:active:not(:disabled) {
    background: var(--ds-secondary-active);
  }

  .btn-primary.ds-button--primary:focus,
  .btn-secondary.ds-button:focus {
    outline: 3px solid var(--ds-focus);
    outline-offset: 2px;
  }

  /* Al seleccionar un punto, retirar temporalmente el diálogo del hit-testing
     para que el clic físico llegue al viewport de OpenLayers. */
  .modal-backdrop.seleccionando-ubicacion {
    pointer-events: none;
    background: transparent;
    backdrop-filter: none;
  }

  .modal-backdrop.seleccionando-ubicacion .modal-content {
    visibility: hidden;
  }

  .btn-primary:disabled,
  .btn-secondary:disabled {
    color: var(--ds-on-disabled);
    background: var(--ds-disabled);
    border-color: var(--ds-border);
    opacity: 1;
    cursor: not-allowed;
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 0.5rem;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Responsive */
  @media (max-width: 640px) {
    .modal-content {
      width: 95%;
      margin: 1rem;
    }

    .modal-body,
    .modal-footer {
      padding: 1rem;
    }

    .modal-header {
      padding: 0;
    }

    .form-row {
      grid-template-columns: 1fr;
    }
  }
</style>

<div class="modal-backdrop"
     class:seleccionando-ubicacion={seleccionandoUbicacion}
     on:click={handleCancel}
     on:keydown={(e) => e.key === 'Escape' && handleCancel()}
     role="button"
     tabindex="0"
     aria-label="Cerrar modal">
  <div class="modal-content"
       use:dialogFocus
       on:click|stopPropagation
       on:keydown|stopPropagation
       role="dialog"
       aria-labelledby="agregar-cliente-title">
    <div class="modal-header">
      <DialogHeader titleId="agregar-cliente-title">
        ➕ Agregar Nuevo Cliente
        <button slot="close" type="button" class="close-button ds-focus" on:click={handleCancel} aria-label="Cerrar">
          &times;
        </button>
      </DialogHeader>
    </div>

    <div class="modal-body">
      {#if errorMessage}
        <div class="alert alert-error">
          ⚠️ {errorMessage}
        </div>
      {/if}

      {#if successMessage}
        <div class="alert alert-success">
          ✅ {successMessage}
        </div>
      {/if}

      <form on:submit|preventDefault={handleSubmit}>
        <!-- Información Básica -->
        <div class="form-section">
          <div class="section-title">📋 Información Básica</div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="nombre">Nombre *</label>
              <input
                id="nombre"
                data-dialog-initial-focus
                type="text"
                class="ds-field"
                bind:value={formData.nombre}
                placeholder="Nombre completo del cliente"
                maxlength="60"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="telefono">Teléfono</label>
              <input
                id="telefono"
                type="tel"
                class="ds-field"
                bind:value={formData.telefono}
                placeholder="+54 11 1234-5678"
                maxlength="30"
              />
            </div>
          </div>

          <div class="form-group full-width">
            <label for="direccion">Dirección *</label>
            <input
              id="direccion"
              type="text"
              class="ds-field"
              bind:value={formData.direccion}
              placeholder="Dirección completa"
              maxlength="50"
              required
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="calle">Calle</label>
              <input
                id="calle"
                type="text"
                class="ds-field"
                bind:value={formData.calle}
                placeholder="Nombre de la calle"
                maxlength="50"
              />
            </div>
            
            <div class="form-group">
              <label for="altura">Altura</label>
              <input
                id="altura"
                type="number"
                class="ds-field"
                bind:value={formData.altura}
                placeholder="Número de altura"
              />
            </div>
          </div>
        </div>

        <!-- Ubicación -->
        <div class="form-section">
          <div class="section-title">📍 Ubicación</div>
          <div class="coordenadas-section">
            <div class="coordenadas-info">
              {coordenadasTexto}
            </div>
            <button 
              type="button" 
               class="btn-seleccionar ds-button ds-button--location"
              on:click={handleSeleccionarUbicacion}
            >
              📍 Seleccionar en Mapa
            </button>
          </div>
        </div>

        <!-- Información del Pedido -->
        <div class="form-section">
          <div class="section-title">📦 Información del Pedido</div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="cantidad">Cantidad</label>
              <input
                id="cantidad"
                type="number"
                class="ds-field"
                step="0.5"
                bind:value={formData.cantidad}
                placeholder="0"
              />
            </div>
            
            <div class="form-group">
              <label for="horario">Horario Preferido</label>
              <input
                id="horario"
                type="time"
                class="ds-field"
                bind:value={formData.horario}
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="nro_pao">Número PAO</label>
              <input
                id="nro_pao"
                type="number"
                class="ds-field"
                bind:value={formData.nro_pao}
                placeholder="Número de PAO"
              />
            </div>
            
            <div class="form-group">
              <div class="checkbox-group">
                <input
                  id="tiene_pedido"
                  type="checkbox"
                  class="ds-choice"
                  bind:checked={formData.tiene_pedido}
                />
                <label for="tiene_pedido">Tiene pedido activo</label>
              </div>
              
              <div class="checkbox-group">
                <input
                  id="es_regalo"
                  type="checkbox"
                  class="ds-choice"
                  bind:checked={formData.es_regalo}
                />
                <label for="es_regalo">Es un regalo</label>
              </div>
            </div>
          </div>

          <div class="form-group full-width">
            <label for="observacion">Observaciones</label>
            <textarea
              id="observacion"
              class="ds-field"
              bind:value={formData.observacion}
              placeholder="Observaciones adicionales..."
              maxlength="200"
            ></textarea>
          </div>
        </div>
      </form>
    </div>

    <div class="modal-footer">
      <button 
        type="button" 
        class="btn btn-secondary ds-button"
        on:click={handleCancel}
        disabled={isLoading}
      >
        Cancelar
      </button>
      
      <button 
        type="button" 
        class="btn btn-primary ds-button ds-button--primary"
        on:click={handleSubmit}
        disabled={isLoading || !coordenadas}
      >
        {#if isLoading}
          <span class="loading-spinner"></span>
        {/if}
        {isLoading ? 'Guardando...' : 'Guardar Cliente'}
      </button>
    </div>
  </div>
</div>
