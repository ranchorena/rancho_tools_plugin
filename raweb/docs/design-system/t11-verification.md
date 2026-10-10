# T11 — Tema integrado en navegación desktop/móvil

Fecha: 2026-10-06. Resultado: **pasa el criterio literal de T11**. RF-11, RF-15–RF-19; depende T3/T4/T9.

> Hecho cuando: selector al final de barra y debajo de acciones móvil; elegir/recargar/cambiar dispositivo funciona sin añadir fila en cabecera móvil.

## Cambio y referencia roja

- Raíz Git `/mnt/c/GIT/github/rancho_tools_plugin`, rama `master`; status y diff previo revisados. App no tenía modificaciones previas; las modificaciones existentes del resto del árbol se preservaron.
- `src/App.svelte`: un controlador compartido al montar, `data-theme` resuelto, limpieza de suscripción al desmontar y prop común para ambos selectores. El adaptador de storage difiere el acceso a localStorage hasta sus métodos, dentro de las capturas de error del controlador existente. Clave existente `raweb.theme.v1`; sin elección, Sistema. No se cambian las políticas/adaptador.
- Selector `theme-desktop` tras Pedidos en la barra; `theme-mobile` tras las cuatro acciones dentro del desplegable. `ThemeSelector.svelte` conserva evento/prop y añade clase `ds-field`, presentación compacta sin margen inferior ni ancho global de 100 %. IDs distintos, etiqueta Tema.
- Navegación: colores literales reemplazados por variables compartidas en barra, marca, acciones desktop/móvil y hamburguesa; foco opaco 3 px/offset 2 px. Dimensiones, breakpoints y animaciones existentes conservados.
- **Rojo UI antes de editar:** App real servida por Windows, Chrome/CDP: 0 selectores frente a 1 esperado en escritorio; código **1**. Medición previa real: cabecera 68 px en 1366×768/800×360 y 80 px en 360×800/768×1024. No tests de strings ni render simulado.

## Método de navegador

- Las URLs Windows `http://192.168.0.102:8080` y `http://172.18.208.1:8080` respondieron HTTP 200. Verificación ejecutada sobre la primera, con `public/index.html`, bundle y hojas reales; se monta App, no una fixture del selector.
- DevTools del harness siguió fallando `Target.setDiscoverTargets: Target closed`. Alternativa conforme a [T4](t4-verification.md)/[T9](t9-verification.md): Chrome Windows **154.0.8037.95** headless, Node Windows, WebSocket/CDP nativo y perfil temporal propio. Sin dependencias/configuración nuevas.
- Harness externo `/tmp/opencode/t11-browser.cjs`. Intercepción CDP **antes de navegar**: recursos de la app se sirven normalmente; WFS responde FeatureCollection vacía y recursos cartográficos/externos responden imagen neutra. No se recibe ni captura información de clientes reales. Solo solicitudes GET; ninguna mutación backend.
- Perfil propio conserva localStorage durante recarga y salida a `about:blank`/reapertura de la misma URL. Dispositivo emulado con `prefers-color-scheme`; tamaños emulados de viewport CSS, DPR 1. Pulsaciones Home/Flecha abajo/End/Tab/Mayús+Tab/Enter enviadas con `Input.dispatchKeyEvent`, sin sustituir el cambio del selector por asignación DOM.

## Verde real

Ejecución final del harness: **código 0**, cinco grupos de comprobaciones, cero errores de consola/excepciones.

| Comprobación | Resultado observado |
| --- | --- |
| Sin elección guardada | Selector Sistema; dispositivo claro → light, oscuro → dark; no se guarda una elección artificial al iniciar. |
| Claro/Oscuro/Sistema desktop | Selección por teclado, escritura exacta light/dark/system en clave existente y restauración de las tres al recargar y al salir/reabrir la URL en el mismo navegador. |
| Cambiar dispositivo | Sistema sigue claro/oscuro en vivo; Claro y Oscuro permanecen explícitos pese a ambos cambios. Comprobado desktop y Sistema vivo móvil. |
| Persistencia móvil | Las tres opciones elegidas por teclado se restauran al recargar/abrir menú; ambos selects coinciden. |
| Cambio responsive | Elección compartida conservada al pasar móvil/escritorio; no se crea otro controlador ni otra clave. |
| Ubicación | Desktop después de Pedidos; móvil debajo de la última acción. Select desktop oculto en móvil, móvil solo dentro del menú abierto. |
| Teclado/foco | Tab desde Pedidos al selector y Mayús+Tab de vuelta, desktop/móvil; Home/Flecha abajo/End seleccionan las tres opciones. Todos los botones de navegación visibles, Menú y selector muestran foco solid 3 px en ambos temas. Menú abre con Enter. |
| Nombres accesibles | Árbol AX: combobox «Tema», botón «Menú» móvil y acciones con sus nombres/textos existentes; asociación label/ID comprobada en ambos selectores. |

| Viewport | Navegación existente | Altura previa | Claro tras integración | Oscuro tras integración |
| --- | --- | ---: | ---: | ---: |
| 1366×768 | Desktop | 68 px | 68 px | 68 px |
| 800×360 | Desktop (breakpoint existente >768) | 68 px | 68 px | 68 px |
| 360×800 | Móvil | 80 px | 80 px | 80 px |
| 768×1024 | Móvil | 80 px | 80 px | 80 px |

Selector dentro del ancho visible en los cuatro casos; acciones desktop permanecen en la cabecera; **ninguna fila nueva ni aumento de altura móvil**. Estas son medidas de navegación, no de cabeceras de formularios RF-14.

Artefactos temporales: `/tmp/opencode/t11-red-result.json`, `t11-green-result.json` y ocho capturas `t11-<ancho>-<alto>-<light|dark>.png`. Revisadas visualmente las capturas 360×800 oscuro y 800×360 claro. Son artefactos de sesión, no enlaces permanentes de aceptación final. Navegador propio cerrado y perfil temporal eliminado tras cada ejecución; servidor Windows existente conservado.

## Base y límites

- `npm run build` exacto desde raweb mediante PowerShell Windows: **código 0**, bundle generado en **7.9 s**. Sin reinstalar ni cambiar permisos/configuración. Build WSL no repetido por bloqueo Rollup Linux ya documentado con node_modules Windows compartidos.
- `node --test` **exacto final**, desde raweb/WSL: **código 0**, tests **23**, suites **0**, pass **23**, fail **0**, cancelled **0**, skipped **0**, todo **0**, duration_ms **380.263397**. Lógica existente en verde; T11 es integración UI, sin nueva política que requiera tests unitarios nuevos.
- Red controlada acredita el ciclo de tema en App real, **no disponibilidad ni flujos reales REST/WFS**, búsquedas, guardados, alta, pedidos o refresh. Esos criterios siguen pendientes de sus tareas.
- Captura móvil muestra la disposición previa del menú `top:56px` bajo una cabecera renderizada de 80 px y controles flotantes de mapa encima del desplegable (z-index existente). No se rediseñó esa convivencia; el selector nuevo está debajo de las acciones y es accesible. No se acredita aceptación integral de navegación/convivencia ni se corrige un comportamiento previo por inferencia.
- Esta tarea no acredita contraste de todos los estados renderizados, ampliación de texto 200 %, temas de diálogos/mapa, retorno de foco al cerrar ni matriz final; esas verificaciones corresponden a tareas posteriores. Las pruebas numéricas de T10 no sustituyen mediciones de cascada/render.
- **Solo T11 completada; parada antes de T12.** Spec sigue aprobada, sin aceptación de entrega.
