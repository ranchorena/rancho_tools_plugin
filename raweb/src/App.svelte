<script>
  import { onMount, tick } from 'svelte';
  import Map from 'ol/Map.js';
  import View from 'ol/View.js';
  import TileLayer from 'ol/layer/Tile.js';
  import OSM from 'ol/source/OSM.js';
  import XYZ from 'ol/source/XYZ.js'; // Para Google Satellite
  import { fromLonLat, toLonLat } from 'ol/proj.js';
  import Feature from 'ol/Feature.js';
  import Point from 'ol/geom/Point.js';
  import CircleGeom from 'ol/geom/Circle.js';
  import VectorLayer from 'ol/layer/Vector.js';
  import VectorSource from 'ol/source/Vector.js';
  import {bbox as bboxStrategy} from 'ol/loadingstrategy.js'; // Estrategia BBOX para WFS
  import GeoJSON from 'ol/format/GeoJSON.js'; // Formato WFS
  import {Style, Circle, Fill, Stroke, Text} from 'ol/style.js'; // Estilos para WFS y marcadores
  import Icon from 'ol/style/Icon.js'; // Para el markerLayer
  import {defaults as defaultControls} from 'ol/control.js'; // Para controles personalizados

  // Importar configuración
  import { API_BASE_URL, INITIAL_COORDINATES, GEOSERVER_BASE_URL } from './config.js';

  // Componente de diálogo (lo crearemos después)
  import BuscarDireccionDialog from './BuscarDireccionDialog.svelte';
  import BuscarCliente from './BuscarCliente.svelte'; // Importar el nuevo componente
  import Pedidos from './Pedidos.svelte'; // Importar el componente Pedidos
  import PedidosHistorico from './PedidosHistorico.svelte';
  import AgregarCliente from './AgregarCliente.svelte'; // Importar componente para agregar clientes
  import GlobalNotification from './GlobalNotification.svelte'; // Importar GlobalNotification
  import AccountMenu from './AccountMenu.svelte';
  import UiIcon from './design-system/Icon.svelte';
  import { createThemeController } from './design-system/theme-controller.mjs';
  import { chooseFocusReturn } from './design-system/focus-policy.mjs';
  import { authorizedFetch, cambiarContrasena, initAuth, login, logout } from './auth/session.mjs';

  let authReady = false;
  let authenticated = false;
  let username = '';
  let authMessage = '';

  let themePreference = 'system';
  let themeController;

  onMount(() => {
    themeController = createThemeController({
      storage: {
        getItem: (key) => window.localStorage.getItem(key),
        setItem: (key, value) => window.localStorage.setItem(key, value)
      },
      mediaQuery: window.matchMedia('(prefers-color-scheme: dark)'),
      applyTheme: (theme) => { document.documentElement.dataset.theme = theme; },
      onPreferenceChange: (preference) => { themePreference = preference; }
    });
    themeController.start();
    return () => themeController.destroy();
  });

  function handleThemeChange(event) {
    themeController.setPreference(event.detail);
  }

  let mapElement;
  let map;
  let markerSource;
  let ubicacionSource;
  let ubicacionWatchId = null;
  let ubicacionActiva = false;
  let ubicacionRecibida = false;
  let ubicacionActual = null;
  let centrarUbicacion = false;
  let pedidoCercanoId = null;
  let temporaryLayers = [];

  let showBuscarDireccionDialog = false;
  let showBuscarClienteDialog = false;
  let showPedidosDialog = false;
  let showPedidosHistoricoDialog = false;
  let showAgregarClienteDialog = false;
  let agregarClienteInicial = null;

  // Variables para agregar cliente
  let modoSeleccionPunto = false;
  let coordenadasSeleccionadas = null;

  // Variables para las capas base
  let osmLayer;
  let satelliteLayer;

  // Variables para las capas
  let pedidosLayer; // VectorLayer con WFS
  let clientesLayer; // VectorLayer con WFS
  let barriosLayer; // VectorLayer con WFS
  let subbarriosLayer; // VectorLayer con WFS
  let plazasLayer; // VectorLayer con WFS
  let tramosLayer; // VectorLayer con WFS, solo la línea
  let tramosSentidoLayer; // VectorLayer con WFS, solo la flecha
  let tramosNombreLayer; // VectorLayer con WFS, solo el nombre

  // Estado para los checkboxes del Layer Switcher
  let showOSMLayer = true; // Por defecto: OpenStreetMap ENCENDIDA
  let showSatelliteLayer = false; // Por defecto: Satelital APAGADA
  let showPedidosLayer = true; // Por defecto: Pedidos ENCENDIDA
  let showPedidosNombre = false; // Por defecto: nombre de pedidos APAGADO
  let showClientesLayer = false;  // Por defecto: Clientes APAGADA
  let showTramosLayer = false; // Por defecto: Tramos APAGADA
  let showTramosSentidoLayer = false; // Por defecto: Tramos sentido APAGADA
  let showTramosNombreLayer = false; // Por defecto: Tramos nombre APAGADA
  let showBarriosLayer = false; // Por defecto: Barrios APAGADA
  let showSubbarriosLayer = false; // Por defecto: Subbarrios APAGADA
  let showPlazasLayer = false; // Por defecto: Plazas APAGADA

  // Estado para el toolbar de capas
  let showLayerToolbar = false;
  let tramosGroupOpen = false;

  // El retorno de foco móvil sigue pudiendo usar el botón de menú si existiera.
  let menuButton;
  let dialogOrigin = null;

  function captureDialogTrigger(event) {
    const trigger = event.currentTarget;
    dialogOrigin = {
      trigger,
      openedFromMobileMenu: Boolean(trigger.closest('.bottom-nav'))
    };
  }

  function isFocusTargetVisible(node) {
    if (!node?.isConnected || !node.getClientRects().length) return false;
    const style = getComputedStyle(node);
    return style.visibility !== 'hidden' && style.visibility !== 'collapse';
  }

  // Reacciones para actualizar la visibilidad de las capas cuando cambian los checkboxes
  $: if (osmLayer) osmLayer.setVisible(showOSMLayer);
  $: if (satelliteLayer) satelliteLayer.setVisible(showSatelliteLayer);
  $: if (pedidosLayer) pedidosLayer.setVisible(showPedidosLayer);
  $: if (pedidosLayer) {
    showPedidosNombre;
    pedidosLayer.setStyle(pedidoStyle);
  }
  $: if (clientesLayer) clientesLayer.setVisible(showClientesLayer);
  $: if (barriosLayer) barriosLayer.setVisible(showBarriosLayer);
  $: if (subbarriosLayer) subbarriosLayer.setVisible(showSubbarriosLayer);
  $: if (plazasLayer) plazasLayer.setVisible(showPlazasLayer);
  $: if (tramosLayer) tramosLayer.setVisible(showTramosLayer);
  $: if (tramosSentidoLayer) tramosSentidoLayer.setVisible(showTramosSentidoLayer);
  $: if (tramosNombreLayer) tramosNombreLayer.setVisible(showTramosNombreLayer);

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

  let pedidosSourceVersion = 0;

  function refreshPedidosLayerMap() {
    if (pedidosLayer) {
      const source = pedidosLayer.getSource();
      if (source && typeof source.refresh === 'function') {
        pedidosSourceVersion += 1;
        source.refresh();
      }
    }
  }

  function refreshClientesLayerMap() {
    if (clientesLayer) {
      const source = clientesLayer.getSource();
      if (source && typeof source.clear === 'function') {
        source.clear();
        // Forzar recarga de la fuente WFS después del clear
        source.refresh();
        console.log("Capa Clientes WFS recargada y refrescada");
      }
    }
  }

  function closeMobileMenu() {
    // La barra inferior permanece visible; no hay un panel móvil que cerrar.
  }

  const TRAMO_LABEL_MAX_SCALE = 10000;
  const TRAMO_ARROW_MAX_SCALE = 25000;
  const MAP_RESOLUTION_TO_SCALE = 1000 / 0.28;

  function tramoStroke(tipoCalle, suelo) {
    const tipo = Number(tipoCalle);
    const sueloN = Number(suelo);
    if (tipo === 1 && sueloN === 1) return { color: '#e29f47', width: 1.5 };
    if (tipo === 1 && sueloN === 2) return { color: '#f0c47f', width: 1.5 };
    if (tipo === 2 && sueloN === 1) return { color: '#3d31a5', width: 2 };
    if (tipo === 2 && sueloN === 2) return { color: '#5c53c4', width: 2 };
    if (tipo === 3 && sueloN === 1) return { color: '#b53c1b', width: 2 };
    return { color: '#b3b3b3', width: 1 };
  }

  function tramoArrowStyles(feature) {
    const sentido = feature.get('sentido');
    if (sentido === null || sentido === undefined) return [];
    const sentidoN = Number(sentido);
    if (sentidoN !== 0 && sentidoN !== 1 && sentidoN !== 2) return [];

    const desde = feature.get('desde');
    if (desde === null || desde === undefined || Number(desde) % 300 !== 0) return [];

    const geometry = feature.getGeometry();
    if (!geometry) return [];
    const parts = geometry.getType() === 'MultiLineString'
      ? geometry.getLineStrings()
      : geometry.getType() === 'LineString'
        ? [geometry]
        : [];

    return parts.flatMap((line) => {
      if (line.getCoordinates().length < 2) return [];
      const mid = line.getCoordinateAt(0.5);
      const start = line.getCoordinateAt(0.4);
      const end = line.getCoordinateAt(0.6);
      const angle = Math.atan2(end[1] - start[1], end[0] - start[0]);

      const flecha = sentidoN === 2 ? '↔' : '→';
      const giro = sentidoN === 1 ? Math.PI : 0;
      return [new Style({
        geometry: new Point(mid),
        text: new Text({
          text: flecha,
          font: '16px sans-serif',
          fill: new Fill({ color: '#555555' }),
          stroke: new Stroke({ color: '#ffffff', width: 2 }),
          rotation: -angle + giro,
          rotateWithView: true
        })
      })];
    });
  }

  function tramoStyle(feature) {
    const stroke = tramoStroke(feature.get('tipo_calle'), feature.get('suelo'));
    return new Style({
      stroke: new Stroke({
        color: stroke.color,
        width: stroke.width,
        lineJoin: 'bevel',
        lineCap: 'square'
      })
    });
  }

  function tramoSentidoStyle(feature, resolution) {
    if (resolution * MAP_RESOLUTION_TO_SCALE > TRAMO_ARROW_MAX_SCALE) return null;
    const arrows = tramoArrowStyles(feature);
    return arrows.length ? arrows : null;
  }

  function tramoNombreStyle(feature, resolution) {
    if (resolution * MAP_RESOLUTION_TO_SCALE > TRAMO_LABEL_MAX_SCALE) return null;
    const name = feature.get('name');
    if (!name) return null;
    return new Style({
      text: new Text({
        text: String(name),
        font: '8px Arial',
        fill: new Fill({ color: '#000000' }),
        placement: 'line',
        overflow: false,
        maxAngle: Math.PI / 2,
        offsetY: -6
      })
    });
  }

  function esPedidoCercano(feature) {
    if (pedidoCercanoId == null) return false;
    const id = feature.get('id');
    if (id != null && String(id) === String(pedidoCercanoId)) return true;
    const fid = feature.getId();
    return fid != null && String(fid).endsWith('.' + pedidoCercanoId);
  }

  function pedidoStyle(feature) {
    const marcado = esPedidoCercano(feature);
    return new Style({
      image: new Circle({
        radius: marcado ? 10 : 6,
        fill: new Fill({
          color: marcado ? '#f59e0b' : '#ff6b6b'
        }),
        stroke: new Stroke({
          color: '#ffffff',
          width: marcado ? 3 : 2
        })
      }),
      text: showPedidosNombre && feature.get('nombre')
        ? new Text({
            text: String(feature.get('nombre')),
            font: '13px sans-serif',
            fill: new Fill({ color: '#111111' }),
            offsetY: -4,
            textAlign: 'center',
            textBaseline: 'bottom'
          })
        : undefined
    });
  }

  function areaNombreStyle(fillColor, strokeColor) {
    return function(feature) {
      return new Style({
        fill: new Fill({ color: fillColor }),
        stroke: new Stroke({ color: strokeColor, width: 1 }),
        text: new Text({
          text: feature.get('nombre') || '',
          font: '600 13px sans-serif',
          fill: new Fill({ color: '#1a1a1a' }),
          stroke: new Stroke({ color: '#ffffff', width: 3 }),
          overflow: true
        })
      });
    };
  }

  async function toggleLayerToolbar() {
    const opening = !showLayerToolbar;
    showLayerToolbar = opening;
    await tick();
    const nextControl = document.querySelector(opening ? '.layer-toolbar input' : '.layer-toolbar-show-btn');
    nextControl?.focus();
  }

  function iniciarMapa() {
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

    ubicacionSource = new VectorSource();
    const ubicacionLayer = new VectorLayer({
      source: ubicacionSource,
      style: estiloUbicacion
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
          return GEOSERVER_BASE_URL + '/ows?service=WFS&version=1.1.0&request=GetFeature&typename=GeneralBelgrano:Pedidos&outputFormat=application/json&srsname=EPSG:3857&bbox=' + extent.join(',') + ',EPSG:3857&_=' + pedidosSourceVersion;
        },
        format: new GeoJSON(),
        strategy: bboxStrategy
      }),
      style: pedidoStyle,
      visible: showPedidosLayer
    });

    // Definición de la capa de Barrios (WFS). En el mapa queda debajo de Clientes.
    barriosLayer = new VectorLayer({
      source: new VectorSource({
        url: function(extent) {
          return GEOSERVER_BASE_URL + '/ows?service=WFS&version=1.1.0&request=GetFeature&typename=GeneralBelgrano:Barrios&outputFormat=application/json&srsname=EPSG:3857&bbox=' + extent.join(',') + ',EPSG:3857';
        },
        format: new GeoJSON(),
        strategy: bboxStrategy
      }),
      declutter: true,
      style: function(feature) {
        return new Style({
          fill: new Fill({
            color: 'rgba(19, 139, 129, 0.35)'
          }),
          stroke: new Stroke({
            color: '#000000',
            width: 1
          }),
          text: new Text({
            text: feature.get('nombre') || '',
            font: '600 13px sans-serif',
            fill: new Fill({
              color: '#1a1a1a'
            }),
            stroke: new Stroke({
              color: '#ffffff',
              width: 3
            }),
            overflow: true
          })
        });
      },
      visible: showBarriosLayer
    });

    subbarriosLayer = new VectorLayer({
      source: new VectorSource({
        url: function(extent) {
          return GEOSERVER_BASE_URL + '/ows?service=WFS&version=1.1.0&request=GetFeature&typename=GeneralBelgrano:subbarrios&outputFormat=application/json&srsname=EPSG:3857&bbox=' + extent.join(',') + ',EPSG:3857';
        },
        format: new GeoJSON(),
        strategy: bboxStrategy
      }),
      declutter: true,
      style: areaNombreStyle('rgba(92, 107, 192, 0.28)', '#3949ab'),
      visible: showSubbarriosLayer
    });

    plazasLayer = new VectorLayer({
      source: new VectorSource({
        url: function(extent) {
          return GEOSERVER_BASE_URL + '/ows?service=WFS&version=1.1.0&request=GetFeature&typename=GeneralBelgrano:plazas&outputFormat=application/json&srsname=EPSG:3857&bbox=' + extent.join(',') + ',EPSG:3857';
        },
        format: new GeoJSON(),
        strategy: bboxStrategy
      }),
      declutter: true,
      style: areaNombreStyle('rgba(46, 125, 50, 0.4)', '#1b5e20'),
      visible: showPlazasLayer
    });

    // Una sola lectura WFS para las tres capas de tramos.
    const tramosSource = new VectorSource({
      url: function(extent) {
        return GEOSERVER_BASE_URL + '/ows?service=WFS&version=1.1.0&request=GetFeature&typename=GeneralBelgrano:tramos&outputFormat=application/json&srsname=EPSG:3857&bbox=' + extent.join(',') + ',EPSG:3857';
      },
      format: new GeoJSON(),
      strategy: bboxStrategy
    });

    // En el mapa quedan encima de Barrios y debajo de Clientes y Pedidos.
    tramosLayer = new VectorLayer({
      source: tramosSource,
      style: tramoStyle,
      visible: showTramosLayer
    });
    tramosSentidoLayer = new VectorLayer({
      source: tramosSource,
      style: tramoSentidoStyle,
      visible: showTramosSentidoLayer
    });
    tramosNombreLayer = new VectorLayer({
      source: tramosSource,
      style: tramoNombreStyle,
      visible: showTramosNombreLayer
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
          radius: 6,
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
        barriosLayer,
        subbarriosLayer,
        plazasLayer,
        tramosLayer,
        tramosSentidoLayer,
        tramosNombreLayer,
        clientesLayer,
        pedidosLayer, // Los pedidos ahora van encima de los clientes
        markerLayer, // Capa para los marcadores (debe estar encima de las WMS)
        ubicacionLayer
      ],
      view: new View({
        center: fromLonLat([INITIAL_COORDINATES.lon, INITIAL_COORDINATES.lat]),
        zoom: 15 // Nivel de zoom inicial
      })
    });

    // Evento de click para mostrar información de pedidos y clientes (WFS)
    map.on('singleclick', function(evt) {
      // Si estamos en modo selección de punto para agregar cliente
      if (modoSeleccionPunto) {
        const coordinate = evt.coordinate;
        // Convertir las coordenadas del mapa (EPSG:3857) a WGS84 (EPSG:4326)
        const [lon, lat] = toLonLat(coordinate);
        
        // Establecer las coordenadas seleccionadas
        coordenadasSeleccionadas = {
          lat: lat,
          lon: lon
        };
        
        // Agregar un marcador temporal en la ubicación seleccionada
        addMarker(lon, lat);
        
        // Restaurar cursor normal
        map.getViewport().style.cursor = '';
        modoSeleccionPunto = false;
        
        return; // Salir temprano para no procesar clicks de features
      }
      
      let foundFeature = null;
      let foundLayer = null;
      
      // Buscar features de pedidos, la capa temporal o clientes en el pixel clickeado
      map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
        const esCapaTemporal = temporaryLayers.includes(layer);
        if (esCapaTemporal || layer === pedidosLayer || layer === clientesLayer) {
          foundFeature = feature;
          foundLayer = layer;
          return true; // Parar la búsqueda al encontrar la primera feature
        }
      });

      if (foundFeature) {
        const properties = foundFeature.getProperties();
        
        // Determinar el tipo de feature
        const isPedido = foundLayer === pedidosLayer || temporaryLayers.includes(foundLayer);
        
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

    const handleResize = () => {
      map?.updateSize();
    };
    window.addEventListener('resize', handleResize);

    // Limpiar el mapa al desmontar el componente
    return () => {
      detenerUbicacion();
      window.removeEventListener('resize', handleResize);
      if (map) {
        map.setTarget(undefined);
        map = undefined;
      }
      document.removeEventListener('click', handleGlobalClick);
    };
  }

  onMount(() => {
    let limpiarMapa = () => {};
    let cancelado = false;
    initAuth()
      .then(async (sesion) => {
        if (cancelado) return;
        authenticated = sesion.authenticated;
        username = sesion.username;
        authReady = true;
        if (!authenticated) return;
        await tick();
        limpiarMapa = iniciarMapa() || (() => {});
      })
      .catch((error) => {
        console.error(error);
        authMessage = 'No se pudo iniciar la sesión con Keycloak.';
        authReady = true;
      });
    return () => {
      cancelado = true;
      limpiarMapa();
    };
  });

  function ingresarConKeycloak() {
    login();
  }

  function cerrarSesion() {
    logout();
  }

  function solicitarCambioContrasena() {
    cambiarContrasena();
  }

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

  function openBuscarDireccion(event) {
    captureDialogTrigger(event);
    showBuscarDireccionDialog = true;
    showBuscarClienteDialog = false; // Asegurar que los otros diálogos estén cerrados
    showPedidosDialog = false;
    showPedidosHistoricoDialog = false;
    showAgregarClienteDialog = false;
    closeMobileMenu(); // Cerrar menú móvil si está abierto
  }

  function openBuscarCliente(event) {
    captureDialogTrigger(event);
    showBuscarClienteDialog = true;
    showBuscarDireccionDialog = false; // Asegurar que los otros diálogos estén cerrados
    showPedidosDialog = false;
    showPedidosHistoricoDialog = false;
    showAgregarClienteDialog = false;
    closeMobileMenu(); // Cerrar menú móvil si está abierto
  }

  function openPedidos(event) {
    captureDialogTrigger(event);
    showPedidosDialog = true;
    showBuscarDireccionDialog = false; // Asegurar que los otros diálogos estén cerrados
    showBuscarClienteDialog = false;
    showPedidosHistoricoDialog = false;
    showAgregarClienteDialog = false;
    closeMobileMenu(); // Cerrar menú móvil si está abierto
  }

  function openPedidosHistorico(event) {
    captureDialogTrigger(event);
    showPedidosHistoricoDialog = true;
    showPedidosDialog = false;
    showBuscarDireccionDialog = false;
    showBuscarClienteDialog = false;
    showAgregarClienteDialog = false;
    closeMobileMenu();
  }

  function openAgregarCliente(event) {
    captureDialogTrigger(event);
    agregarClienteInicial = null;
    showAgregarClienteDialog = true;
    showBuscarDireccionDialog = false; // Asegurar que los otros diálogos estén cerrados
    showBuscarClienteDialog = false;
    showPedidosDialog = false;
    showPedidosHistoricoDialog = false;
    closeMobileMenu(); // Cerrar menú móvil si está abierto
  }

  function openAgregarClienteFromSearch(event) {
    agregarClienteInicial = event.detail;
    showAgregarClienteDialog = true;
    showBuscarClienteDialog = false;
    showBuscarDireccionDialog = false;
    showPedidosDialog = false;
    showPedidosHistoricoDialog = false;
  }

  async function closeDialogs() {
    const origin = dialogOrigin;
    dialogOrigin = null;
    showBuscarDireccionDialog = false;
    showBuscarClienteDialog = false;
    showPedidosDialog = false;
    showPedidosHistoricoDialog = false;
    showAgregarClienteDialog = false;
    modoSeleccionPunto = false;
    coordenadasSeleccionadas = null;
    if (map) {
      // Pequeño delay para asegurar que el DOM está actualizado si se re-renderiza el mapa
      setTimeout(() => {
        map.updateSize();
      }, 0);
    }
    // Solo el cierre final devuelve foco; los cambios internos y el mapa no pasan aquí.
    await tick();
    if (!origin || dialogOrigin || showBuscarDireccionDialog || showBuscarClienteDialog ||
        showPedidosDialog || showPedidosHistoricoDialog || showAgregarClienteDialog) return;
    const destination = chooseFocusReturn({
      triggerPresent: origin.trigger.isConnected,
      triggerVisible: isFocusTargetVisible(origin.trigger),
      openedFromMobileMenu: origin.openedFromMobileMenu,
      menuButtonPresent: Boolean(menuButton?.isConnected),
      menuButtonVisible: isFocusTargetVisible(menuButton)
    });
    if (destination === 'trigger') origin.trigger.focus();
    if (destination === 'menu') menuButton.focus();
  }

  function handlePedidosAction(event) {
    openPedidos(event);
  }

  // Funciones para agregar cliente
  function handleUbicacionGeorreferenciada(event) {
    const { lat, lon } = event.detail;
    modoSeleccionPunto = false;
    coordenadasSeleccionadas = { lat, lon };
    if (map) {
      map.getViewport().style.cursor = '';
      addMarker(lon, lat);
    }
  }

  function handleSeleccionarUbicacion() {
    // Activar modo de selección de punto
    modoSeleccionPunto = true;
    coordenadasSeleccionadas = null;
    
    // Cambiar cursor del mapa
    if (map) {
      map.getViewport().style.cursor = 'crosshair';
    }
  }

  function handleClienteAgregado(event) {
    const { cliente, message } = event.detail;
    
    // Mostrar notificación de éxito
    handleShowGlobalNotification({
      detail: {
        message: message,
        type: 'success'
      }
    });

    // Refrescar la capa de clientes para mostrar el nuevo cliente
    if (clientesLayer) {
      clientesLayer.getSource().refresh();
    }

    // Hacer zoom al nuevo cliente si tiene coordenadas
    if (cliente.longitud && cliente.latitud) {
      setTimeout(() => {
        map.getView().animate({
          center: fromLonLat([cliente.longitud, cliente.latitud]),
          zoom: 18,
          duration: 1000
        });
        
        // Agregar un marcador temporal
        addMarker(cliente.longitud, cliente.latitud);
      }, 500);
    }

    // Cerrar el diálogo
    closeDialogs();
  }

  async function handleBuscarDireccion(event) {
    const direccion = event.detail.direccion;
    console.log("Buscando dirección:", direccion);

    try {
      const response = await authorizedFetch(`${API_BASE_URL}/api/direcciones/buscar`, {
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
        map.getView().animate({
            center: fromLonLat([data.longitud, data.latitud]),
            zoom: 17,
            duration: 1000
        });
        await closeDialogs();
      } else {
        alert("No se recibieron coordenadas válidas del backend.");
      }

    } catch (error) {
      console.error('Error al buscar dirección:', error);
      alert(`Error al buscar dirección: ${error.message}`);
    }
  }

  function medialunaIcon() {
    return new Icon({
      src: '/imagenes/medialuna.svg?v=2',
      width: 16,
      height: 16,
      anchor: [0.5, 0.5]
    });
  }

  function colorUbicacion() {
    const color = getComputedStyle(document.documentElement).getPropertyValue('--ds-location').trim();
    return /^#[0-9a-fA-F]{6}$/.test(color) ? color : '#047857';
  }

  function colorConAlfa(hex, alfa) {
    const valor = parseInt(hex.slice(1), 16);
    const rojo = (valor >> 16) & 255;
    const verde = (valor >> 8) & 255;
    const azul = valor & 255;
    return `rgba(${rojo}, ${verde}, ${azul}, ${alfa})`;
  }

  function estiloUbicacion(feature) {
    const color = colorUbicacion();
    if (feature.get('tipo') === 'precision') {
      return new Style({
        fill: new Fill({ color: colorConAlfa(color, 0.18) }),
        stroke: new Stroke({ color: colorConAlfa(color, 0.55), width: 1 })
      });
    }
    return new Style({
      image: new Circle({
        radius: 7,
        fill: new Fill({ color }),
        stroke: new Stroke({ color: '#ffffff', width: 2 })
      })
    });
  }

  function mostrarAviso(message, type) {
    handleShowGlobalNotification({ detail: { message, type } });
  }

  function actualizarUbicacion(posicion) {
    if (!ubicacionSource || !map) return;
    const lon = posicion.coords.longitude;
    const lat = posicion.coords.latitude;
    const centro = fromLonLat([lon, lat]);
    const precision = Number(posicion.coords.accuracy);
    ubicacionSource.clear();
    if (Number.isFinite(precision) && precision > 0) {
      ubicacionSource.addFeature(new Feature({
        geometry: new CircleGeom(centro, precision),
        tipo: 'precision'
      }));
    }
    ubicacionSource.addFeature(new Feature({
      geometry: new Point(centro),
      tipo: 'punto'
    }));
    ubicacionActual = { lat, lon };
    if (!centrarUbicacion) return;
    centrarUbicacion = false;
    const zoom = map.getView().getZoom();
    map.getView().animate({
      center: centro,
      zoom: zoom < 16 ? 17 : zoom,
      duration: 600
    });
  }

  function detenerUbicacion() {
    if (ubicacionWatchId != null && navigator.geolocation) {
      navigator.geolocation.clearWatch(ubicacionWatchId);
    }
    ubicacionWatchId = null;
    ubicacionActiva = false;
    ubicacionRecibida = false;
    ubicacionActual = null;
    centrarUbicacion = false;
    if (ubicacionSource) ubicacionSource.clear();
    quitarPedidoCercano();
  }

  function quitarPedidoCercano() {
    if (pedidoCercanoId == null) return;
    pedidoCercanoId = null;
    if (pedidosLayer) pedidosLayer.changed();
    closeFeatureTooltip();
  }

  function posicionarTooltipEnMapa(coordinate) {
    if (!map || !mapElement) return;
    const pixel = map.getPixelFromCoordinate(coordinate);
    if (!pixel) return;
    const mapa = mapElement.getBoundingClientRect();
    const tooltipWidth = 250;
    const tooltipHeight = 200;
    let x = mapa.left + pixel[0] + 15;
    let y = mapa.top + pixel[1] - 15;
    if (x + tooltipWidth > window.innerWidth) x = mapa.left + pixel[0] - tooltipWidth - 15;
    if (y < 0) y = mapa.top + pixel[1] + 15;
    if (y + tooltipHeight > window.innerHeight) y = window.innerHeight - tooltipHeight - 10;
    if (window.innerWidth <= 768) {
      x = Math.max(10, Math.min(x, window.innerWidth - tooltipWidth - 10));
      y = Math.max(10, Math.min(y, window.innerHeight - tooltipHeight - 10));
    }
    tooltipPosition = { x, y };
  }

  function seleccionarPedidoEnMapa(pedido) {
    const lon = Number(pedido?.longitud);
    const lat = Number(pedido?.latitud);
    if (!map || !Number.isFinite(lon) || !Number.isFinite(lat)) return;
    pedidoCercanoId = pedido.id;
    showPedidosLayer = true;
    if (pedidosLayer) pedidosLayer.changed();
    const coordinate = fromLonLat([lon, lat]);
    selectedFeatureData = {
      id: pedido.id_pedido || pedido.id || 'N/A',
      nombre: pedido.nombre || 'N/A',
      direccion: pedido.direccion || 'N/A',
      cantidad: pedido.cantidad ?? 'N/A',
      fecha: pedido.fecha || 'N/A',
      telefono: pedido.telefono || 'N/A',
      horario: pedido.horario || 'N/A',
      observaciones: pedido.observaciones || 'N/A',
      calle: pedido.calle || 'N/A',
      altura: pedido.altura ?? 'N/A'
    };
    tooltipType = 'pedido';
    showFeatureTooltip = true;
    const mostrar = () => posicionarTooltipEnMapa(coordinate);
    mostrar();
    map.getView().animate({
      center: coordinate,
      zoom: 18,
      duration: 700
    }, mostrar);
  }

  async function marcarPedidoCercano() {
    if (!ubicacionActiva || !ubicacionActual) {
      mostrarAviso('Activá la posición del móvil para buscar el pedido más cercano.', 'warning');
      return;
    }
    try {
      const params = new URLSearchParams({
        latitud: String(ubicacionActual.lat),
        longitud: String(ubicacionActual.lon)
      });
      const response = await authorizedFetch(`${API_BASE_URL}/api/pedidos/cercano?${params}`);
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        mostrarAviso(data.error || 'No se pudo buscar el pedido más cercano.', 'error');
        return;
      }
      if (!data.pedido) {
        quitarPedidoCercano();
        mostrarAviso('No hay pedidos activos para marcar.', 'warning');
        return;
      }
      seleccionarPedidoEnMapa(data.pedido);
    } catch (error) {
      console.error('Error al buscar el pedido más cercano:', error);
      mostrarAviso('No se pudo buscar el pedido más cercano.', 'error');
    }
  }

  function alternarUbicacion() {
    if (ubicacionActiva) {
      detenerUbicacion();
      return;
    }
    if (!navigator.geolocation) {
      mostrarAviso('Este navegador no puede obtener la posición del móvil.', 'error');
      return;
    }
    ubicacionActiva = true;
    centrarUbicacion = true;
    ubicacionWatchId = navigator.geolocation.watchPosition(
      (posicion) => {
        ubicacionRecibida = true;
        actualizarUbicacion(posicion);
      },
      (error) => {
        if (ubicacionRecibida) return;
        detenerUbicacion();
        mostrarAviso(
          error.code === 1
            ? 'Hay que permitir la ubicación para ver el móvil en el mapa.'
            : 'No se pudo obtener la posición del móvil.',
          'error'
        );
      },
      { enableHighAccuracy: true, maximumAge: 10000, timeout: 20000 }
    );
  }

  function addMarker(lon, lat, marker) {
    if (!markerSource) return;

    // Limpiar marcadores anteriores
    markerSource.clear();

    const feature = new Feature({
      geometry: new Point(fromLonLat([lon, lat]))
    });
    if (marker === 'medialuna') {
      feature.setStyle(new Style({
        image: medialunaIcon()
      }));
    }
    markerSource.addFeature(feature);
  }

  function handleZoomToLocation(event) {
    const { longitude, latitude, marker } = event.detail;
    if (map && longitude && latitude) {
      // Animar el zoom al cliente seleccionado
      map.getView().animate({
        center: fromLonLat([longitude, latitude]),
        zoom: 18, // Zoom cercano para ver el cliente
        duration: 1000 // Duración de la animación en ms
      });

      addMarker(longitude, latitude, marker);
    }
  }

  function limpiarMapa() {
    quitarPedidoCercano();
    if (markerSource) markerSource.clear();
    temporaryLayers.forEach((layer) => {
      if (map) map.removeLayer(layer);
    });
    temporaryLayers = [];
    closeFeatureTooltip();
  }

  function handleVerHistoricoEnMapa(event) {
    if (!map) return;
    limpiarMapa();
    const ids = [...new Set(
      (event.detail.pedidos || [])
        .map((pedido) => Number(pedido.id_cliente))
        .filter((id) => Number.isInteger(id) && id > 0)
    )];
    if (!ids.length) return;

    const cql = `id IN (${ids.join(',')})`;
    const source = new VectorSource({
      format: new GeoJSON(),
      url: GEOSERVER_BASE_URL
        + '/ows?service=WFS&version=1.1.0&request=GetFeature&typename=GeneralBelgrano:Pedidos&outputFormat=application/json&srsname=EPSG:3857&CQL_FILTER='
        + encodeURIComponent(cql)
    });
    const layer = new VectorLayer({
      source,
      style: new Style({
        image: medialunaIcon()
      })
    });
    map.addLayer(layer);
    temporaryLayers = [layer];
    source.once('featuresloadend', () => {
      const extent = source.getExtent();
      if (extent && extent.every((value) => Number.isFinite(value))) {
        map.getView().fit(extent, { padding: [48, 48, 48, 48], maxZoom: 17, duration: 600 });
      }
    });
  }

  async function handleBuscarDireccionCliente(event) {
    const direccion = event.detail.direccion;
    console.log("Buscando dirección del cliente:", direccion);

    try {
      const response = await authorizedFetch(`${API_BASE_URL}/api/direcciones/buscar`, {
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
      console.log("Respuesta del backend para cliente:", data);

      if (data.latitud && data.longitud) {
        // Centrar el mapa en la ubicación del cliente sin agregar marcador
        map.getView().animate({
            center: fromLonLat([data.longitud, data.latitud]),
            zoom: 18, // Zoom cercano para ver el cliente
            duration: 1000 // Duración de la animación en ms
        });
        
        console.log(`Cliente ubicado en: ${data.latitud}, ${data.longitud}`);
      } else {
        console.warn("No se recibieron coordenadas válidas para el cliente.");
        handleShowGlobalNotification({
          detail: {
            message: 'Cliente actualizado, pero no se pudo geocodificar su dirección.',
            type: 'warning'
          }
        });
      }

    } catch (error) {
      console.error('Error al buscar dirección del cliente:', error);
      handleShowGlobalNotification({
        detail: {
          message: 'Cliente actualizado, pero hubo un error al buscar su ubicación.',
          type: 'warning'
        }
      });
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

{#if !authReady}
<main class="auth-gate auth-gate-pending" aria-busy="true">
  <p class="auth-pending">Comprobando sesión…</p>
</main>
{:else if !authenticated}
<main class="auth-gate">
  <header class="auth-bar"><span>RAWEB</span></header>
  <section class="auth-card">
    <h1>RAWEB</h1>
    <p class="auth-subtitle">Ingresá con tu cuenta de Rancho.</p>
    {#if authMessage}<p class="auth-message">{authMessage}</p>{/if}
    <button type="button" class="auth-login" on:click={ingresarConKeycloak}>Ingresar con Keycloak</button>
  </section>
</main>
{:else}
<main>
  <nav class="navbar" aria-label="Principal">
    <div class="navbar-brand">
      <h1>RAWEB</h1>
    </div>

    <div class="nav-buttons d-mobile-none">
      <button on:click={openBuscarDireccion} class:active={showBuscarDireccionDialog}>
        <UiIcon name="pin" size={16} />
        <span>Buscar dirección</span>
      </button>
      <button on:click={openBuscarCliente} class:active={showBuscarClienteDialog}>
        <UiIcon name="user" size={16} />
        <span>Buscar cliente</span>
      </button>
      <button on:click={openAgregarCliente} class:active={showAgregarClienteDialog}>
        <UiIcon name="plus" size={16} />
        <span>Agregar cliente</span>
      </button>
      <button on:click={handlePedidosAction} class:active={showPedidosDialog}>
        <UiIcon name="box" size={16} />
        <span>Pedidos</span>
      </button>
      <button on:click={openPedidosHistorico} class:active={showPedidosHistoricoDialog}>
        <UiIcon name="history" size={16} />
        <span>Pedidos histórico</span>
      </button>
    </div>

    <div class="navbar-tools">
      <AccountMenu
        {username}
        {themePreference}
        on:themechange={handleThemeChange}
        on:changepassword={solicitarCambioContrasena}
        on:logout={cerrarSesion}
      />
    </div>
  </nav>

  <nav class="bottom-nav" aria-label="Acciones">
    <button type="button" on:click={openBuscarDireccion} class:active={showBuscarDireccionDialog}>
      <span class="bottom-nav-mark"><UiIcon name="pin" size={18} /></span>
      <span>Dirección</span>
    </button>
    <button type="button" on:click={openBuscarCliente} class:active={showBuscarClienteDialog}>
      <span class="bottom-nav-mark"><UiIcon name="user" size={18} /></span>
      <span>Clientes</span>
    </button>
    <button type="button" class="bottom-nav-add" on:click={openAgregarCliente} class:active={showAgregarClienteDialog}>
      <span class="bottom-nav-mark"><UiIcon name="plus" size={18} /></span>
      <span>Agregar</span>
    </button>
    <button type="button" on:click={handlePedidosAction} class:active={showPedidosDialog}>
      <span class="bottom-nav-mark"><UiIcon name="box" size={18} /></span>
      <span>Pedidos</span>
    </button>
    <button type="button" on:click={openPedidosHistorico} class:active={showPedidosHistoricoDialog}>
      <span class="bottom-nav-mark"><UiIcon name="history" size={18} /></span>
      <span>Historial</span>
    </button>
  </nav>

  <div class="map-container" bind:this={mapElement}>
    <!-- El mapa siempre está presente en el DOM -->
    
    <!-- Toolbar de capas flotante -->
    {#if showLayerToolbar}
      <div class="layer-toolbar">
                 <div class="layer-toolbar-header">
           <span class="layer-toolbar-title"><UiIcon name="layers" size={16} /> Capas</span>
            <button type="button" class="layer-toolbar-toggle" on:click={toggleLayerToolbar} title="Cerrar panel de capas" aria-label="Cerrar panel de capas">
             <UiIcon name="close" size={16} />
           </button>
         </div>
        
        <div class="layer-toolbar-content">
          <div class="layer-group">
            <div class="layer-group-title">Capas de Datos</div>
            <label class="layer-item">
              <input class="ds-choice" type="checkbox" bind:checked={showClientesLayer} />
              <span class="layer-name">● Clientes</span>
            </label>
            <label class="layer-item">
              <input class="ds-choice" type="checkbox" bind:checked={showPedidosLayer} />
              <span class="layer-name">▪ Pedidos</span>
            </label>
            <label class="layer-item layer-subitem">
              <input class="ds-choice" type="checkbox" bind:checked={showPedidosNombre} disabled={!showPedidosLayer} />
              <span class="layer-name">Nombre</span>
            </label>
            <div class="layer-subgroup" role="group" aria-labelledby="layer-group-tramos">
              <button
                type="button"
                class="layer-subgroup-toggle"
                id="layer-group-tramos"
                aria-expanded={tramosGroupOpen}
                aria-controls="layer-group-tramos-items"
                on:click={() => tramosGroupOpen = !tramosGroupOpen}
              >
                <span class="layer-subgroup-chevron" class:is-open={tramosGroupOpen} aria-hidden="true"></span>
                Tramos
              </button>
              {#if tramosGroupOpen}
                <div id="layer-group-tramos-items">
                  <label class="layer-item">
                    <input class="ds-choice" type="checkbox" bind:checked={showTramosLayer} />
                    <span class="layer-name">━ Tramos</span>
                  </label>
                  <label class="layer-item">
                    <input class="ds-choice" type="checkbox" bind:checked={showTramosSentidoLayer} />
                    <span class="layer-name">➤ Tramos sentido</span>
                  </label>
                  <label class="layer-item">
                    <input class="ds-choice" type="checkbox" bind:checked={showTramosNombreLayer} />
                    <span class="layer-name">A Tramos nombre</span>
                  </label>
                </div>
              {/if}
            </div>
            <label class="layer-item">
              <input class="ds-choice" type="checkbox" bind:checked={showPlazasLayer} />
              <span class="layer-name">▣ Plazas</span>
            </label>
            <label class="layer-item">
              <input class="ds-choice" type="checkbox" bind:checked={showSubbarriosLayer} />
              <span class="layer-name">▢ Subbarrios</span>
            </label>
            <label class="layer-item">
              <input class="ds-choice" type="checkbox" bind:checked={showBarriosLayer} />
              <span class="layer-name">▢ Barrios</span>
            </label>
          </div>
          
          <div class="layer-group">
            <div class="layer-group-title">Capas Base</div>
            <label class="layer-item">
              <input class="ds-choice" type="checkbox" bind:checked={showOSMLayer} />
              <span class="layer-name">○ OpenStreetMap</span>
            </label>
            <label class="layer-item">
              <input class="ds-choice" type="checkbox" bind:checked={showSatelliteLayer} />
              <span class="layer-name">◉ Satelital</span>
            </label>
          </div>
        </div>
      </div>
    {:else}
             <button type="button" class="layer-toolbar-show-btn" on:click={toggleLayerToolbar} title="Mostrar panel de capas" aria-label="Mostrar panel de capas">
         <UiIcon name="layers" size={18} />
       </button>
    {/if}

    <!-- Botón flotante para agregar cliente -->
    <button type="button" class="add-client-floating-btn" on:click={openAgregarCliente} title="Agregar nuevo cliente" aria-label="Agregar nuevo cliente">
      <UiIcon name="plus" size={20} />
    </button>
    <button
      type="button"
      class="ubicacion-btn"
      class:activa={ubicacionActiva}
      on:click={alternarUbicacion}
      title={ubicacionActiva ? 'Ocultar posición del móvil' : 'Mostrar posición del móvil'}
      aria-label={ubicacionActiva ? 'Ocultar posición del móvil' : 'Mostrar posición del móvil'}
      aria-pressed={ubicacionActiva}
    >
      <UiIcon name="locate" size={20} />
    </button>
    <button
      type="button"
      class="pedido-cercano-btn"
      class:activa={ubicacionActiva}
      on:click={marcarPedidoCercano}
      disabled={!ubicacionActiva}
      title={ubicacionActiva ? 'Marcar el pedido más cercano' : 'Activá la posición del móvil para buscar el pedido más cercano'}
      aria-label={ubicacionActiva ? 'Marcar el pedido más cercano' : 'Activá la posición del móvil para buscar el pedido más cercano'}
    >
      <UiIcon name="nearest" size={20} />
    </button>
    <button type="button" class="map-clear-btn" on:click={limpiarMapa}>Limpiar</button>
  </div>

  {#if showBuscarDireccionDialog}
    <BuscarDireccionDialog
      on:close={closeDialogs}
      on:buscar={handleBuscarDireccion}
    />
  {/if}

  {#if showBuscarClienteDialog}
    <BuscarCliente
      coordenadas={coordenadasSeleccionadas}
      seleccionandoUbicacion={modoSeleccionPunto}
      on:close={closeDialogs}
      on:showGlobalNotification={handleShowGlobalNotification}
      on:refreshPedidosLayer={refreshPedidosLayerMap}
      on:buscarDireccionCliente={handleBuscarDireccionCliente}
      on:agregarCliente={openAgregarClienteFromSearch}
      on:zoomToLocation={handleZoomToLocation}
      on:seleccionarUbicacion={handleSeleccionarUbicacion}
      on:ubicacionGeorreferenciada={handleUbicacionGeorreferenciada}
    />
  {/if}

  {#if showPedidosDialog}
    <Pedidos
      on:close={closeDialogs}
      on:zoomToLocation={handleZoomToLocation}
      on:refreshPedidosLayer={refreshPedidosLayerMap}
      on:showGlobalNotification={handleShowGlobalNotification}
    />
  {/if}

  {#if showPedidosHistoricoDialog}
    <PedidosHistorico
      on:close={closeDialogs}
      on:zoomToLocation={handleZoomToLocation}
      on:verEnMapa={handleVerHistoricoEnMapa}
      on:refreshPedidosLayer={refreshPedidosLayerMap}
      on:showGlobalNotification={handleShowGlobalNotification}
    />
  {/if}

  {#if showAgregarClienteDialog}
    <AgregarCliente
      coordenadas={coordenadasSeleccionadas}
      seleccionandoUbicacion={modoSeleccionPunto}
      valoresIniciales={agregarClienteInicial}
      on:close={closeDialogs}
      on:seleccionarUbicacion={handleSeleccionarUbicacion}
      on:ubicacionGeorreferenciada={handleUbicacionGeorreferenciada}
      on:clienteAgregado={handleClienteAgregado}
    />
  {/if}

  <!-- Tooltip de información de pedidos y clientes -->
  {#if showFeatureTooltip && selectedFeatureData}
    <div class="feature-tooltip" 
         style="left: {tooltipPosition.x}px; top: {tooltipPosition.y}px;" 
         on:click|stopPropagation
         on:keydown|stopPropagation
         role="dialog"
         aria-label="Información del elemento seleccionado">
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
            <div class="feature-tooltip-data">{selectedFeatureData.cantidad} {Number(selectedFeatureData.cantidad) === 1 ? 'docena' : 'docenas'}</div>
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
{/if}

<style>
  /* Estilos responsive base */
  main {
    display: flex;
    flex-direction: column;
    height: 100dvh;
    min-height: 100dvh;
    overflow: hidden;
    -webkit-touch-callout: none;
    -webkit-user-select: none;
    -webkit-tap-highlight-color: transparent;
    touch-action: pan-x pan-y;
  }

  .navbar {
    background-color: var(--ds-background);
    color: var(--ds-text);
    padding: 0.3rem 1rem;
    padding-top: calc(0.3rem + env(safe-area-inset-top));
    display: flex;
    flex-wrap: nowrap;
    justify-content: flex-start;
    align-items: center;
    gap: 1.25rem;
    border-bottom: 1px solid var(--ds-divider);
    z-index: 1000;
    position: relative;
    min-height: var(--ds-header-height);
  }

  .navbar-brand {
    flex: 0 0 auto;
  }

  .navbar-brand h1 {
    margin: 0;
    font-size: var(--ds-type-brand);
    color: var(--ds-text);
    font-weight: 700;
    line-height: 1.2;
  }

  .nav-buttons {
    display: flex;
    flex: 0 1 auto;
    flex-wrap: wrap;
    gap: 0.2rem;
    align-items: center;
    min-width: 0;
  }

  .navbar-tools {
    flex: 0 0 auto;
    margin-left: auto;
    display: flex;
    align-items: center;
  }

  @media (min-width: 769px) {
    .nav-buttons button {
      width: auto;
      margin-bottom: 0;
    }
  }

  .nav-buttons button {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    margin: 0;
    padding: 0.35rem 0.7rem;
    min-height: 2.125rem;
    cursor: pointer;
    border: 1px solid transparent;
    border-radius: var(--ds-radius-small);
    background-color: transparent;
    color: var(--ds-text);
    font-size: var(--ds-type-nav);
    font-weight: 600;
    transition: background-color var(--ds-motion) ease, color var(--ds-motion) ease;
    white-space: nowrap;
  }

  .nav-buttons button:hover {
    background-color: var(--ds-secondary-hover);
    border-color: transparent;
  }

  .nav-buttons button.active {
    background-color: var(--ds-selected);
    border-color: transparent;
    color: var(--ds-primary);
  }

  .nav-buttons button:focus-visible,
  .bottom-nav button:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
    box-shadow: none;
  }

  .bottom-nav {
    display: none;
  }

  /* Toolbar de capas flotante */
  .layer-toolbar {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    width: 250px;
    background: var(--ds-surface);
    color: var(--ds-text);
    border-radius: var(--ds-radius-medium);
    box-shadow: var(--ds-shadow-panel);
    border: 1px solid var(--ds-border);
    z-index: 1000;
    font-size: 0.875rem;
    max-height: calc(100dvh - var(--ds-header-height) - 2rem);
    overflow-y: auto;
  }

  .layer-toolbar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.3rem 1rem;
    border-bottom: 1px solid var(--ds-divider);
    background: var(--ds-background);
    border-radius: 8px 8px 0 0;
    min-height: 32px;
  }

  .layer-toolbar-title {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-weight: 600;
    color: var(--ds-text);
    font-size: var(--ds-type-label);
    line-height: 1.2;
  }

  .layer-toolbar-toggle {
    background: none;
    border: none;
    font-size: 0.875rem;
    color: var(--ds-text-muted);
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
    background: var(--ds-secondary-hover);
    color: var(--ds-text);
  }

  .layer-toolbar-toggle:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
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
    color: var(--ds-text-muted);
    margin-bottom: 0.5rem;
    font-size: 0.8rem;
    text-transform: none;
    letter-spacing: 0;
  }

  .layer-subgroup {
    margin: 0 0 0.5rem 0.35rem;
    padding: 0.15rem 0 0.15rem 0.65rem;
    border-left: 2px solid var(--ds-divider);
  }

  .layer-subgroup-toggle {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    width: 100%;
    margin: 0 0 0.25rem;
    padding: 0.15rem 0.15rem;
    border: none;
    background: transparent;
    color: var(--ds-text-muted);
    font: inherit;
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1.2;
    text-align: left;
    cursor: pointer;
    border-radius: 4px;
  }

  .layer-subgroup-toggle:hover {
    color: var(--ds-text);
  }

  .layer-subgroup-toggle:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
  }

  .layer-subgroup-chevron {
    width: 0.4rem;
    height: 0.4rem;
    border-right: 1.5px solid currentColor;
    border-bottom: 1.5px solid currentColor;
    transform: rotate(-45deg);
    transition: transform var(--ds-motion) ease;
    flex-shrink: 0;
  }

  .layer-subgroup-chevron.is-open {
    transform: rotate(45deg);
  }

  @media (prefers-reduced-motion: reduce) {
    .layer-subgroup-chevron {
      transition: none;
    }
  }

  .layer-subgroup .layer-item {
    padding-top: 0.35rem;
    padding-bottom: 0.35rem;
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
    background: var(--ds-secondary-hover);
    border-color: var(--ds-border);
  }

  .layer-item:last-child {
    margin-bottom: 0;
  }

  .layer-subitem {
    margin-top: -0.25rem;
    margin-left: 1.5rem;
    padding-top: 0.25rem;
    padding-bottom: 0.25rem;
  }

  .layer-item input[type="checkbox"] {
    margin-right: 0.75rem;
    margin-bottom: 0;
    width: auto;
    transform: scale(1.1);
  }

  .layer-name {
    color: var(--ds-text);
    font-weight: 500;
  }

  .layer-toolbar-show-btn {
    position: absolute;
    top: 0.75rem;
    right: 0.75rem;
    width: 44px;
    height: 44px;
    margin: 0;
    background: var(--ds-surface);
    color: var(--ds-text);
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-medium);
    box-shadow: var(--ds-shadow-sm);
    cursor: pointer;
    font-size: 1.05rem;
    transition: background-color var(--ds-motion) ease;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .layer-toolbar-show-btn:hover {
    background: var(--ds-secondary-hover);
  }

  .layer-toolbar-show-btn:focus-visible,
  .add-client-floating-btn:focus-visible,
  .ubicacion-btn:focus-visible,
  .pedido-cercano-btn:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
  }

  :global(:root[data-theme="dark"]) .layer-toolbar-show-btn:focus-visible,
  :global(:root[data-theme="dark"]) .add-client-floating-btn:focus-visible,
  :global(:root[data-theme="dark"]) .ubicacion-btn:focus-visible,
  :global(:root[data-theme="dark"]) .pedido-cercano-btn:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
  }

  /* Botón flotante para agregar cliente */
  .add-client-floating-btn {
    position: absolute;
    top: 4.35rem;
    right: 0.75rem;
    width: 44px;
    height: 44px;
    margin: 0;
    background: var(--ds-location);
    border: 1px solid var(--ds-location);
    border-radius: var(--ds-radius-round);
    box-shadow: var(--ds-shadow-sm);
    cursor: pointer;
    font-size: 1.35rem;
    color: var(--ds-on-location);
    transition: background-color var(--ds-motion) ease;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
  }

  .add-client-floating-btn:hover {
    background: var(--ds-location-hover);
    border-color: var(--ds-location-hover);
  }

  .add-client-floating-btn:active {
    background: var(--ds-location-active);
  }

  .ubicacion-btn {
    position: absolute;
    top: calc(4.35rem + 44px + 0.5rem);
    right: 0.75rem;
    width: 44px;
    height: 44px;
    margin: 0;
    padding: 0;
    background: var(--ds-surface);
    color: var(--ds-text);
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-round);
    box-shadow: var(--ds-shadow-sm);
    cursor: pointer;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .ubicacion-btn:hover {
    background: var(--ds-secondary-hover);
  }

  .ubicacion-btn.activa,
  .ubicacion-btn.activa:hover,
  .pedido-cercano-btn.activa,
  .pedido-cercano-btn.activa:hover {
    background: var(--ds-location);
    color: var(--ds-on-location);
    border-color: var(--ds-location);
  }

  .pedido-cercano-btn {
    position: absolute;
    top: calc(4.35rem + 88px + 1rem);
    right: 0.75rem;
    width: 44px;
    height: 44px;
    margin: 0;
    padding: 0;
    background: var(--ds-surface);
    color: var(--ds-text-muted);
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-round);
    box-shadow: var(--ds-shadow-sm);
    cursor: pointer;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .pedido-cercano-btn:disabled {
    opacity: 0.45;
    cursor: not-allowed;
    background: var(--ds-surface);
    color: var(--ds-text-muted);
    border-color: var(--ds-border);
  }

  .map-clear-btn {
    position: absolute;
    left: 0.75rem;
    bottom: 2.25rem;
    z-index: 1000;
    width: max-content;
    min-height: 36px;
    margin: 0;
    padding: 0.35rem 0.7rem;
    background: var(--ds-surface);
    color: var(--ds-text);
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-medium);
    box-shadow: var(--ds-shadow-sm);
    cursor: pointer;
    font: inherit;
    font-size: 0.8125rem;
    font-weight: 600;
  }

  .map-clear-btn:hover {
    background: var(--ds-secondary-hover);
  }

  .map-clear-btn:focus-visible {
    outline: 2px solid var(--ds-focus);
    outline-offset: 1px;
  }

  .bottom-nav button {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.1rem;
    width: 100%;
    min-height: 44px;
    margin: 0;
    padding: 0.3rem 0.15rem;
    border: none;
    border-radius: var(--ds-radius-small);
    background: transparent;
    color: var(--ds-text-muted);
    font-size: 0.68rem;
    font-weight: 500;
    line-height: 1.15;
  }

  .bottom-nav button.active {
    color: var(--ds-on-selected);
    background: var(--ds-selected);
  }

  .bottom-nav-mark {
    display: flex;
    line-height: 1;
  }

  .bottom-nav-add {
    color: var(--ds-on-location);
    background: var(--ds-location);
    border-radius: var(--ds-radius-medium);
  }

  .bottom-nav-add.active {
    background: var(--ds-location-active);
    color: var(--ds-on-location);
  }



  /* Contenedor del mapa */
  .map-container {
    flex: 1 1 auto;
    width: 100%;
    position: relative;
    min-height: 0;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-x pan-y;
    overflow: hidden;
    background: var(--ds-background);
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
    top: 0.75rem;
    left: 0.75rem;
    display: flex;
    flex-direction: column;
    background: var(--ds-surface);
    border: 1px solid var(--ds-border);
    border-radius: var(--ds-radius-medium);
    box-shadow: var(--ds-shadow-sm);
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
    background: var(--ds-surface) !important;
    color: var(--ds-text) !important;
    cursor: pointer !important;
    transition: background-color 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border-radius: 0 !important;
  }

  :global(.ol-zoom button:hover) {
    background: var(--ds-secondary-hover) !important;
    transform: none !important;
  }

  :global(.ol-zoom button:focus-visible) {
    outline: 2px solid var(--ds-focus) !important;
    outline-offset: -2px !important;
    box-shadow: none !important;
  }

  :global(.ol-attribution) {
    bottom: 0.35rem;
    right: 0.35rem;
    font-size: 0.75rem;
    background: var(--ds-surface);
    color: var(--ds-text);
    border: 1px solid var(--ds-border);
    padding: 2px 4px;
    border-radius: var(--ds-radius-small);
    box-shadow: var(--ds-shadow-sm);
  }

  :global(.ol-attribution ul) {
    margin: 0;
    padding: 0;
    list-style: none;
    font-size: 0.7rem;
  }

  :global(.ol-attribution a) {
    color: var(--ds-primary);
  }

  :global(.ol-attribution a:hover) {
    color: var(--ds-primary-hover);
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
    color: var(--ds-text) !important;
  }

  :global(.ol-attribution button:focus-visible) {
    outline: 2px solid var(--ds-focus) !important;
    outline-offset: -2px !important;
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

  /* La barra de acciones de escritorio usa flex; en móvil la reemplaza la barra inferior. */
  .d-mobile-none {
    display: flex;
  }

  @media (max-width: 768px) {
    .d-mobile-none {
      display: none;
    }

    main {
      padding-bottom: calc(var(--ds-bottom-nav-height) + env(safe-area-inset-bottom));
    }

    .navbar-brand h1 {
      font-size: 1rem;
    }

    .bottom-nav {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      align-items: center;
      gap: 0.15rem;
      position: fixed;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 1000;
      min-height: var(--ds-bottom-nav-height);
      padding: 0.25rem 0.35rem calc(0.25rem + env(safe-area-inset-bottom));
      background: var(--ds-surface);
      color: var(--ds-text);
      border-top: 1px solid var(--ds-border);
    }

    .layer-toolbar {
      width: min(280px, calc(100vw - 5.5rem));
      max-height: calc(100dvh - var(--ds-header-height) - var(--ds-bottom-nav-height) - 1.5rem);
      top: 0.5rem;
      right: 0.5rem;
    }

    .layer-toolbar-show-btn,
    .add-client-floating-btn,
    .ubicacion-btn,
    .pedido-cercano-btn {
      right: 0.5rem;
    }

    .layer-toolbar-show-btn {
      top: 0.5rem;
    }

    .add-client-floating-btn {
      top: 4rem;
    }

    .ubicacion-btn {
      top: calc(4rem + 44px + 0.5rem);
    }

    .pedido-cercano-btn {
      top: calc(4rem + 88px + 1rem);
    }

    .map-clear-btn {
      bottom: 0.75rem;
    }

    @media (max-width: 480px) {
      .navbar {
        padding-inline: 0.5rem;
      }

      .layer-toolbar-content {
        padding: 0.75rem;
      }

      .layer-item {
        padding: 0.375rem;
        margin-bottom: 0.375rem;
      }

      .bottom-nav button {
        font-size: 0.62rem;
      }
    }
  }

  @media (max-width: 768px) and (orientation: landscape) {
    .bottom-nav {
      min-height: 3.25rem;
    }

    .layer-toolbar {
      max-height: calc(100dvh - var(--ds-header-height) - 4.5rem);
    }
  }

  /* Tablet */
  @media (min-width: 769px) and (max-width: 1100px) {
    .nav-buttons {
      flex-wrap: nowrap;
    }

    .nav-buttons button {
      padding: 0.3rem 0.45rem;
      font-size: 0.8125rem;
      gap: 0.3rem;
    }

    .layer-toolbar {
      width: 280px;
      right: 1rem;
    }
  }



  /* Estilos para el tooltip de información de pedidos y clientes */
  .feature-tooltip {
    position: fixed;
    background-color: var(--ds-surface);
    color: var(--ds-text);
    border: 1px solid var(--ds-border);
    border-radius: 6px;
    font-size: 0.85em;
    pointer-events: auto; /* Permitir que el tooltip pueda ser clickeado */
    display: block; /* Mostrar siempre */
    box-shadow: var(--ds-shadow-panel);
    min-width: 180px;
    max-width: 250px;
    max-height: calc(100vh - 20px);
    overflow-y: auto;
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
    color: var(--ds-text);
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
      max-height: calc(100vh - 20px);
    }
  }

  main.auth-gate {
    display: grid;
    grid-template-rows: 3.25rem minmax(0, 1fr);
    align-items: center;
    justify-items: center;
    height: 100dvh;
    min-height: 100dvh;
    padding: 0;
    overflow: hidden;
    background: #111827;
    color: #f9fafb;
  }

  main.auth-gate-pending {
    grid-template-rows: 1fr;
  }

  .auth-pending {
    margin: 0;
    color: #d1d5db;
    font-size: 0.875rem;
  }

  .auth-bar {
    justify-self: stretch;
    align-self: start;
    display: flex;
    align-items: center;
    height: 3.25rem;
    padding: 0 1rem;
    border-bottom: 1px solid color-mix(in srgb, #9ca3af 42%, transparent);
    background: #111827;
    color: #f9fafb;
    font-size: 1rem;
    font-weight: 700;
    line-height: 1.2;
  }

  .auth-card {
    width: min(420px, calc(100% - 2rem));
    margin-block: 1.5rem;
    padding: 1.75rem 1.5rem 1.5rem;
    display: grid;
    justify-items: center;
    text-align: center;
    border: 1px solid color-mix(in srgb, #9ca3af 42%, transparent);
    border-radius: 12px;
    background: #1f2937;
    box-shadow: 0 4px 12px rgb(0 0 0 / 15%);
  }

  .auth-card h1 {
    margin: 0;
    color: #f9fafb;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.25;
  }

  .auth-subtitle {
    margin: 0.75rem 0 0;
    color: #d1d5db;
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.5;
  }

  .auth-message {
    margin: 0.75rem 0 0;
    color: #fecaca;
    font-size: 0.8125rem;
  }

  button.auth-login {
    width: 100%;
    min-height: 44px;
    margin: 1.5rem 0 0;
    padding: 0 0.75rem;
    border: 1px solid #93c5fd;
    border-radius: 8px;
    background-color: #93c5fd;
    color: #111827;
    font-size: 0.875rem;
    font-weight: 600;
    line-height: 1.2;
    box-shadow: none;
  }

  button.auth-login:hover:not(:disabled) {
    background-color: #bfdbfe;
    border-color: #bfdbfe;
    color: #111827;
  }

  button.auth-login:active:not(:disabled) {
    background-color: #60a5fa;
    border-color: #60a5fa;
    color: #111827;
  }

  @media (max-width: 768px) {
    main.auth-gate {
      padding-bottom: 0;
    }

    .auth-card {
      width: min(420px, calc(100% - 1.5rem));
      padding: 1.5rem 1.25rem 1.25rem;
    }

    button.auth-login {
      min-height: 44px;
      margin-bottom: 0;
      padding: 0 0.75rem;
      font-size: 0.875rem;
    }
  }
</style>
