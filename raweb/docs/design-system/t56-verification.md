# T56 — Igualación visual de cierres

Fecha: 2026-10-07. RF-19, RF-20, RF-24; RNF-2/RNF-3. **Estado: T56 completa y marcada; implementación CSS y verificación visual documentadas.**

## Referencia y rojo previo

Se contrastó con Buscar Dirección en Chrome sin Dark Reader. El baseline T51 computa 32×32 px en escritorio y 36×36 px hasta 768 px; círculo de radio 50 %, superficie transparente, texto `--ds-text-muted`, hover `--ds-secondary-hover`/`--ds-on-secondary` y foco de 3 px con offset 2 px. La altura renderizada de 32 px proviene de `min-height:32px`, no de la declaración `width/height:28px`.

Antes del cambio, en 1366×768 el cierre de Dirección medía 32×32, con tipografía renderizada de 16 px. Cliente y Pedidos medían 32×32 pero usaban 20 px; Alta medía 32×32 y usaba 24 px. En la medición previa a 360×800, Cliente seguía en 32×32 en vez de 36×36; Alta ya era 36×36, pero su glifo era 24 px. Los cierres de Pedidos tenían además una regla móvil de 24×24 en el CSS previo. Los cierres podían usar tamaños de glifo diferentes aunque sus cajas fueran circulares.

## Cambios realizados

En `BuscarCliente.svelte`, `AgregarCliente.svelte` y `Pedidos.svelte` se alinearon tipografía, caja base y estados con el baseline; se añadió el foco compartido que faltaba en Cliente. Los breakpoints hasta 768 px fijan 36×36 px. Se conservaron los nombres `aria-label="Cerrar"`, el contenido y los handlers de cierre. No se tocaron acciones Cancelar/Guardar. Los estados activos locales usan los mismos tokens de color que hover para coincidir con el estado hover que permanece aplicado mientras se pulsa el botón baseline.

## Medición verde parcial en Chrome

La matriz siguiente compara los cuatro cierres, en Claro y Oscuro. Todos los visibles midieron las dimensiones señaladas, radio `50%`, fondo transparente y tipografía de 16 px; posición y cabecera se midieron con `getBoundingClientRect`. En todos los casos el círculo quedó dentro del área de la cabecera y su `overflow` computado fue `visible`.

| Viewport | Dirección | Cliente/edición | Alta | Pedidos |
|---|---|---|---|---|
| 360×800 | 36×36; cabecera 45; y=4–40 | 36×36; cabecera 36; y=0–36 | 36×36; cabecera 36; y=0–36 | 36×36; cabecera 45; y=4–40 |
| 800×360 | 32×32; cabecera 41; y=4–36 | 32×32; cabecera 32; y=0–32 | 32×32; cabecera 32; y=0–32 | 32×32; cabecera 41; y=4–36 |
| 768×1024 | 36×36; cabecera 45; y=4–40 | 36×36; cabecera 36; y=0–36 | 36×36; cabecera 36; y=0–36 | 36×36; cabecera 45; y=4–40 |
| 1366×768 | 32×32; cabecera 41; y=4–36 | 32×32; cabecera 32; y=0–32 | 32×32; cabecera 32; y=0–32 | 32×32; cabecera 41; y=4–36 |

En Claro, texto de cierre `#4b5563`; hover fondo `#e9ecef` y texto blanco/según token de acción secundaria; anillo `#1d4ed8` 3 px/offset 2 px. En Oscuro, texto `#d1d5db`; hover fondo `#4b5563` y texto blanco; anillo `#93c5fd` 3 px/offset 2 px. El hover real se comparó en Chrome para Dirección y Cliente en Oscuro: ambos computaron fondo `rgb(75,85,99)` y texto blanco. El foco visible y el cierre por clic se comprobaron en los cuatro diálogos de la matriz. El foco claro/oscuro se midió con outline computado de 3 px y offset de 2 px. Los tokens corresponden a los pares aprobados en T10; no se calculó una nueva razón para el glifo del cierre.

La automatización observó desaparición del diálogo tras activar cada botón de cierre, con nombre accesible «Cerrar». Pedidos llegó a abrirse durante estas mediciones, pero la interceptación no resultó fiable: el registro de red mostró solicitudes WFS salientes y varios intentos de GET a `/api/clientes/pedidos` que terminaron en `ERR_CONNECTION_REFUSED`. No se inspeccionó ningún cuerpo ni registro; no hubo POST/PUT/DELETE ni guardados. Por la condición explícita de aislamiento de red, estas aperturas no validan el cierre integrado seguro de Pedidos ni permiten completar la matriz funcional. No continuar abriendo Pedidos bajo esta interceptación.

En la comprobación móvil previa de T56, el diálogo Pedidos se abrió a 360×800 desde una acción del menú móvil. Al cerrarlo, el foco volvió al botón «Menú» y el menú quedó cerrado. Conforme a RF-21, ese es el resultado esperado cuando el disparador desaparece al cerrarse el menú; no es un fallo ni un incumplimiento de foco. Esta observación no despeja el bloqueo de red: hubo un GET WFS con estado 200 de temporalidad no atribuida y no se inspeccionó ningún cuerpo, por lo que el aislamiento de GET/WFS de Pedidos no quedó probado.

## Comprobaciones automatizadas

- `node --test tests/design-system/*.test.mjs`: código 0; 26 tests, 26 pass, 0 fail/cancelled/skipped/todo (310.305565 ms), tras el último cambio de código.
- `cmd.exe /c "cd /d C:\GIT\github\rancho_tools_plugin\raweb && npm run build"`: código 0; Rollup creó `public/build/bundle.js` en 7.4 s, sin warnings.
- Chrome DevTools: sin Dark Reader. Los estilos geométricos, tamaños, colores normales y foco de las cuatro cabeceras pasaron en la matriz arriba descrita. Consola al cierre de la sesión registró rechazos de conexión de los GET mencionados y el aviso de cinco campos sin id/name; no se inspeccionaron cuerpos de red. WFS fue solicitado pese al initScript de mock; por ello la verificación de requests no satisface el criterio de red aislada.

## Bloqueo / decisión de estado

**Seguimiento seguro de interceptación, 2026-10-07:** antes de recargar se conectó por WebSocket CDP a los cuatro targets de la aplicación y se enviaron `Network.enable` y `Network.setBlockedURLs` con patrones para `*://*/*ows*` y `*://*/api/clientes/pedidos*`; CDP confirmó la aceptación en cada target. Tras recargar el target de trabajo, la lista de Network mostró una solicitud GET a `/geoserver/ows` con estado 200. De acuerdo con el criterio de parada, se detuvo inmediatamente la comprobación: no se abrió Pedidos, no se examinó ni guardó ningún cuerpo, encabezado o atributo, y no se intentaron escrituras. La solicitud 200 demuestra que la interceptación no aisló WFS de forma fiable; no se atribuye temporalidad ni resultado al GET de Pedidos en este intento. A continuación se limpió `Network.setBlockedURLs` (`urls: []`) en los cuatro targets; Chrome queda sin bloqueo de red y la app accesible online. No se inspeccionó tabla, mensaje ni contenido del diálogo.

**T56 permanece `[ ]` y no se completa.** La matriz visual anterior y sus comprobaciones automatizadas siguen documentadas, pero esta sesión no pudo demostrar aislamiento efectivo y por ello no verificó el cierre integrado seguro de Pedidos. No se repitieron runner/build porque esta sesión fue solo una verificación sin cambios de código. El retorno del foco a «Menú» en la comprobación móvil anterior es el resultado esperado por RF-21 y no constituye un bloqueo. T30, T31 y T32 conservan intacto su estado.

## Verificación integrada con servicios detenidos — 2026-10-07

El usuario confirmó que GeoServer/WFS y API/raapi estaban detenidos/no levantados. Se utilizó `http://localhost:52948/`, la aplicación correcta; `localhost:8080` corresponde a Keycloak. El bundle del frontend cargó desde el puerto 52948. Durante reload, la solicitud GeoServer `/geoserver/ows` respondió 502, consistente con el servicio detenido. Al abrir Pedidos, OPTIONS y GET a `http://localhost:5000/api/clientes/pedidos` terminaron en `ERR_CONNECTION_REFUSED`, consistente con raapi no levantada. Estos metadatos acreditan que los servicios de datos no entregaron registros en esta prueba. No se inspeccionaron headers, cuerpos, atributos ni contenido de tabla. Tiles públicos OSM respondieron 200/304. No hubo mutaciones.

### Pedidos: render, geometría, estados y cierre

Mediciones reales en Chrome, sin Dark Reader:

| Tema / viewport | Caja y forma | Colores normal / foco | Cabecera y clipping | Cierre y foco |
|---|---|---|---|---|
| Oscuro, escritorio 1366×768 | 32×32 px; `border-radius:50%`; fondo transparente | texto `rgb(209,213,219)`; foco `rgb(147,197,253)`, outline 3 px/offset 2 px | y=231.3–272.3, altura 41 px; círculo íntegro/contained | `aria-label="Cerrar"`; clic cerró y devolvió foco al disparador Pedidos |
| Claro, escritorio 1366×768 | 32×32 px; `border-radius:50%`; fondo transparente | texto `rgb(75,85,99)`; foco `rgb(29,78,216)`, outline 3 px/offset 2 px | altura 41 px; círculo íntegro/contained | clic cerró y devolvió foco al disparador Pedidos |
| Claro, móvil táctil 360×800 | 36×36 px; `border-radius:50%`; fondo transparente | texto `rgb(75,85,99)`; foco `rgb(29,78,216)`, outline 3 px/offset 2 px | cabecera y=8–53 (45 px); círculo y=12–48, íntegro | abierto desde acción Pedidos del menú móvil; cierre devolvió foco a Menú y mantuvo menú cerrado (RF-21) |
| Oscuro, móvil 360×800 | 36×36 px; `border-radius:50%`; fondo transparente | texto `rgb(209,213,219)`; foco `rgb(147,197,253)`, outline 3 px/offset 2 px | cabecera y=8–53; círculo completo/contained | cierre devolvió foco a Menú y mantuvo menú cerrado (RF-21) |

Dirección, Cliente/edición y Alta, sus etiquetas/nombres accesibles, estados visuales y cierres se habían verificado en la matriz browser previa documentada arriba. Con esta ejecución Pedidos queda cubierto en ambos temas, tamaños desktop/móvil y los dos orígenes de foco. Los cuatro cierres mantienen nombre, handlers y flujos de cierre; Cancelar y Guardar no forman parte de este cambio. La verificación Pedidos no dependió de leer filas/atributos y no se obtuvo ni transcribió contenido de tabla.

## Comprobaciones automatizadas y estado

- No se repitieron pruebas ni build: no hubo cambios de código desde `node --test tests/design-system/*.test.mjs` (código 0, 26/26 pass) y build Windows (código 0, 7.4 s).
- T56 cumple su alcance RF-24 de los botones de cierre con la evidencia visual previa de los otros tres diálogos y la verificación integrada segura de Pedidos. No se afirma que esta prueba valide carga/datos de pedidos ni flujos de servicio.
- **T56 completa y marcada.** T30 permanece incompleta; T31 completa; T32 bloqueada por T30+T31. No se iniciaron T30 ni T32.
