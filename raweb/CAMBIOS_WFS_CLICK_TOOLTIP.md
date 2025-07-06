# Cambios realizados: Capa de Pedidos WFS con Click y Tooltip

## Resumen de cambios

Se ha revertido la capa de pedidos de WMS a WFS y se ha implementado un sistema de click para mostrar información del pedido en un tooltip flotante que se puede cerrar haciendo click fuera del tooltip.

## Cambios principales

### 1. Reversión de WMS a WFS

**Cambio realizado:**
```javascript
// Ahora usa WFS nuevamente
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
      fill: new Fill({ color: '#ff6b6b' }),
      stroke: new Stroke({ color: '#ffffff', width: 2 })
    })
  }),
  visible: showPedidosLayer
});
```

### 2. Eliminación del evento problemático

**Problema anterior:**
- El evento `pointermove` llamaba continuamente a `fetch()` causando problemas de CORS
- Generaba múltiples peticiones innecesarias al servidor

**Solución:**
- Eliminado completamente el evento `pointermove`
- Implementado evento `singleclick` que solo se ejecuta al hacer click

### 3. Implementación del sistema de click

**Funcionalidad implementada:**
```javascript
map.on('singleclick', function(evt) {
  const features = [];
  
  // Buscar features de pedidos en el pixel clickeado
  map.forEachFeatureAtPixel(evt.pixel, function(feature, layer) {
    if (layer === pedidosLayer) {
      features.push(feature);
    }
  });

  if (features.length > 0) {
    // Mostrar información del pedido
    const feature = features[0];
    const properties = feature.getProperties();
    
    selectedPedidoData = {
      id: properties.id_pedido || properties.id || 'N/A',
      nombre: properties.nombre || 'N/A',
      direccion: properties.direccion || 'N/A',
      cantidad: properties.cantidad || 'N/A',
      fecha: properties.fecha || 'N/A',
      telefono: properties.telefono || 'N/A',
      horario: properties.horario || 'N/A',
      observaciones: properties.observaciones || 'N/A'
    };
    
    tooltipPosition = evt.coordinate;
    showPedidoTooltip = true;
    tooltipOverlay.setPosition(evt.coordinate);
  } else {
    // Click fuera de cualquier pedido - cerrar tooltip
    closePedidoTooltip();
  }
});
```

### 4. Tooltip interactivo

**Características del tooltip:**
- Se muestra al hacer click en un pedido
- Contiene toda la información del pedido
- Tiene un botón de cierre (×)
- Se puede cerrar haciendo click fuera del tooltip
- Usa `stopPropagation` para evitar que se cierre al hacer click dentro

**Implementación del tooltip:**
```svelte
{#if showPedidoTooltip && selectedPedidoData}
  <div bind:this={tooltipElement} class="pedido-tooltip" on:click|stopPropagation>
    <div class="pedido-tooltip-header">
      <h4>Información del Pedido</h4>
      <button class="tooltip-close-btn" on:click={closePedidoTooltip}>×</button>
    </div>
    <div class="pedido-tooltip-content">
      <!-- Información del pedido -->
    </div>
  </div>
{:else}
  <div bind:this={tooltipElement} style="display: none;"></div>
{/if}
```

### 5. Gestión del estado del tooltip

**Variables de estado:**
- `showPedidoTooltip`: Controla si el tooltip está visible
- `selectedPedidoData`: Contiene los datos del pedido seleccionado
- `tooltipPosition`: Coordenadas donde se muestra el tooltip

**Función de cierre:**
```javascript
function closePedidoTooltip() {
  showPedidoTooltip = false;
  selectedPedidoData = null;
  tooltipPosition = null;
}
```

### 6. Estilos del tooltip

**Diseño moderno:**
- Fondo translúcido con `backdrop-filter: blur(5px)`
- Bordes redondeados
- Sombra suave
- Botón de cierre interactivo
- Diseño responsive

### 7. Imports restaurados

**Imports necesarios para WFS:**
```javascript
import {bbox as bboxStrategy} from 'ol/loadingstrategy.js';
import GeoJSON from 'ol/format/GeoJSON.js';
import {Style, Circle, Fill, Stroke} from 'ol/style.js';
```

## Información mostrada en el tooltip

- **ID**: Identificador del pedido
- **Nombre**: Nombre del cliente
- **Dirección**: Dirección del pedido
- **Cantidad**: Cantidad del pedido
- **Fecha**: Fecha del pedido
- **Teléfono**: Teléfono del cliente
- **Horario**: Horario de entrega
- **Observaciones**: Observaciones del pedido

## Comportamiento del tooltip

1. **Al hacer click en un pedido:**
   - Se muestra el tooltip con la información completa
   - El tooltip se posiciona en las coordenadas del click
   - Se activa el overlay de OpenLayers

2. **Al hacer click fuera de un pedido:**
   - Se cierra automáticamente el tooltip
   - Se limpia el estado del tooltip

3. **Al hacer click en el botón de cierre:**
   - Se cierra el tooltip mediante la función `closePedidoTooltip()`

4. **Al hacer click dentro del tooltip:**
   - Se usa `stopPropagation` para evitar que se cierre
   - Permite interactuar con el contenido del tooltip

## Beneficios de la implementación

1. **Eliminación de problemas de CORS**: Sin peticiones continuas de `pointermove`
2. **Mejor experiencia de usuario**: Click intencional para ver información
3. **Información completa**: Todos los campos del pedido visibles
4. **Interfaz intuitiva**: Fácil de abrir y cerrar
5. **Rendimiento mejorado**: Solo una petición por click
6. **Preparado para proxy**: WFS funcionará correctamente con proxy nginx

## Preparación para proxy nginx

La implementación actual de WFS está lista para funcionar con un proxy nginx que maneje las peticiones CORS. El proxy deberá:

1. Interceptar las peticiones a `/ows?service=WFS`
2. Reenviarlas al servidor GeoServer
3. Añadir los headers CORS necesarios
4. Devolver la respuesta al cliente

## Archivos modificados

- `raweb/src/App.svelte`: Cambios principales en la aplicación
- `raweb/CAMBIOS_WFS_CLICK_TOOLTIP.md`: Esta documentación

## Próximos pasos

1. Implementar el proxy nginx para solucionar definitivamente los problemas de CORS
2. Configurar las rutas del proxy para interceptar las peticiones WFS
3. Probar la funcionalidad completa con el proxy activo