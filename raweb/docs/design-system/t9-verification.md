# T9 — Fundaciones y clases de controles/campos/foco

Fecha: 2026-10-06. Resultado: **pasa el criterio literal de T9**. RF-1, RF-2, RF-5, RF-13, RF-19.

> Hecho cuando: hoja compartida cargada, variables claro/oscuro y escalas definidas; controles nativos mantienen dimensiones particulares y foco visible sin reglas globales de movimiento nuevas.

## Referencia roja y método

- Git raíz `/mnt/c/GIT/github/rancho_tools_plugin`, rama `master`; status y diffs previos revisados, modificaciones anteriores preservadas.
- Harness externo `/tmp/opencode/t9-browser.cjs`, Node Windows v22.17.1, Chrome Windows 154.0.8037.95 headless, perfil propio y servidor loopback. WebSocket/CDP nativo, sin instalación. Sigue el método de [T4](t4-verification.md) y [T8](t8-verification.md).
- Se sirve el `public/index.html` real con sus hojas reales, retirando únicamente el script App en la respuesta temporal e insertando controles HTML nativos ficticios. No se modifica App ni se monta un catálogo/integración posterior. La fixture usa las clases públicas de Button, campos, casillas y radios; esta comprobación CSS no vuelve a acreditar el contrato Svelte de Button.
- **Rojo antes de editar código, salida 1:** CSS computado de raíz sin `--ds-primary`; fallo «Falta variable --ds-primary en render real». Cajas medidas previamente en 360×800; evidencia temporal `/tmp/opencode/t9-red-result.json`. No es un test de strings ni una simulación de render.
- Primer lanzamiento tuvo una ruta UNC mal escapada y no ejecutó el navegador; se corrigió la invocación. Primeros intentos verdes detectaron página headless sin foco efectivo (`outline-style: none`); se habilitó `Emulation.setFocusEmulationEnabled` en el harness. El CSS quedó intacto. El siguiente intento pasó; se amplió la medición a estados hover/active de las tres variantes y bordes contra la superficie efectiva, y volvió a pasar.

## Archivos y fundaciones definidas

- `public/design-system.css`: variables semánticas de claro/respaldo y oscuro explícito, escalas y clases de presentación. Conserva azules de acción, verde de ubicación, neutros y significados existentes; ajustes cromáticos para legibilidad, sin nueva dirección visual.
- `public/index.html`: carga `/design-system.css` después de global y antes del CSS del bundle.

| Fundación / propósito | Valores y ejemplo de uso definidos |
| --- | --- |
| Color / distinguir operaciones y estados | `--ds-primary` buscar/guardar; secondary cancelar/cerrar; location selección de punto; selected selección; success/warning/error significados existentes con superficie propia, sin reclasificar mensajes. Ejemplo `.ds-button--primary`, `.ds-button--location`. Claro primario `#2563eb`/blanco, oscuro `#93c5fd`/`#111827`; ubicación `#047857`/blanco y `#6ee7b7`/`#111827`. |
| Tipografía / escala compartida disponible | Familia sistema y Courier New; 0.875/1/1.5 rem, pesos 400/500/600, líneas 1.5/1.25. Variables disponibles para migración; no se impone fuente/tamaño a controles particulares. |
| Espaciado / dimensiones | 0.25/0.5/0.75/1/1.5/2 rem; referencias existentes 44/48 px controles generales y 30/28 px mapa. No se aplican como mínimos universales. |
| Bordes / radios | 1/2 px, radios 6/8/12 px y 50 %; borde cromático compartido en `.ds-field`, sin cambiar grosor/radio local. |
| Elevación | Panel `0 4px 12px rgb(0 0 0 / 15%)`, diálogo `0 20px 25px -5px rgb(0 0 0 / 20%)`; variables disponibles, no nuevos niveles de convivencia. |
| Iconografía / movimiento | Conservar símbolos/emojis y nombres accesibles existentes; comentario explícito sobre animaciones locales. No reglas nuevas de animación, transform, transición o reduced-motion. |

Clases: `.ds-surface`, `.ds-button` con primary/secondary/location, `.ds-field`, `.ds-choice`, `.ds-focus`. Hover/active, disabled y readonly presentados sobre elementos nativos; no añaden validación ni estado funcional. Foco solid 3 px, offset 2 px, opaco, sin cambiar caja ni interceptar teclas. Las clases no fijan width/height/padding/margin/min-height.

## Verde real y mediciones

Ejecución final navegador: **salida 0**, cinco grupos de comprobaciones pasan.

- Orden de hojas computado: `/global.css` → `/design-system.css` → `/build/bundle.css`; variables de ambos temas y 22 valores de escala consultados en CSS computado, todos presentes.
- Comparación de la misma fixture con hoja desactivada/activada en **360×800, 800×360, 768×1024 y 1366×768**, ambos temas: igualdad exacta de width, height, padding, margin y min-height para botones, cierre particular, campos, readonly, textarea, select, checkbox y radio. Iguales transform, animation-name y transition: `none`, `none`, `border-color 0.2s, box-shadow 0.2s`.
- Ejemplos 360×800: botón/campo **336×52 px**, cierre particular **32×32 px**, casilla/radio **18×18 px**; idénticos antes/después. No se convierte el cierre ni los controles particulares a mínimos generales.
- Foco sobre diez controles habilitados: outline solid **3 px**, offset **2 px** en ambos temas y cuatro viewports. Tab nativo primario → secundario; Espacio marca checkbox. No handlers añadidos por CSS.
- Cero errores de consola; solicitudes solo a página, tres hojas y favicon propios. Ninguna REST/WFS.
- Captura real revisada `/tmp/opencode/t9-screenshot.png`; resultado y mediciones `/tmp/opencode/t9-green-result.json`. Artefactos temporales; servidor y navegador propios cerrados, perfil eliminado.

Contraste calculado sin redondear para comparar, sobre **colores computados del render opaco real**. Texto de botones/campos en escritorio 14–16 px/peso 400–500: umbral normal 4,5; indicador/borde contra superficie efectiva: umbral 3. Tabla resumida redondeada solo para mostrar:

| Elemento / estado | Claro | Oscuro |
| --- | ---: | ---: |
| Primario normal / hover / active | 5,17 / 6,70 / 8,72 | 9,84 / 12,48 / 6,98 |
| Secundario normal / hover / active | 13,93 / 12,38 / 11,27 | 10,31 / 7,56 / 4,83 |
| Ubicación normal / hover / active | 5,48 / 7,68 / 9,72 | 11,64 / 13,83 / 9,23 |
| Disabled texto/fondo | 6,10 | 7,00 |
| Campo/textarea/select texto/fondo | 14,68 | 14,05 |
| Readonly texto/fondo | 7,17 | 12,04 |
| Foco/superficie (diez controles) | 6,70 (`#1d4ed8`/`#ffffff`) | 8,14 (`#93c5fd`/`#1f2937`) |
| Borde/superficie (secundario/campo/textarea/select) | 4,83 (`#6b7280`/`#ffffff`) | 5,78 (`#9ca3af`/`#1f2937`) |

## Comprobaciones de base y límites

- `npm run build` exacto desde raweb en Windows/PowerShell: **código 0**, bundle generado en **11.4 s**.
- `node --test` **exacto final**, raweb/WSL: **código 0**, tests **18**, suites **0**, pass **18**, fail **0**, cancelled **0**, skipped **0**, todo **0**, duration_ms **266.672409**. Tests de políticas existentes, no prueba del render CSS; sin tests de strings.
- Build WSL no repetido: bloqueo conocido por Rollup Linux ausente con dependencias Windows compartidas. Sin npm ci, dependencias, permisos ni configuración nuevos.
- T9 acredita únicamente las fundaciones/clases aisladas y su carga real. No acredita migración de App/diálogos, texto 200 % de experiencias, catálogo, contraste de todos los tokens/mensajes, degradados/transparencias, marcas nativas de selección o controles sobre mapa. API/GeoServer/base no comprobados; no necesarios para esta fixture CSS aislada.
- **T9 completada. Parada antes de T10 y de cualquier integración posterior.**
