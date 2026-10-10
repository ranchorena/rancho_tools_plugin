# T12 — Captura del disparador y retorno de foco en App

Fecha: 2026-10-06. **Pasa el criterio de coordinación de T12**. RF-9, RF-16, RF-21; dependencias T5, T6 y T11 completas.

> Hecho cuando: cierre final tras tick retorna a disparador visible o Menú cerrado; selección de punto no provoca retorno ni reapertura.

## Autoridad y cambio acotado

- [Tarea literal](../../specs/001-design-system/tasks.md), [plan](../../specs/001-design-system/plan.md) §3/§4 y [spec](../../specs/001-design-system/spec.md) RF-9/RF-16/RF-21. Raíz Git `/mnt/c/GIT/github/rancho_tools_plugin`, rama `master`; status/diff previo revisados, cambios anteriores preservados, incluidos T11 en App y los registros documentales.
- Único archivo de producto editado: `src/App.svelte`. Captura `event.currentTarget` y origen móvil antes de cerrar el menú en las cuatro aperturas; Pedidos transmite el evento y alta flotante comparte la captura. Referencia al botón Menú mediante `bind:this`.
- `closeDialogs` conserva su cierre/limpieza/actualización de mapa; consume el origen, espera `tick()`, mide presencia/visibilidad DOM y usa `chooseFocusReturn` existente. Evita retorno si se abrió otro diálogo mientras esperaba. No abre Menú ni escoge un destino alternativo para origen escritorio.
- Las rutas existentes `close`, búsqueda de dirección y `clienteAgregado` siguen compartiendo ese cierre final. Seleccionar ubicación y el `singleclick` cartográfico no pasan por él. No se incorporó foco interior a los diálogos: corresponde a T13/T15/T19/T22.

## Rojo primero y método

- Chrome Windows/CDP sobre **App real** servida en el endpoint de T11, con sus hojas y bundle. Antes de editar, abrir dirección, enfocar/clicar cierre: diálogo desmontado pero `document.activeElement !== trigger`. Assertion esperada `trigger:true`, observada `false`; **código 1**. Sin tests de strings ni render falso.
- Harness externo `/tmp/opencode/t12-browser.cjs`: reutiliza transporte CDP/aislamiento/limpieza de `t11-browser.cjs`, Node Windows **v22.17.1**, Chrome **154.0.8037.95**, WebSocket nativo. Intercepta antes de navegar todos los recursos externos: WFS vacío, cartografía neutra, GET de pedidos con un registro exclusivamente ficticio y búsqueda de dirección ficticia respondida localmente. No llegan solicitudes a servicios persistentes.
- Se corrigieron solo errores del harness (ruta UNC, delimitadores de reutilización, timeout CDP y cabeceras CORS de respuestas controladas). Primer intento verde excedió 120 s; se detuvieron exclusivamente procesos propios T12 y se repitió con timeout explícito/CORS. Ese intento no se contó como evidencia positiva.

## Verde real — código 0, seis grupos, cero errores

| Caso | Observación ejecutada |
| --- | --- |
| Cuatro diálogos por navegación | Cierre × retorna al disparador desktop o a Menú móvil; menú permanece cerrado y diálogo desmontado. |
| Alta flotante | Retorna al propio botón visible, también en móvil; no usa Menú por inferencia. |
| Matriz | Los cinco disparadores anteriores pasan en claro/oscuro a 1366×768, 800×360, 360×800 y 768×1024. Tema aplicado directamente solo en harness para aislar el retorno. |
| Momento del retorno | Listener `focusin` observa el retorno a disparador/Menú con `.modal-content` ya ausente; ninguna traza retorna antes del desmontaje. |
| Otras rutas | Escape en input de dirección y clic backdrop retornan; Enter con dirección ficticia cierra/retorna antes de la respuesta controlada; fila de pedido ficticio emite zoom/cierre y retorna. |
| Disparador desaparecido / Menú oculto | Abrir desde menú móvil, pasar a desktop y cerrar: no enfoca la acción desmontada ni Menú oculto; no inventa otro destino. |
| Selección de punto | Abrir alta móvil, pasar temporalmente a desktop, activar Seleccionar en Mapa: foco permanece en ese botón, cursor crosshair, formulario abierto y menú cerrado. Pointerdown/pointerup DOM dirigidos al viewport **real** de OpenLayers producen singleclick y actualizan el texto a `Lat/Lon` con seis decimales; cursor vuelve a normal. Cero eventos `focusin`, mismo foco/formulario, sin retorno ni reapertura. Volver a móvil y cerrar finalmente retorna a Menú: conserva el origen. |
| Sustitución interna | Abrir dirección y después clientes captura el último disparador; cierre final retorna a Buscar Cliente. |
| Consola/red | Cero excepciones/errores registrados. GET, OPTIONS y POST de búsqueda controlados; ninguna escritura persistente ni PUT/PATCH/DELETE. |

Artefactos temporales: `/tmp/opencode/t12-red-result.json`, `t12-green-result.json`, `t12-mobile-return.png` y harness. Captura revisada: móvil oscuro, foco visible en Menú y menú cerrado tras el cierre del alta. Son artefactos de sesión, no evidencias permanentes de aceptación final. Ejecuciones finales cerraron navegador propio y eliminaron su perfil; servidor Windows existente conservado.

## Comprobaciones obligatorias

- `npm run build` exacto desde raweb mediante PowerShell Windows: **código 0**, bundle generado en **7.7 s**. Sin instalación, permisos/configuración ni dependencias nuevas. Build WSL no repetido por Rollup Linux ausente ya documentado.
- `node --test` **exacto final**, raweb/WSL: **código 0**, tests **23**, suites **0**, pass **23**, fail **0**, cancelled **0**, skipped **0**, todo **0**, duration_ms **460.212781**. La lógica pura de T5 sigue cubierta; la nueva coordinación DOM se acredita por el rojo/verde real anterior.
- `git diff --check -- src/App.svelte`: código 0.

## Límites explícitos

- El overlay previo del alta permanece montado: los eventos de punto se dirigen al viewport en el harness para probar el manejador real y su coordinación de foco. **No acredita hit-testing/clic físico del usuario a través de ese overlay ni cumplimiento integral del alta con mapa**. Ese flujo y su acceso efectivo siguen pendientes de T21/T46; no se corrigió su disposición por inferencia en T12.
- Guardados de cliente/alta no se ejecutaron: sin mutaciones. Su suscripción al cierre compartido se conservó y revisó en fuente; no se afirma validación de persistencia, refresh ni eventos de éxito reales.
- API/GeoServer/base reales no verificados; respuestas controladas acreditan coordinación de App, no negocio/servicios. Foco interior, cabeceras, texto 200 %, contraste completo y aceptación final continúan pendientes de sus tareas.
- **Solo T12 completada. Parada antes de T13; spec sigue aprobada, sin aceptación de entrega.**
