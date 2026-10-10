# T4 — Verificación aislada del selector «Tema»

Fecha: 2026-10-06. Resultado: **pasa el criterio literal de T4**.

## Entorno y método

- Componente real: `src/design-system/ThemeSelector.svelte`, sin cambios durante esta verificación.
- Chrome instalado en Windows: `Chrome/154.0.8037.95`, modo headless; Node Windows v22.17.1.
- Harness temporal en `/tmp/opencode/`, compilado con Svelte/Rollup ya instalados. Entrada virtual, sin crear un entry en `src/` ni cambiar configuración. El bundle aislado se generó fuera de `public/build/`.
- Servidor HTTP temporal en loopback Windows; página con botón Antes, dos instancias del componente y botón Después. Un padre ficticio compartía `value` y registraba `event.detail`. No se montó App ni se usaron datos reales.
- Automatización mediante WebSocket nativo de Node y protocolo CDP de Chrome. `Input.dispatchKeyEvent` envió pulsaciones al navegador; las comprobaciones se hicieron sobre el DOM renderizado y los eventos del componente. No se inspeccionaron strings del código como prueba de UI.
- Captura real obtenida y revisada: `/tmp/opencode/t4-screenshot.png`; resultado estructurado: `/tmp/opencode/t4-result.json`. Son artefactos temporales de esta sesión, no enlaces permanentes de la matriz final. El servidor y el navegador propios se cerraron y su perfil temporal se eliminó.

## Resultados observados

| Comprobación | Evidencia de ejecución | Resultado |
| --- | --- | --- |
| Tres opciones en ambas instancias | `select.options`: Claro/light, Oscuro/dark, Sistema/system; cajas renderizadas con ancho positivo | Pasa |
| Etiqueta e IDs | `select.labels`: texto Tema y `htmlFor` correspondiente; IDs distintos `theme-desktop` y `theme-mobile` | Pasa |
| Valor inicial | Ambos selects muestran `system` | Pasa |
| Recorrido nativo | Tab: Antes → primer selector → segundo selector → Después. Mayús+Tab: primer selector → Antes y Después → segundo selector | Pasa |
| Selección y evento por teclado | En segundo selector: Home → light, Flecha abajo → dark, End → system; eventos exactamente `[light, dark, system]` | Pasa |
| Preferencia compartida | Tras cada evento, el padre actualizó props; preferencia del padre y valores de ambas instancias coincidieron | Pasa |
| Sin preferencia independiente del padre | Con actualización automática del padre desactivada y prop dark, Home emitió light mientras el padre y la otra instancia siguieron en dark. Posterior actualización externa a system llevó ambas instancias a system | Pasa |
| Consola y red | Cero excepciones/errores registrados; solicitudes únicamente a página, bundle y favicon del harness local; ninguna REST/WFS | Pasa |

## Comprobaciones de base

- `node --test` exacto, desde raweb en WSL, Node v24.19.0: salida 0; 9 tests, 9 pass, 0 fail/cancelled/skipped/todo; 341.4254 ms. Son pruebas de políticas/adaptador, no la evidencia UI anterior.
- `npm run build` exacto, desde raweb mediante PowerShell Windows: salida 0; Rollup generó `public/build/bundle.js` en 8.8 s. Se usó la configuración existente.
- El mismo `npm run build` desde WSL: salida 1 por ausencia de `@rollup/rollup-linux-x64-gnu`. No se reinstalaron dependencias. El build exitoso corresponde a Windows, no a WSL.

## Alcance cerrado

Solo T4. La ausencia del selector en la aplicación principal es esperable antes de T11. Esta evidencia no acredita integración, persistencia en navegador, temas/contraste finales, ubicación desktop/móvil ni matriz de aceptación completa. Las dos instancias del harness comprueban IDs y contrato compartido; no representan el layout integrado. T5 y T11 no se ejecutaron.
