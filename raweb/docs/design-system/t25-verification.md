# Verificación T25 — Presentación de notificación global

Fecha: 2026-10-06. RF-6, RF-8, RF-11, RF-13, RF-16.

## Cambio realizado

- `GlobalNotification.svelte` consume los tokens compartidos de superficie, texto, borde y sombra.
- Las variantes existentes `success` y `error` usan los pares semánticos `--ds-success-surface`/`--ds-success` y `--ds-error-surface`/`--ds-error`.
- Los demás valores de `type` mantienen la presentación genérica, ahora adaptada al tema.
- No cambian el markup, el mensaje, las clases condicionales, las props, el temporizador, la sustitución del timer anterior, la limpieza al destruir ni el comportamiento existente de cierre. No se agrega botón ni política nueva.

## Comprobaciones

- Se inspeccionó el diff previo del componente antes de modificarlo. Ya constaba modificado y con finales CRLF; se preservó su lógica y formato existente.
- No se creó un test de strings ni una simulación de render para una tarea UI.
- `node --test tests/design-system/*.test.mjs`, desde `raweb/`: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; 376.157002 ms. Es el runner existente y no prueba el render del componente.
- `npm run build`, en Windows PowerShell desde `raweb/`: código 0; bundle generado en 8.3 s.
- Verificación visual bloqueada: `chrome-devtools_list_pages` devolvió `Protocol error (Target.setDiscoverTargets): Target closed`. Los harness disponibles (`t11-browser.cjs`, `t14-browser.cjs`) no cubren esta notificación. No se observaron render, consola, temporización ni requests en navegador.

## Estado de evidencia

Implementación, runner y build pasan. La comprobación visual integrada de success/error/otros tipos en claro y oscuro, además de duración y sustitución observables, queda pendiente; no se marca como verificada. No se accedió a API, GeoServer ni datos reales.
