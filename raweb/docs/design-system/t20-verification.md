# T20 — Campos básicos de alta

Fecha: 2026-10-06. **T20 completada.** RF-4, RF-5, RF-7, RF-11 y RF-13; depende de T19.

## Cambio acotado

- En `AgregarCliente.svelte`, los campos nombre, dirección, calle, altura y teléfono reciben `ds-field`.
- Se mantienen tipos `text`, `text`, `text`, `number` y `tel`; IDs y asociación `label for`; bindings `formData.nombre`, `direccion`, `calle`, `altura` y `telefono`; `required` de nombre/dirección y `maxlength` existentes. No se cambian las validaciones JS ni el procesamiento/payload.
- Reglas locales de los inputs con `ds-field` aplican tokens compartidos de texto, superficie, borde y foco en ambos temas. Se conserva el padding, tamaño, transición y demás geometría local del campo.

## Verificación renderizada en Chrome Windows

- Harness temporal `t20-browser.cjs`, Node Windows 22.17.1 y Chrome Windows; conexión CDP nativa de Node, sin dependencias nuevas. La app real se abrió en `http://127.0.0.1:8080/`; WFS y teselas se interceptaron antes de navegar con respuestas vacías/controladas.
- Resultado: ocho combinaciones de viewport/tema (360×800, 800×360, 768×1024 y 1366×768; Claro y Oscuro), con los cinco inputs visibles en cada una. Nombre, dirección y calle midieron 44 px de alto; altura y teléfono también conservaron 44 px. Padding 12 px y fuente 14.4 px. Anchuras respondieron al layout existente: 288 px en móvil, 256 px en campos de fila y 528 px en dirección a escritorio/tablet.
- Colores efectivos repetidos en los cinco inputs: Claro, texto `rgb(31, 41, 55)`, superficie `rgb(255, 255, 255)`, borde `rgb(156, 163, 175)`; Oscuro, texto `rgb(249, 250, 251)`, superficie `rgb(31, 41, 55)`, borde `rgb(156, 163, 175)`. Nombre/campo enfocado usa el borde de foco renderizado; en algunos viewports la cascada mantiene ese borde por foco al tomar la medición. El foco medido en ambos temas fue outline sólido de 3 px y offset 2 px (`rgb(29,78,216)` claro; `rgb(147,197,253)` oscuro).
- La ejecución confirmó inputs/tipos text, text, text, number, tel; cada label apunta por `for` al ID correspondiente; required de nombre/dirección y maxlength 60/50/50/ninguno/30. Auditoría del componente confirma bindings `formData.nombre`, `direccion`, `calle`, `altura` y `telefono` y que no cambiaron validaciones.
- La página produjo cero excepciones/errores de consola. Requests observadas: sólo GET; WFS y teselas fueron controlados; no se envió el formulario ni se realizaron mutaciones.

## Comprobaciones

- Auditoría del diff: sólo se añadieron clases/reglas de presentación para los cinco campos dentro del cambio UI; bindings, reglas JS y payload intactos.
- `node --test` exacto desde `raweb/`: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; `duration_ms 374.273631` (ejecutado previamente, no repetido porque no cambió código).
- `npm run build` desde Windows PowerShell/Node: código 0; sin warnings; bundle compilado en 8.8 s (ejecutado previamente, no repetido porque no cambió código).
- Harness CDP Windows: código 0, 8 mediciones viewport/tema, 40 registros de campos; cero errores, sólo GET y ninguna alta enviada. Resultado bruto temporal `t20-browser-result.json`; harness y JSON temporales retirados tras resumir las mediciones aquí.

T20 cumple el criterio literal y está marcada completa. Detener aquí; T21 no ejecutada.
