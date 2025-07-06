<script>
  import { onMount } from 'svelte';
  import Map from 'ol/Map.js';
  import View from 'ol/View.js';
  import TileLayer from 'ol/layer/Tile.js';
  import ImageLayer from 'ol/layer/Image.js'; // Descomentado temporalmente
  import ImageWMS from 'ol/source/ImageWMS.js'; // Descomentado temporalmente
  import OSM from 'ol/source/OSM.js';
  // import Overlay from 'ol/Overlay.js'; // Asegurarse que está comentado o eliminado
  import { fromLonLat } from 'ol/proj.js';
  import Feature from 'ol/Feature.js';
  import Point from 'ol/geom/Point.js';
  import VectorLayer from 'ol/layer/Vector.js';
  import VectorSource from 'ol/source/Vector.js';
  import {bbox as bboxStrategy} from 'ol/loadingstrategy.js'; // Estrategia BBOX
  import GeoJSON from 'ol/format/GeoJSON.js'; // Formato WFS
  import {Style, Circle, Fill, Stroke} from 'ol/style.js'; // Estilos para WFS
  import Icon from 'ol/style/Icon.js'; // Sigue siendo para el markerLayer

  // Importar configuración
  import { API_BASE_URL, INITIAL_COORDINATES, GEOSERVER_BASE_URL } from './config.js';

  // Componente de diálogo (lo crearemos después)
  import BuscarDireccionDialog from './BuscarDireccionDialog.svelte';
  import BuscarCliente from './BuscarCliente.svelte'; // Importar el nuevo componente
  import GlobalNotification from './GlobalNotification.svelte'; // Importar GlobalNotification

  let mapElement;
  // let tooltipElement; // Confirmado: Comentado/Eliminado
  // let tooltipOverlay; // Confirmado: Comentado/Eliminado
  let map;
  let markerSource;

  let showBuscarDireccionDialog = false;
  let showBuscarClienteDialog = false;

  // Variables para las capas Vectoriales (WFS)
  let pedidosLayer; // Será VectorLayer
  let clientesLayer; // Será VectorLayer

  // Estado para los checkboxes del Layer Switcher
  let showPedidosLayer = true; // Por defecto: Pedidos ENCENDIDA
  let showClientesLayer = false;  // Por defecto: Clientes APAGADA

  // Estado para el menú móvil
  let mobileMenuOpen = false;

  // Reacciones para actualizar la visibilidad de las capas cuando cambian los checkboxes
  // Esto seguirá funcionando igual para VectorLayer
  $: if (pedidosLayer) pedidosLayer.setVisible(showPedidosLayer);
  $: if (clientesLayer) clientesLayer.setVisible(showClientesLayer);

  // Estado para la notificación global
  let globalNotificationMessage = "";
  let globalNotificationType = "success";

  function handleShowGlobalNotification(event) {
    globalNotificationMessage = event.detail.message;
    globalNotificationType = event.detail.type || "success";
    // El componente GlobalNotification se encargará de resetear el mensaje o de ocultarse
    // Para permitir que se muestre de nuevo si el mensaje es el mismo, podemos borrarlo aquí tras un pequeño delay
    // o asegurar que GlobalNotification reaccione a cambios de message incluso si es el mismo (lo hace con el $: if message)
    // Si se quiere que GlobalNotification se resetee para volver a aparecer con el mismo mensaje:
    setTimeout(() => {
        globalNotificationMessage = ""; // Esto lo ocultará después de que GlobalNotification lo haya mostrado y temporizado
    }, 3500); // Un poco más que la duración del toast para asegurar que no parpadee
  }

  function refreshPedidosLayerMap() {
    if (pedidosLayer) {
      const source = pedidosLayer.getSource();
      if (source && typeof source.updateParams === 'function') {
        source.updateParams({'TIMESTAMP': new Date().getTime()});
        console.log("Capa Pedidos refrescada");
      }
    }
  }

  function toggleMobileMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }

  function closeMobileMenu() {
    mobileMenuOpen = false;
  }

  onMount(() => {
    markerSource = new VectorSource();
    const markerLayer = new VectorLayer({
      source: markerSource,
      style: new Style({
        image: new Icon({
          anchor: [0.5, 46],
          anchorXUnits: 'fraction',
          anchorYUnits: 'pixels',
          src: 'https://openlayers.org/en/latest/examples/data/icon.png'
        })
      })
    });

    // Crear el Overlay para el tooltip -- ELIMINADO
    // tooltipOverlay = new Overlay({
    //   element: tooltipElement,
    //   autoPan: {
    //     animation: {
    //       duration: 250,
    //     },
    //   },
    // });

    // Definición de la capa de Pedidos (WMS)
    // Se asigna a la variable global para que el watcher pueda accederla
    pedidosLayer = new ImageLayer({
      source: new ImageWMS({
        url: GEOSERVER_BASE_URL, // Usar la variable importada
        params: {
          'LAYERS': 'GeneralBelgrano:Pedidos',
          'VERSION': '1.1.0',
          // 'STYLES': 'geomPoint', // Revertido: Se usará el estilo por defecto del servidor
        },
        serverType: 'geoserver',
      }),
      visible: showPedidosLayer // Usar la variable de estado
    });

    // Definición de la capa de Clientes (WMS)
    // Se asigna a la variable global para que el watcher pueda accederla
    clientesLayer = new ImageLayer({
      source: new ImageWMS({
        url: GEOSERVER_BASE_URL, // Usar la variable importada
        params: {
          'LAYERS': 'GeneralBelgrano:Clientes',
          'VERSION': '1.1.0',
          // 'STYLES': 'geomPoint' // Revertido: Se usará el estilo por defecto del servidor
        },
        serverType: 'geoserver',
      }),
      visible: showClientesLayer // Usar la variable de estado
    });

    map = new Map({
      target: mapElement,
      layers: [
        new TileLayer({
          source: new OSM() // Capa base de OpenStreetMap
        }),
        clientesLayer,
        pedidosLayer, // Los pedidos ahora van encima de los clientes
        markerLayer // Capa para los marcadores (debe estar encima de las WMS)
      ],
      view: new View({
        center: fromLonLat([INITIAL_COORDINATES.lon, INITIAL_COORDINATES.lat]),
        zoom: 15 // Nivel de zoom inicial
      }),
      // overlays: [tooltipOverlay] // ELIMINADO
    });

    // Limpiar el mapa al desmontar el componente
    // Listener para el movimiento del puntero en el mapa (para el tooltip) -- ELIMINADO
    // map.on('pointermove', (evt) => { ... });

    return () => {
      if (map) {
        map.setTarget(undefined);
        map = undefined;
      }
    };
  });

  // function openBuscarDireccion() { // Reemplazado por setView
  //   showBuscarDireccionDialog = true;
  // }

  // function setView(viewName) {
  //   currentView = viewName;
  //   // Si volvemos al mapa y el mapa no estaba visible, podría necesitar un updateSize si su div contenedor cambió.
  //   // Por ahora, asumimos que el div del mapa siempre existe y solo se oculta/muestra su contenido o el componente completo.
  //   if (viewName === 'map' && map) {
  //     // Pequeño delay para asegurar que el DOM está actualizado si se re-renderiza el mapa
  //     setTimeout(() => {
  //       map.updateSize();
  //     }, 0);
  //   }
  // }

  function openBuscarDireccion() {
    showBuscarDireccionDialog = true;
    showBuscarClienteDialog = false; // Asegurar que el otro diálogo esté cerrado
    closeMobileMenu(); // Cerrar menú móvil si está abierto
  }

  function openBuscarCliente() {
    showBuscarClienteDialog = true;
    showBuscarDireccionDialog = false; // Asegurar que el otro diálogo esté cerrado
    closeMobileMenu(); // Cerrar menú móvil si está abierto
  }

  function closeDialogs() {
    showBuscarDireccionDialog = false;
    showBuscarClienteDialog = false;
    if (map) {
      // Pequeño delay para asegurar que el DOM está actualizado si se re-renderiza el mapa
      setTimeout(() => {
        map.updateSize();
      }, 0);
    }
  }

  function handlePedidosAction() {
    alert('Funcionalidad "Pedidos" no implementada.');
    closeMobileMenu();
  }

  async function handleBuscarDireccion(event) {
    const direccion = event.detail.direccion;
    // showBuscarDireccionDialog = false; // Ya no se cierra aquí, se cierra con el botón X o Cancelar del diálogo
    closeDialogs(); // Cerrar el diálogo después de la búsqueda
    console.log("Buscando dirección:", direccion);

    try {
      const response = await fetch(`${API_BASE_URL}/buscar_direccion`, { // Endpoint sin /api al inicio
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ direccion: direccion }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `Error del servidor: ${response.status}`);
      }

      const data = await response.json();
      console.log("Respuesta del backend:", data);

      if (data.latitud && data.longitud) {
        addMarker(data.longitud, data.latitud);
        // Centrar el mapa en el nuevo marcador
        map.getView().animate({
            center: fromLonLat([data.longitud, data.latitud]),
            zoom: 17, // Zoom más cercano al marcador
            duration: 1000 // Duración de la animación en ms
        });
      } else {
        alert("No se recibieron coordenadas válidas del backend.");
      }

    } catch (error) {
      console.error('Error al buscar dirección:', error);
      alert(`Error al buscar dirección: ${error.message}`);
    }
  }

  function addMarker(lon, lat) {
    if (!markerSource) return;

    // Limpiar marcadores anteriores
    markerSource.clear();

    const marker = new Feature({
      geometry: new Point(fromLonLat([lon, lat]))
    });
    markerSource.addFeature(marker);
  }

</script>

<main>
  <nav class="navbar">
    <div class="navbar-brand">
      <h1>RAWEB</h1>
    </div>

    <!-- Menú desktop -->
    <div class="nav-buttons d-mobile-none">
      <button on:click={openBuscarDireccion} class:active={showBuscarDireccionDialog}>
        📍 Buscar Dirección
      </button>
      <button on:click={openBuscarCliente} class:active={showBuscarClienteDialog}>
        👤 Buscar Cliente
      </button>
      <button on:click={handlePedidosAction}>
        📦 Pedidos
      </button>
    </div>

    <!-- Layer switcher desktop -->
    <div class="layer-switcher d-mobile-none">
      <label>
        <input type="checkbox" bind:checked={showClientesLayer} /> Clientes
      </label>
      <label>
        <input type="checkbox" bind:checked={showPedidosLayer} /> Pedidos
      </label>
    </div>

    <!-- Botón hamburguesa para móviles -->
    <button class="mobile-menu-toggle d-mobile-block" on:click={toggleMobileMenu} aria-label="Menú">
      <span class="hamburger-line" class:active={mobileMenuOpen}></span>
      <span class="hamburger-line" class:active={mobileMenuOpen}></span>
      <span class="hamburger-line" class:active={mobileMenuOpen}></span>
    </button>
  </nav>

  <!-- Menú móvil desplegable -->
  {#if mobileMenuOpen}
    <div class="mobile-menu d-mobile-block" class:open={mobileMenuOpen}>
      <div class="mobile-menu-content">
        <div class="mobile-nav-buttons">
          <button on:click={openBuscarDireccion} class:active={showBuscarDireccionDialog}>
            📍 Buscar Dirección
          </button>
          <button on:click={openBuscarCliente} class:active={showBuscarClienteDialog}>
            👤 Buscar Cliente
          </button>
          <button on:click={handlePedidosAction}>
            📦 Pedidos
          </button>
        </div>
        
        <div class="mobile-layer-switcher">
          <h3>Capas del Mapa</h3>
          <label>
            <input type="checkbox" bind:checked={showClientesLayer} /> Clientes
          </label>
          <label>
            <input type="checkbox" bind:checked={showPedidosLayer} /> Pedidos
          </label>
        </div>
      </div>
    </div>
  {/if}

  <!-- Overlay para cerrar menú móvil -->
  {#if mobileMenuOpen}
    <div class="mobile-menu-overlay" on:click={closeMobileMenu}></div>
  {/if}

  <div class="map-container" bind:this={mapElement}>
    <!-- El mapa siempre está presente en el DOM -->
  </div>

  {#if showBuscarDireccionDialog}
    <BuscarDireccionDialog
      on:close={closeDialogs}
      on:buscar={handleBuscarDireccion}
    />
  {/if}

  {#if showBuscarClienteDialog}
    <BuscarCliente
      on:close={closeDialogs}
      on:showGlobalNotification={handleShowGlobalNotification}
      on:refreshPedidosLayer={refreshPedidosLayerMap}
    />
  {/if}

  <GlobalNotification message={globalNotificationMessage} type={globalNotificationType} />

  <!-- Elemento para el Tooltip -->
  <!-- <div bind:this={tooltipElement} class="ol-tooltip"></div> -->
</main>

<style>
  /* Estilos responsive base */
  :global(body, html) {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    font-family: Arial, sans-serif;
  }

  main {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
  }

  /* Navbar responsive */
  .navbar {
    background-color: #f8f9fa;
    padding: 0.75rem 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    z-index: 1000;
    position: relative;
    min-height: 60px;
  }

  .navbar-brand h1 {
    margin: 0;
    font-size: 1.5rem;
    color: #007bff;
    font-weight: 600;
  }

  /* Botones de navegación desktop */
  .nav-buttons {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .nav-buttons button {
    margin: 0;
    padding: 0.5rem 1rem;
    cursor: pointer;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    background-color: #fff;
    color: #495057;
    font-size: 0.875rem;
    font-weight: 500;
    transition: all 0.2s ease;
    white-space: nowrap;
  }

  .nav-buttons button:hover {
    background-color: #e9ecef;
    border-color: #adb5bd;
    transform: translateY(-1px);
  }

  .nav-buttons button.active {
    background-color: #007bff;
    border-color: #007bff;
    color: #fff;
  }

  /* Layer switcher desktop */
  .layer-switcher {
    display: flex;
    align-items: center;
    gap: 1rem;
    font-size: 0.875rem;
  }

  .layer-switcher label {
    display: flex;
    align-items: center;
    cursor: pointer;
    margin: 0;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
  }

  .layer-switcher label:hover {
    background-color: rgba(0,123,255,0.1);
  }

  .layer-switcher input[type="checkbox"] {
    margin-right: 0.5rem;
    margin-bottom: 0;
    width: auto;
  }

  /* Botón hamburguesa móvil */
  .mobile-menu-toggle {
    display: none;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 44px;
    height: 44px;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 8px;
  }

  .hamburger-line {
    width: 24px;
    height: 3px;
    background-color: #495057;
    margin: 2px 0;
    transition: all 0.3s ease;
    border-radius: 1.5px;
  }

  .hamburger-line.active:nth-child(1) {
    transform: rotate(45deg) translate(5px, 5px);
  }

  .hamburger-line.active:nth-child(2) {
    opacity: 0;
  }

  .hamburger-line.active:nth-child(3) {
    transform: rotate(-45deg) translate(7px, -6px);
  }

  /* Menú móvil */
  .mobile-menu {
    position: fixed;
    top: 60px;
    left: 0;
    right: 0;
    background-color: #fff;
    border-bottom: 1px solid #dee2e6;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    z-index: 999;
    transform: translateY(-100%);
    transition: transform 0.3s ease;
  }

  .mobile-menu.open {
    transform: translateY(0);
  }

  .mobile-menu-content {
    padding: 1rem;
  }

  .mobile-menu-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0,0,0,0.5);
    z-index: 998;
  }

  /* Botones navegación móvil */
  .mobile-nav-buttons {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
  }

  .mobile-nav-buttons button {
    width: 100%;
    padding: 1rem;
    font-size: 1rem;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    background-color: #fff;
    color: #495057;
    font-weight: 500;
    transition: all 0.2s ease;
    text-align: left;
  }

  .mobile-nav-buttons button:hover,
  .mobile-nav-buttons button:focus {
    background-color: #f8f9fa;
    border-color: #007bff;
  }

  .mobile-nav-buttons button.active {
    background-color: #007bff;
    border-color: #007bff;
    color: #fff;
  }

  /* Layer switcher móvil */
  .mobile-layer-switcher {
    border-top: 1px solid #dee2e6;
    padding-top: 1rem;
  }

  .mobile-layer-switcher h3 {
    margin: 0 0 1rem 0;
    font-size: 1rem;
    color: #495057;
    font-weight: 600;
  }

  .mobile-layer-switcher label {
    display: flex;
    align-items: center;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.2s ease;
  }

  .mobile-layer-switcher label:hover {
    background-color: #f8f9fa;
  }

  .mobile-layer-switcher input[type="checkbox"] {
    margin-right: 0.75rem;
    margin-bottom: 0;
    width: auto;
    transform: scale(1.2);
  }

  /* Contenedor del mapa */
  .map-container {
    flex-grow: 1;
    width: 100%;
    position: relative;
    min-height: 0; /* Importante para flex */
  }

  /* Estilos para OpenLayers */
  :global(.ol-viewport) {
    width: 100%;
    height: 100%;
  }

  :global(.ol-zoom) {
    top: 0.5rem;
    left: 0.5rem;
  }

  :global(.ol-attribution) {
    bottom: 0.25rem;
    right: 0.25rem;
    font-size: 0.75rem;
  }

  /* Media queries responsivas */
  @media (max-width: 768px) {
    .navbar {
      padding: 0.5rem 1rem;
      min-height: 56px;
    }

    .navbar-brand h1 {
      font-size: 1.25rem;
    }

    .mobile-menu-toggle {
      display: flex;
    }

    .mobile-menu {
      top: 56px;
    }

    /* Ajustes para pantallas muy pequeñas */
    @media (max-width: 480px) {
      .navbar {
        padding: 0.5rem;
      }

      .navbar-brand h1 {
        font-size: 1.1rem;
      }

      .mobile-menu-content {
        padding: 0.75rem;
      }

      .mobile-nav-buttons button {
        padding: 0.875rem;
      }
    }
  }

  /* Landscape móvil */
  @media (max-width: 768px) and (orientation: landscape) {
    .mobile-menu {
      max-height: calc(100vh - 56px);
      overflow-y: auto;
    }
  }

  /* Tablet */
  @media (min-width: 769px) and (max-width: 1024px) {
    .nav-buttons button {
      padding: 0.5rem 0.75rem;
      font-size: 0.8rem;
    }

    .layer-switcher {
      gap: 0.75rem;
      font-size: 0.8rem;
    }
  }

  /* Estilos para el tooltip, basados en ejemplos de OpenLayers */
  .ol-tooltip {
    position: absolute;
    background-color: white;
    color: black;
    border: 1px solid #cccccc;
    padding: 8px;
    border-radius: 4px;
    font-size: 0.9em;
    pointer-events: none;
    display: none;
    white-space: nowrap;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    z-index: 1010;
  }
</style>