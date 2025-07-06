# Cambios realizados: Capa de Pedidos WFS a WMS

## Resumen de cambios

Se ha modificado la aplicación web Svelte para cargar la capa de pedidos como WMS en lugar de WFS, solucionando los problemas de CORS y añadiendo funcionalidad de hover para mostrar información básica.

## Cambios principales

### 1. Cambio de WFS a WMS

**Antes (WFS):**
```javascript
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

**Después (WMS):**
```javascript
pedidosLayer = new ImageLayer({
  source: new ImageWMS({
    url: GEOSERVER_BASE_URL + '/wms',
    params: {
      'LAYERS': 'GeneralBelgrano:Pedidos',
      'VERSION': '1.1.0',
    },
    serverType: 'geoserver',
  }),
  visible: showPedidosLayer
});
```

### 2. Funcionalidad de hover implementada

Se añadió un evento `pointermove` que:
- Realiza una petición `GetFeatureInfo` al servidor WMS
- Muestra información básica (ID, Nombre, Dirección) en un tooltip
- Solo se activa cuando la capa de pedidos está visible

### 3. Tooltip de hover

Se creó un nuevo tooltip específico para el hover:
- Aparece al pasar el mouse sobre un pedido
- Desaparece cuando el mouse se aleja
- Diseño moderno con fondo translúcido y blur

### 4. Imports y dependencias actualizados

**Removidos (ya no necesarios):**
- `bbox as bboxStrategy` de `ol/loadingstrategy.js`
- `GeoJSON` de `ol/format/GeoJSON.js`
- `Circle, Fill, Stroke` de `ol/style.js`

**Añadidos:**
- `Overlay` de `ol/Overlay.js` para el tooltip

### 5. Funcionalidad de click removida

Como WMS no permite hacer click en features individuales como WFS, se removió:
- El evento `singleclick` que mostraba información completa
- El diálogo modal de información del pedido
- Las funciones `showPedidoInfo()` y `closePedidoInfoDialog()`
- Los estilos CSS del diálogo modal

### 6. Función de refresh actualizada

Se actualizó la función `refreshPedidosLayerMap()` para trabajar con capas WMS:
```javascript
function refreshPedidosLayerMap() {
  if (pedidosLayer) {
    const source = pedidosLayer.getSource();
    if (source && typeof source.refresh === 'function') {
      source.refresh();
      console.log("Capa Pedidos WMS refrescada");
    } else {
      // Para capas WMS, actualizar los parámetros para forzar recarga
      source.updateParams({'_dc': Date.now()});
      console.log("Capa Pedidos WMS recargada");
    }
  }
}
```

## Beneficios de los cambios

1. **Solución de CORS**: WMS no tiene los mismos problemas de CORS que WFS
2. **Mejor rendimiento**: WMS envía imágenes renderizadas en lugar de datos vectoriales
3. **Funcionalidad de hover**: Información básica al pasar el mouse
4. **Interfaz más limpia**: Tooltip discreto en lugar de modal intrusivo
5. **Consistencia**: Ambas capas (clientes y pedidos) ahora usan WMS

## Información mostrada en el hover

- **ID**: Identificador del pedido
- **Nombre**: Nombre del cliente
- **Dirección**: Dirección del pedido

## Consideraciones técnicas

- La capa de pedidos mantendrá su estilo visual definido en GeoServer
- El tooltip solo funciona cuando la capa de pedidos está visible
- Las peticiones GetFeatureInfo se realizan en formato JSON
- Se limita a 1 feature por consulta para mejor rendimiento

## Archivos modificados

- `raweb/src/App.svelte`: Cambios principales en la lógica de la aplicación
- `raweb/CAMBIOS_CAPA_PEDIDOS_WMS.md`: Este archivo de documentación