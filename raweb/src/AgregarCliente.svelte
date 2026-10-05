<script>
  import { createEventDispatcher } from 'svelte';
  import { API_BASE_URL } from './config.js';

  const dispatch = createEventDispatcher();

  // Props
  export let coordenadas = null; // { lat, lon } - coordenadas seleccionadas en el mapa

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
    background: white;
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
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
  }

  .close-button {
    background: none;
    border: none;
    color: white;
    font-size: 1.5rem;
    cursor: pointer;
    padding: 0.25rem;
    border-radius: 4px;
    transition: background-color 0.2s;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .close-button:hover {
    background: rgba(255, 255, 255, 0.2);
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
    color: #374151;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e5e7eb;
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
    color: #374151;
    margin-bottom: 0.5rem;
    font-size: 0.9rem;
  }

  .form-group input,
  .form-group textarea {
    padding: 0.75rem;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 0.9rem;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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
  }

  .coordenadas-section {
    background: #f8fafc;
    border: 2px dashed #cbd5e1;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
  }

  .coordenadas-info {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 1rem;
  }

  .btn-seleccionar {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .btn-seleccionar:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
  }

  .alert {
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
    font-weight: 500;
  }

  .alert-error {
    background-color: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
  }

  .alert-success {
    background-color: #f0fdf4;
    color: #16a34a;
    border: 1px solid #bbf7d0;
  }

  .modal-footer {
    padding: 1.5rem 2rem;
    background: #f8fafc;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    border-top: 1px solid #e5e7eb;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
    font-size: 0.9rem;
  }

  .btn-secondary {
    background: #f1f5f9;
    color: #64748b;
    border: 1px solid #cbd5e1;
  }

  .btn-secondary:hover {
    background: #e2e8f0;
    color: #475569;
  }

  .btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
  }

  .btn-primary:disabled {
    opacity: 0.6;
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

    .modal-header,
    .modal-body,
    .modal-footer {
      padding: 1rem;
    }

    .form-row {
      grid-template-columns: 1fr;
    }
  }
</style>

<div class="modal-backdrop" 
     on:click={handleCancel}
     on:keydown={(e) => e.key === 'Escape' && handleCancel()}
     role="button"
     tabindex="0"
     aria-label="Cerrar modal">
  <div class="modal-content" 
       on:click|stopPropagation
       on:keydown|stopPropagation
       role="dialog"
       aria-labelledby="agregar-cliente-title">
    <div class="modal-header">
      <h2 id="agregar-cliente-title">➕ Agregar Nuevo Cliente</h2>
      <button class="close-button" on:click={handleCancel} aria-label="Cerrar">
        &times;
      </button>
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
                type="text"
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
              class="btn-seleccionar"
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
                bind:value={formData.nro_pao}
                placeholder="Número de PAO"
              />
            </div>
            
            <div class="form-group">
              <div class="checkbox-group">
                <input
                  id="tiene_pedido"
                  type="checkbox"
                  bind:checked={formData.tiene_pedido}
                />
                <label for="tiene_pedido">Tiene pedido activo</label>
              </div>
              
              <div class="checkbox-group">
                <input
                  id="es_regalo"
                  type="checkbox"
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
        class="btn btn-secondary" 
        on:click={handleCancel}
        disabled={isLoading}
      >
        Cancelar
      </button>
      
      <button 
        type="button" 
        class="btn btn-primary" 
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
