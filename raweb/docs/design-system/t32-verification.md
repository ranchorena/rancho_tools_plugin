# Verificación T32 — entrada aislada del catálogo

Fecha: 2026-10-07. Alcance: RF-10 y RF-22, únicamente T32.

## Referencia roja previa

- Chrome en la ruta normal `http://localhost:52948/`, viewport de 1366 CSS px de ancho (la altura de ventana era inferior a 768 px en esa observación).
- En la compilación previa al arreglo, el DOM contenía `.navbar` y `.nav-buttons`, pero `getComputedStyle(.navbar)` devolvía `display:block`, fondo transparente y no había ninguna regla de `App.svelte` en las hojas cargadas. El grupo `.nav-buttons` medía 1358 px y cada uno de sus cuatro botones también 1358 px; el margen inferior efectivo era 12 px. `public/global.css` aplicaba `button { width:100% }`.
- El código fuente de `App.svelte` sí declaraba `.navbar { display:flex; flex-wrap:wrap }` y, dentro de `@media (min-width:769px)`, `.nav-buttons button { width:auto; margin-bottom:0 }`. Por tanto, el viewport era de escritorio; el fallo era la ausencia del CSS scoped en el bundle normal, no la activación del breakpoint móvil.
- Esta regresión se introdujo al sustituir el import estático de App por `import('./App.svelte')`: la extracción de `rollup-plugin-css-only` junto con `inlineDynamicImports` no incluyó el CSS de esa dependencia dinámica en `bundle.css`.
- La observación roja anterior de la pestaña con query ya montada (líneas siguientes) se conserva como referencia del catálogo; no sustituye esta referencia del fallo de CSS en la ruta normal.
- Se cambió la URL de la pestaña ya cargada a `/?catalog=design-system` sin recargar para observar el comportamiento actual: seguían visibles el `main`/navegación de RAWEB y las acciones Buscar Dirección, Buscar Cliente, Agregar Cliente y Pedidos. No había un elemento identificativo de catálogo.
- La lista de metadatos de red disponible para esa carga normal contenía 82 solicitudes; una solicitud WFS a `/geoserver/ows` terminó 502 y otra falló con `ERR_CONNECTION_REFUSED`. Se observaron solo URL, método y estado; no se leyeron cuerpos ni información personal. No se observaron llamadas `/api` ni `/buscar_direccion` en esa lista. La carga de OSM fue externa a los servicios de datos.
- La navegación directa/recarga solicitada a `http://localhost:52948/?catalog=design-system` no pudo completarse: `net::ERR_CONNECTION_REFUSED`. Por tanto, la referencia roja es una observación real de la app ya montada con la query visible, no una carga inicial directa del modo.

## Implementación

- `src/main.js` consulta `catalog=design-system`; importa estáticamente los módulos App y Catalog para que Rollup extraiga también el CSS scoped de App. En modo catálogo solo instancia `Catalog.svelte`; no construye App, no ejecuta su `onMount`, no crea el mapa OpenLayers y no inicia REST/WFS. En la ruta normal instancia App de forma síncrona.
- `Catalog.svelte` presenta el inventario T31 y sus conteos, con estilos compartidos y una estructura responsive. No agrega ejemplos ni estados de producto.
- `rollup.config.js` conserva la salida IIFE de un solo bundle con CSS extraído; no fue necesario modificar su configuración.

## Comprobaciones

- `node --test tests/design-system/*.test.mjs`: código 0; 33 tests, 33 pass, 0 fail/cancelled/skipped/todo (361.429321 ms).
- Build exacto `cmd.exe /c "cd /d C:\GIT\github\rancho_tools_plugin\raweb && npm run build"`: código 0; bundle generado en 8.1 s.
- El servidor del puerto 52948 no estaba disponible al empezar; comprobé el puerto libre y lancé solo `sirv` directo sobre `public/` en 52948. No usé 8080 ni inicié GeoServer/raapi. Un primer arranque mediante el script npm heredó `--port 8080` y eligió un puerto alternativo; detuve únicamente ese proceso y usé el binario `sirv` con el puerto exacto.
- Chrome verificó la ruta normal en 1366×768: `bundle.css` carga las reglas scoped de App; `.navbar` computa fondo oscuro `rgb(17,24,39)`, `display:flex`, dirección row y wrap; altura 68 px. `.nav-buttons` mide 743.56×44 px. Los cuatro botones computan `width:auto`, anchos 162.20/146.69/156.22/107.16 px y altura 44 px; el selector Tema está en la misma fila. El botón hamburguesa está oculto. El mapa OpenLayers se monta. Esto resuelve la referencia roja de fila completa de 1358 px.
- Chrome verificó móvil táctil 360×800: el botón Menú mide 44×48 px y se muestra; navegación desktop oculta. Tras abrir Menú se ven las cuatro acciones apiladas, cada una de 336×51 px, y el selector Tema debajo; el panel ocupa 360×394 px.
- Catálogo cargado directamente y recargado con caché ignorada en `http://localhost:52948/?catalog=design-system`: «Catálogo de componentes», «Inventario» y conteos 12/41/48/3 visibles. No hay `.navbar`, viewport de OpenLayers ni shell de App en el DOM. Cada carga hizo 6 GET locales de documento/estilos/bundle/favicon y cero requests a `/api`, `/buscar_direccion` u `/ows`; en catálogo no aparecen errores de consola.
- Ruta normal tras rebuild: cinco assets locales, un GET WFS inicial a `localhost:8086/geoserver/ows` falló `ERR_CONNECTION_REFUSED` y solicitudes de teselas OSM. No se inspeccionó ningún cuerpo o datos y no se hicieron POST/PUT/DELETE ni guardados. No hubo solicitudes `/api` ni `/buscar_direccion`. Consola: error del recurso WFS rechazado y warning existente de meta obsoleta; ningún otro error observado.
- El servidor `sirv` directo que lancé en 52948 se detuvo con SIGTERM tras la verificación (PID 276500). El proceso `sirv` iniciado accidentalmente en puerto alternativo también se detuvo; no se tocó el servidor que ya estaba en 8080.

## Estado

**T32 completada `[x]` y verificada de nuevo tras reparar su regresión de CSS.** Catálogo directo/recarga aislado sin App montada, mapa/OpenLayers en DOM ni REST/WFS; ruta normal carga las reglas CSS de App y presenta cuatro acciones y Tema en fila a 1366×768, y conserva Menú móvil a 360×800. Runner/build ejecutados en esta corrección y pasan. GeoServer/raapi siguen detenidos; no se inspeccionaron cuerpos de respuestas ni se realizaron mutaciones. T30 permanece `[ ]` por el pinch efectivo diferido al usuario; T50 continúa bloqueada por T30. T33 no iniciada.
