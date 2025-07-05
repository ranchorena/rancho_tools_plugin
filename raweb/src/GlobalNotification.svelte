<script>
  import { onMount, onDestroy } from 'svelte';

  export let message = "";
  export let type = "success"; // 'success' o 'error' u otros que se definan
  export let duration = 3000; // Duración en ms

  let visible = false;
  let timer;

  function show() {
    visible = true;
    if (timer) clearTimeout(timer); // Limpiar timer anterior si existe
    timer = setTimeout(() => {
      hide();
    }, duration);
  }

  function hide() {
    visible = false;
  }

  // Mostrar cuando el mensaje cambia y no está vacío
  $: if (message && message.trim() !== "") {
    show();
  } else {
    // Si el mensaje se borra externamente, ocultar inmediatamente
    // Esto es útil si App.svelte borra el mensaje para ocultarlo programáticamente antes del timeout
    if (visible) hide();
  }

  onMount(() => {
    // Si el componente se monta con un mensaje, mostrarlo.
    // Esto es en caso de que el prop 'message' se establezca al mismo tiempo que se monta el componente.
    if (message && message.trim() !== "") {
      show();
    }
  });

  onDestroy(() => {
    if (timer) clearTimeout(timer);
  });
</script>

{#if visible}
  <div class="global-notification-backdrop">
    <div class="global-notification-content" class:success={type === 'success'} class:error={type === 'error'}>
      <p>{message}</p>
      <!-- Podríamos añadir un botón de cierre manual si se desea -->
      <!-- <button on:click={hide}>&times;</button> -->
    </div>
  </div>
{/if}

<style>
  .global-notification-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.1); /* Un fondo sutil para indicar modalidad, opcional */
    display: flex;
    justify-content: center;
    align-items: center; /* Centrar verticalmente */
    z-index: 2000; /* Muy alto para estar sobre otros elementos */
    pointer-events: none; /* Para no interferir con clicks si solo es el mensaje */
  }

  .global-notification-content {
    background-color: #333;
    color: white;
    padding: 15px 30px;
    border-radius: 8px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    text-align: center;
    min-width: 250px;
    max-width: 80%;
    pointer-events: auto; /* Permitir clicks si hay botones dentro, o para otros usos */
  }

  .global-notification-content.success {
    background-color: #4CAF50; /* Verde para éxito */
  }

  .global-notification-content.error {
    background-color: #f44336; /* Rojo para error */
  }

  .global-notification-content p {
    margin: 0;
    font-size: 1.1em;
  }
</style>
