# T54 — Pedidos uniforme con Buscar Dirección

2026-10-06. RF-11, RF-13, RF-16, RF-19, RF-21, RF-24; RNF-2/RNF-3. **T54 completada: evidencia visual original más cierre del hallazgo de Enter nativo autorizado y verificado abajo. Parada, sin T55.** Las secciones originales conservan el historial del pase visual y del hallazgo anterior.

## Rojo y cambio acotado

Leídos AGENTS, skill SDD, constitución, spec/plan/tareas, MEMORY, baseline T51, cierre T53 y fuentes Pedidos/Buscar Dirección. Git: raíz `rancho_tools_plugin`, rama `master`, cambios previos preservados; diff específico revisado. El diff global no pudo completarse por permisos en un XML previo de GeoServer; no se cambió ese archivo.

[Rojo real Oscuro](t54-red-dark.png): viewport 1034×605; modal blanco/texto `#333`, 1000×574.75 px; cabecera `#f8f9fa`, **53 px**, título `#1f2937`, sección `#f8f9fa`. Contradice el patrón y el tema.

Solo CSS y clase visual de `src/Pedidos.svelte`: superficie/texto semánticos en modal, cabecera, cuerpo heredado, secciones, cabecera de tabla, carga y estadísticas; títulos/separadores comunes; cierre normal/hover/active/foco. `margin:0` en cierre elimina el margen global que hacía superar 48 px. Filas normales hover usan texto de selección; regalos conservan fondo de advertencia y usan su texto semántico. Error conserva el par de error compartido. No hay campos ni acciones primarias en Pedidos: no se añaden para imitar Dirección.

Script, nueve columnas, cálculos/precio, mensajes, ramas, bindings, eventos, dimensiones declaradas, padding, breakpoints, scroll y animaciones permanecen intactos. La única corrección geométrica es la cabecera compacta aprobada. No se cambian App, lógica ni contratos.

## Navegador y matriz

Chrome Windows 154 con herramientas MCP DevTools, pestaña aislada `t54-fixtures` (page4), aplicación real `localhost:8080`. [JSON de estilos/cajas/ratios/flujos](t54-browser-evidence.json). La pestaña original page1 no se usa para capturar datos. Interceptores fetch/XHR instalados **antes de navegar**, REST ficticio y WFS vacío; ninguna consulta REST/WFS real ni escritura. Teselas públicas de mapa en el navegador.

| Viewport efectivo, ambos temas | Modal ancho×alto | Cabecera | Cuerpo clientWidth/scrollWidth; clientHeight/scrollHeight | Tabla clientWidth/scrollWidth |
| --- | --- | ---: | --- | --- |
| 360×800 | 352×784 | 41 | 344/344; 743/798 | 288/600 |
| 800×360 | 768×342 | 41 | 760/760; 301/693 | 660/800 |
| 768×1024 | 752×851.25 | 41 | 752/752; 810/810 | 684/800 |
| 1366×768 | 1000×678.375 | 41 | 1000/1000; 637/637 | 900/900 |
| 360×800, texto 200 % | 352×784 | 43.55 | 344/344; 740/1344 | 288/1004 |
| 1366×768, texto 200 % | 1000×729.59 | 47.39 | 992/992; 682/997 | 884/1336 |

Texto duplicado por elemento a partir de la fuente computada, sin cambiar viewport/DPR; estilos temporales restaurados después. Título móvil 14.4→28.8 px, escritorio 16→32 px. Sin recorte de título/cierre ni overflow horizontal del cuerpo; tabla mantiene su desplazamiento horizontal. Móvil: scroll horizontal 312 px normal y 716 px ampliado; scroll vertical del cuerpo 55/604 px permite llegar a la última estadística. Escritorio ampliado: tabla con scroll vertical (clientHeight390/scrollHeight459); última estadística alcanzable al desplazar el cuerpo. Cabeceras de una línea ≤48 px; no se necesita excepción de dos líneas.

Referencia Buscar Dirección abierta y medida en esta sesión: superficie/texto `#fff/#1f2937` y `#1f2937/#f9fafb`, cierre muted y acción primaria de los tokens vigentes. Pedidos comparte superficies/títulos/cierre y pares semánticos de estados con ese patrón; tamaños particulares conservados.

### Contraste efectivo Claro / Oscuro

Fondos transparentes compuestos con ancestros; fórmula WCAG sRGB, sin redondear antes de comparar. Outline sin trazo no cuenta como foco observado. Se esperan las transiciones antes de medir.

| Parte/estado | Claro | Oscuro | Umbral |
| --- | ---: | ---: | --- |
| Modal/cuerpo/cabecera/títulos/secciones/tabla/tarjetas | 14.68 | 14.05 | Texto ≥4.5 |
| Cierre normal, ayuda, labels y carga | 7.56 | 9.96 | Texto ≥4.5 |
| Cierre hover / active físico | 12.38 / 11.27 | 7.56 / 4.83 | Texto ≥4.5 |
| Fila normal hover | 7.15 | 8.72 | Texto ≥4.5 |
| Regalo normal/hover | 6.15 | 6.96 | Texto ≥4.5 |
| Error (rama de array vacío) | 5.91 | 6.93 | Texto ≥4.5 |
| Bordes de superficie | 4.83 | 5.78 | Trazo ≥3 |
| Menor borde de tabla contra regalo | 4.34 | 3.42 | Trazo ≥3 |
| Foco cierre/fila normal sobre superficie | 6.70 | 8.14 | Foco ≥3 |
| Foco fila normal hover | 5.49 | 4.84 | Foco ≥3 |
| Foco regalo normal/hover | 6.02 | 4.81 | Foco ≥3 |

Hover y active del cierre con puntero MCP real; transición desactivada únicamente en el cierre temporal de la pestaña para medir active durante pointerdown. Dinero conserva `--ds-success` sobre superficie; sus muestras pasan el umbral de texto en JSON. No se introduce un estado deshabilitado inexistente.

## Flujos, hallazgos y límites

- Dos pedidos ficticios conservan **3.5 total, 1.5 vendidas, $1750.00**, incluido el regalo en valor total tal como calcula el código actual. Datos ausentes muestran los mismos `N/A`; observación larga mantiene scroll/columnas.
- GET retenido verifica `🔄 Cargando pedidos...` en ambos temas. Array vacío `[]` verifica exactamente `No se encontraron clientes con pedidos.` en la rama de error y sin tabla/estadísticas. No se ejercita fallo HTTP: no se atribuye una prueba de transporte al mero render de esa rama.
- Objeto vacío `{message: ...}`: defecto previo registrado en T24/plan; `pedidos=results` llega a `forEach` con objeto. Se documenta por fuente, sin disparar una excepción artificial ni corregir lógica.
- Clic físico sobre fila en móvil cierra, devuelve foco a **Menú cerrado** y provoca un nuevo bbox WFS mock centrado en coordenadas ficticias `[-58.6,-35.7]`, con zoom cercano. Espacio móvil Claro y escritorio Oscuro; Enter móvil Oscuro: cierran y devuelven foco al disparador correcto. Tab/Mayús+Tab entre cierre y filas funcionan; cierre Enter desde menú móvil retorna a Menú. Fila sin coordenadas conserva diálogo; Espacio previene desplazamiento (scroll0).
- **Hallazgo que impide marcar T54:** Enter nativo en fila de escritorio reaparece con foco en Cerrar y un segundo GET de pedidos. Reproducido dos veces; la repetición usa clic MCP en el disparador visible → Tab → Enter, y registra **dos GET** desde la apertura. `keydown` Enter aislado sí cierra una vez, retorna a Pedidos y no hace GET adicional. Se diferencia de la prueba móvil, que pasa. Los manejadores de teclado/cierre/retorno no fueron modificados en T54; no se afirma una prueba roja anterior de esta interacción ni se corrige por inferencia. Requiere decisión de alcance antes de intervenir en eventos.
- El helper inicial eligió el disparador desktop oculto en móvil y no podía acreditar retorno al Menú. Esas muestras se conservan en JSON como diagnóstico (`close-click-mobile`); se corrigió el helper para elegir el disparador visible y se repitió con clic físico en Menú/Pedidos. Los errores de evaluación del helper no fueron errores de consola del producto. No cuentan como evidencia positiva las muestras `desktop-light-Enter` que registran `closed:false`.
- Consola DevTools sin warnings/errores; lista fetch/XHR de red vacía porque todas las respuestas se simularon. Registro local de mocks solo GET. API/GeoServer reales, persistencia y aceptación integral T47 no acreditadas.

## Evidencias y comprobaciones finales

- Escritorio [Claro](t54-light-desktop.png) / [Oscuro](t54-dark-desktop.png).
- Móvil [Claro](t54-light-mobile.png) / [Oscuro](t54-dark-mobile.png); [Oscuro texto200 %](t54-dark-mobile-text200.png).
- Carga [Claro](t54-light-loading.png) / [Oscuro](t54-dark-loading.png).
- Vacío/error [Claro](t54-light-empty.png) / [Oscuro](t54-dark-empty.png).
- `node --test` **exacto final**: código0; tests23/suites0/pass23/fail0/cancelled0/skipped0/todo0; **292.499694 ms**. Runner del plan con glob también pasa 23/23 (326.178437 ms).
- `npm run build` **Windows final**: código0; **7.5 s**, sin warnings; dependencias existentes, sin reinstalar. Build inicial de esta tarea0, 7.8 s. Código idéntico entre builds y mediciones.
- `git diff --check -- src/Pedidos.svelte`: código2 por numerosas líneas CRLF/espacios de cambios previos; no se normaliza el archivo ni se declara limpio.

**T54 permanece sin marcar:** evidencia visual completa y checks pasan, pero la verificación de Enter nativo escritorio presenta el hallazgo descrito. No se ejecuta T55 ni ninguna tarea siguiente.

## Cierre focal autorizado — Enter nativo (2026-10-06)

El usuario autorizó explícitamente esta corrección dentro de RF-19/RF-21 y la excepción de RF-16, tras diagnóstico del reviewer. Antes de editar, rojo real en Chrome DevTools sobre App: **clic Pedidos → Tab → Enter** produce `keydown` en TR sin cancelar, retorno de foco a Pedidos, `keypress`/clic nativos en ese botón y **dos GET**, diálogo reabierto con foco en Cerrar.

Cambio único de código en `handlePedidoRowKeydown`: después del rechazo por `shouldActivateRow`, `event.preventDefault()` para ambas teclas aceptadas, antes de `onPedidoClick`. El filtro de repeat/descendientes y el manejador de negocio son los mismos. No hay cambio de spec, cálculos ni CSS en este cierre.

[Evidencia adicional rojo/verde](t54-keyboard-evidence.json): Chrome Windows 154, App real `localhost:8080`, clic y teclado nativos MCP. Fixture GET con IDs ficticios 99001/99002, WFS vacío interceptado por fetch/XHR. Los eventos Svelte `zoomToLocation`/`close` se observaron envolviendo temporalmente la creación de CustomEvent en la pestaña, sin modificar producto ni ejecutar el manejador desde el test.

| Comprobación posterior | Resultado |
| --- | --- |
| Escritorio, Enter nativo (Sistema/claro y Oscuro) | Cierra; un GET de apertura, sin segundo GET; foco en Pedidos; keydown cancelado, sin keypress/clic residual. Primera ejecución además observa bbox WFS centrado en coordenadas ficticias. |
| Escritorio Oscuro clic / escritorio Espacio | Un `zoomToLocation` con `{-58.6,-35.7}`, un `close`, un GET de apertura; foco en Pedidos, diálogo cerrado. |
| Escritorio Oscuro Enter instrumentado | Un `zoomToLocation`, un `close`, un GET de apertura; misma secuencia nativa clic→Tab→Enter. |
| Móvil 360×800 Oscuro Enter / Claro Espacio / Claro clic | Un zoom, un cierre y un GET por apertura; foco AX «Menú», menú cerrado, sin reapertura. |
| Repeat Enter/Espacio y Enter/Espacio desde TD descendiente | Cuatro keydown DOM dirigidos: ninguno cancelado, ningún zoom/cierre; diálogo permanece abierto. Esta comprobación del filtro es sintética, distinta de las activaciones nativas anteriores. |

La matriz visual completa original (ambos temas, cuatro viewports, texto200 %, contraste, cabecera, scroll, estadísticas y carga/vacío) se reutiliza con atribución a su pase anterior: este cambio de una línea no toca estilos ni datos. Se satisfacen conjuntamente los criterios originales de T54 y la interacción que bloqueaba su marca.

Checks finales: `node --test` **exacto**, código0, tests23/suites0/pass23/fail0/cancelled0/skipped0/todo0, **340.006446 ms**. `npm run build` Windows PowerShell, código0, **7.5 s**, sin warnings de build ni reinstalación. DevTools: ningún error; un warning previo de meta `apple-mobile-web-app-capable` obsoleta. Red fetch/XHR final sin solicitudes reales durante los casos verdes. Un reload de preparación sin reinstalar init permitió GET WFS real; no se inspeccionaron cuerpos ni se hicieron escrituras. Se reinstaló init antes de todos los casos verdes; las comprobaciones no usan esos datos. Servicios reales y defecto de objeto vacío no quedan acreditados por los mocks.

**T54 marcada completa; hallazgo anterior resuelto. T55 sin iniciar.** Git mantiene los cambios previos; diff global bloqueado por permisos del XML previo de GeoServer.
