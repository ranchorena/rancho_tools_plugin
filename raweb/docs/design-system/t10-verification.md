# T10 — Verificador de contraste opaco de la paleta

Fecha: 2026-10-06. RF-13, RF-23; RNF-2. Tarea de lógica, dependiente de T9.

> Hecho cuando: tests 21:1/1:1/umbrales y pares opacos de ambas paletas pasan; listado deja explícitos los pares que necesitan medición renderizada.

## Método y archivos

- Raíz Git y rama comprobadas: `/mnt/c/GIT/github/rancho_tools_plugin`, `master`; status y cambios previos revisados y preservados.
- [Soporte de contraste](../../tests/design-system/support/contrast.mjs): `contrastRatio(foreground, background)` convierte hex sRGB opaco a luminancia relativa y calcula `(mayor + 0,05)/(menor + 0,05)`, sin redondear. Admite #rgb/#rrggbb; rechaza alfa y otros formatos para no confundir composición con contraste opaco.
- [Tests](../../tests/design-system/contrast.test.mjs): negro/blanco 21:1, igualdad 1:1, simetría, formatos inválidos y valores a ambos lados de 4,5 y 3. `#777777`/blanco da 4,478089453577214 y falla 4,5 aunque redondeado parezca 4,5; `#959595`/blanco falla 3 aunque redondeado parezca 3.
- Los tests extraen las 28 variables hex de cada bloque explícito de tema de [la hoja real](../../public/design-system.css), sin copiar paletas. El inventario de pares y umbrales está declarado en el test. Son comprobaciones numéricas de datos CSS, no tests de strings que pretendan acreditar UI.
- Referencias de render anteriores: [T4](t4-verification.md) y [T9](t9-verification.md), consultadas para delimitar alcance; no se atribuyen sus ejecuciones a T10.

## Rojo → verde y verificaciones

- Primero se escribió el test. `node --test tests/design-system/*.test.mjs` dio **código 1**, tests19/suites0/pass18/fail1/cancelled0/skipped0/todo0, 247.119596 ms: módulo `support/contrast.mjs` ausente. Rojo esperado antes de implementar.
- Después se implementó el soporte. `node --test` **exacto final**, desde raweb en WSL/Node v24.19.0: **código 0**, tests **23**, suites **0**, pass **23**, fail **0**, cancelled **0**, skipped **0**, todo **0**, duration_ms **372.090862**. Cinco tests nuevos; los 18 previos pasan. La salida diagnóstica conserva cada ratio sin redondear.
- `npm run build` desde raweb mediante PowerShell Windows con herramientas instaladas: **código 0**, `public/build/bundle.js` generado en **6.9 s**. Sin instalaciones ni cambios de permisos/configuración. Build WSL no repetido por dependencia Rollup Linux ausente ya documentada.
- Navegador: **no aplica a la lógica sin integración de T10**. No hay ejecución ni captura nueva, ni solicitudes REST/WFS. No se modificaron componentes, App ni la paleta; API/GeoServer/base no comprobados en T10.

## Pares opacos comprobados

**34 por tema, 68 en total:** 18 de texto ≥4,5 y 16 de controles/estados ≥3. Valores mostrados redondeados a cinco decimales; comparación siempre con ratio completo.

Nombres relativos a `--ds-`; normal/hover/active son las tres variables de fondo declaradas. El umbral de texto normal también supera el de texto grande (3), sin asumir tamaño/peso renderizado.

| Texto / fondo (umbral 4,5) | Claro | Oscuro |
| --- | ---: | ---: |
| text / surface | 14,67912 | 14,04666 |
| text / background | 13,92558 | 16,97539 |
| text-muted / surface | 7,55738 | 9,96199 |
| text-muted / background | 7,16943 | 12,03906 |
| on-primary / primary normal, hover, active | 5,16856 / 6,70162 / 8,72241 | 9,83750 / 12,48456 / 6,97749 |
| on-secondary / secondary normal, hover, active | 13,92558 / 12,37891 / 11,27293 | 10,30736 / 7,55738 / 4,83449 |
| on-location / location normal, hover, active | 5,48392 / 7,68368 / 9,71929 | 11,63822 / 13,83204 / 9,22778 |
| on-selected / selected | 7,14918 | 8,72241 |
| success / success-surface | 6,81165 | 6,48866 |
| warning / warning-surface | 6,15265 | 6,96247 |
| error / error-surface | 5,91460 | 6,92556 |
| on-disabled / disabled | 6,10406 | 6,99509 |

| Control/estado (umbral 3) | Claro / surface | Claro / background | Oscuro / surface | Oscuro / background |
| --- | ---: | ---: | ---: | ---: |
| border | 4,83449 | 4,58632 | 5,78182 | 6,98733 |
| focus | 6,70162 | 6,35760 | 8,14026 | 9,83750 |
| primary | 5,16856 | 4,90323 | 8,14026 | 9,83750 |
| primary-hover | 6,70162 | 6,35760 | 10,33063 | 12,48456 |
| primary-active | 8,72241 | 8,27466 | 5,77367 | 6,97749 |
| location | 5,48392 | 5,20241 | 9,63030 | 11,63822 |
| location-hover | 7,68368 | 7,28924 | 11,44562 | 13,83204 |
| location-active | 9,71929 | 9,22036 | 7,63573 | 9,22778 |

## Pares que necesitan medición renderizada

Este listado identifica límites pendientes, no excepciones al contraste aprobado:

| Par/ámbito | Medición pendiente y motivo |
| --- | --- |
| Texto/fondo de cabeceras, botones y estados con degradado | Medir todos los puntos relevantes del fondo efectivo; extremos opacos aislados no acreditan el degradado ni cascada local. |
| Texto, bordes y foco de paneles, información, controles flotantes y OpenLayers / OSM y satélite | Fondos variables, capas translúcidas y blur requieren composición y render real en ambos temas. |
| Texto/borde/foco / fondo efectivo de campos, botones, navegación, tablas, estadísticas y mensajes migrados | Verificar CSS computado, hover/active/selección/readonly/disabled/carga aplicables, tamaño/peso y adyacencias reales; los pares declarados no acreditan adopción ni todos los estados. |
| Marca e interior de checkbox/radio/select / fondo nativo efectivo | `accent-color` no determina por sí solo marca, superficie ni estados dibujados por el navegador. |
| Foco / superficies adyacentes particulares y estados seleccionados | El test solo usa surface/background; no certifica el anillo contra cualquier fondo, selección o superposición. |
| Sombras/elevación translúcidas / fondo compuesto | Los tokens contienen alfa; el soporte los excluye. Medir si identifican controles/estados necesarios, sin asumir que toda sombra tiene ese papel. |
| Alertas nativas y validación visual del navegador | **No aplica — control del navegador**, exclusión aprobada; funcionamiento se verifica por separado. |

Las mediciones completas de catálogo/experiencias corresponden a tareas posteriores del plan. T10 verifica su criterio numérico y el listado; no completa RF-13/RF-23/RNF-2 de la entrega ni certifica conformidad total. Sin bloqueos para el criterio de T10; límites de render e integración pendientes explícitos.
