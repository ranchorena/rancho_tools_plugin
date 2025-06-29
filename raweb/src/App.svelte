<script>
  import { onMount } from 'svelte';
  import Map from 'ol/Map.js';
  import View from 'ol/View.js';
  import TileLayer from 'ol/layer/Tile.js';
  import OSM from 'ol/source/OSM.js';
  import { fromLonLat } from 'ol/proj.js';
  import Feature from 'ol/Feature.js';
  import Point from 'ol/geom/Point.js';
  import VectorLayer from 'ol/layer/Vector.js';
  import VectorSource from 'ol/source/Vector.js';
  import Style from 'ol/style/Style.js';
  import Icon from 'ol/style/Icon.js';

  // Componente de diálogo (lo crearemos después)
  import BuscarDireccionDialog from './BuscarDireccionDialog.svelte';

  let mapElement;
  let map;
  let showBuscarDireccionDialog = false;
  let markerSource;

  const initialCoordinates = {
    lon: -58.49442773720401,
    lat: -35.76850886708026
  };

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

    map = new Map({
      target: mapElement,
      layers: [
        new TileLayer({
          source: new OSM() // Capa base de OpenStreetMap
        }),
        markerLayer // Capa para los marcadores
      ],
      view: new View({
        center: fromLonLat([initialCoordinates.lon, initialCoordinates.lat]),
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

  function openBuscarDireccion() {
    showBuscarDireccionDialog = true;
  }

  function handleCloseDialog() {
    showBuscarDireccionDialog = false;
  }

  async function handleBuscarDireccion(event) {
    const direccion = event.detail.direccion;
    showBuscarDireccionDialog = false; // Cerrar diálogo
    console.log("Buscando dirección:", direccion);

    try {
      const response = await fetch('http://localhost:5000/buscar_direccion', { // Asegúrate que el puerto coincida con tu backend
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
    <button on:click={openBuscarDireccion}>Buscar Dirección</button>
    <button on:click={() => alert('Funcionalidad "Buscar Cliente" no implementada.')}>Buscar Cliente</button>
    <button on:click={() => alert('Funcionalidad "Pedidos" no implementada.')}>Pedidos</button>
  </nav>

  <div class="map-container" bind:this={mapElement}>
    <!-- El mapa se renderizará aquí -->
  </div>

  {#if showBuscarDireccionDialog}
    <BuscarDireccionDialog
      on:close={handleCloseDialog}
      on:buscar={handleBuscarDireccion}
    />
  {/if}
</main>

<style>
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