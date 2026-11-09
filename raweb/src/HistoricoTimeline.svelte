<script>
  import { createEventDispatcher } from 'svelte';
  import Icon from './design-system/Icon.svelte';
  import {
    acercarFecha,
    etiquetaEscala,
    etiquetasVisibles,
    fechaAnterior,
    fechaDesdePosicion,
    fechaSiguiente,
    estadisticasFecha,
    parseFechaEditable,
    posicionFecha,
    textoCantidad,
    textoDiaMesAnio,
    textoFecha,
    textoValor
  } from './historico-timeline.mjs';

  export let fechas = [];
  export let fechaActual = '';
  export let pedidos = [];
  export let reproduciendo = false;
  export let intervaloSegundos = 1;

  const dispatch = createEventDispatcher();

  let pista;
  let anchoPista = 0;
  let arrastrando = false;
  let punteroActivo = false;
  let posicionArrastre = null;
  let editandoFecha = false;
  let textoEdicion = '';
  let fechaInvalida = false;

  $: anterior = fechaAnterior(fechaActual, fechas);
  $: siguiente = fechaSiguiente(fechaActual, fechas);
  $: indice = Math.max(0, fechas.indexOf(fechaActual));
  $: texto = textoFecha(fechaActual);
  $: estadisticas = estadisticasFecha(pedidos);
  $: if (!editandoFecha) textoEdicion = texto;
  $: posicion = arrastrando && posicionArrastre != null
    ? posicionArrastre
    : posicionFecha(fechaActual, fechas);
  $: marcas = fechas.map((fecha) => ({
    fecha,
    posicion: posicionFecha(fecha, fechas),
    etiqueta: etiquetaEscala(fecha)
  }));
  $: visibles = etiquetasVisibles(fechas, anchoPista);

  function emitirFecha(fecha) {
    if (!fecha) return;
    dispatch('cambiarFecha', { fecha });
  }

  function alFocoFecha(event) {
    if (reproduciendo) dispatch('reproducir', { activo: false });
    editandoFecha = true;
    fechaInvalida = false;
    textoEdicion = textoDiaMesAnio(fechaActual);
    event.currentTarget.value = textoEdicion;
    event.currentTarget.select();
  }

  function confirmarFecha(input) {
    if (!editandoFecha) return;
    const iso = parseFechaEditable(input.value);
    editandoFecha = false;
    if (!iso) {
      fechaInvalida = true;
      textoEdicion = texto;
      return;
    }
    fechaInvalida = false;
    const cercana = acercarFecha(iso, fechas);
    textoEdicion = textoFecha(cercana || fechaActual);
    if (cercana && cercana !== fechaActual) emitirFecha(cercana);
  }

  function alTeclaFecha(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      confirmarFecha(event.currentTarget);
      event.currentTarget.blur();
    } else if (event.key === 'Escape') {
      event.preventDefault();
      editandoFecha = false;
      fechaInvalida = false;
      textoEdicion = texto;
      event.currentTarget.blur();
    }
  }

  function alBlurFecha(event) {
    confirmarFecha(event.currentTarget);
  }

  function acotarRatio(ratio) {
    if (!Number.isFinite(ratio)) return 0;
    return Math.min(1, Math.max(0, ratio));
  }

  function ratioDesdeEvento(event) {
    if (!pista) return 0;
    const rect = pista.getBoundingClientRect();
    if (!rect.width) return 0;
    return (event.clientX - rect.left) / rect.width;
  }

  function soltarEn(ratio) {
    emitirFecha(fechaDesdePosicion(acotarRatio(ratio), fechas));
  }

  function alPointerDown(event) {
    if (event.button !== 0) return;
    event.preventDefault();
    if (reproduciendo) dispatch('reproducir', { activo: false });
    punteroActivo = true;
    arrastrando = true;
    pista.setPointerCapture(event.pointerId);
    posicionArrastre = acotarRatio(ratioDesdeEvento(event));
    pista.focus();
  }

  function alPointerMove(event) {
    if (!punteroActivo) return;
    posicionArrastre = acotarRatio(ratioDesdeEvento(event));
  }

  function alPointerUp(event) {
    if (!punteroActivo) return;
    const ratio = ratioDesdeEvento(event);
    punteroActivo = false;
    arrastrando = false;
    posicionArrastre = null;
    soltarEn(ratio);
  }

  function alTecla(event) {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') {
      event.preventDefault();
      if (anterior) emitirFecha(anterior);
    } else if (event.key === 'ArrowRight' || event.key === 'ArrowUp') {
      event.preventDefault();
      if (siguiente) emitirFecha(siguiente);
    } else if (event.key === 'Home') {
      event.preventDefault();
      if (fechas.length) emitirFecha(fechas[0]);
    } else if (event.key === 'End') {
      event.preventDefault();
      if (fechas.length) emitirFecha(fechas[fechas.length - 1]);
    }
  }

  function publicarIntervalo(event) {
    const valor = Number(event.currentTarget.value);
    if (!Number.isFinite(valor) || valor < 0.2) return;
    dispatch('intervalo', { segundos: valor });
  }

  function cerrarIntervalo(event) {
    const valor = Number(event.currentTarget.value);
    const segundos = Number.isFinite(valor) ? Math.max(0.2, valor) : intervaloSegundos;
    event.currentTarget.value = String(segundos);
    dispatch('intervalo', { segundos });
  }

  function alternarReproduccion() {
    dispatch('reproducir', { activo: !reproduciendo });
  }
</script>

<div class="barra" role="region" aria-label="Pedidos históricos">
  <div class="controles">
    <span class="titulo" title="Pedidos históricos"><Icon name="history" size={16} /></span>
    <button type="button" aria-label="Cerrar pedidos históricos" title="Cerrar" on:click={() => dispatch('cerrar')}>
      <Icon name="close" size={16} />
    </button>
    <span class="paso">
      <span class="fila-fecha">
        <button type="button" aria-label="Fecha anterior" title="Fecha anterior" disabled={!anterior} on:click={() => emitirFecha(anterior)}>&lt;</button>
        <input
          class="fecha"
          class:invalida={fechaInvalida}
          type="text"
          inputmode="numeric"
          autocomplete="off"
          spellcheck="false"
          aria-label="Fecha. Escribí día/mes/año y presioná Enter"
          title="Escribí una fecha y presioná Enter para ir a la más cercana con pedidos"
          bind:value={textoEdicion}
          on:focus={alFocoFecha}
          on:keydown={alTeclaFecha}
          on:blur={alBlurFecha}
          on:input={() => fechaInvalida = false}
        />
        <button type="button" aria-label="Fecha siguiente" title="Fecha siguiente" disabled={!siguiente} on:click={() => emitirFecha(siguiente)}>&gt;</button>
      </span>
      <span class="estadisticas" aria-label="Estadísticas del día">
        <span title="Cantidad total"><span class="dato">cant.</span> {textoCantidad(estadisticas.cantidadTotal)}</span>
        <span title="Cantidad vendida"><span class="dato">tot.</span> {textoCantidad(estadisticas.cantidadVendidas)}</span>
        <span title="Valor total"><span class="dato">val.</span> {textoValor(estadisticas.valorTotal)}</span>
      </span>
    </span>
    <button type="button" class="salto" aria-label="Ir a la última fecha" title="Ir a la última fecha" disabled={!siguiente} on:click={() => emitirFecha(fechas[fechas.length - 1])}>&gt;|</button>
    <button
      type="button"
      aria-label={reproduciendo ? 'Pausar' : 'Reproducir'}
      title={reproduciendo ? 'Pausar' : 'Reproducir'}
      disabled={!siguiente && !reproduciendo}
      on:click={alternarReproduccion}
    >
      <Icon name={reproduciendo ? 'pause' : 'play'} size={16} />
    </button>
    <label class="intervalo">
      <input
        type="number"
        min="0.2"
        max="99"
        step="0.1"
        value={intervaloSegundos}
        aria-label="Intervalo en segundos"
        on:input={publicarIntervalo}
        on:change={cerrarIntervalo}
      />
      <span>s</span>
    </label>
  </div>
  <div
    class="pista"
    bind:this={pista}
    bind:clientWidth={anchoPista}
    role="slider"
    tabindex="0"
    aria-valuemin={fechas.length ? 1 : 0}
    aria-valuemax={fechas.length}
    aria-valuenow={fechas.length ? indice + 1 : 0}
    aria-valuetext={texto}
    aria-label="Línea de tiempo de pedidos"
    on:pointerdown={alPointerDown}
    on:pointermove={alPointerMove}
    on:pointerup={alPointerUp}
    on:pointercancel={alPointerUp}
    on:keydown={alTecla}
  >
    <span class="linea"></span>
    {#each marcas as marca, i (marca.fecha)}
      {#if visibles[i]}
        <span class="marca" style="left: {marca.posicion * 100}%"></span>
        <span class="etiqueta" style="left: {marca.posicion * 100}%">
          <span class="anio">{marca.etiqueta.anio}</span>
          <span class="dia">{marca.etiqueta.dia}</span>
        </span>
      {/if}
    {/each}
    <span class="pulgar" style="left: {posicion * 100}%"></span>
  </div>
</div>

<style>
  .barra {
    position: absolute;
    left: 0.75rem;
    right: 0.75rem;
    bottom: 0.65rem;
    z-index: 1000;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem 0.45rem;
    padding: 0.25rem 0.5rem 0.95rem;
    background: rgb(17 24 39 / 92%);
    color: #f9fafb;
    border-radius: var(--ds-radius-large);
    box-shadow: var(--ds-shadow-panel);
    user-select: none;
  }

  .controles {
    display: flex;
    flex: 0 0 auto;
    flex-wrap: nowrap;
    align-items: center;
    gap: 0.15rem;
  }

  .titulo {
    display: inline-flex;
    align-items: center;
    margin-right: 0.15rem;
  }

  button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 26px;
    height: 26px;
    margin: 0;
    padding: 0;
    border: 0;
    border-radius: var(--ds-radius-small);
    background: transparent;
    color: #f9fafb;
    font: inherit;
    font-size: 0.95rem;
    font-weight: 700;
    line-height: 1;
    cursor: pointer;
  }

  button:hover:not(:disabled) {
    background: rgb(255 255 255 / 12%);
  }

  button:focus-visible {
    outline: 2px solid #93c5fd;
    outline-offset: 1px;
  }

  button:disabled {
    opacity: 0.35;
    cursor: default;
  }

  .salto {
    width: auto;
    padding: 0 0.35rem;
    font-size: 0.82rem;
    letter-spacing: -0.03em;
  }

  .paso {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
  }

  .fila-fecha {
    display: inline-flex;
    align-items: center;
    gap: 0;
  }

  .paso button {
    width: 16px;
  }

  .estadisticas {
    position: absolute;
    top: calc(100% + 1px);
    left: 50%;
    display: flex;
    gap: 0.4rem;
    color: #e5e7eb;
    font-size: 0.625rem;
    font-variant-numeric: tabular-nums;
    line-height: 1.1;
    white-space: nowrap;
    transform: translateX(-50%);
    pointer-events: none;
  }

  .dato {
    margin-right: 0.12rem;
    color: #9ca3af;
    font-size: 0.5625rem;
    font-weight: 600;
  }

  .fecha {
    width: 5.4rem;
    height: 26px;
    margin: 0;
    padding: 0 0.15rem;
    field-sizing: content;
    border: 1px solid transparent;
    border-radius: var(--ds-radius-small);
    background: transparent;
    color: #f9fafb;
    font: inherit;
    font-size: 0.875rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    text-align: center;
  }

  .fecha:hover,
  .fecha:focus {
    border-color: rgb(255 255 255 / 35%);
    background: rgb(255 255 255 / 8%);
  }

  .fecha:focus-visible {
    outline: 2px solid #93c5fd;
    outline-offset: 1px;
  }

  .fecha.invalida {
    border-color: #fca5a5;
  }

  .intervalo {
    display: inline-flex;
    align-items: center;
    height: 26px;
    gap: 0.2rem;
    margin-left: 0.15rem;
    color: #e5e7eb;
    font-size: 0.75rem;
    line-height: 1;
  }

  .intervalo input {
    width: 2rem;
    height: 26px;
    margin: 0;
    padding: 0 0.15rem;
    text-align: center;
    -moz-appearance: textfield;
    border: 1px solid rgb(255 255 255 / 28%);
    border-radius: var(--ds-radius-small);
    background: rgb(255 255 255 / 8%);
    color: #f9fafb;
    font: inherit;
    font-size: 0.8125rem;
    font-variant-numeric: tabular-nums;
  }

  .intervalo input::-webkit-outer-spin-button,
  .intervalo input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
  }

  .intervalo input:focus-visible {
    outline: 2px solid #93c5fd;
    outline-offset: 1px;
  }

  .pista {
    position: relative;
    flex: 1 1 140px;
    height: 32px;
    min-width: 140px;
    touch-action: none;
    cursor: pointer;
  }

  .pista:focus-visible {
    outline: 2px solid #93c5fd;
    outline-offset: 2px;
  }

  .linea {
    position: absolute;
    top: 5px;
    right: 0;
    left: 0;
    height: 4px;
    border-radius: 999px;
    background: #2563eb;
  }

  .marca {
    position: absolute;
    top: 5px;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #fff;
    transform: translateX(-50%);
    pointer-events: none;
  }

  .etiqueta {
    position: absolute;
    top: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    color: #e5e7eb;
    font-size: 0.5625rem;
    line-height: 1;
    white-space: nowrap;
    transform: translateX(-50%);
    pointer-events: none;
  }

  .anio {
    font-weight: 700;
  }

  .pulgar {
    position: absolute;
    top: 1px;
    z-index: 1;
    width: 12px;
    height: 12px;
    border: 2px solid #1d4ed8;
    border-radius: 50%;
    background: #fff;
    box-shadow: 0 1px 3px rgb(0 0 0 / 35%);
    transform: translateX(-50%);
    pointer-events: none;
  }

  @media (max-width: 768px) {
    .barra {
      left: 0.5rem;
      right: 0.5rem;
      bottom: 0.45rem;
    }

    .fecha {
      width: 5.1rem;
      font-size: 0.8125rem;
    }
  }
</style>
