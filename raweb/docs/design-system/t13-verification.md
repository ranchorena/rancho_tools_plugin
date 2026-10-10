# T13 — Cabecera/foco del diálogo de dirección

Fecha: 2026-10-06. **Pasa el criterio literal de T13**. RF-9, RF-14, RF-21; T8 y T12 completas.

> T13. Cabecera/foco del diálogo de dirección.
> Hecho cuando: cabecera/foco y cierres anteriores funcionan; alerta de entrada vacía sigue nativa.

## Autoridad y cambios

- Leídos AGENTS raíz/raweb, skill SDD, constitución, spec/plan/tasks 001, MEMORY, coverage y evidencia T12. Raíz Git `/mnt/c/GIT/github/rancho_tools_plugin`, rama `master`; status/diff anteriores revisados y preservados.
- Único archivo de producto editado: `src/BuscarDireccionDialog.svelte`. Integra DialogHeader (título/ID/slot cierre) y dialogFocus sobre contenido. Primer control habilitado: Cerrar, conforme al adaptador aprobado; sin trap ni retorno en destroy.
- Reemplaza altura/padding/título locales de cabecera por la primitiva. Acota box-sizing, mínimo y margen del cierre para impedir expansión global; type button explícito. Marco, scroll, breakpoints, animación/reduced-motion, handlers, alertas y propagación conservados.

## Rojo primero

- Harness externo `/tmp/opencode/t13-browser.cjs`, transporte/aislamiento T11/T12, Chrome Windows 154.0.8037.95, Node Windows v22.17.1 y WebSocket/CDP nativo. App real y hojas/bundle del servidor existente; WFS vacío/cartografía neutra interceptados antes de navegar.
- **Rojo real antes de editar: código 1**, foco interior `false !== true`; cabecera desktop **69 px**. Sin tests de strings/render falso.
- Tres errores iniciales del harness (UNC, delimitador, nombre duplicado) corregidos antes del rojo; no evidencia de producto. Dos verdes fallaron por header53/61 px: mínimo/margen globales del cierre corregidos en componente, sin relajar umbral.

## Verde real — código 0, seis grupos

| Caso | Resultado ejecutado |
| --- | --- |
| Matriz normal ambos temas | 360×800 y 768×1024: **45 px**; 800×360 y 1366×768: **41 px**, incluido borde. Título real una línea, ≤48 px, sin recorte/superposición. |
| Entrada/teclado/retorno | Foco automático Cerrar, Tab input, Mayús+Tab Cerrar, Enter cierra y retorna al disparador desktop o Menú móvil cerrado. |
| Texto200 % | Duplicación de fuentes computadas de cabecera/descendientes en DOM real sin cambiar viewport; título **16→32 px**. Ambos temas: móvil360×800 **89 px**, desktop1366×768 **49 px**, título/cierre sin recorte/superposición. |
| Cierres | Escape input y backdrop enfocado, clic backdrop; clic interior no cierra. No se agrega Escape global desde controles que detenían propagación. |
| Vacío | Enter input y clic Buscar: **dos alertas nativas CDP**, tipo alert, mensaje exacto «Por favor, ingrese una dirección.». Se aceptan y el diálogo permanece. Apariencia/tema/contraste N/A — navegador. |
| Sin trap/AX | Mayús+Tab desde Cerrar sale sin cerrar; AX nombra diálogo «📍 Buscar Dirección» y botón «Cerrar». |
| Consola/red | Cero errores, solo GET; externos controlados, sin mutaciones ni datos reales. |

Artefactos temporales `/tmp/opencode/t13-red-result.json`, `t13-green-result.json`, `t13-mobile.png` (revisada) y harness. Navegador/perfil propios cerrados/eliminado; servidor existente conservado. Artefactos de sesión, no aceptación final.

## Checks y límites

- `npm run build` exacto en raweb/PowerShell Windows: **código0**, final **9.3s**. WSL no repetido por Rollup Linux ausente conocido; sin instalaciones/permisos/configuración nuevos.
- `node --test` **exacto final** raweb/WSL: **código0**, tests23/suites0/pass23/fail0/cancelled0/skipped0/todo0, **412.097782ms**.
- `git diff --check -- src/BuscarDireccionDialog.svelte`: **código2** por CRLF/espacios anteriores (diff previo ya era conversión completa LF→CRLF), preservados sin normalización masiva; no se presenta limpio.
- Título real normal una línea; dos líneas aisladas acreditadas T8, no nueva comprobación integrada sustituyendo el título real.
- Servicios API/GeoServer/base y POST válido pendientes. Ambos temas acreditan geometría/foco, no migración cromática/contraste completo: captura mantiene formulario claro bajo oscuro; campos/acciones corresponden a T14. Ampliación integral shell/formulario pendiente T30/T44.
- **Solo T13 completa; parada antes de T14**, spec aprobada sin aceptación de entrega.
