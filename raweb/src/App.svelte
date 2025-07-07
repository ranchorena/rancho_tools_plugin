<script>
  import { onMount } from 'svelte';
  import Map from 'ol/Map.js';
  import View from 'ol/View.js';
  import TileLayer from 'ol/layer/Tile.js';
  import OSM from 'ol/source/OSM.js';
  import XYZ from 'ol/source/XYZ.js'; // Para Google Satellite
  import { fromLonLat } from 'ol/proj.js';
  import Feature from 'ol/Feature.js';
  import Point from 'ol/geom/Point.js';
  import VectorLayer from 'ol/layer/Vector.js';
  import VectorSource from 'ol/source/Vector.js';
  import {bbox as bboxStrategy} from 'ol/loadingstrategy.js'; // Estrategia BBOX para WFS
  import GeoJSON from 'ol/format/GeoJSON.js'; // Formato WFS
  import {Style, Circle, Fill, Stroke} from 'ol/style.js'; // Estilos para WFS y marcadores
  import Icon from 'ol/style/Icon.js'; // Para el markerLayer
  import {defaults as defaultControls} from 'ol/control.js'; // Para controles personalizados

  // Importar configuración
  import { API_BASE_URL, INITIAL_COORDINATES, GEOSERVER_BASE_URL } from './config.js';

  // Componente de diálogo (lo crearemos después)
  import BuscarDireccionDialog from './BuscarDireccionDialog.svelte';
  import BuscarCliente from './BuscarCliente.svelte'; // Importar el nuevo componente
  import Pedidos from './Pedidos.svelte'; // Importar el componente Pedidos
  import GlobalNotification from './GlobalNotification.svelte'; // Importar GlobalNotification

  let mapElement;
  let map;
  let markerSource;

  let showBuscarDireccionDialog = false;
  let showBuscarClienteDialog = false;
  let showPedidosDialog = false;

  // Variables para las capas base
  let osmLayer;
  let satelliteLayer;

  // Variables para las capas
  let pedidosLayer; // VectorLayer con WFS
  let clientesLayer; // VectorLayer con WFS

  // Estado para los checkboxes del Layer Switcher
  let baseLayerType = 'osm'; // 'osm' o 'satellite'
  let showPedidosLayer = true; // Por defecto: Pedidos ENCENDIDA
  let showClientesLayer = false;  // Por defecto: Clientes APAGADA

  // Variables computadas para las capas base
  $: showOSMLayer = baseLayerType === 'osm';
  $: showSatelliteLayer = baseLayerType === 'satellite';

  // Estado para el toolbar de capas
  let showLayerToolbar = false;

  // Estado para el menú móvil
  let mobileMenuOpen = false;

  // Reacciones para actualizar la visibilidad de las capas cuando cambian los checkboxes
  $: if (osmLayer) osmLayer.setVisible(showOSMLayer);
  $: if (satelliteLayer) satelliteLayer.setVisible(showSatelliteLayer);
  $: if (pedidosLayer) pedidosLayer.setVisible(showPedidosLayer);
  $: if (clientesLayer) clientesLayer.setVisible(showClientesLayer);

  // Estado para la notificación global
  let globalNotificationMessage = "";
  let globalNotificationType = "success";

  // Variables para el tooltip de click (para WFS de pedidos y clientes)
  let showFeatureTooltip = false;
  let selectedFeatureData = null;
  let tooltipPosition = { x: 0, y: 0 }; // Posición en píxeles
  let tooltipType = null; // 'pedido' o 'cliente'

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
      if (source && typeof source.clear === 'function') {
        source.clear();
        console.log("Capa Pedidos WFS recargada");
      }
    }
  }

  function refreshClientesLayerMap() {
    if (clientesLayer) {
      const source = clientesLayer.getSource();
      if (source && typeof source.clear === 'function') {
        source.clear();
        console.log("Capa Clientes WFS recargada");
      }
    }
  }

  function toggleMobileMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }

  function closeMobileMenu() {
    mobileMenuOpen = false;
  }

  function toggleLayerToolbar() {
    showLayerToolbar = !showLayerToolbar;
  }

  onMount(() => {
    // Event listener global para cerrar tooltip al hacer click fuera
    function handleGlobalClick(event) {
      if (showFeatureTooltip) {
        // Verificar si el click fue fuera del tooltip
        const tooltipElement = document.querySelector('.feature-tooltip');
        if (tooltipElement && !tooltipElement.contains(event.target)) {
          closeFeatureTooltip();
        }
      }
    }
    
    document.addEventListener('click', handleGlobalClick);
    
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

    // Tooltip se maneja con CSS puro, sin overlay de OpenLayers

    // Definición de las capas base
    osmLayer = new TileLayer({
      source: new OSM(),
      visible: showOSMLayer
    });

    satelliteLayer = new TileLayer({
      source: new XYZ({
        url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        maxZoom: 20
      }),
      visible: showSatelliteLayer
    });

    // Definición de la capa de Pedidos (WFS) - Restaurado a WFS como debe ser
    pedidosLayer = new VectorLayer({
      source: new VectorSource({
        url: function(extent) {
          return GEOSERVER_BASE_URL + '/ows?service=WFS&version=1.1.0&request=GetFeature&typename=GeneralBelgrano:Pedidos&outputFormat=application/json&srsname=EPSG:3857&bbox=' + extent.join(',') + ',EPSG:3857';
        },
        format: new GeoJSON(),
        strategy: bboxStrategy
      }),
      style: new Style({
        image: new Circle({
          radius: 6,
          fill: new Fill({
            color: '#ff6b6b'
          }),
          stroke: new Stroke({
            color: '#ffffff',
            width: 2
          })
        })
      }),
      visible: showPedidosLayer
    });

    // Definición de la capa de Clientes (WFS)
    clientesLayer = new VectorLayer({
      source: new VectorSource({
        url: function(extent) {
          return GEOSERVER_BASE_URL + '/ows?service=WFS&version=1.1.0&request=GetFeature&typename=GeneralBelgrano:Clientes&outputFormat=application/json&srsname=EPSG:3857&bbox=' + extent.join(',') + ',EPSG:3857';
        },
        format: new GeoJSON(),
        strategy: bboxStrategy
      }),
      style: new Style({
        image: new Circle({
          radius: 8,
          fill: new Fill({
            color: '#4285f4'
          }),
          stroke: new Stroke({
            color: '#ffffff',
            width: 2
          })
        })
      }),
      visible: showClientesLayer
    });

    map = new Map({
      target: mapElement,
      controls: defaultControls({
        rotate: false, // Desactivar el control de rotación
        attribution: true,
        zoom: true
      }),
      layers: [
        osmLayer, // Capa base OSM
        satelliteLayer, // Capa base Satelital
        clientesLayer,
        pedidosLayer, // Los pedidos ahora van encima de los clientes
        markerLayer // Capa para los marcadores (debe estar encima de las WMS)
      ],
      view: new View({
        center: fromLonLat([INITIAL_COORDINATES.lon, INITIAL_COORDINATES.lat]),
        zoom: 15 // Nivel de zoom inicial
      })
    });

    // Evento de click para mostrar información de pedidos y clientes (WFS)
    map.on('singleclick', function(evt) {
      let foundFeature = null;
      let foundLayer = null;
      
      // Buscar features de pedidos o clientes en el pixel clickeado
      map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
        if (layer === pedidosLayer || layer === clientesLayer) {
          foundFeature = feature;
          foundLayer = layer;
          return true; // Parar la búsqueda al encontrar la primera feature
        }
      });

      if (foundFeature) {
        const properties = foundFeature.getProperties();
        
        // Determinar el tipo de feature
        const isPedido = foundLayer === pedidosLayer;
        
        selectedFeatureData = {
          id: properties.id_pedido || properties.id || 'N/A',
          nombre: properties.nombre || 'N/A',
          direccion: properties.direccion || 'N/A',
          cantidad: properties.cantidad || 'N/A',
          fecha: properties.fecha || 'N/A',
          telefono: properties.telefono || 'N/A',
          horario: properties.horario || 'N/A',
          observaciones: properties.observaciones || 'N/A',
          calle: properties.calle || 'N/A',
          altura: properties.altura || 'N/A'
        };
        
        tooltipType = isPedido ? 'pedido' : 'cliente';
        showFeatureTooltip = true;
        
        // Posicionar el tooltip usando coordenadas CSS (no overlay)
        const pixel = evt.pixel;
        const mapRect = mapElement.getBoundingClientRect();
        
        // Calcular posición con ajustes para evitar que se salga de la pantalla
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const tooltipWidth = 300; // max-width del tooltip
        const tooltipHeight = 200; // altura estimada del tooltip
        
        let x = pixel[0] + 15; // 15px a la derecha del click
        let y = pixel[1] - 15; // 15px arriba del click
        
        // Ajustar si se sale por la derecha
        if (x + tooltipWidth > viewportWidth) {
          x = pixel[0] - tooltipWidth - 15; // Mover a la izquierda del click
        }
        
        // Ajustar si se sale por arriba
        if (y < 0) {
          y = pixel[1] + 15; // Mover abajo del click
        }
        
        // Ajustar si se sale por abajo
        if (y + tooltipHeight > viewportHeight) {
          y = viewportHeight - tooltipHeight - 10; // Mover arriba
        }
        
        // En móviles, posicionar más centrado
        if (viewportWidth <= 768) {
          x = Math.max(10, Math.min(x, viewportWidth - tooltipWidth - 10));
          y = Math.max(10, Math.min(y, viewportHeight - tooltipHeight - 10));
        }
        
        tooltipPosition = { x, y };
      } else {
        // Click fuera de cualquier feature - cerrar tooltip
        closeFeatureTooltip();
      }
    });

    // Limpiar el mapa al desmontar el componente
    return () => {
      if (map) {
        map.setTarget(undefined);
        map = undefined;
      }
      // Limpiar event listener global
      document.removeEventListener('click', handleGlobalClick);
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
    showBuscarClienteDialog = false; // Asegurar que los otros diálogos estén cerrados
    showPedidosDialog = false;
    closeMobileMenu(); // Cerrar menú móvil si está abierto
  }

  function openBuscarCliente() {
    showBuscarClienteDialog = true;
    showBuscarDireccionDialog = false; // Asegurar que los otros diálogos estén cerrados
    showPedidosDialog = false;
    closeMobileMenu(); // Cerrar menú móvil si está abierto
  }

  function openPedidos() {
    showPedidosDialog = true;
    showBuscarDireccionDialog = false; // Asegurar que los otros diálogos estén cerrados
    showBuscarClienteDialog = false;
    closeMobileMenu(); // Cerrar menú móvil si está abierto
  }

  function closeDialogs() {
    showBuscarDireccionDialog = false;
    showBuscarClienteDialog = false;
    showPedidosDialog = false;
    if (map) {
      // Pequeño delay para asegurar que el DOM está actualizado si se re-renderiza el mapa
      setTimeout(() => {
        map.updateSize();
      }, 0);
    }
  }

  function handlePedidosAction() {
    openPedidos();
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

  function handleZoomToLocation(event) {
    const { longitude, latitude } = event.detail;
    if (map && longitude && latitude) {
      // Animar el zoom al cliente seleccionado
      map.getView().animate({
        center: fromLonLat([longitude, latitude]),
        zoom: 18, // Zoom cercano para ver el cliente
        duration: 1000 // Duración de la animación en ms
      });
      
      // Opcionalmente agregar un marcador temporal
      addMarker(longitude, latitude);
    }
  }

  function handleZoomToClient(event) {
    const { clientId } = event.detail;
    if (map && clientesLayer && clientId) {
      // Buscar el cliente en la capa WFS de clientes
      const source = clientesLayer.getSource();
      const features = source.getFeatures();
      
      // Buscar el feature con el ID del cliente
      const clientFeature = features.find(feature => {
        const props = feature.getProperties();
        return props.id == clientId || props.id_cliente == clientId;
      });
      
      if (clientFeature) {
        // Obtener las coordenadas del feature
        const geometry = clientFeature.getGeometry();
        if (geometry && geometry.getType() === 'Point') {
          const coordinates = geometry.getCoordinates();
          
          // Animar el zoom al cliente encontrado
          map.getView().animate({
            center: coordinates,
            zoom: 18, // Zoom cercano para ver el cliente
            duration: 1000 // Duración de la animación en ms
          });
          
          console.log(`Cliente ${clientId} encontrado y zoom realizado`);
        } else {
          console.warn(`Cliente ${clientId} encontrado pero sin geometría Point válida`);
        }
      } else {
        console.warn(`Cliente ${clientId} no encontrado en la capa de clientes. Asegúrate de que la capa esté cargada.`);
        // Mostrar mensaje al usuario
        handleShowGlobalNotification({
          detail: {
            message: 'Cliente actualizado, pero no se pudo encontrar su ubicación en el mapa. Asegúrate de que la capa de clientes esté activa.',
            type: 'warning'
          }
        });
      }
    }
  }

  function closeFeatureTooltip() {
    showFeatureTooltip = false;
    selectedFeatureData = null;
    tooltipPosition = { x: 0, y: 0 };
    tooltipType = null;
  }

  // Funciones relacionadas con el tooltip de pedidos se manejan con closePedidoTooltip()

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
      <button on:click={handlePedidosAction} class:active={showPedidosDialog}>
        📦 Pedidos
      </button>
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
          <button on:click={handlePedidosAction} class:active={showPedidosDialog}>
            📦 Pedidos
          </button>
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
    
    <!-- Toolbar de capas flotante -->
    {#if showLayerToolbar}
      <div class="layer-toolbar">
                 <div class="layer-toolbar-header">
           <span class="layer-toolbar-title">▣ Capas</span>
           <button class="layer-toolbar-toggle" on:click={toggleLayerToolbar} title="Cerrar panel de capas">
             ✕
           </button>
         </div>
        
        <div class="layer-toolbar-content">
          <div class="layer-group">
            <div class="layer-group-title">Capas de Datos</div>
            <label class="layer-item">
              <input type="checkbox" bind:checked={showClientesLayer} />
              <span class="layer-name">● Clientes</span>
            </label>
            <label class="layer-item">
              <input type="checkbox" bind:checked={showPedidosLayer} />
              <span class="layer-name">▪ Pedidos</span>
            </label>
          </div>
          
          <div class="layer-group">
            <div class="layer-group-title">Capas Base</div>
            <label class="layer-item">
              <input type="radio" bind:group={baseLayerType} value="osm" />
              <span class="layer-name">○ OpenStreetMap</span>
            </label>
            <label class="layer-item">
              <input type="radio" bind:group={baseLayerType} value="satellite" />
              <span class="layer-name">◉ Satelital</span>
            </label>
          </div>
        </div>
      </div>
    {:else}
             <button class="layer-toolbar-show-btn" on:click={toggleLayerToolbar} title="Mostrar panel de capas">
         ▣
       </button>
    {/if}
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
      on:zoomToClient={handleZoomToClient}
    />
  {/if}

  {#if showPedidosDialog}
    <Pedidos
      on:close={closeDialogs}
      on:zoomToLocation={handleZoomToLocation}
    />
  {/if}

  <!-- Tooltip de información de pedidos y clientes -->
  {#if showFeatureTooltip && selectedFeatureData}
    <div class="feature-tooltip" 
         style="left: {tooltipPosition.x}px; top: {tooltipPosition.y}px;" 
         on:click|stopPropagation>
      <div class="feature-tooltip-content">
        <div class="feature-tooltip-data">{selectedFeatureData.id}</div>
        <div class="feature-tooltip-data">{selectedFeatureData.nombre}</div>
        <div class="feature-tooltip-data">{selectedFeatureData.direccion}</div>
        {#if tooltipType === 'cliente'}
          {#if selectedFeatureData.calle !== 'N/A'}
            <div class="feature-tooltip-data">{selectedFeatureData.calle}</div>
          {/if}
          {#if selectedFeatureData.altura !== 'N/A'}
            <div class="feature-tooltip-data">{selectedFeatureData.altura}</div>
          {/if}
        {/if}
        {#if tooltipType === 'pedido'}
          {#if selectedFeatureData.cantidad !== 'N/A'}
            <div class="feature-tooltip-data">{selectedFeatureData.cantidad}</div>
          {/if}
          {#if selectedFeatureData.fecha !== 'N/A'}
            <div class="feature-tooltip-data">{selectedFeatureData.fecha}</div>
          {/if}
        {/if}
        {#if selectedFeatureData.telefono !== 'N/A'}
          <div class="feature-tooltip-data">{selectedFeatureData.telefono}</div>
        {/if}
        {#if selectedFeatureData.horario !== 'N/A'}
          <div class="feature-tooltip-data">{selectedFeatureData.horario}</div>
        {/if}
        {#if selectedFeatureData.observaciones !== 'N/A'}
          <div class="feature-tooltip-data">{selectedFeatureData.observaciones}</div>
        {/if}
      </div>
    </div>
  {/if}

  <GlobalNotification message={globalNotificationMessage} type={globalNotificationType} />
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
    /* Mejoras para móvil */
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
    touch-action: pan-x pan-y;
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

  /* Toolbar de capas flotante */
  .layer-toolbar {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 250px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(0, 0, 0, 0.1);
    z-index: 1000;
    font-size: 0.875rem;
    max-height: calc(100vh - 200px);
    overflow-y: auto;
  }

  .layer-toolbar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    background: rgba(248, 249, 250, 0.8);
    border-radius: 8px 8px 0 0;
    min-height: 32px;
  }

  .layer-toolbar-title {
    font-weight: 600;
    color: #495057;
    font-size: 0.85rem;
    line-height: 1.2;
  }

  .layer-toolbar-toggle {
    background: none;
    border: none;
    font-size: 0.875rem;
    color: #6c757d;
    cursor: pointer;
    padding: 0.125rem;
    border-radius: 4px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
  }

  .layer-toolbar-toggle:hover {
    background: rgba(0, 0, 0, 0.1);
    color: #495057;
  }

  .layer-toolbar-content {
    padding: 1rem;
  }

  .layer-group {
    margin-bottom: 1rem;
  }

  .layer-group:last-child {
    margin-bottom: 0;
  }

  .layer-group-title {
    font-weight: 600;
    color: #495057;
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .layer-item {
    display: flex;
    align-items: center;
    cursor: pointer;
    margin: 0 0 0.5rem 0;
    padding: 0.5rem;
    border-radius: 6px;
    transition: all 0.2s ease;
    border: 1px solid transparent;
  }

  .layer-item:hover {
    background: rgba(0, 123, 255, 0.05);
    border-color: rgba(0, 123, 255, 0.2);
  }

  .layer-item:last-child {
    margin-bottom: 0;
  }

  .layer-item input[type="checkbox"],
  .layer-item input[type="radio"] {
    margin-right: 0.75rem;
    margin-bottom: 0;
    width: auto;
    transform: scale(1.1);
  }

  .layer-name {
    color: #495057;
    font-weight: 500;
  }

  .layer-toolbar-show-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 44px;
    height: 44px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    font-size: 1.2rem;
    color: #495057;
    transition: all 0.2s ease;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .layer-toolbar-show-btn:hover {
    background: rgba(255, 255, 255, 1);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
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
    display: none; /* Oculto por defecto */
  }

  .mobile-menu.open {
    transform: translateY(0);
    display: block;
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



  /* Contenedor del mapa */
  .map-container {
    flex-grow: 1;
    width: 100%;
    position: relative;
    min-height: 0; /* Importante para flex */
    /* Optimizaciones para móvil */
    -webkit-overflow-scrolling: touch;
    touch-action: pan-x pan-y;
    overflow: hidden;
  }

  /* Estilos para OpenLayers */
  :global(.ol-viewport) {
    width: 100%;
    height: 100%;
  }

  /* Controles de OpenLayers - mantener pequeños y no responsivos */
  :global(.ol-zoom),
  :global(.ol-attribution) {
    position: absolute;
  }

  :global(.ol-zoom) {
    top: 0.5rem;
    left: 0.5rem;
    display: flex;
    flex-direction: column;
    background: rgba(255, 255, 255, 0.8);
    border-radius: 4px;
    overflow: hidden;
  }

  :global(.ol-zoom button) {
    width: 30px !important;
    height: 30px !important;
    min-height: 30px !important;
    padding: 0 !important;
    margin: 0 !important;
    font-size: 18px !important;
    line-height: 1 !important;
    border: none !important;
    background: rgba(255, 255, 255, 0.8) !important;
    color: #333 !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 0 !important;
  }

  :global(.ol-zoom button:hover) {
    background: rgba(255, 255, 255, 0.9) !important;
    transform: none !important;
  }

  :global(.ol-zoom button:focus) {
    outline: 2px solid #3b82f6 !important;
    outline-offset: -2px !important;
    box-shadow: none !important;
  }

  :global(.ol-attribution) {
    bottom: 0.25rem;
    right: 0.25rem;
    font-size: 0.75rem;
    background: rgba(255, 255, 255, 0.8);
    padding: 2px 4px;
    border-radius: 3px;
  }

  :global(.ol-attribution ul) {
    margin: 0;
    padding: 0;
    list-style: none;
    font-size: 0.7rem;
  }

  :global(.ol-attribution button) {
    width: auto !important;
    height: auto !important;
    min-height: auto !important;
    padding: 1px 3px !important;
    margin: 0 !important;
    font-size: 0.7rem !important;
    background: transparent !important;
    border: none !important;
  }



  /* Ajustes para móviles - mantener controles pequeños */
  @media (max-width: 768px) {
    :global(.ol-zoom) {
      top: 0.25rem;
      left: 0.25rem;
    }

    :global(.ol-zoom button) {
      width: 28px !important;
      height: 28px !important;
      min-height: 28px !important;
      font-size: 16px !important;
    }

    :global(.ol-attribution) {
      bottom: 0.125rem;
      right: 0.125rem;
      font-size: 0.65rem;
    }
  }

  /* Clases de utilidad responsivas */
  .d-mobile-none {
    display: flex;
  }

  .d-mobile-block {
    display: none;
  }

  /* Media queries responsivas */
  @media (max-width: 768px) {
    .d-mobile-none {
      display: none;
    }

    .d-mobile-block {
      display: flex;
    }

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
      display: none; /* Asegurar que esté oculto por defecto en móvil */
    }

    .mobile-menu.open {
      display: block; /* Mostrar cuando esté abierto */
    }

    /* Toolbar responsivo en móviles */
    .layer-toolbar {
      width: 280px;
      max-width: calc(100vw - 4rem);
      top: 0.5rem;
      right: 0.5rem;
      left: auto; /* Eliminar left para que solo use right */
    }

    .layer-toolbar-show-btn {
      top: 0.5rem;
      right: 0.5rem;
      width: 40px;
      height: 40px;
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

      /* Toolbar aún más compacto en pantallas muy pequeñas */
      .layer-toolbar {
        width: 260px;
        max-width: calc(100vw - 6rem);
      }

      .layer-toolbar-content {
        padding: 0.75rem;
      }

      .layer-item {
        padding: 0.375rem;
        margin-bottom: 0.375rem;
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

    .layer-toolbar {
      width: 280px;
      right: 1rem;
    }
  }

  /* Estilos para el tooltip original (mantenido por compatibilidad) */
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

  /* Estilos para el tooltip de información de pedidos y clientes */
  .feature-tooltip {
    position: fixed;
    background-color: rgba(255, 255, 255, 0.95);
    color: #333;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 0.85em;
    pointer-events: auto; /* Permitir que el tooltip pueda ser clickeado */
    display: block; /* Mostrar siempre */
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    min-width: 180px;
    max-width: 250px;
    backdrop-filter: blur(5px);
    z-index: 10000; /* Asegurar que esté encima de todo */
  }

  .feature-tooltip-content {
    padding: 0.75rem;
    font-size: 0.9em;
  }

  .feature-tooltip-data {
    margin-bottom: 0.4rem;
    font-size: 0.9rem;
    color: #495057;
    line-height: 1.3;
    word-break: break-word;
    font-weight: 500;
  }

  .feature-tooltip-data:last-child {
    margin-bottom: 0;
  }

  /* Estilos responsive para el tooltip */
  @media (max-width: 768px) {
    .feature-tooltip {
      min-width: 200px;
      max-width: calc(100vw - 20px);
      font-size: 0.9em;
    }

    .feature-tooltip-content {
      padding: 1rem;
    }

    .feature-tooltip-data {
      margin-bottom: 0.5rem;
      font-size: 1rem;
      line-height: 1.4;
    }
  }

  @media (max-width: 480px) {
    .feature-tooltip {
      min-width: 180px;
      max-width: calc(100vw - 16px);
      font-size: 0.85em;
    }

    .feature-tooltip-content {
      padding: 0.75rem;
    }

    .feature-tooltip-data {
      margin-bottom: 0.4rem;
      font-size: 0.9rem;
      line-height: 1.3;
    }
  }

  /* Landscape móvil - tooltip más compacto */
  @media (max-width: 768px) and (orientation: landscape) {
    .feature-tooltip {
      max-height: calc(100vh - 40px);
      overflow-y: auto;
    }

    .feature-tooltip-content {
      max-height: calc(100vh - 80px);
      overflow-y: auto;
    }
  }
</style>