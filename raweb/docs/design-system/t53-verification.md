# T53 — Alta uniforme con Buscar Dirección

Fecha: 2026-10-06. RF-11, RF-13, RF-16, RF-24; RNF-2/RNF-3. **T53 completada; parada antes de T54.**

## Referencia roja y cambio

Inspección de Git antes de editar: raíz `rancho_tools_plugin`, rama `master`, numerosas modificaciones previas preservadas; diff específico de Alta/tareas/MEMORY revisado. Leídos constitución, spec/plan/tareas aprobados, memoria, [baseline T51](t51-baseline.md), [T52](t52-implementation.md) y [flujo T21](t21-verification.md).

[Rojo real en Oscuro](t53-red-dark.png), Chrome Windows 154, viewport inicial efectivo 1034×605: marco blanco y texto `#333`; cabecera degradada violeta; selección de mapa degradada verde; secciones/etiquetas `#374151`, coordenadas `#64748b` sobre `#f8fafc`, footer `#f8fafc`. Marco 600×544.5, cabecera 44 px, ubicación 528×130.61, selección 492×45 y footer 600×105. Contradicen RF-24 y el tema oscuro.

Solo presentación de `src/AgregarCliente.svelte`: marco/cabecera/cuerpo/ubicación/footer con superficie común, títulos/etiquetas/texto/bordes semánticos; cierre secundario, ubicación verde **sólida** compartida, primario/secundario y sus estados. Se eliminan ambos degradados y la opacidad del deshabilitado, sustituyéndola por los pares compartidos. Casillas nativas mantienen 13×13 px; contorno semántico de 1 px identifica el control en ambos temas, foco 3 px separado 2 px. Separador de cabecera mediante sombra interior de 1 px para conservar la caja de 44/48 px.

La comprobación al 200 % detectó Cancelar saliendo por el lado izquierdo; `min-width:0; overflow-wrap:anywhere` en acciones permite partir el texto sin cambiar distribución ni cajas a tamaño normal. No se modificaron script, validaciones, mensajes, bindings, eventos, payload, selección del mapa, dimensiones declaradas, scroll, padding, breakpoints, spinner ni animaciones. No se editó App ni otras experiencias.

## Navegador y medición

Pestaña aislada `t53-fixtures`, app real `http://localhost:8080`, herramientas MCP DevTools. [JSON de estilos/cajas/ratios/flujos](t53-browser-evidence.json) distingue `prior` (primera implementación/ajuste de texto) de `final` (contorno de casilla añadido). Superficies transparentes compuestas sobre ancestros; ratios WCAG sRGB sobre fondos efectivos. No se interpreta el `color` CSS de una casilla nativa como su glifo interno; el contorno medido sí es un trazo CSS real.

Referencia Buscar Dirección abierta en esta sesión: muestras `reference-direccion-settled`, tras esperar transiciones, confirman en Claro superficie/texto `#fff/#1f2937`, primario `#2563eb`; en Oscuro `#1f2937/#f9fafb`, primario `#93c5fd`. Alta usa los mismos tokens vigentes que T51/T52. Las muestras previas sin espera se conservan como diagnóstico, no como aceptación del color final. Outline/borde sin trazo o foco inactivo no constituyen fallos de control ni mediciones de foco visible.

### Matriz efectiva (ambos temas)

| Viewport CSS px | Marco | Cabecera | Cuerpo clientWidth/scrollWidth; clientHeight/scrollHeight | Resultado |
| --- | --- | ---: | --- | --- |
| 360×800 | 328×720 | 48 | 320/320; 565/1458 | Pasa |
| 800×360 | 600×324 | 44 | 592/592; 175/1051 | Pasa |
| 768×1024 | 600×921.59 | 48 | 592/592; 761/1082 | Pasa |
| 1366×768 | 600×691.19 | 44 | 592/592; 542/1051 | Pasa |
| 360×800, texto 200 % | 328×720 | 80 | 320/320; 466/2186 | Pasa, título y cierre completos |
| 1366×768, texto 200 % | 600×691.19 | 44 | 592/592; 527/1437 | Pasa |

Fuente computada duplicada **por elemento**, sin cambiar viewport/DPR, restaurada después: campo 14.4→28.8 px; título 16→32 px. La excepción de crecimiento de cabecera ampliada es RF-14. Se recorrieron todos los campos, título, cierre y acciones mediante scroll y cajas: listas finales de recortes vacías, sin overflow horizontal del cuerpo. No equivale a prueba de dispositivo táctil. Las matrices 800/768 se midieron antes de añadir exclusivamente el outline de casillas (sin efecto de caja); móvil/escritorio se repitieron con el último build y dieron las mismas dimensiones.

### Contraste renderizado (Claro / Oscuro)

| Par efectivo | Claro | Oscuro | Criterio |
| --- | ---: | ---: | --- |
| Superficies, títulos, secciones, etiquetas, campos | 14.68 | 14.05 | Texto ≥4.5 |
| Coordenadas/placeholder/cierre normal | 7.56 | 9.96 | Texto ≥4.5 |
| Guardar normal / hover | 5.17 / 6.70 | 9.84 / 12.48 | Texto ≥4.5 |
| Guardar active físico | 8.72 | 6.98 | Texto ≥4.5 |
| Seleccionar normal / hover / active físico | 5.48 / 7.68 / 9.72 | 11.64 / 13.83 / 9.23 | Texto ≥4.5 |
| Cancelar normal / hover / active | 13.93 / 12.38 / 11.27 | 10.31 / 7.56 / 4.83 | Texto ≥4.5 |
| Guardar deshabilitado / carga | 6.10 | 7.00 | Texto ≥4.5 |
| Error/validación | 5.91 | 6.93 | Texto ≥4.5 |
| Campos, footer, ubicación, contorno casillas | 4.83 | 5.78 | Trazo ≥3 |
| Foco campos/observación/casillas/acciones/cierre contra exterior | 6.70 | 8.14 | Foco ≥3 |

Hover de primario/ubicación/secundario medido con puntero real; active de primario/ubicación/secundario medido en `pointerdown` real en ambos temas. Para tomar el color final de active sin una muestra intermedia, se desactivó temporalmente la transición **solo en los botones de la pestaña**; no se cambia el movimiento del producto. El par de éxito compartido se respalda por `node --test` y tokens, sin presentar un éxito inline inexistente como render observado. Guardar/Cancelar carga conservan tokens y mensajes. El éxito inline se cierra inmediatamente por el manejador existente de App: se verifica el evento/cierre, no se fabrica una pantalla de éxito. La presentación semántica de éxito ya existente permanece intacta.

## Flujos y aislamiento

- Mock de REST en `fetch`, WFS vacío en **XHR** antes de navegación; todos los POST respondidos en la pestaña. Teselas públicas reales. Una recarga inicial sin repetir `initScript` perdió el interceptor y permitió GET WFS; no se inspeccionaron ni publicaron sus cuerpos. Se corrigió navegando/recompilando con interceptor explícito antes de cargar; las capturas finales tienen WFS vacío. Ninguna escritura real en ninguna fase.
- Clic **físico** MCP sobre el viewport OpenLayers, etiquetado temporalmente para localizarlo en el árbol AX: escritorio entrega `lat -35.768509 / lon -58.494428`; móvil entrega coordenadas del centro ficticio después del zoom simulado. Se oculta el formulario durante selección, reaparece el mismo diálogo, se habilita Guardar; no se roba foco ni se cierra por el clic. La etiqueta de fixture no existe en código de producto.
- Cancelar físico en escritorio/móvil cierra y devuelve foco al alta flotante; número de POST permanece igual al previo a cancelar. Tab desde Cerrar lleva a Nombre; Mayús+Tab retorna a Cerrar. Las funciones de foco no fueron modificadas.
- Validaciones de nombre y dirección conservan los textos exactos; no envían POST. Ausencia de coordenadas mantiene Guardar deshabilitado. Error HTTP mock `Error ficticio T53.` conserva formulario; carga retenida muestra `Guardando...`, spinner existente y ambos botones deshabilitados, en ambos temas.
- POST ficticio completo conserva nombre/dirección/calle/altura/teléfono, cantidad **2.5**, horario **15:30**, PAO **953**, observación, ambas casillas y coordenadas numéricas en latitud/longitud sin intercambiar ejes. Respuesta de éxito `{mensaje,cliente}` produce cierre y retorno de foco y nuevas consultas WFS mock, acreditando el flujo previo con fixtures. No acredita persistencia ni disponibilidad real de API/GeoServer (aceptación integral T46 pendiente).
- Consola final sin warnings/errores; lista DevTools fetch/XHR vacía porque las respuestas fueron simuladas, con solicitudes registradas en JSON local.

## Capturas y comprobaciones

- Móvil normal [Claro](t53-light-mobile.png) / [Oscuro](t53-dark-mobile.png).
- Pedido/acciones escritorio [Claro](t53-light-order.png) / [Oscuro](t53-dark-order.png).
- [Móvil Oscuro con fuente real 200 %](t53-dark-mobile-text200.png).
- `node --test` **exacto** desde raweb: código **0**, tests **23**, suites **0**, pass **23**, fail/cancelled/skipped/todo **0**; **489.02403 ms** (último código).
- `npm run build` en Windows PowerShell desde raweb: código **0**, bundle en **7.3 s**, sin warnings. Dependencias existentes; sin reinstalación ni herramientas nuevas.
- `git diff --check -- src/AgregarCliente.svelte`: código **2**, tres avisos de whitespace en líneas CRLF de contexto previo; se conserva el estilo mixto existente, no se declara limpio.

Solo T53 queda cerrada. T54 no ejecutada; no es aceptación final de RF-24 ni de la entrega.

## Seguimiento visual acotado — cierre circular

Fecha: 2026-10-07. Hotfix dentro de T53/RF-24; no cambia el alcance aprobado ni reabre otras tareas.

- **Rojo, DOM real Chrome página 1, `http://localhost:8080/`, Claro, sin Dark Reader:** `.close-button` medía 32×32 px con `border-radius: 4px`; aria-label `Cerrar` y foco computado `3px` con offset `2px`. Buscar Dirección usa `border-radius: 50%` y 28×28 px. El defecto reproducido fue únicamente la forma del cierre.
- **Cambio:** en `src/AgregarCliente.svelte`, solo `.close-button { border-radius: 50%; }`. Se preservan tamaño 32×32, texto, handler, nombre accesible, reglas de foco/hover y marco. No se cambiaron otros diálogos.
- **Verde comprobado en DOM:** probe temporal sobre el mismo botón de Alta aplicó el radio `50%` y lo retiró al acabar; no modificó la aplicación persistente ni recargó la página. Claro y Oscuro computaron `50%`, 32×32 px, nombre `Cerrar`, foco visible de 3 px/offset 2 px y foco efectivo. El azul de foco Claro fue `rgb(29, 78, 216)` y Oscuro `rgb(147, 197, 253)`. La página no se recargó para evitar nuevas solicitudes WFS/REST; el verde DOM es el probe de estilo, y la compilación posterior acredita el CSS fuente.
- **Acciones, mismo DOM Claro:** Cancelar habilitado, fondo `rgb(248, 249, 250)`, texto `rgb(31, 41, 55)`. Guardar Cliente deshabilitado, fondo `rgb(229, 231, 235)`, texto `rgb(75, 85, 99)`, porque `coordenadas` sigue nulo. Cancelar es secundaria y Guardar continúa deshabilitado hasta seleccionar ubicación; no se unificaron colores ni se alteró la semántica. No se verificó Guardar habilitado con ubicación.
- La medición verde se hizo en la sesión sin Dark Reader. El usuario confirmó que la discrepancia de color/tema en su ventana normal se debía a Dark Reader; no se atribuye ese mismatch a la aplicación.
- `node --test tests/design-system/*.test.mjs`: código 0, 26/26 pass, 0 fallos/cancelados/omitidos/todo (323.307697 ms). Build solicitado, sin instalar dependencias: `cmd.exe /c "cd /d C:\\GIT\\github\\rancho_tools_plugin\\raweb && npm run build"`; código 0, bundle generado en 9.5 s, sin warnings.

Este seguimiento cierra solo el defecto de radio de cierre reportado dentro de T53. No modifica el estado de T30 (incompleta) ni la dependencia/bloqueo de T32.
