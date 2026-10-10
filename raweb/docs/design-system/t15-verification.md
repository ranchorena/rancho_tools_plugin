# T15 — Cabecera/foco de búsqueda de clientes

Fecha: 2026-10-06. **Pasa el criterio literal de T15.** RF-9, RF-14, RF-21; depende de T12 y T14.

## Implementación y referencia

- `BuscarCliente.svelte` compone `DialogHeader` con el ID accesible existente `modal-title` y aplica `dialogFocus` al diálogo. El cierre sigue despachando `close`; App conserva el retorno coordinado por T12.
- La presentación de cabecera usa superficie, texto y borde del tema explícito. Se retiró únicamente la media query cromática automática `prefers-color-scheme` que se oponía a la elección Claro/Oscuro. Las reglas de ancho, altura máxima, scroll y `modalSlideIn` se conservaron.
- Referencia roja real en Chrome Windows 154.0.8037.95, antes de editar: con tema Oscuro, cabecera `rgb(248, 249, 250)` y altura 68.7 px; al abrir, el foco permanecía en `body`. El marco medía 797 px, el cuerpo tenía `overflow-y:auto` y la animación de entrada activa.

## Verificación renderizada

Harness temporal externo mediante Node Windows 22.17.1 y CDP nativo. App real en `http://192.168.0.102:8080/`; teselas y solicitudes externas interceptadas. No se ejecutaron búsquedas, guardados ni escrituras REST.

| Comprobación | Resultado |
| --- | --- |
| Tema Claro/Oscuro | Cabecera usa superficie/texto semánticos; en oscuro fondo `rgb(31, 41, 55)` y texto `rgb(249, 250, 251)`. |
| Viewports | 360×800, 800×360, 768×1024 y 1366×768, en ambos temas. Cabecera entre 43.95 y 47.99 px, dentro del máximo RF-14 de 48 px. |
| Foco y cierre | Al abrir, foco en el botón «Cerrar» dentro del diálogo. Al cerrar, vuelve al disparador visible en escritorio; desde acción móvil vuelve a «Menú» y el menú permanece cerrado. |
| Marco y desplazamiento | Ancho máximo de 800 px y variantes responsive conservadas; cuerpo con `overflow-y:auto`. |
| Animación | La animación de entrada existente `modalSlideIn` permanece activa. |

## Capturas

- [Tema Claro, 1366×768](t15-light.png)
- [Tema Oscuro, 1366×768](t15-dark.png)

## Comprobaciones del proyecto

- `node --test tests/design-system/*.test.mjs`: código 0; 23 tests, 23 pass, 0 fail; 304.600072 ms.
- `npm run build` en Windows: código 0; Rollup creó `public/build/bundle.js` en 10.4 s, sin advertencias Svelte.
- `npm run build` en WSL no compila por dependencia opcional preexistente ausente `@rollup/rollup-linux-x64-gnu`; se verificó el build de Windows requerido. No se reinstalaron dependencias.
- T15 completada. T16 no iniciada.
