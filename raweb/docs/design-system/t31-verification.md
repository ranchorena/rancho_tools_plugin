# T31 — Contrato de inventario del catálogo

Fecha: 2026-10-07. Tarea lógica/datos, sin integración DOM ni servicios.

## Alcance y correspondencia

Implementación pura en `src/design-system/catalog.mjs`, basada en las familias, variantes, estados y límites ya registrados en [coverage T1](coverage.md) y en RF-1–RF-4, RF-10, RF-22 y RF-23. No se montan componentes, no se consultan REST/WFS y no se añaden dependencias ni scripts.

| Familia | Variantes descritas | Estados aplicables | No aplicables explícitos |
| --- | --- | --- | --- |
| C-BUTTON | navegación, primario, secundario/neutro, ubicación, cierre/icono | normal, hover, active, focus, disabled, loading | selected (solo acción nav), message |
| C-FIELD | texto, número, teléfono, hora, área de texto, solo lectura | normal, focus, disabled (CSS declarado) | hover, selected, loading |
| C-CHOICE | casilla, radio exclusivo | checked, unchecked, focus, hover | disabled, loading, message |
| C-THEME | Claro, Oscuro, Sistema (aprobados RF-17) | normal, selected, focus | disabled, loading |
| C-DIALOG | los cuatro diálogos existentes | open, closed, focus (coordinación N/O en T1) | disabled, loading del marco |
| C-NAV | escritorio, móvil | normal, hover, focus, active, open, closed | disabled, loading |
| C-TABLE | clientes, pedidos, fila normal/regalo | normal, hover, selected, focus (T1 lo registra N/O en implementación previa) | disabled, loading/message en la tabla |
| C-STATS | tres tarjetas informativas existentes | normal | focus, active, selected, disabled, loading propio |
| C-NOTICE | variantes globales/locales y alerta nativa | visible, hidden, loading, success, error, message | focus, selected, disabled |
| C-PANEL | panel/disparador cerrado | open, closed, checked, hover, scroll | loading, message |
| C-FLOAT | capas, alta, zoom, atribución | normal, hover, focus, active existente | disabled local, loading, message |
| C-INFO | información de cliente/pedido | visible, hidden, scroll | focus, selected, disabled, loading |

Las notas de las filas acotan cada etiqueta al significado documentado en coverage: por ejemplo, `disabled` de campo corresponde a la regla CSS observada, no afirma un binding deshabilitado; `focus` de tabla se registra como no observado en T1, no como comportamiento ya comprobado. La lista de estados permitidos en test es un vocabulario de estados observados/aprobados en las fuentes, no una política de producto.

## Integridad cuantitativa y alertas

- Familias: **12**, IDs únicos, en correspondencia con C-BUTTON, C-FIELD, C-CHOICE, C-THEME, C-DIALOG, C-NAV, C-TABLE, C-STATS, C-NOTICE, C-PANEL, C-FLOAT y C-INFO de coverage.
- Trazabilidad de cada familia: al menos una referencia RF válida (RF-1–RF-24) y al menos una experiencia X-NAV/X-DIR/X-CLI/X-ADD/X-PED/X-NOT/X-MAP.
- Variantes: **41** en total; derivadas de las diferencias y variantes existentes/aprobadas del inventario T1, no una guía visual/renderizada.
- Estados: **48 aplicables** y **34 no aplicables**. Cada declaración tiene procedencia T1; cada no aplicable además explica el límite. El test prohíbe duplicar un estado o clasificarlo simultáneamente en ambas listas y restringe IDs al vocabulario explicitado.
- Alertas: **3**, A-01, A-02 y A-03, con disparador/mensaje existente, referencia RF-23, clasificación `native-browser-excluded` para apariencia y contraste, y `verify-trigger-message-function` para mantener verificable su funcionamiento. No se reemplazan ni se les asigna tema/contraste.

## Rojo/verde y comandos exactos

Prueba significativa escrita antes de la implementación: `tests/design-system/catalog.test.mjs` importa el contrato esperado y comprueba inventario completo, unicidad/trazabilidad, variantes, estados aplicables/no aplicables y exclusión visual/funcionalidad verificable de alertas.

1. Rojo válido, desde `raweb/`, antes de crear el módulo:
   `node --test tests/design-system/*.test.mjs`
   Resultado: código **1**; 24 contabilizados, 23 pass y 1 fail de carga por `ERR_MODULE_NOT_FOUND` de `src/design-system/catalog.mjs`. El fallo corresponde a la ausencia real del contrato.
2. Un intento anterior desde la raíz Git encontró 0 tests; no se considera evidencia de rojo ni de verde. El rojo anterior se repitió desde `raweb/` con el comando requerido.
3. Verde final, desde `raweb/`:
   `node --test tests/design-system/*.test.mjs`
   Resultado: código **0**; tests **26**, pass **26**, fail **0**, cancelled/skipped/todo **0**; duración **318.806083 ms**. Incluye las tres pruebas nuevas y las 23 preexistentes.
4. Build Windows ya instalado, sin reinstalar dependencias:
   `cmd.exe /c "cd /d C:\GIT\github\rancho_tools_plugin\raweb && npm run build"`
   Resultado: código **0**; Rollup creó `public/build/bundle.js` en **7.4 s**.

## Resultado

**T31 completa** conforme al contrato de inventario y a sus pruebas de datos. Esto no verifica el render, interacción de un catálogo visual, API/WFS ni la aceptación integral de RF-22/RF-23. Este registro es anterior a la replanificación aprobada que desacopló T32 de T30; el estado y la verificación incremental de T32 se mantienen en [T32](t32-verification.md). T30 permanece incompleta.
