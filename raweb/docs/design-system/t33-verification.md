# Verificación T33 — ejemplos de fundaciones e identidad

Fecha: 2026-10-07. Alcance: RF-1–RF-3, RF-13 y RF-22; únicamente T33.

## Referencia roja en navegador

- Chrome, `http://localhost:52948/?catalog=design-system`, 1366×768 CSS px, carga directa previa a la compilación T33.
- La respuesta de documento y los CSS base se solicitaron, pero `bundle.css` y `bundle.js` respondieron `net::ERR_CONNECTION_REFUSED`; `document.body.innerText` estaba vacío, no había encabezado ni regiones de catálogo y no se podían consultar ejemplos de fundaciones o identidad. Por tanto, la vista cargada no presentaba los ejemplos requeridos. El intento de cargar nuevamente después de compilar confirmó que no había servidor escuchando en el puerto: se sirvió entonces `public/` temporalmente en `127.0.0.1:52948`.
- La referencia registra estado real del navegador, no una comprobación de cadenas fuente. No se observaron ni solicitaron datos de clientes/pedidos.

## Implementación

- `src/design-system/Catalog.svelte` agrega al catálogo las secciones «Fundaciones visuales» y «Identidad actual y reglas compartidas».
- Las muestras muestran swatches de color semántico, propósito, valores de tipografía y espacio, bordes/radios/sombras y ejemplos de iconografía presente. Se basan exclusivamente en valores de `public/design-system.css` y rasgos documentados en `docs/design-system/coverage.md`.
- La comparación describe azules de acción/navegación, verde de ubicación, tipografía actual incluida la declaración local Arial, espaciado dimensional particular, bordes/radios/sombras locales e iconos/símbolos existentes. Declara la limitación de que el inventario no establece un único valor efectivo de color, espaciado o sombra para toda la UI.
- Se avisa explícitamente que las muestras son ilustrativas y no representan nuevos estados del producto. No se añaden controles ni interacciones al catálogo.

## Verificación verde

- `node --test tests/design-system/*.test.mjs`: código 0; 33 tests, 33 pass, 0 fail/cancelled/skipped/todo (454.461197 ms).
- Build exacto `cmd.exe /c "cd /d C:\\GIT\\github\\rancho_tools_plugin\\raweb && npm run build"`: código 0; Rollup generó `public/build/bundle.js` en 12 s.
- Servidor: el puerto 52948 no escuchaba; lancé únicamente `./node_modules/.bin/sirv public --host 127.0.0.1 --port 52948 --single`, PID 281549. Se detuvo con SIGTERM tras la verificación. No se iniciaron raapi ni GeoServer.
- Chrome carga directamente `/?catalog=design-system`: título «Catálogo del design system — RAWEB»; inventario, fundaciones y comparación visibles; sin App, navegación ni mapa montados.
- Ambos temas se verificaron cambiando el atributo de tema usado por la hoja compartida. Claro: fondo `#f8f9fa`, texto `#1f2937`, primario `#2563eb`, ubicación `#047857` y muestra renderizada `rgb(37, 99, 235)`. Oscuro: fondo `#111827`, texto `#f9fafb`, primario `#93c5fd`, ubicación `#6ee7b7` y muestra renderizada `rgb(147, 197, 253)`. Las superficies de tarjetas computaron blanco en Claro y `rgb(31, 41, 55)` en Oscuro.
- Responsive: 360×800, catálogo de 336 px dentro del viewport de 360 px y ancho del documento igual al viewport en ambos temas; sin desbordamiento horizontal. 1366×768, ancho del catálogo 960 px y documento sin desbordamiento horizontal. Las tres regiones (inventario, fundaciones, identidad) se mantienen presentes.
- Solicitudes de la carga final: seis GET locales (documento, CSS, JS, favicon); cero rutas `/api`, `/buscar_direccion` o `/ows`. No hubo POST/PUT/DELETE. Consola final sin errores; warning existente de `apple-mobile-web-app-capable` obsoleto. Las solicitudes rechazadas de la referencia roja ocurrieron cuando los bundles no estaban disponibles y no forman parte de la carga verde.
- Límite: el catálogo no agrega selector de tema; la comprobación Claro/Oscuro aplicó el atributo que consume el CSS para verificar el render de cada tema, sin añadir una interacción fuera del alcance de T33.

## Estado

**T33 completada `[x]`.** Se ven los valores, propósitos y muestras de las fundaciones junto con la comparación documentada en ambos temas, con contenido ilustrativo y sin datos reales. T30 permanece `[ ]` por el pinch real diferido; T50 continúa gated por T30. T34 no iniciada.
