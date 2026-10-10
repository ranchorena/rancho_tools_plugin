# Verificación T28 — Información del elemento seleccionado

Fecha: 2026-10-07. RF-4, RF-15, RF-16, RF-19.

## Alcance y referencia roja

Se inspeccionaron `src/App.svelte` (contenido condicional cliente/pedido, listener de clic exterior y estilos locales), `public/design-system.css` y `public/global.css`. La información existente contiene ID, nombre y dirección; añade calle/altura para cliente o cantidad/fecha para pedido y los campos no ausentes de teléfono, horario y observaciones. El tooltip usa `role="dialog"` y nombre accesible existentes. El cierre existente es clic exterior/sobre mapa; los clics y keydown internos paran propagación. No hay botón de cierre ni handler de selección cartográfica por teclado.

**Rojo observado en Chrome DevTools**, página 1 de `http://localhost:8080/`, tema Oscuro, viewport 360×800. Para no exponer datos de servicio, se añadió temporalmente al DOM un fixture de presentación con las clases scoped actuales y contenido sintético: “ID ficticio: 9001”, “Cliente Ficticio”, “CALLE FICTICIA 100” y observación larga repetida. `getComputedStyle` midió fondo `rgba(255,255,255,.95)`, texto del panel `rgb(51,51,51)` y texto de fila `rgb(73,80,87)`. El contenido ocupó 496 px de alto. En el viewport apaisado 800×360 excedía el área visible; antes de la corrección el overflow era `visible` y no había desplazamiento. El fixture no reproduce una selección real ni afirma comportamiento de servicio.

## Cambio mínimo

En el CSS local de `.feature-tooltip`, superficie, borde y texto adoptan `--ds-surface`, `--ds-border` y `--ds-text`; `.feature-tooltip-data` adopta `--ds-text`. El contenedor recibe `max-height: calc(100vh - 20px)` y `overflow-y: auto` para permitir acceso al contenido largo en ambas orientaciones. Se conserva el contenido/orden/condiciones de markup, dimensiones min/max de ancho, posicionamiento, prioridad visual, rol/nombre, cierre por clic exterior y propagación actual. No se agregaron botones, interacciones ni selección cartográfica por teclado.

## Verde de navegador (fixture de presentación)

En Chrome DevTools se insertó y retiró manualmente un elemento DOM temporal usando las clases de alcance del CSS compilado y solo datos ficticios. Se cambió el tema con el selector existente. No se llamó al handler del mapa ni se añadió una feature.

| Tema | Viewport | Superficie / texto medidos | Contenido y scroll |
| --- | --- | --- | --- |
| Claro | 360×800 | fondo `rgb(255,255,255)`; texto `rgb(31,41,55)` | conserva texto sintético; 496 px, cabe en el viewport, `overflow-y:auto` |
| Oscuro | 360×800 | fondo `rgb(31,41,55)`; texto `rgb(249,250,251)` | conserva texto sintético; 496 px, cabe en el viewport, `overflow-y:auto` |
| Claro | 800×360 | fondo `rgb(255,255,255)`; texto `rgb(31,41,55)` | caja limitada a 340 px; contenido 644 px; scroll 306 px |
| Oscuro | 800×360 | fondo `rgb(31,41,55)`; texto `rgb(249,250,251)` | caja limitada a 340 px; contenido 644 px; `scrollTop=100` alcanzado; rango 306 px |

Tras retirar el fixture se dirigieron eventos `keydown` Enter y Espacio al viewport del mapa: no apareció tooltip ni contenido seleccionado. Esta comprobación no sustituye una prueba física completa de teclado; documenta que no se añadió una ruta de selección por teclado.

## Límites, requests y consola

- No se seleccionaron features del servicio: el navegador ya tenía una solicitud WFS Pedidos GET de lectura y mosaicos OSM GET cargados. No se transcriben respuesta, URL con parámetros ni atributos, y no se usaron como fixture/evidencia. No hubo POST/PUT/DELETE ni guardados.
- Consola después de recargar el bundle: sin errores; un warning previo deprecado de `apple-mobile-web-app-capable`. No se registró warning de canvas en esta ejecución.
- El disparador real de selección y el cierre por clic exterior **no se ejecutaron integradamente**: hacerlo con los datos WFS disponibles habría expuesto/representado registros reales, y no se preparó un mock WFS aislado. La conservación se constató por diff del handler/markup sin cambios, pero la observación no demuestra el flujo funcional. No se acredita el criterio completo ni se marca T28.

## Comprobaciones automatizadas

- Desde `raweb/`, comando exacto `node --test tests/design-system/*.test.mjs`: código **0**; 23 tests, 23 pass, 0 fail, 0 cancelled, 0 skipped, 0 todo; **245.531462 ms**.
- Build Windows PowerShell: `npm run build`, código **0**; Rollup generó `public/build/bundle.js` en **8.5 s**. Bundle recargado en la app.
- No se ejecutó un segundo runner/build después de documentar; los cambios posteriores a estos resultados fueron solo documentación.

## Estado

E-T28 acredita la referencia roja y la adaptación de superficie/overflow con fixture visual sintético en Claro/Oscuro. La verificación integrada aislada ejercitó disparador real, contenido/rol accesible, propagación interior, cierre exterior y ausencia de selección por Enter/Espacio usando un Pedido ficticio. La ruta Clientes no se solicitó en esta carga. **T28 completa; no iniciar T29.**

## Verificación integrada con WFS ficticio aislado (2026-10-07)

Se recargó `http://localhost:8080/` en Chrome DevTools instalando un `initScript` antes de ejecutar la aplicación. El script interceptó `XMLHttpRequest` únicamente para `GetFeature` WFS de `GeneralBelgrano:Clientes` y `GeneralBelgrano:Pedidos`, devolviendo una FeatureCollection fabricada con geometría Point EPSG:3857 en el centro inicial del mapa. No se inspeccionó ni reprodujo ninguna respuesta WFS real. Contadores permitieron constatar una solicitud mock de Pedidos, cero de Clientes y cero solicitudes WFS sin clasificar; el elemento visible fue ficticio (ID `990028`).

En viewport apaisado 800×360 se hizo clic en el marcador ficticio con secuencia pointer/mouse sobre el canvas OpenLayers. El tooltip real de Svelte apareció con `role="dialog"`, `aria-label="Información del elemento seleccionado"` y texto sintético `Cliente T28 Ficticio`, `CALLE FICTICIA 100`, `1`, `2026-10-07`, `000000000`, `12:00` y `OBS FICTICIA T28`. Clic dentro conservó el diálogo (propagación detenida); Enter y Espacio dirigidos al canvas no generaron selección. Un clic exterior real en el encabezado cerró el tooltip. Se reabrió con clic en el marcador en Oscuro; estilo computado: fondo `rgb(31, 41, 55)` y texto `rgb(249, 250, 251)`; clic exterior volvió a cerrarlo. No se hicieron POST/PUT/DELETE ni guardados.

Límite: la fuente Clientes no emitió solicitud en esta carga y su ruta no quedó verificada integradamente; el comprobante de disparador/cierre es del tipo Pedido. La consola mostró solo los warnings conocidos de meta deprecado y Canvas2D `willReadFrequently`, sin errores.
