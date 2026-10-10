# T17 — Tabla de resultados y activación por teclado

Fecha: 2026-10-06. **Pasa el criterio literal de T17.** RF-4, RF-5 y RF-19; depende de T5 y T16.

## Implementación

- Las filas de resultados de clientes reciben `tabindex="0"` y su manejador de teclado delega en `shouldActivateRow` de T5.
- Enter y Espacio activan `selectClient` una vez; Espacio previene el desplazamiento predeterminado. El manejador solo acepta eventos cuyo `target` es la propia fila, por lo que no intercepta controles descendientes.
- Se conservan el manejador de clic, las cinco columnas, el ancho mínimo existente de 600 px y `overflow: auto` del contenedor.

## Referencia roja y verificación Chrome Windows

- Rojo real previo: fila sin `tabindex` (`null`, esperado `0`), con cinco celdas y `min-width: 600px`.
- Verde: clic, Enter y Espacio seleccionan el cliente ficticio una sola vez; Espacio no desplaza la página; Enter en un botón descendiente no selecciona la fila.
- Medición de overflow: tabla de 600 px dentro de contenedor de 258 px (`scrollWidth: 600`, `clientWidth: 258`, `overflow-x: auto`), cinco celdas conservadas.
- Chrome Windows 154.0.8037.95 vía CDP/Node Windows 22.17.1. Búsqueda controlada `POST /api/clientes/buscar` con `{"criterio":"nombre","nombre_cliente":"FICTICIO"}` y respuesta de cliente sintética; WFS/teselas interceptados. Sin PUT/POST de mutación, errores de consola ni excepciones.

## Comprobaciones

- `npm run build` en Windows: código 0; Rollup completó en 9.4 s.
- `node --test` exacto desde `raweb/`: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; 329.908125 ms.
- Harness temporal usado: `t17-browser.cjs`; se elimina al terminar la verificación.

T17 completada; T18 no iniciada.
