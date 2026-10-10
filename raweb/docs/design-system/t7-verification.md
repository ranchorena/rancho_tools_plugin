# T7 — Botón reutilizable nativo

Fecha: 2026-10-06. Resultado: **pasa el criterio literal de T7**. RF-4, RF-5, RF-19, RF-20.

> Hecho cuando: type, disabled, nombre accesible y eventos reenviados funcionan en ejemplo aislado; no submit accidental.

## Referencia roja previa a implementación

- El componente todavía no existía. Fixture real Svelte con botones nativos dentro de un formulario ficticio, sin type en la acción ordinaria; submit interceptado por el padre, sin navegación ni escrituras.
- Chrome Windows 154.0.8037.95: el botón resolvió `type=submit` y el clic provocó **1 envío**, esperado **0**. Aserción roja real, código **1**; cero errores de consola y ninguna REST/WFS.
- Resultado temporal: `/tmp/opencode/t7-red-result.json`. Esta referencia reproduce el riesgo nativo; no se atribuye el fallo a un flujo de producto existente.

## Implementación y método

- `src/design-system/Button.svelte`: elemento button nativo, props `variant='primary'`, `type='button'`, `disabled=false`, slot texto/icono, atributos nativos mediante `$$restProps`, clase adicional pública `class`; reenvía `on:click`, `on:keydown`, `on:focus` sin reemplazar el evento DOM.
- Clases `ds-button` y `ds-button--<variant>` preparan el contrato de presentación compartida. No se define una paleta ni se valida contraste en T7; fundaciones de T9 pendientes.
- Harness externo `/tmp/opencode/t7-build.mjs` y `t7-browser.cjs`, siguiendo [T4](t4-verification.md) y [T6](t6-verification.md). Entrada/fixture virtuales, sin archivos de entrada en src ni cambios de configuración. Variable temporal `T7_BUTTON=1` sustituye los botones de referencia por el componente real.
- PowerShell ejecuta Node Windows v22.17.1 sobre `\\wsl.localhost\Ubuntu\tmp\opencode\t7-build.mjs` y luego `t7-browser.cjs`; compila con Svelte/Rollup existentes. Chrome headless con perfil aislado, servidor loopback propio y CDP/WebSocket nativo; sin dependencias nuevas.
- DOM renderizado, árbol Accessibility de Chrome y pulsaciones `Input.dispatchKeyEvent`; no assertions de strings fuente ni falsos de render. Solo contenido ficticio. App no montada.

## Verde observado

Ejecución completa: **código 0**, siete comprobaciones pasan.

| Comprobación real | Resultado |
| --- | --- |
| Acción sin type explícito resuelve button, clic produce 0 envíos | Pasa |
| Tipos resueltos: button/button/button/submit/reset | Pasa |
| Slot de texto e icono; AX nombres «Acción ficticia» y «Cerrar ejemplo»; aria-label/title, clase adicional, data-atributo, name/value conservados | Pasa |
| Tab entra a la acción, omite disabled; Mayús+Tab retorna. Enter y Espacio activan exactamente una vez cada uno, sin envío. Eventos recibidos focus/keydown/click/keydown/click son Event nativos y conservan currentTarget y key | Pasa |
| Disabled bloquea clic/foco; actualización de prop habilita foco/Enter y vuelve a deshabilitar | Pasa |
| Submit explícito con Enter produce 1 envío interceptado; reset con Enter restaura defaultValue nativo sin nuevo envío | Pasa |
| Cero errores de consola; red solo página/bundle/favicon local, ninguna REST/WFS | Pasa |

- Durante la verificación se corrigieron dos expectativas del harness: el Tab de salida genera keydown en el botón anterior, por lo que se filtran los eventos de la instancia habilitada; reset restaura `defaultValue` DOM (vacío en este input compilado por Svelte), no su value inicial. El componente no cambió tras esos hallazgos.
- Captura real revisada `/tmp/opencode/t7-screenshot.png` (foco nativo en Restablecer); resultados `/tmp/opencode/t7-green-result.json`. Artefactos temporales, no evidencia permanente de aceptación final. Servidor/navegador propios cerrados y perfil temporal eliminado.

## Base y límites

- `npm run build` exacto desde raweb mediante PowerShell Windows: **código 0**, bundle generado en **11.6 s**. Button también compilado y montado en el bundle aislado.
- `node --test` **exacto**, final desde raweb en WSL: **código 0**, tests **18**, suites **0**, pass **18**, fail **0**, cancelled **0**, skipped **0**, todo **0**, duration_ms **324.330055**. Pruebas existentes de políticas; no acreditan UI. No se añadieron tests Node de strings.
- Build WSL no repetido: bloqueo conocido por `@rollup/rollup-linux-x64-gnu` ausente en dependencias compartidas Windows, documentado en T6. No se instalaron dependencias ni se cambiaron permisos/configuración.
- Solo T7. Sin integración App/diálogos, servicios ni validación de temas/contraste finales. La evidencia acredita el contrato aislado, no completa todos los RF ni la matriz de aceptación. T8 y tareas posteriores no ejecutadas.
