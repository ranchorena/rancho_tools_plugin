# T16 — Migrar controles de los tres criterios de clientes

Fecha: 2026-10-06. **Pasa el criterio literal de T16.** RF-4–RF-7, RF-11–RF-13 y RF-19; depende de T15.

## Alcance implementado

- Los campos de nombre, dirección, calle y altura reciben `ds-field`; las tres acciones Buscar reciben `ds-button ds-button--primary` y `type="button"` explícito.
- Campos, acciones primarias y foco consumen las variables/clases comunes en Claro y Oscuro. Se conservan tamaños y disposición responsive locales.
- No se modificaron funciones, bindings, endpoints, validaciones ni manejo de carga.

## Referencia roja y verificación Chrome Windows

- Harness temporal externo `/tmp/opencode/t16-browser.cjs`, Node Windows 22.17.1 y CDP nativo. Aplicación servida en `http://192.168.0.102:8080/`.
- **Rojo previo a la migración, código 1:** en el diálogo real, los tres grupos carecían de `ds-field` y `ds-button--primary`; sus campos permanecían blancos al seleccionar Oscuro. La búsqueda no se activó en la referencia roja.
- **Verde final, código 0:** nueve combinaciones de viewport/tema (referencia inicial más los cuatro viewports en ambos temas); los tres grupos renderizan campos y botones con las clases comunes, superficies y primarios cambian correctamente según tema y el foco del botón es sólido de 3 px.
- Viewports comprobados: 360×800, 800×360, 768×1024 y 1366×768; temas Claro y Oscuro.
- Con respuestas JSON ficticias interceptadas y demoradas: el indicador «🔄 Cargando...» permanece visible durante cada POST. Los payloads observados fueron exactamente:
  - `{"criterio":"nombre","nombre_cliente":"CLIENTE FICTICIO"}`
  - `{"criterio":"direccion","direccion":"CALLE FICTICIA 100"}`
  - `{"criterio":"calle_altura","calle":"CALLE FICTICIA","altura":null}`
- Los tres criterios vacíos conservan su validación local y no generan solicitudes adicionales.
- WFS, teselas y recursos REST externos se interceptaron por CDP antes de llegar a servicios; los POST fueron controlados, no hubo escrituras reales ni errores de consola/CDP.

## Capturas

- [Claro, 1366×768](t16-light.png)
- [Oscuro, 1366×768](t16-dark.png)

## Comprobaciones del proyecto

- `npm run build` en Windows PowerShell/Node: código 0; Rollup generó `public/build/bundle.js` en 10.2 s. No se reinstalaron dependencias.
- `node --test` exacto desde `raweb/`: código 0; 23 tests, suites 0, pass 23, fail 0, cancelled 0, skipped 0, todo 0; 378.013343 ms.
- T16 completada. T17 no ejecutada.
