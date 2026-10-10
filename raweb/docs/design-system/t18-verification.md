# T18 — Campos y acciones de edición de clientes

Fecha: 2026-10-06. **Pasa el criterio literal de T18.** RF-4–RF-7, RF-11–RF-13, RF-16 y RF-19; depende de T17.

## Implementación

- Campos ID/nombre de solo lectura y Docenas, N.º PaO, Horario y Observaciones usan `ds-field`; Tiene Pedido y Es Regalo usan `ds-choice`.
- Guardar Cambios usa `ds-button ds-button--primary`; `type="button"` evita cualquier submit accidental.
- Se preservan `bind:value`/`bind:checked`, IDs, etiquetas, dimensiones particulares, validación HH:MM:SS, payload y flujo de cierre. No se añadieron reglas de negocio.

## Referencia roja y verificación Chrome Windows

- Chrome Windows 154.0.8037.95, Node Windows 22.17.1 vía CDP nativo. App en `http://192.168.0.102:8080/`; búsqueda y cliente 9001 completamente ficticios.
- Rojo previo real en Oscuro: la aserción CDP observó los cuatro controles editables sin `ds-field`, las casillas sin `ds-choice` y Guardar sin la clase primaria compartida; falló como se esperaba antes de cambiar el markup. El resultado estructurado fue temporal y no se conserva.
- Verde: clases de los controles/acción verificadas en Claro y Oscuro en 360×800, 800×360, 768×1024 y 1366×768. [Captura real del formulario en Oscuro](t18-dark.png).
- El PUT observado fue `/api/clientes/actualizar/9001` con `{"docenas":2.5,"nro_pao":456,"tiene_pedido":false,"es_regalo":true,"observaciones":"Observación ficticia editada","horario":"15:45:00"}`. Así se verifican los nombres `docenas`/`observaciones` y los bindings de los campos/casillas.
- Se observó la notificación de éxito `Actualización ficticia correcta`, refresh WFS (`GET /geoserver/ows`), geocodificación `POST /buscar_direccion` con `{"direccion":"CALLE FICTICIA 100"}` y cierre del diálogo.
- Búsqueda, PUT, geocodificación, WFS y teselas fueron interceptados antes de servicios; cero mutaciones reales y cero errores de consola/CDP. No acredita backend, GeoServer ni T45.

## Comprobaciones

- `node --test` exacto desde `raweb/`: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; 278.000508 ms.
- `npm run build` en Windows PowerShell/Node: código 0; Rollup generó `public/build/bundle.js` en 8.1 s.
- T18 completada; detener antes de T19.
