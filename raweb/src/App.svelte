<script>
  import { onMount } from 'svelte';
  import Map from 'ol/Map.js';
  import View from 'ol/View.js';
  import TileLayer from 'ol/layer/Tile.js';
  import ImageLayer from 'ol/layer/Image.js'; // Importar ImageLayer
  import ImageWMS from 'ol/source/ImageWMS.js'; // Importar ImageWMS
  import OSM from 'ol/source/OSM.js';
  import { fromLonLat } from 'ol/proj.js';
  import Feature from 'ol/Feature.js';
  import Point from 'ol/geom/Point.js';
  import VectorLayer from 'ol/layer/Vector.js';
  import VectorSource from 'ol/source/Vector.js';
  import Style from 'ol/style/Style.js';
  import Icon from 'ol/style/Icon.js';

  // Importar configuración
  import { API_BASE_URL, INITIAL_COORDINATES } from './config.js';

  // Componente de diálogo (lo crearemos después)
  import BuscarDireccionDialog from './BuscarDireccionDialog.svelte';
  import BuscarCliente from './BuscarCliente.svelte'; // Importar el nuevo componente

  let mapElement;
  let map;
  // let showBuscarDireccionDialog = false; // Reemplazado por currentView
  let markerSource;

  // Estado para controlar la vista actual
  // let currentView = 'map'; // 'map', 'buscarDireccion', 'buscarCliente'
  // Se reemplaza currentView por dos flags booleanos para superponer los dialogs
  let showBuscarDireccionDialog = false;
  let showBuscarClienteDialog = false;

  onMount(() => {
    markerSource = new VectorSource();
    const markerLayer = new VectorLayer({
      source: markerSource,
      style: new Style({
        image: new Icon({
          anchor: [0.5, 46], // ancla en la parte inferior central del icono
          anchorXUnits: 'fraction',
          anchorYUnits: 'pixels',
          src: 'https://openlayers.org/en/latest/examples/data/icon.png' // Icono de marcador por defecto de OL
        })
      })
    });

    // Definición de la capa de Pedidos (WMS)
    const pedidosLayer = new ImageLayer({
      source: new ImageWMS({
        url: 'http://localhost:8087/geoserver/GeneralBelgrano/wms',
        params: {'LAYERS': 'GeneralBelgrano:Pedidos', 'VERSION': '1.1.0'},
        serverType: 'geoserver', // Tipo de servidor GeoServer
      }),
      visible: false // Por defecto apagada
    });

    // Definición de la capa de Clientes (WMS)
    const clientesLayer = new ImageLayer({
      source: new ImageWMS({
        url: 'http://localhost:8087/geoserver/GeneralBelgrano/wms',
        params: {'LAYERS': 'GeneralBelgrano:Clientes', 'VERSION': '1.1.0'},
        serverType: 'geoserver',
      }),
      visible: true // Por defecto encendida
    });

    map = new Map({
      target: mapElement,
      layers: [
        new TileLayer({
          source: new OSM() // Capa base de OpenStreetMap
        }),
        pedidosLayer, // Añadir capa de Pedidos
        clientesLayer, // Añadir capa de Clientes
        markerLayer // Capa para los marcadores (debe estar encima de las WMS si se quiere ver el marcador sobre ellas)
      ],
      view: new View({
        center: fromLonLat([INITIAL_COORDINATES.lon, INITIAL_COORDINATES.lat]),
        zoom: 15 // Nivel de zoom inicial
      })
    });

    // Limpiar el mapa al desmontar el componente
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
      const response = await fetch(`${API_BASE_URL}/buscar_direccion`, { // URL desde config.js
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
    <button on:click={openBuscarDireccion} class:active={showBuscarDireccionDialog}>Buscar Dirección</button>
    <button on:click={openBuscarCliente} class:active={showBuscarClienteDialog}>Buscar Cliente</button>
    <button on:click={() => alert('Funcionalidad "Pedidos" no implementada.')}>Pedidos</button>
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
    <BuscarCliente on:close={closeDialogs}/>
    <!-- Asegúrate de que BuscarCliente emita un evento 'close' -->
  {/if}
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
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    z-index: 1000; /* Asegura que esté sobre el mapa */
  }

  .navbar button {
    margin: 0 10px;
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
</style>