# T55 — Matriz integrada de uniformidad RF-24

Fecha: 2026-10-07. RF-13–RF-16, RF-23, RF-24; RNF-1–RNF-3, RNF-6.

## Resultado

Los cuatro diálogos comparten el patrón de Buscar Dirección en Claro y Oscuro. Se preservan sus dimensiones y estructuras particulares; Agregar Cliente ya no tiene un degradado exclusivo.

| Diálogo | Claro | Oscuro | Cabecera normal | Evidencia |
|---|---|---|---:|---|
| Buscar Dirección | Superficie/campo `#fff`, texto `#1f2937`, acción `#2563eb` con texto blanco | Superficie/campo `#1f2937`, texto `#f9fafb`, borde `#9ca3af`, acción `#93c5fd` con texto `#111827` | 41 px escritorio; 45 px móvil (T14) | [Baseline T51](t51-baseline.md), [T14](t14-verification.md) |
| Buscar Cliente/edición | Superficie, sección y campos `#fff`, texto `#1f2937`, bordes `#6b7280`, acción `#2563eb` | Superficie, sección y campos `#1f2937`, texto `#f9fafb`, bordes `#9ca3af`, acción `#93c5fd` | 44 px escritorio; 48 px móvil | [T52: capturas y medidas](t52-implementation.md) |
| Agregar Cliente | Superficie `#fff`, texto `#1f2937`, campos y acciones semánticos; sin degradado | Superficie `#1f2937`, texto `#f9fafb`, campos y acciones semánticos; sin degradado | 44–48 px | [T53: verificación](t53-verification.md) |
| Pedidos | Superficie/secciones `#fff`, texto `#1f2937`; estados existentes claros | Superficie/secciones `#1f2937`, texto `#f9fafb`; estados existentes oscuros | 41 px escritorio; 43.55/47.39 px ampliada (T54) | [T54: matriz y teclado](t54-verification.md) |

Los pares de contraste renderizados y estados de tabla/edición/estadísticas se remiten a T52–T54, donde se probaron con fixtures ficticios. Las mediciones de T14 siguen atribuidas a esa ejecución; la consola aportada por el usuario para T51 es evidencia distinta. Las dimensiones máximas de marco (500, 800, 600 y 1000 px declarados) se conservan conforme a RF-16; uniformidad visual no homogeneiza estructura ni tamaño.

## Pase integrado actual

- Chrome DevTools MCP conectado a la instancia de prueba de Windows mediante `127.0.0.1:9222`, con raweb en `http://localhost:8080/`.
- Inspección directa de `getComputedStyle` en ambos temas en los cuatro diálogos; revisión de campos, acciones y estados visibles. Se comprobó además Buscar Cliente con fila ficticia seleccionada y sección de edición en escritorio/móvil; T53/T54 aportan ejecuciones completas con fixtures, incluidas ubicación, pedidos, tablas y estadísticas.
- En la pasada directa, Buscar Dirección y Buscar Cliente, Alta y Pedidos reflejaron colores de superficie/texto de sus tokens en ambos temas. Agregar Cliente computó `backgroundImage: none` en cabecera y marco en ambos temas.
- Las comprobaciones completas de viewports, ampliación, contraste, clic físico de ubicación y acciones de teclado se reutilizan de T52–T54; no se atribuyen a la pasada directa donde no se midieron.
- Consola de la página inspeccionada: sin mensajes. No se ejecutaron guardados ni mutaciones. Una búsqueda de solo lectura con la cadena ficticia `Cliente Ficticio DS` llegó al endpoint local y devolvió vacío. La inicialización de App realizó GET WFS/teselas; no se inspeccionaron sus respuestas/cuerpos. Pedidos se abrió con GET vacío controlado. No se afirma verificación de servicios reales ni cambios persistentes.
- `node --test`: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo (499.331294 ms).
- `npm run build` desde PowerShell/Windows, invocado desde WSL: código 0; bundle generado en 12.1 s.

## Límites

Esta matriz satisface T55 y distingue las mediciones reutilizadas de las tomadas en el pase integrado. No equivale a aceptación final T50: catálogo/guía, otras experiencias y T27–T50 continúan pendientes. Las alertas nativas conservan la exclusión de apariencia/contraste. No se cambió lógica de negocio ni cartografía.
