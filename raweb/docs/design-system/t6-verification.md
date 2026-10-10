# T6 — Acción de foco interior sin trap

Fecha: 2026-10-06. Resultado: **pasa el criterio literal de T6**. RF-9, RF-21.

## Referencia roja, antes de implementar

- Harness Svelte real aislado, sin acción de foco (el módulo todavía no existe), compilado con dependencias existentes y entrada/componente virtuales fuera del repositorio.
- Chrome Windows 154.0.8037.95 mediante CDP/WebSocket nativo de Node Windows v22.17.1. Pulsaciones reales y aserciones sobre DOM; no tests de strings ni simulación de render.
- Tras enfocar `before` y montar el contenido con controles, esperar `tick()`: `document.activeElement.id` sigue siendo `before`; esperado `first`. **Rojo real**, código 1, aserción `before !== first`.
- Consola sin errores; red solo página, bundle y favicon locales. Resultado temporal: `/tmp/opencode/t6-red-result.json`.
- Primer comando falló por escapado de ruta UNC antes de ejecutar el harness; se corrigió la invocación, sin cambiar configuración ni dependencias.

## Método reproducible

- Harness temporal: `/tmp/opencode/t6-build.mjs` y `t6-browser.cjs`, adaptación del método de [T4](t4-verification.md).
- Desde WSL, PowerShell Windows ejecuta Node sobre `\\wsl.localhost\Ubuntu\tmp\opencode\t6-build.mjs` y luego `t6-browser.cjs`. Sin `T6_ACTION`, referencia roja; con variable de entorno temporal `T6_ACTION=1`, compila el mismo ejemplo usando `dialogFocus` real.
- La fixture contiene disparador, contenido condicional y botón externo ficticio; su padre registra/desmonta por Escape o botón. No monta App, diálogos de producto ni servicios. Las reglas de cierre son del ejemplo; la acción solo gestiona entrada de foco.

## Resultado verde observado

La acción real `src/design-system/dialog-focus.mjs` espera `tick()`, enfoca el primer control habilitado visible y recorrible; sin controles añade `tabindex=-1` al contenido. Desmontar cancela la entrada pendiente y limpia únicamente el tabindex añadido. No tiene listeners de teclado/cierre, trap, inert ni retorno de foco.

| Comprobación DOM/teclado real | Resultado |
| --- | --- |
| Montaje enfoca `first`, omitiendo disabled, hidden, descendiente de fieldset disabled y tabindex negativo | Pasa |
| Tab: primer control → Cerrar → botón externo; Mayús+Tab recorre inversamente y sale al disparador | Pasa |
| Desmontaje interno mientras el botón externo tiene foco: conserva ese foco, no emite cierre | Pasa |
| Contenido sin controles recibe foco con tabindex -1; Tab permite salir al botón externo | Pasa |
| Montaje y desmontaje antes de tick: foco pendiente cancelado, botón externo conserva foco | Pasa |
| Escape y activación nativa de Cerrar con Enter: padre recibe exactamente `escape`, `button`, desmonta, sin retorno automático al disparador | Pasa |
| Fondo accesible durante apertura sin cierre automático; cero errores de consola, ninguna solicitud REST/WFS | Pasa |

- Un primer intento verde pasó foco/Tab/desmontaje pero falló al activar Cerrar: el harness enviaba Enter sin el campo CDP `text`. Se corrigió solo la pulsación del harness con `text: '\r'`; la acción no se modificó. Nueva ejecución completa: **código 0, siete comprobaciones pasan**.
- Captura real revisada: `/tmp/opencode/t6-screenshot.png`, contenido aún montado y foco en botón externo. Resultado estructurado: `/tmp/opencode/t6-green-result.json`. Artefactos temporales, no enlaces permanentes de aceptación final. Servidor/navegador propios cerrados y perfil temporal eliminado.

## Verificaciones de base y límites

- `node --test` **exacto**, desde raweb en WSL Node v24.19.0: código 0; tests **18**, suites **0**, pass **18**, fail **0**, cancelled **0**, skipped **0**, todo **0**, duration_ms **2001.746298**. Se ejecutaron las pruebas existentes de políticas; no acreditan DOM. El rojo/verde de esta tarea UI es el ejemplo real anterior, sin tests Node de strings ni falsos de render.
- `npm run build` Windows PowerShell/Node v22.17.1: código 0, bundle generado en **10.2 s**. El módulo nuevo también se compiló/importó en el bundle aislado; aún no se importa en el producto.
- `npm run build` WSL: código 1, falta `@rollup/rollup-linux-x64-gnu` en dependencias compartidas con Windows. Sin instalar/reinstalar dependencias ni cambiar configuración permanente.
- Solo T6. App, diálogos y lógica de negocio no modificados. No acredita retorno coordinado por App (T12), selección real de ubicación ni flujos con API/GeoServer, que no se ejecutaron. La matriz visual/temas de aceptación corresponde a tareas posteriores. T7 no iniciada.
