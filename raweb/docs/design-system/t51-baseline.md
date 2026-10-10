# T51 — Baseline renderizado de Buscar Dirección

Fecha de cierre: 2026-10-06. **Criterio de T51 satisfecho**. RF-13, RF-14, RF-24; RNF-2. La evidencia nueva de estilos fue aportada por el usuario desde Chrome en Windows; no se ejecutó una sesión nueva de navegador en este cierre.

## Evidencia Chrome Windows aportada ahora

El usuario aportó dos capturas de consola con `getComputedStyle`, identificadas como Claro y Oscuro, junto con capturas actuales de la interfaz. Los límites del diálogo aparecen colapsados en las capturas de interfaz, por lo que no se extraen de ellas tamaños/rectángulos numéricos.

| Parte | Claro — output actual del usuario | Oscuro — output actual del usuario |
| --- | --- | --- |
| Marco/cuerpo del diálogo | texto `rgb(31, 41, 55)`, fondo blanco, borde `rgb(31, 41, 55)` | texto `rgb(249, 250, 251)`, fondo `rgb(31, 41, 55)`, borde `rgb(249, 250, 251)` |
| Cabecera/título | fondos transparentes/heredados; texto `rgb(31, 41, 55)` | fondos transparentes/heredados; texto `rgb(249, 250, 251)` |
| Campo | fondo blanco, texto `rgb(31, 41, 55)`, borde `rgb(107, 114, 128)` | fondo `rgb(31, 41, 55)`, texto `rgb(249, 250, 251)`, borde `rgb(156, 163, 175)` |
| Acción primaria | texto blanco, fondo y borde `rgb(37, 99, 235)` | texto `rgb(249, 250, 251)`, fondo y borde `rgb(37, 99, 235)` |
| Footer | se reportó borde de footer en output actual; aplica el token de borde oscuro/claro | se reportó borde de footer en output actual; aplica el token de borde oscuro/claro |

Los fondos transparentes de cabecera/título heredan visualmente la superficie del diálogo; no se cuentan como una superficie opaca independiente. El output aportado corresponde a estilos computados actuales; no equivale a una ejecución automatizada de esta sesión.

## Contraste de los pares aportados

Ratios calculados a partir de los RGB anteriores mediante la fórmula WCAG sRGB para colores opacos; el cálculo no es una medición nueva del navegador. Se toma como fondo efectivo del texto de cabecera/título la superficie heredada del diálogo.

| Tema y par | Ratio | Criterio aplicable | Resultado |
| --- | ---: | --- | --- |
| Claro: texto de diálogo/campo/título `#1f2937` sobre `#ffffff` | 14.68:1 | texto normal ≥4,5:1 | Pasa |
| Claro: borde de campo `#6b7280` sobre `#ffffff` | 4.83:1 | control identificable ≥3:1 | Pasa |
| Claro: acción `#ffffff` sobre `#2563eb` | 5.17:1 | texto normal ≥4,5:1 | Pasa |
| Oscuro: texto de diálogo/campo/título `#f9fafb` sobre `#1f2937` | 14.05:1 | texto normal ≥4,5:1 | Pasa |
| Oscuro: borde de campo `#9ca3af` sobre `#1f2937` | 5.78:1 | control identificable ≥3:1 | Pasa |
| Oscuro: acción `#f9fafb` sobre `#2563eb` | 4.95:1 | texto normal ≥4,5:1 | Pasa |

Los valores actuales de texto, campo y acción respaldan los pares indicados. El borde del marco y el borde de footer no se recalculan aquí porque el output resumido no aporta explícitamente cada color/fondo efectivo de esos trazos; las combinaciones computadas de esas superficies se documentaron en la prueba T14.

## Evidencia T14 reutilizada

- La implementación cromática actual de `src/BuscarDireccionDialog.svelte` conserva los tokens semánticos que se comprobaron en T14 (`--ds-surface`, `--ds-text`, `--ds-border`, `--ds-primary`, `--ds-on-primary`) y las clases `ds-field`/`ds-button--primary`. El diff local frente a `HEAD` es la migración y los ajustes de estructura/foco registrados en T14; no se observa un cambio cromático posterior a esa verificación que entre en conflicto con los valores actuales aportados.
- [Verificación automatizada T14](t14-verification.md) registra Chrome Windows 154.0.8037.95, ambos temas y cuatro viewports (360×800, 800×360, 768×1024, 1366×768), capturas [Claro](t14-light.png) y [Oscuro](t14-dark.png), cabecera medida de 41–45 px, muestras de contraste de texto/placeholder/acción/cierre ≥4,5:1 y borde/foco ≥3:1. Esos tamaños y resultados pertenecen a la ejecución T14, no son mediciones numéricas de las capturas actuales del usuario.
- Se reutiliza T14 porque el patrón/estilos geométricos pertinentes permanecen sin cambios desde esa verificación; los datos de color actuales se atribuyen por separado al output reciente del usuario. Las capturas actuales no se presentan como capturas automatizadas ni como medición de rectángulos.

## Veredicto y límites

El criterio T51 queda satisfecho combinando la inspección actual de estilos computados aportada por el usuario con las capturas y medidas automatizadas T14, cuyo código de presentación no presenta cambios posteriores conflictivos. Los pares actuales de texto, campo y acción calculados cumplen RNF-2 en los dos temas. No se afirma una nueva medición de cabecera, rectángulos, estados de foco/hover ni todas las combinaciones de borde/footer a partir de las capturas colapsadas; esos aspectos medidos se atribuyen únicamente a T14. Esto cierra solo el baseline T51 y no constituye aceptación final de RF-24 ni inicia T52.
