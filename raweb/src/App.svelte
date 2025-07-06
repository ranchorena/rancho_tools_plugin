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
  }

  function openBuscarCliente() {
    showBuscarClienteDialog = true;
    showBuscarDireccionDialog = false; // Asegurar que el otro diálogo esté cerrado
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
    <div class="nav-buttons">
      <button on:click={openBuscarDireccion} class:active={showBuscarDireccionDialog}>Buscar Dirección</button>
      <button on:click={openBuscarCliente} class:active={showBuscarClienteDialog}>Buscar Cliente</button>
      <button on:click={() => alert('Funcionalidad "Pedidos" no implementada.')}>Pedidos</button>
    </div>
    <div class="layer-switcher">
      <label>
        <input type="checkbox" bind:checked={showClientesLayer} /> Clientes
      </label>
      <label>
        <input type="checkbox" bind:checked={showPedidosLayer} /> Pedidos
      </label>
    </div>
  </nav>

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
  /* Estilos existentes... */
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
    height: 100vh; /* Ocupa toda la altura de la ventana */
  }

  .navbar {
    background-color: #f0f0f0;
    padding: 10px;
    display: flex; /* Cambiado para flex layout */
    justify-content: space-between; /* Espacio entre botones y layer switcher */
    align-items: center; /* Alineación vertical */
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    z-index: 1000; /* Asegura que esté sobre el mapa */
  }

  .nav-buttons button { /* Estilos específicos para los botones de navegación */
    margin-right: 10px; /* Margen solo a la derecha para espaciar botones */
    /* Quitar margen izquierdo si ya no es necesario por flex */
  }
   .nav-buttons button:last-child {
    margin-right: 0; /* El último botón no necesita margen a la derecha */
  }


  /* Estilos generales de botón dentro de navbar, si se quieren compartir */
  .navbar button {
    /* margin: 0 10px; No, usar el de .nav-buttons o .layer-switcher */
    padding: 8px 15px;
    cursor: pointer;
    border: 1px solid #ccc;
    border-radius: 4px;
    background-color: #fff;
  }

  .navbar button:hover {
    background-color: #e9e9e9;
  }
  .navbar button.active {
    background-color: #d1d5db; /* Un color para indicar activo */
    font-weight: bold;
  }

  .layer-switcher {
    display: flex;
    align-items: center;
    gap: 15px; /* Espacio entre los checkboxes */
    padding-right: 10px; /* Un poco de espacio al final de la navbar */
  }

  .layer-switcher label {
    display: flex;
    align-items: center;
    cursor: pointer;
    font-size: 0.9em;
  }

  .layer-switcher input[type="checkbox"] {
    margin-right: 5px;
  }

  .map-container {
    flex-grow: 1; /* El mapa ocupa el espacio restante */
    width: 100%;
    position: relative; /* Necesario para que el mapa se muestre correctamente */
  }

  /* Estilos para OpenLayers (importante para que se vea el mapa) */
  :global(.ol-viewport) {
    width: 100%;
    height: 100%;
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
    pointer-events: none; /* El tooltip no debe capturar eventos del mouse */
    display: none; /* Oculto por defecto */
    white-space: nowrap; /* Evitar que el contenido se divida en múltiples líneas si es corto */
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    z-index: 1010; /* Encima del mapa pero debajo de los diálogos */
  }
</style>