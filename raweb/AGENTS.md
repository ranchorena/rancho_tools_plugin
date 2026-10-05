# RAWEB — Instrucciones para agentes

Estas instrucciones complementan `../AGENTS.md` y se aplican a `raweb/`.

## Ejecución y verificación

- Ejecutar los comandos desde `raweb/`: `npm ci` para instalar, `npm run build` para compilar y `npm run dev` para desarrollar. No hay workspace npm en la raíz.
- La aplicación usa Svelte 3, Rollup 4 y OpenLayers 10; `README.md` conserva instrucciones de la plantilla upstream. Usar `package.json` y `rollup.config.js` como fuente de verdad.
- `npm run dev` compila en modo watch e inicia sirv automáticamente en `http://localhost:8080`. `npm start` sirve lo ya compilado; no reconstruye la aplicación.
- `public/build/` contiene JS, CSS y sourcemaps generados e ignorados por Git; editar `src/`, no los bundles.
- No existen scripts de test, lint ni typecheck. Para cambios de código, ejecutar `npm run build` y comprobar el flujo afectado en el navegador, incluyendo consola y solicitudes REST/WFS. La verificación funcional necesita API y GeoServer accesibles; indicar los requisitos faltantes.

## Configuración de URLs

- `rollup.config.js` carga `.env` desde el directorio de ejecución y reemplaza `__API_URL__` y `__GEOSERVER_URL__` en `src/config.js` durante la compilación. Configurar `raweb/.env` usando `.env.example`; no publicar sus valores sensibles.
- Los valores por defecto locales son `http://localhost:5000` y `http://localhost:8086/geoserver`. Cambiar variables del contenedor en ejecución no modifica el bundle: hay que recompilar.
- Compose usa el `.env` de la raíz y pasa argumentos de build. Su API por defecto (`http://backend:5000`) es un hostname interno de Docker; las dos URLs deben ser resolubles desde el navegador. El puerto GeoServer por defecto de build es 8087 y el de runtime es 8086.

## Organización y eventos

- `src/main.js` monta `App.svelte` sobre `document.body`. `App.svelte` controla mapa, fuentes, tooltips, visibilidad de diálogos y navegación móvil; las llamadas REST están distribuidas entre este componente y los diálogos, sin capa de servicios separada.
- Los diálogos se comunican mediante `createEventDispatcher`; revisar las suscripciones en `App.svelte` al cambiar eventos. `BuscarDireccionDialog` emite `buscar`; `BuscarCliente` emite `showGlobalNotification`, `refreshPedidosLayer` y `buscarDireccionCliente` después de guardar; `Pedidos` emite `zoomToLocation`.
- El alta cruza dos componentes: `AgregarCliente` emite `seleccionarUbicacion`, `App.svelte` captura el clic y devuelve la prop `coordenadas` con `{lat, lon}`. El evento `clienteAgregado` refresca la fuente de clientes, centra el mapa y cierra los diálogos.
- `public/global.css` y los bloques `<style>` de cada componente participan en los estilos. Los diálogos y el menú tienen variantes móviles; comprobar apertura, cierre y scroll en pantallas pequeñas cuando se cambie su layout.

## Contratos REST y mapa

- Antes de cambiar payloads o respuestas, revisar `../raapi/server.py` y `../raapi/API.py`. La edición QGIS usa proveedores de capas directamente; comprobar sus campos si se modifican datos compartidos.
- Buscar clientes: `POST /api/clientes/buscar` con `criterio` (`nombre`, `direccion` o `calle_altura`). Buscar dirección: `POST /buscar_direccion` con `{direccion}`; esta ruta no lleva prefijo `/api`.
- Actualizar: `PUT /api/clientes/actualizar/<id>` recibe `docenas` y `observaciones`; alta y lectura usan `cantidad` y `observacion`. El backend realiza esa traducción; conservar la diferencia.
- Alta: `POST /api/clientes/agregar` devuelve `{mensaje, cliente}`. `GET /api/clientes/pedidos` devuelve una lista o, si está vacío, `{message: ...}` con HTTP 200; no asumir que toda respuesta exitosa es un array.
- Las capas de clientes y pedidos se consultan por WFS en `/ows`, con nombres `GeneralBelgrano:Clientes` y `GeneralBelgrano:Pedidos`, GeoJSON y EPSG:3857. Sus datos vienen de GeoServer, mientras las grillas y los guardados usan REST; revisar el refresco de fuentes después de mutaciones.
- REST entrega y recibe coordenadas EPSG:4326. Usar `fromLonLat([longitud, latitud])` para centrar o crear geometrías y `toLonLat` para convertir clics; no intercambiar ejes. El backend transforma las altas a EPSG:5347.
- `docs/` contiene reportes históricos de cambios WMS/WFS; contrastar sus ejemplos con `App.svelte` antes de reutilizarlos.

## Reglas
- Lee `docs/constitution.md` y la spec activa (`specs/NNN-*/`) antes de tocar código.
  