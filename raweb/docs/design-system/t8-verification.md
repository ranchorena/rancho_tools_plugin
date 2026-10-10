# T8 — Cabecera reutilizable de altura natural

Fecha: 2026-10-06. Resultado: **pasa el criterio literal de T8**. RF-4, RF-14, RF-20.

> Hecho cuando: ejemplo una línea/dos líneas móvil cumple 48/64 px; a texto 200 % título y cierre no se recortan.

## Referencia roja anterior al código

- Fixture Svelte real con títulos ficticios y estilos de cabecera de `src/AgregarCliente.svelte`: flex, título 1.5rem/600, cierre 2rem y padding móvil 1rem (reglas de líneas 145–174 y 373–376). No se montó el formulario ni se usaron datos reales.
- Chrome Windows 154.0.8037.95, viewport 360×800: una línea **64 px**, dos líneas **92 px**. Falló la primera aserción `64 <= 48`, **código 1**. Cero errores de consola, ninguna REST/WFS.
- Referencia temporal: `/tmp/opencode/t8-red-result.json`. Es una reproducción aislada de las reglas existentes, no una verificación del alta integrada.

## Implementación y método

- `src/design-system/DialogHeader.svelte`: prop `titleId`, slot de título dentro de h2 y slot nombrado `close`. El padre aporta Button y callback; la cabecera no despacha operaciones ni decide cierre.
- Altura natural, título 1rem/1.25, padding vertical .25rem, espacio para cierre que no se encoge; texto puede partir palabras largas. Cierre nativo con dimensiones mínimas en rem, sin altura fija. Sin max-height, truncamiento ni overflow oculto.
- Harness externo `/tmp/opencode/t8-build.mjs` y `t8-browser.cjs`, siguiendo [T7](t7-verification.md): entradas virtuales, Svelte/Rollup existentes, Node Windows v22.17.1, Chrome headless con perfil propio, servidor loopback y WebSocket/CDP nativo. PowerShell ejecuta los scripts por `\\wsl.localhost\Ubuntu\tmp\opencode\`; `T8_HEADER=1` monta el componente real.
- Se midieron DOM, cajas y rangos de texto; se inspeccionó árbol Accessibility y se activó cierre con Enter CDP. No se añadieron tests de strings ni dependencias.
- Primer intento del componente: el título ficticio pensado para dos líneas cabía en una a 16 px; la aserción de número de líneas falló. Se alargó el fixture a «Buscar dirección del ejemplo ficticio de prueba» y se comprobó que ahora ocupa dos líneas. No se modificó el componente para forzar el resultado. El título corto de la referencia roja permanece idéntico.
- Texto 200 %: raíz de 16 a 32 px sin cambiar viewport/DPR; fuentes computadas de título y cierre duplicadas. No es zoom de página ni una simulación de render.

## Verde real

Ejecución final **código 0**, cuatro grupos de comprobaciones pasan:

| Viewport | Texto | Altura título corto / largo | Líneas corto / largo |
| --- | --- | --- | --- |
| 360×800 | 100 % (16 px) | 40 / 48 px | 1 / 2 |
| 800×360 | 100 % | 40 / 40 px | 1 / 1 |
| 768×1024 | 100 % | 40 / 40 px | 1 / 1 |
| 1366×768 | 100 % | 40 / 40 px | 1 / 1 |
| 360×800 | 200 % (32 px) | 96 / 216 px | 2 / 5 |
| 1366×768 | 200 % | 80 / 80 px | 1 / 1 |

- En todos los casos, rangos de título y caja de cierre dentro de la cabecera, sin superposición, overflow de título ni reglas de recorte. La altura crece a texto ampliado conforme a RF-14.
- IDs de ambos títulos correctos y distintos; dos botones con nombre AX «Cerrar ejemplo». Enter activa exactamente una vez el callback del padre.
- Cero errores de consola; red limitada a página/bundle/favicon propios, ninguna REST/WFS.
- Captura real móvil 200 % revisada: `/tmp/opencode/t8-screenshot.png`; mediciones completas: `/tmp/opencode/t8-green-result.json`. Artefactos temporales, no aceptación final. Servidor y navegador propios cerrados, perfil eliminado.

## Base y límites

- `npm run build` exacto desde raweb en Windows/PowerShell: **código 0**, bundle generado en **8.2 s**. El componente también compiló y se montó en el harness aislado.
- `node --test` **exacto final** desde raweb/WSL: **código 0**, tests **18**, suites **0**, pass **18**, fail **0**, cancelled **0**, skipped **0**, todo **0**, duration_ms **352.313838**. Tests existentes de políticas, no acreditan render UI.
- Build WSL no repetido por bloqueo Rollup Linux conocido; sin instalaciones ni cambios de permisos/configuración.
- Solo T8: esta evidencia acredita el contrato aislado. Temas/paleta/contraste finales, CSS compartido, integración de diálogos y servicios corresponden a tareas posteriores; no se acredita cumplimiento global de los RF ni aceptación de la spec. Parada antes de T9.
