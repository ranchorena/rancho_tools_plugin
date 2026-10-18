<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import { API_BASE_URL } from './config.js';
  import { authorizedFetch } from './auth/session.mjs';
  import DialogHeader from './design-system/DialogHeader.svelte';
  import Icon from './design-system/Icon.svelte';
  import { dialogFocus } from './design-system/dialog-focus.mjs';

  export let cliente;
  export let coordenadas = null;
  export let seleccionandoUbicacion = false;

  const dispatch = createEventDispatcher();

  function fechaManana() {
    const manana = new Date();
    manana.setDate(manana.getDate() + 1);
    const mes = String(manana.getMonth() + 1).padStart(2, '0');
    const dia = String(manana.getDate()).padStart(2, '0');
    return `${manana.getFullYear()}-${mes}-${dia}`;
  }

  function isoATexto(iso) {
    const partes = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
    return partes ? `${partes[3]}/${partes[2]}/${partes[1]}` : '';
  }

  function textoAIso(texto) {
    const partes = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec((texto || '').trim());
    if (!partes) return null;
    const dia = Number(partes[1]);
    const mes = Number(partes[2]);
    const anio = Number(partes[3]);
    const fecha = new Date(anio, mes - 1, dia);
    if (fecha.getFullYear() !== anio || fecha.getMonth() !== mes - 1 || fecha.getDate() !== dia) return null;
    return `${partes[3]}-${partes[2]}-${partes[1]}`;
  }

  function formatearFecha(valor) {
    const digitos = String(valor || '').replace(/\D/g, '').slice(0, 8);
    if (digitos.length <= 2) return digitos;
    if (digitos.length <= 4) return `${digitos.slice(0, 2)}/${digitos.slice(2)}`;
    return `${digitos.slice(0, 2)}/${digitos.slice(2, 4)}/${digitos.slice(4)}`;
  }

  function puntoInicial(origen) {
    const lat = Number(origen?.latitud);
    const lon = Number(origen?.longitud);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
    return { lat, lon };
  }

  let formData = {
    tiene_pedido: true,
    es_regalo: false,
    cantidad: 1,
    fecha: fechaManana(),
    horario: '',
    nro_pao: '',
    observacion: '',
    direccion: cliente?.direccion || ''
  };

  let punto = puntoInicial(cliente);
  let esperandoMapa = false;
  let puntoAlPedirMapa = null;
  let georreferenciando = false;
  let guardando = false;
  let errorMessage = '';
  let cargaToken = 0;
  let fechaTexto = isoATexto(formData.fecha);
  let calendario;

  function pedidoNuevo(fecha) {
    return {
      tiene_pedido: true,
      es_regalo: false,
      cantidad: 1,
      fecha,
      horario: '',
      nro_pao: '',
      observacion: '',
      direccion: cliente?.direccion || ''
    };
  }

  function aplicarPedido(fecha, pedido) {
    fechaTexto = isoATexto(fecha);
    if (!pedido) {
      formData = pedidoNuevo(fecha);
      punto = puntoInicial(cliente);
      return;
    }
    formData = {
      tiene_pedido: true,
      es_regalo: false,
      cantidad: pedido.cantidad ?? '',
      fecha,
      horario: '',
      nro_pao: pedido.nro_pao ?? '',
      observacion: pedido.observacion || '',
      direccion: pedido.direccion || cliente?.direccion || ''
    };
    const lat = Number(pedido.latitud);
    const lon = Number(pedido.longitud);
    punto = Number.isFinite(lat) && Number.isFinite(lon) ? { lat, lon } : puntoInicial(cliente);
  }

  async function cargarPedidoDeLaFecha(fecha) {
    const token = ++cargaToken;
    if (!fecha) return;
    errorMessage = '';
    try {
      const response = await authorizedFetch(
        `${API_BASE_URL}/api/clientes/${cliente.id}/pedido?fecha=${encodeURIComponent(fecha)}`
      );
      const data = await response.json().catch(() => ({}));
      if (token !== cargaToken || formData.fecha !== fecha) return;
      if (!response.ok) {
        errorMessage = data.error || 'No se pudo consultar el pedido.';
        return;
      }
      aplicarPedido(fecha, data.pedido);
    } catch (error) {
      console.error('Error al consultar el pedido:', error);
      if (token === cargaToken) {
        errorMessage = 'No se pudo consultar el pedido.';
      }
    }
  }

  onMount(() => {
    cargarPedidoDeLaFecha(formData.fecha);
  });

  $: if (
    esperandoMapa &&
    coordenadas &&
    coordenadas !== puntoAlPedirMapa &&
    coordenadas.lat != null &&
    coordenadas.lon != null
  ) {
    tomarPuntoMapa(coordenadas);
  }

  function tomarPuntoMapa(coords) {
    punto = { lat: Number(coords.lat), lon: Number(coords.lon) };
    esperandoMapa = false;
  }

  $: coordenadasTexto = punto
    ? `Lat: ${punto.lat.toFixed(6)}, Lon: ${punto.lon.toFixed(6)}`
    : 'No seleccionadas';

  function handleTienePedido(event) {
    if (!event.currentTarget.checked) {
      cargaToken += 1;
      formData.cantidad = '';
      formData.fecha = '';
      fechaTexto = '';
      formData.nro_pao = '';
      return;
    }
    formData.cantidad = 1;
    formData.fecha = fechaManana();
    fechaTexto = isoATexto(formData.fecha);
    cargarPedidoDeLaFecha(formData.fecha);
  }

  function handleFechaInput(event) {
    fechaTexto = formatearFecha(event.currentTarget.value);
  }

  function aplicarFechaIso(iso) {
    if (!iso) {
      errorMessage = 'La fecha debe tener el formato dd/mm/aaaa.';
      return;
    }
    fechaTexto = isoATexto(iso);
    errorMessage = '';
    if (iso === formData.fecha) return;
    formData.fecha = iso;
    cargarPedidoDeLaFecha(iso);
  }

  function handleFecha() {
    fechaTexto = formatearFecha(fechaTexto);
    if (!fechaTexto) {
      cargaToken += 1;
      formData.fecha = '';
      return;
    }
    aplicarFechaIso(textoAIso(fechaTexto));
  }

  function mostrarCalendario() {
    if (!calendario) return;
    const iso = textoAIso(fechaTexto) || formData.fecha || '';
    if (iso) calendario.value = iso;
    try {
      if (typeof calendario.showPicker === 'function') {
        calendario.showPicker();
        return;
      }
    } catch (error) {
      console.error('No se pudo abrir el calendario:', error);
    }
    calendario.focus();
    calendario.click();
  }

  function handleCalendario(event) {
    aplicarFechaIso(event.currentTarget.value);
  }

  function handleSeleccionarUbicacion() {
    puntoAlPedirMapa = coordenadas;
    esperandoMapa = true;
    dispatch('seleccionarUbicacion');
  }

  async function handleGeorreferenciar() {
    const direccion = formData.direccion.trim();
    if (!direccion) {
      errorMessage = 'Ingresá una dirección para georreferenciar.';
      return;
    }

    georreferenciando = true;
    errorMessage = '';
    try {
      const response = await authorizedFetch(`${API_BASE_URL}/api/direcciones/buscar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ direccion })
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || data.latitud == null || data.longitud == null) {
        errorMessage = data.error || 'No se encontró la dirección.';
        return;
      }
      punto = { lat: Number(data.latitud), lon: Number(data.longitud) };
      dispatch('ubicacionGeorreferenciada', punto);
    } catch (error) {
      console.error('Error al georreferenciar:', error);
      errorMessage = 'No se pudo georreferenciar la dirección.';
    } finally {
      georreferenciando = false;
    }
  }

  async function guardar() {
    if (!formData.tiene_pedido || !punto) return;
    const fechaIso = textoAIso(fechaTexto);
    if (!fechaIso) {
      errorMessage = 'La fecha debe tener el formato dd/mm/aaaa.';
      return;
    }
    formData.fecha = fechaIso;

    guardando = true;
    errorMessage = '';
    try {
      const payload = {
        tiene_pedido: true,
        docenas: formData.cantidad !== '' && formData.cantidad != null ? parseFloat(formData.cantidad) : null,
        fecha: fechaIso,
        horario: formData.horario || null,
        nro_pao: formData.nro_pao !== '' && formData.nro_pao != null ? parseInt(formData.nro_pao, 10) : null,
        es_regalo: formData.es_regalo,
        observaciones: formData.observacion.trim(),
        direccion_pedido: formData.direccion.trim(),
        latitud: punto.lat,
        longitud: punto.lon
      };
      const response = await authorizedFetch(`${API_BASE_URL}/api/clientes/actualizar/${cliente.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        errorMessage = data.error || 'No se pudo registrar el pedido.';
        return;
      }
      dispatch('guardado', {
        message: data.mensaje || 'Pedido registrado correctamente.',
        latitud: punto.lat,
        longitud: punto.lon
      });
    } catch (error) {
      console.error('Error al guardar el pedido:', error);
      errorMessage = 'No se pudo registrar el pedido.';
    } finally {
      guardando = false;
    }
  }

  function cerrar() {
    dispatch('close');
  }
</script>

<div
  class="modal-backdrop"
  class:seleccionando-ubicacion={seleccionandoUbicacion}
  on:click|stopPropagation={cerrar}
  on:keydown|stopPropagation={(event) => event.key === 'Escape' && cerrar()}
  role="presentation"
>
  <div
    class="modal-content"
    use:dialogFocus
    on:click|stopPropagation
    on:keydown|stopPropagation={(event) => event.key === 'Escape' && cerrar()}
    role="dialog"
    aria-labelledby="agregar-pedido-title"
  >
    <div class="modal-header">
      <DialogHeader titleId="agregar-pedido-title">
        <Icon name="plus" size={18} />
        Agregar pedido
        <button slot="close" type="button" class="close-button ds-button ds-button--icon" on:click={cerrar} aria-label="Cerrar">
          <Icon name="close" size={16} />
        </button>
      </DialogHeader>
    </div>

    <div class="modal-body">
      {#if errorMessage}
        <div class="alert"><Icon name="alert" size={16} /> {errorMessage}</div>
      {/if}

      <div class="form-row">
        <div class="form-group">
          <label for="pedido-cliente-id">ID Cliente</label>
          <input id="pedido-cliente-id" class="ds-field" type="text" value={cliente.id} readonly>
        </div>
        <div class="form-group">
          <label for="pedido-cliente-nombre">Nombre</label>
          <input id="pedido-cliente-nombre" class="ds-field" type="text" value={cliente.nombre || ''} readonly>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="pedido-cliente-direccion">Dirección</label>
          <input id="pedido-cliente-direccion" class="ds-field" type="text" value={cliente.direccion || ''} readonly>
        </div>
        <div class="form-group">
          <label for="pedido-cliente-telefono">Teléfono</label>
          <input id="pedido-cliente-telefono" class="ds-field" type="text" value={cliente.telefono || ''} readonly>
        </div>
      </div>

      <div class="section-title">Información del pedido</div>
      <div class="pedido-opciones">
        <div class="checkbox-group">
          <input id="pedido-tiene" class="ds-choice" type="checkbox" bind:checked={formData.tiene_pedido} on:change={handleTienePedido}>
          <label for="pedido-tiene">Tiene pedido activo</label>
        </div>
        <div class="checkbox-group">
          <input id="pedido-regalo" class="ds-choice" type="checkbox" bind:checked={formData.es_regalo}>
          <label for="pedido-regalo">Es un regalo</label>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="pedido-cantidad">Cantidad</label>
          <input id="pedido-cantidad" class="ds-field field-cantidad" type="number" step="0.5" bind:value={formData.cantidad}>
        </div>
        <div class="form-group">
          <label for="pedido-fecha">Fecha</label>
          <div class="ds-date-control">
            <input id="pedido-fecha" class="ds-date-text" type="text" inputmode="numeric" maxlength="10" placeholder="dd/mm/aaaa" autocomplete="off" bind:value={fechaTexto} on:input={handleFechaInput} on:change={handleFecha}>
            <span class="ds-date-picker">
              <button type="button" on:click={mostrarCalendario} aria-label="Mostrar calendario">
                <Icon name="calendar" size={16} />
              </button>
              <input id="pedido-fecha-calendario" class="ds-date-native" type="date" tabindex="-1" aria-hidden="true" bind:this={calendario} value={formData.fecha} on:change={handleCalendario}>
            </span>
          </div>
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="pedido-horario">Horario Preferido</label>
          <input id="pedido-horario" class="ds-time" type="time" bind:value={formData.horario}>
        </div>
        <div class="form-group">
          <label for="pedido-pao">Número PAO</label>
          <input id="pedido-pao" class="ds-field field-pao" type="number" bind:value={formData.nro_pao}>
        </div>
      </div>
      <div class="form-group">
        <label for="pedido-observacion">Observaciones</label>
        <textarea id="pedido-observacion" class="ds-field" bind:value={formData.observacion} maxlength="200"></textarea>
      </div>

      <div class="section-title">Ubicación del pedido</div>
      <div class="form-group">
        <label for="pedido-direccion">Dirección del pedido</label>
        <div class="direccion-row">
          <input id="pedido-direccion" class="ds-field" type="text" bind:value={formData.direccion} maxlength="50">
          <button type="button" class="btn-geo ds-button ds-button--location" on:click={handleGeorreferenciar} disabled={georreferenciando}>
            <Icon name="pin" size={16} />
            {georreferenciando ? 'Buscando...' : 'Georreferenciar'}
          </button>
        </div>
      </div>
      <div class="coordenadas">
        <div class="coordenadas-info">{coordenadasTexto}</div>
        <button type="button" class="btn-geo ds-button ds-button--location" on:click={handleSeleccionarUbicacion}>
          <Icon name="pin" size={16} /> Seleccionar en mapa
        </button>
      </div>
    </div>

    <div class="modal-footer">
      <button type="button" class="ds-button" on:click={cerrar} disabled={guardando}>Cancelar</button>
      <button type="button" class="ds-button ds-button--primary" on:click={guardar} disabled={guardando || !punto || !formData.tiene_pedido}>
        {guardando ? 'Guardando...' : 'Guardar'}
      </button>
    </div>
  </div>
</div>

<style>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    z-index: 1100;
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba(0, 0, 0, 0.5);
    padding: 1rem;
  }

  .modal-backdrop.seleccionando-ubicacion {
    pointer-events: none;
    background: transparent;
  }

  .modal-backdrop.seleccionando-ubicacion .modal-content {
    visibility: hidden;
  }

  .modal-content {
    width: min(640px, calc(100vw - 2rem));
    max-height: min(90vh, 900px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: var(--ds-surface);
    color: var(--ds-text);
    border-radius: 12px;
    box-shadow: var(--ds-shadow-dialog);
  }

  .modal-body {
    overflow-y: auto;
    padding: 1rem 1.25rem;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 0.6rem;
    padding: 0.9rem 1.25rem;
    background: var(--ds-background);
    box-shadow: inset 0 1px var(--ds-divider);
  }

  .modal-footer button {
    width: auto;
    margin: 0;
  }

  .close-button {
    width: 2rem;
    height: 2rem;
    margin: 0;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .alert {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 1rem;
    padding: 0.75rem;
    border: 1px solid var(--ds-error);
    border-radius: 8px;
    background: var(--ds-error-surface);
    color: var(--ds-error);
  }

  .section-title {
    margin: 0.5rem 0 0.75rem;
    font-weight: 600;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 1rem;
  }

  label {
    margin-bottom: 0.35rem;
    font-weight: 500;
  }

  input, textarea {
    width: 100%;
    margin: 0;
    box-sizing: border-box;
  }

  textarea {
    min-height: 80px;
    resize: vertical;
  }

  input[readonly] {
    color: var(--ds-text-muted);
  }

  .direccion-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .direccion-row input {
    flex: 1;
    min-width: 0;
    width: auto;
  }

  .btn-geo, .close-button {
    flex: 0 0 auto;
    width: auto;
    margin: 0;
    white-space: nowrap;
  }

  .btn-geo {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
  }

  .pedido-opciones, .checkbox-group {
    display: flex;
    align-items: center;
    gap: 0.75rem 1.5rem;
    margin-bottom: 1rem;
  }

  .checkbox-group {
    margin-bottom: 0;
  }

  .checkbox-group input {
    width: auto;
    margin: 0;
  }

  .ds-date-control .ds-date-text {
    width: 10ch;
    flex: 0 0 auto;
  }

  input.ds-time {
    width: fit-content;
    max-width: 100%;
    align-self: flex-start;
    field-sizing: content;
  }

  .field-cantidad { width: 7.5rem; max-width: 100%; }
  .field-pao { width: 8rem; max-width: 100%; }

  .coordenadas {
    margin-bottom: 1rem;
    padding: 0.9rem;
    text-align: center;
    border: 2px dashed var(--ds-border);
    border-radius: 8px;
  }

  .coordenadas-info {
    margin-bottom: 0.75rem;
    font-family: 'Courier New', monospace;
  }

  @media (max-width: 640px) {
    .form-row { grid-template-columns: 1fr; }
    .direccion-row { flex-wrap: wrap; }
  }
</style>
