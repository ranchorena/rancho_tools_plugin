# Verificación T30 — Ampliación y cascada del shell

Fecha: 2026-10-07. RF-11, RF-14, RF-16, RF-19; RNF-3.

## Referencia previa

Antes de editar, Chrome DevTools página 1 en `http://localhost:8080/`, 800×360, modo móvil apaisado, tema oscuro:

- El meta viewport real era `width=device-width,initial-scale=1,user-scalable=no,maximum-scale=1,viewport-fit=cover`: contenía dos restricciones explícitas de ampliación.
- `getComputedStyle(document.body).fontFamily` y el título «RAWEB» devolvían `Arial, sans-serif`, debido a `:global(body, html)` en `App.svelte`, en vez de la familia de sistema declarada en `global.css`.
- `main` medía 360 px de alto/scrollHeight 360 px y declaraba `overflow:hidden`; navbar 68 px y mapa 292 px. Esa referencia confirma clipping potencial del shell, pero no se observó un elemento cortado en tamaño normal y no se registra un fallo visual de cabecera que no se haya visto.

## Cambio acotado

- `public/index.html`: se retiraron solo `user-scalable=no` y `maximum-scale=1`; se conservan `width`, `initial-scale` y `viewport-fit`.
- `src/App.svelte`: se eliminó la regla local que imponía Arial. `main` usa altura mínima de viewport, permite scroll vertical y mantiene oculto el desbordamiento horizontal; navbar/acciones pueden envolver y el mapa conserva una base flexible de `60vh`.
- No se cambiaron endpoints, operaciones, componentes de diálogo ni reglas de negocio.

## Método exacto de ampliación de texto

En la consola de Chrome se duplicó el tamaño computado en píxeles de cada elemento que contiene texto directo, aplicándolo como estilo inline `!important` al elemento, incluyendo los nodos de diálogo montados después de abrirlos. No se cambió viewport ni DPR. Se comprobó `getComputedStyle` (títulos de 32 px desde 16 px, botones de navegación de 28–32 px desde 14–16 px) y sus cajas/scroll. Este método es una ampliación de texto instrumentada para la verificación, no se presenta como equivalente a page zoom ni a pinch.

## Resultados de navegador

Chrome DevTools conectado a la aplicación recompilada. Ambos temas se aplicaron sobre el documento. Viewports de texto ampliado: móvil 360×800 (mobile/touch, DPR 1) y desktop 1366×768 (DPR 1).

| Comprobación | Claro | Oscuro |
| --- | --- | --- |
| Familia heredada | `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif` en body/producto | Misma familia heredada; sin regla Arial en App |
| Shell desktop ×2, 1366×768 | `main` scrollHeight 857/clientHeight 768; navbar 396 px; acciones y selector Tema distribuidos en filas, dentro del área desplazable | Mismo layout y disponibilidad; controles flotantes permanecen dentro de la región del mapa desplazable |
| Menú móvil ×2, 360×800 | Las cuatro acciones y selector Tema quedan dentro del menú: acciones entre y=68–444; selector y=484–526 | Igual geometría; las cuatro acciones y Tema siguen presentes y visibles |
| Dirección, cabecera ×2 | 88 px; título 32 px y cierre dentro de cabecera; Buscar visible | 79,2 px; título/cierre dentro de cabecera; Buscar visible |
| Buscar Cliente, cabecera ×2 | 48 px móvil; título y cierre contenidos; Buscar alcanzable tras scroll del cuerpo (scrollTop 133 de rango 133) | Igual; título/cierre contenidos y Buscar alcanzable por scroll |
| Agregar Cliente, cabecera ×2 | 80 px; título/cierre contenidos; Cancelar visible al desplazar contenido (scrollTop 1553 móvil, 830 desktop) | Igual; Cancelar permanece alcanzable |
| Pedidos, cabecera ×2 | 40,4 px móvil / 44,1 px desktop; título/cierre contenidos; contenido del cuerpo desplaza | Igual; título/cierre contenidos y cuerpo desplazable |

En los cuatro diálogos el título y el cierre quedaron dentro de la caja de cabecera; no se observó texto recortado en el render. Algunas mediciones redondeadas mostraron `scrollHeight` del título un píxel mayor que `clientHeight` por altura fraccionaria, sin que la caja del título/cierre excediera la cabecera. La altura natural crece; no se aplica un máximo/overflow local que recorte el texto ampliado. Dirección, Cliente y Alta probaron acciones de contenido; en Pedidos el cierre de cabecera es la acción correspondiente y tabla/cuerpo usa su scroll existente.

### Límite de zoom y scroll

- Tras retirar las restricciones, el meta viewport computado quedó `width=device-width,initial-scale=1,viewport-fit=cover`; el documento ya no pide al navegador limitar la ampliación.
- `visualViewport.scale` estuvo accesible y se registró en **1**. Se enviaron `Control++` y `Control+Shift+Equal` desde la herramienta DevTools; ninguno cambió escala, `innerWidth` ni DPR. No se pudo ejecutar un gesto pinch ni demostrar un cambio efectivo de page zoom. Por tanto, se confirma que el viewport permite la ampliación según su configuración, pero no se afirma que se haya observado una escala distinta de 1.
- El menú móvil cupo íntegro en 360×800. En desktop ampliado el shell creció a 857 px y tuvo scroll vertical real, conservando acceso a navegación/selector y mapa/controles.

## Solicitudes y consola

La recarga se hizo con un `initScript` anterior a la aplicación que intentó sustituir respuestas WFS GetFeature en el nivel de `XMLHttpRequest`. Una evaluación posterior instaló un mock de respuesta vacía para GET de pedidos REST, antes de abrir Pedidos. Sin embargo, la lista de red de Chrome mostró un GET WFS de Pedidos. No se inspeccionó su cuerpo ni atributos; debido a que el registro de red no permite asegurar que el request quedara bloqueado antes de salir, la interceptación no se considera evidencia suficiente de aislamiento. No se enviaron POST/PUT/DELETE ni se guardaron datos. La lista también mostró los recursos locales y teselas GET de OpenStreetMap. Consola: un warning preexistente por `apple-mobile-web-app-capable` obsoleto; ningún error.


## Reintento CDP 2026-10-07

- Chrome existente respondió en `http://127.0.0.1:9222/json/version` (Chrome 154.0.8037.95). Node v24.19.0 usó `fetch`/`WebSocket` nativos, encontró la página `http://localhost:8080/` vía `/json/list` y conectó al WebSocket CDP del target; no se instaló nada ni se abrió/configuró acceso adicional.
- Lectura inicial con `Runtime.evaluate`: `visualViewport.scale=1`, `innerWidth=360`, `innerHeight=800`, `devicePixelRatio=1`.
- Se envió `Input.synthesizePinchGesture` con `x=180`, `y=400`, `scaleFactor=1.5`, `relativeSpeed=800` y `gestureSourceType="touch"`. La orden CDP no devolvió respuesta en 5 s (`timeout Input.synthesizePinchGesture`); por ello no se obtuvo medición posterior al gesto ni se atribuye una escala efectiva. La lectura posterior a `Emulation.clearDeviceMetricsOverride` y recarga de restauración siguió en escala 1 y viewport 360×800/DPR 1.
- El script interrumpido no llegó a instalar ni verificar `Fetch.enable`; no se repitió una carga de inspección con interceptación fiable. No se examinó ningún cuerpo, respuesta ni registro de red del intento. Tampoco se enviaron operaciones de mutación deliberadas. No hay evidencia de cero solicitudes WFS salientes.
- En consecuencia, no se repitieron las comprobaciones visuales dependientes de una carga aislada ni se generaron nuevas capturas. El zoom real y el aislamiento de WFS continúan sin demostrar.

## Comprobaciones automatizadas

- Desde `raweb/`, `node --test tests/design-system/*.test.mjs`: código **0**; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; **248.555652 ms**.
- Build desde `raweb/`: `cmd.exe /c "cd /d C:\GIT\github\rancho_tools_plugin\raweb && npm run build"`; código **0**, Rollup generó `public/build/bundle.js` en **7.8 s**. No se instalaron dependencias ni se cambió configuración.
- `git diff --check` en los dos archivos de código señaló líneas existentes en CRLF de `public/index.html` como trailing whitespace; no se normalizó el archivo completo para preservar sus finales de línea.

## Estado

La configuración de viewport, tipografía heredada, scroll del shell, disponibilidad de acciones y crecimiento de las cabeceras fueron comprobados. **T30 permanece sin marcar**: `Input.synthesizePinchGesture` agotó el tiempo sin respuesta y tampoco hay evidencia de interceptación WFS efectiva. El intento se detiene aquí; T31 no iniciada.

## Hotfix visual de navegación desktop — 2026-10-07

### Hallazgo y corrección

- La referencia reportada muestra el grupo de navegación en columna. La causa quedó comprobada en la cascada: `public/global.css` asigna `width: 100%` a todos los `button`; `.nav-buttons` y `.navbar` permiten wrap. Por eso cada acción crecía al ancho de la línea y el grupo las distribuía verticalmente.
- Cambio mínimo en `src/App.svelte`: dentro de `@media (min-width: 769px)`, botones de `.nav-buttons` recuperan `width: auto` y `margin-bottom: 0`. Se mantiene el wrap de grupo/navbar para que el shell continúe adaptándose cuando el contenido ampliado no quepa; reglas del menú móvil no cambian. No cambia orden, etiquetas, navegación ni selector.

### Verificación visual de regresión

Chrome DevTools, aplicación local ya cargada; se inyectó en la página una regla CSS equivalente al cambio para validar el layout sin recargar ni ejecutar servicios. El bundle recompilado se comprobó por separado. Temas aplicados mediante el selector:

| Viewport | Tema | Resultado |
| --- | --- | --- |
| 1580×870 | Oscuro | Título y cuatro botones más selector en línea. Barra 68 px; grupo 743.6×44 px. Los botones miden 107–162 px de ancho y 44 px de alto; ninguno ocupa 100 %. |
| 1366×768 | Claro | Misma línea horizontal; barra 68 px; grupo 743.6×44 px. Botones entre x=606 y x=1203; selector x=1257–1350. No se impone una barra de 270 px. |
| 360×800 | Claro | Hamburguesa visible (44×48 px); al abrir se ven las cuatro acciones en el menú móvil, apiladas como corresponde, y el selector Tema debajo. El menú ocupa 360×394 px y los botones conservan su ancho completo móvil. |

Las mediciones móviles usan el DOM ya cargado; no se recargó la aplicación para evitar emitir nuevas consultas. La regla de wrap conserva el acceso/scroll de texto ×2 documentado en los resultados T30 anteriores (shell desktop 857/768 px de alto y menú móvil completo). Pinch efectivo sigue pendiente, no se infiere de esta corrección.

### Red, consola y automatización

- La vista ya cargada tenía una solicitud GET WFS de Pedidos en su registro de red. No se abrió ni inspeccionó su respuesta/cuerpo y no se interactuó con las capas ni los servicios; no se afirma aislamiento WFS. No se enviaron POST/PUT/DELETE.
- Consola: solo el warning previo de `apple-mobile-web-app-capable` obsoleto; sin errores.
- `node --test tests/design-system/*.test.mjs`: código 0, 26/26 pass, 0 fail/cancelled/skipped/todo (301.761757 ms).
- `cmd.exe /c "cd /d C:\GIT\github\rancho_tools_plugin\raweb && npm run build"`: código 0, bundle generado en 9.1 s, sin warnings.

La corrección elimina la regresión observada; **T30 sigue incompleta y sin marcar** porque pinch efectivo y aislamiento WFS aún no están demostrados. T31 permanece completa; T32 pendiente y bloqueada por T30.

## Intento CDP con aplicación y servicios detenidos — 2026-10-07

- Target correcto localizado en `http://localhost:52948/` mediante `http://127.0.0.1:9222/json/list`; Chrome 154 y Node v24 con `fetch`/`WebSocket` nativos. `Page.enable`, `Runtime.enable` y `Network.enable` completaron. Chrome respondió que `Input.enable` no existe; los comandos de entrada CDP se invocan directamente.
- Antes del gesto: `visualViewport.scale=1`, `innerWidth=1366`, `innerHeight=768`, DPR 1; meta viewport `width=device-width,initial-scale=1,viewport-fit=cover`.
- Emulación aplicada: 360×800, DPR 1, `mobile=true`, pantalla 360×800 y touch emulation activa con un punto. Antes del gesto: escala 1, `innerWidth=360`, `innerHeight=800`, DPR 1.
- Se intentó `Input.synthesizePinchGesture` en (180,400), factor 1.5, touch, velocidad relativa 800 y espera máxima de 30 s. CDP agotó el plazo sin respuesta. Se realizó el único reintento permitido con velocidad 600 y el mismo plazo; también agotó el plazo.
- Medición posterior: `visualViewport.scale=1`, `innerWidth=360`, `innerHeight=800`, DPR 1. No se demuestra ampliación por pinch. Se limpió la emulación de viewport, se desactivó touch emulation y la app volvió a escritorio: escala 1, `innerWidth=1580`, `innerHeight=825`, DPR 1, meta viewport intacto.
- Red observada únicamente como metadatos: `GET /geoserver/ows?...` (WFS Pedidos), carga fallida sin status HTTP. No se inspeccionaron headers, cuerpos, respuestas ni registros. No aparecieron respuestas WFS/REST HTTP 200; no se enviaron POST/PUT/DELETE ni se guardó nada.
- Hubo un contacto CDP inicial fallido porque `Input.enable` no es método válido; no llegó a registrar mediciones ni ejecutar gesto. No se repitieron runner ni build.

**Resultado:** el pinch efectivo continúa sin demostrarse; T30 permanece sin marcar y T32 sigue bloqueada. La carga fallida no constituye evidencia de aislamiento total de solicitudes.
