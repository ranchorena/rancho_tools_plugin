# Rancho Tools — Instrucciones para agentes

## Alcance y trabajo existente

- Este repositorio tiene una única raíz Git que contiene `raapi`, `raweb`, `raqgis` y la infraestructura de GeoServer; las aplicaciones no son repositorios Git independientes. Antes de editar, ejecutar `git rev-parse --show-toplevel`, `git branch --show-current` y `git status --short`.
- El árbol de trabajo está en reorganización: los archivos del plugin se trasladaron de la raíz a `raqgis/`, y los reportes de cambios a `raweb/docs/`. Preservar las modificaciones, eliminaciones y archivos sin seguimiento existentes; no restaurar las rutas antiguas de la raíz basándose en el historial Git o en los README de las plantillas.
- Los commits, pushes, pulls, merges, rebases, cambios de rama, resets y limpiezas destructivas de Git requieren una solicitud explícita. Los cambios de esquema de base de datos, la eliminación de datos persistentes y los cambios en entornos compartidos de QA/UAT requieren confirmación.

## Puntos de entrada y contratos

- Web: `raweb/src/main.js` monta `App.svelte`, que controla el mapa de OpenLayers, las fuentes de las capas y los eventos de los diálogos. Las llamadas REST también están en los componentes de los diálogos; no hay una capa de servicios de API separada. Se usa Svelte 3 con Rollup 4, no Vite/SvelteKit; `raweb/README.md` conserva principalmente texto de la plantilla original.
- Backend: `raapi/server.py` define las rutas Flask; `API.py` implementa consultas y actualizaciones; `tables.py` obtiene las definiciones de las tablas mediante reflexión de PostgreSQL. Revisar tanto los manejadores de rutas como `API.py` antes de cambiar los payloads web, y comprobar el uso de los campos en web y QGIS antes de cambiar la semántica de datos compartidos.
- QGIS: `raqgis/__init__.py::classFactory` carga `rancho_tools_plugin.py::RAnchoTools`; sus métodos `run*` abren los diálogos. Los archivos Python de los diálogos cargan los `.ui` adyacentes mediante `uic.loadUiType`; editar los archivos fuente de la interfaz en lugar de generar formularios Python.
- Las búsquedas y los guardados de QGIS usan directamente las capas del proyecto y sus proveedores, no `raapi`. El guardado de clientes llama a `startEditing`/`changeAttributeValue`/`commitChanges`; seguir ese flujo de persistencia por separado del flujo REST.
- QGIS requiere capas del proyecto llamadas `clientes - Todos`, `clientes` y `tramos`, y grupos `Clientes` y `Tramos`. El proyecto `.qgz` y el destino KML en `rancho_tools_plugin.py` son rutas locales de Windows codificadas en el código, no archivos de prueba incluidos. Cargar el plugin desde `raqgis/`, no desde la raíz del espacio de trabajo.
- `raqgis/resources.py` se genera a partir de `resources.qrc`. El `compile.bat` de la raíz invoca `pyrcc5` de QGIS 3.16/Python 3.7 con rutas específicas de una máquina; verificarlas antes de usarlo. Mantener el código del plugin compatible con el entorno de ejecución PyQt5/QGIS existente.

## Comandos y verificación

Ejecutar los comandos npm desde `raweb/` (no hay workspace npm en la raíz):

```sh
npm ci
npm run build
npm run dev
```

- `npm run build` es la comprobación de compilación disponible para el frontend. `npm run dev` ejecuta Rollup en modo watch e inicia sirv automáticamente en el puerto 8080; `npm start` solo sirve la salida existente en `public/`. Los bundles, CSS y sourcemaps generados están en `raweb/public/build/`, ignorado por Git.
- No hay una suite de pruebas automatizadas, flujos de CI ni scripts de lint o verificación de tipos. No inventar comandos `npm test`, `npm run check` o pytest. Después de compilar, verificar en el navegador los diálogos y flujos del mapa afectados; los flujos QGIS requieren QGIS y el proyecto configurado. Informar exactamente qué comprobaciones se ejecutaron y qué requisitos faltaron.
- Preparación del backend, desde `raapi/` en un entorno Python: `python -m pip install -r requirements.txt`, seguido de `python -m flask --app server run --host 0.0.0.0 --port 5000`. La imagen Docker usa Python 3.9; las importaciones locales presuponen este directorio de trabajo.
- Al importar el backend se realiza inmediatamente la reflexión de tablas, por lo que se necesita una base PostgreSQL accesible y con las tablas requeridas. `raapi/config.py` solo lee variables del entorno del proceso, no `.env`: proporcionar `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` y, opcionalmente, `DB_SCHEMA` (por defecto `generalbelgrano`). El acceso local a la base de Compose usa el puerto 5433, no el 5432 predeterminado del backend.

## Particularidades de URLs y datos GIS

- `raweb/rollup.config.js` carga `.env` relativo al directorio de trabajo y reemplaza `__API_URL__`/`__GEOSERVER_URL__` en `src/config.js` durante la compilación. Usar `raweb/.env` para compilaciones locales; Compose lee el `.env` de la raíz y pasa argumentos de build. Cambiar únicamente el entorno del contenedor en ejecución no modifica las URLs de un frontend ya compilado.
- Ambas URLs deben ser accesibles desde el navegador. El argumento de build predeterminado de la API en Compose, `http://backend:5000`, usa un hostname interno de Docker; configurar una `API_URL` accesible desde el navegador. El puerto GeoServer predeterminado de build es 8087 y el de runtime es 8086; elegir explícitamente el endpoint deseado y recompilar.
- `App.svelte` carga `GeneralBelgrano:Clientes` y `GeneralBelgrano:Pedidos` mediante WFS de GeoServer en EPSG:3857. Las coordenadas REST están en EPSG:4326; las conversiones de OpenLayers usan `[longitud, latitud]`. `API.agregarCliente` transforma la geometría insertada a EPSG:5347; preservar estas diferencias entre sistemas de referencia de coordenadas.
- Las claves del DTO de actualización difieren de las de alta y lectura: `docenas` se traduce al campo `cantidad` de la base de datos, y `observaciones` a `observacion` en `API.actualizarCliente`. No unificar estos nombres entre endpoints sin actualizar sus consumidores.
- `GET /api/clientes/pedidos` devuelve un array cuando hay resultados, pero `{message: ...}` con HTTP 200 cuando está vacío. `/buscar_direccion` no lleva el prefijo `/api`. Preservar estos comportamientos al ajustar las llamadas.

## Infraestructura local

- El `docker-compose.yml` de la raíz inicia frontend (8080), backend (5000), PostgreSQL (puerto 5433 del host) y el proxy Nginx de GeoServer (8086). No inicia GeoServer: `rageoserver-proxy/nginx.conf` redirige a `host.docker.internal:8087/geoserver/`, por lo que se necesita GeoServer ejecutándose por separado y que ese hostname pueda resolverse.
- La inicialización de la base de Compose monta `generalbelgrano.dump`, ausente en este checkout; obtenerlo antes de iniciar una base nueva. `db_init/restore_dump.sh` restaura únicamente `generalbelgrano` durante la primera inicialización del volumen persistente. Compose usa la imagen estándar `postgres:13-alpine`, mientras que las consultas de la API necesitan funciones PostGIS; verificar su disponibilidad en lugar de asumir que Compose lo instala. Nunca eliminar el volumen de la base para reintentar la configuración sin autorización.
- Mantener los archivos `.env` locales e ignorados por Git; usar `.env.example` para identificar las variables y nunca copiar credenciales de configuraciones locales o archivos de almacenes de datos de GeoServer a instrucciones, logs o código fuente.
