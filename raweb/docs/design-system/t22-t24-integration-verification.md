# Pase integrado T22–T24 — Pedidos

Fecha: 2026-10-06. RF-4–RF-6, RF-9, RF-11–RF-14, RF-16, RF-19, RF-21, RF-23.

## Resultado

**Bloqueado antes de iniciar la ejecución funcional.** No se declara pase integrado ni fallo funcional de `Pedidos.svelte`.

- La inspección de `chrome-devtools_list_pages` devolvió `Protocol error (Target.setDiscoverTargets): Target closed`.
- Los harness CDP existentes del checkout (`t11-browser.cjs`, `t14-browser.cjs`) ejercitan navegación y búsqueda de dirección; ninguno es un harness de Pedidos. El harness de T17 (`t17-browser.cjs`) no está presente en este checkout.
- Sin una sesión Chrome Windows/CDP operativa no se pudieron interceptar GET/WFS/teselas, inyectar exclusivamente R-PED, ni observar consola, foco, teclado o render. No se accedió a backend, GeoServer ni datos reales.

## Criterios no ejecutados

Quedan pendientes, en ambos temas y los viewports 360×800, 800×360, 768×1024 y 1366×768:

- T22: altura/title/cierre de `DialogHeader`, foco inicial dentro del diálogo, retorno al disparador y cierre con Escape; carga conservando distribución.
- T23: clic/Enter/Espacio con un único `zoomToLocation` y cierre; columnas/scroll horizontal, prevención del desplazamiento con Espacio y presentación de filas.
- T24: estados carga/error con tokens claro/oscuro y tarjetas para R-PED (3.5 total, 1.5 vendidas, $1750.00); dimensiones/disposición de tarjetas.
- Consola sin errores y respuesta vacía `{message: ...}` observada sin inferir ni aplicar corrección.

No se ejecutaron `node --test` ni `npm run build`: el pase funcional no pudo comenzar y se detuvo conforme al protocolo indicado. No se hicieron cambios de código, no se marcaron tareas nuevas y T25 sigue sin ejecutar.

## Para reanudar

Restablecer Chrome Windows/CDP o proporcionar un harness de Pedidos que permita interceptar REST/WFS/teselas antes de navegar. Repetir el pase completo con respuestas ficticias controladas y registrar mediciones/resultados antes de considerar el criterio integrado verificado.
