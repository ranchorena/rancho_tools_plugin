# T24 — Estadísticas y mensajes de pedidos

Fecha: 2026-10-06. RF-4, RF-6, RF-11, RF-13, RF-16.

## Cambio y conservación

- `Pedidos.svelte` presenta la sección y tarjetas de estadísticas con `--ds-background`, `--ds-surface`, `--ds-text`, `--ds-text-muted` y `--ds-border`; el valor monetario usa `--ds-success`. Los mensajes existentes de error y carga usan los tokens semánticos de error y superficie/texto. Los mismos tokens se resuelven en los temas claro y oscuro.
- Se conservaron las dimensiones y disposición responsive de las tarjetas, sus textos y la presentación/momento de los mensajes. No se cambió el flujo de carga ni su clasificación.
- `calcularEstadisticas`, el precio por docena, las condiciones de regalo y el formato mostrado permanecen sin cambios. La referencia ficticia R-PED de `coverage.md` (cantidades 1.5 y 2; una venta y un regalo) da los resultados de referencia existentes: total 3.5, vendidas 1.5 y valor total 1750.00. Esta referencia es un cálculo derivado de la lógica existente, no una ejecución de navegador.
- Fallo previo conservado y registrado: si GET entrega el objeto `{message: ...}` de respuesta vacía conforme al contrato documentado, la ruta actual asigna ese objeto y `calcularEstadisticas()` invoca `forEach`, por lo que puede fallar antes de mostrar el mensaje vacío. No se alteró por inferencia.

## Comprobaciones ejecutadas

- `node --test` exacto final: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; 436.156723 ms.
- `npm run build` en Windows PowerShell/Node: código 0; bundle generado sin warnings en 8.8 s.
- No se ejecutó verificación integrada en navegador. El pase conjunto T22–T24 sigue pendiente; no hay capturas ni comprobación renderizada de temas, carga, foco, retorno o distribución que declarar como pasada.
