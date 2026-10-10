# T19 — Cabecera y foco del alta

Fecha: 2026-10-06. **Pasa el criterio literal de T19.** RF-9, RF-14 y RF-21; depende de T8, T12 y T18.

## Implementación

- `AgregarCliente.svelte` usa `DialogHeader` con el ID `agregar-cliente-title` ya asociado al diálogo y el cierre dentro del slot aprobado.
- `dialogFocus` se aplica al contenido del diálogo; conserva el foco dentro al abrir y deja al padre coordinar el retorno al cerrar.
- Se mantienen marco, ancho, scroll, degradado, overlay, formulario, eventos y mapa. El padding del encabezado se ajusta a la primitiva compartida; no se cambia `App.svelte` ni la interacción de selección de ubicación.

## Referencia roja y verificación Chrome Windows

- Chrome Windows 154.0.8037.95 y Node Windows 22.17.1 mediante CDP nativo; App local en `http://192.168.0.102:8080/`. La referencia previa midió cabecera de 104 px a 360×800 y 112 px a 768×1024, superando el máximo aprobado de 48 px.
- Verde posterior: 360×800, 800×360, 768×1024 y 1366×768, en Claro y Oscuro. La caja de cabecera midió respectivamente 48, 44, 48 y 44 px. Capturas: [360×800 claro](t19-360-800-light.png), [oscuro](t19-360-800-dark.png); [800×360 claro](t19-800-360-light.png), [oscuro](t19-800-360-dark.png); [768×1024 claro](t19-768-1024-light.png), [oscuro](t19-768-1024-dark.png); [1366×768 claro](t19-1366-768-light.png), [oscuro](t19-1366-768-dark.png).
- `aria-labelledby="agregar-cliente-title"` conservado. Al abrir, el foco llega al botón de cierre dentro del diálogo. Enter cierra el diálogo y, tras el tick de App, devuelve foco al botón disparador visible en las ocho combinaciones.
- El contenedor `.map-container` permanece en el DOM y no se cambió el overlay. La selección física de ubicación y el alta no se ejecutaron en T19; quedan para las tareas que cubren el flujo de alta.
- WFS y teselas interceptados antes de servicios; requests observadas solo GET, sin escrituras, sin errores de consola/CDP. No acredita servicios reales ni T21/T46.

## Comprobaciones

- `node --test` exacto desde `raweb/`: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; 350.020974 ms.
- `npm run build` en Windows PowerShell/Node: código 0; builds posteriores al ajuste de altura completaron en 9.7 s (la primera compilación, antes del ajuste final, en 13.2 s).
- T19 completada; detener antes de T20.
