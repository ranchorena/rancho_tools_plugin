# Cobertura preliminar — Design system de raweb

## Alcance y método

- Tarea: **T1**, inventario documental del estado existente al 2026-10-06. Base: [spec aprobada](../../specs/001-design-system/spec.md), [plan aprobado](../../specs/001-design-system/plan.md), [tareas](../../specs/001-design-system/tasks.md) y [constitución](../constitution.md).
- Trazabilidad T1: RF-1–RF-4, RF-6–RF-9 y RF-23. Las experiencias se delimitan por RF-15; RF-16 limita los cambios. Este inventario no define nuevos valores permitidos, validaciones, estados, políticas ni excepciones.
- Resultado documental: inspección estática realizada de App, los cuatro diálogos, GlobalNotification, global.css y todos sus estilos locales. Los valores siguientes son declaraciones de fuente, no medidas de cajas renderizadas ni colores efectivos de la cascada.
- Referencias visuales: código/CSS actual y escenarios ficticios descritos abajo. No hay capturas ni catálogo ejecutado en T1. Ninguna fila equivale a aceptación visual o funcional de RF-23.
- Leyenda: **E** = existente en fuente; **N/O** = no observado en esa experiencia; **N/A** = no aplicable al elemento indicado; **pendiente** = requiere ejecución posterior. Foco nativo o CSS declarado no acredita recorrido, visibilidad efectiva ni retorno de foco.

## Fuentes de referencia

| ID | Fuente inspeccionada | Puntos de referencia |
| --- | --- | --- |
| S-APP | [App.svelte](../../src/App.svelte) | Script 33–127, 240–337, 366–580; markup 593–784; estilos 786–1455: navegación, capas, controles y datos seleccionados. |
| S-DIR | [BuscarDireccionDialog.svelte](../../src/BuscarDireccionDialog.svelte) | Validación/teclas 8–28; markup 31–68; estilos 70–337. |
| S-CLI | [BuscarCliente.svelte](../../src/BuscarCliente.svelte) | Búsquedas/edición 28–205; estilos 208–808; markup 810–961. |
| S-ADD | [AgregarCliente.svelte](../../src/AgregarCliente.svelte) | Validaciones/alta/coordenadas 8–115; estilos 118–383; markup 385–593. |
| S-PED | [Pedidos.svelte](../../src/Pedidos.svelte) | Carga/cálculos/zoom 17–81; estilos 84–392; markup 394–486. |
| S-NOT | [GlobalNotification.svelte](../../src/GlobalNotification.svelte) | Mensaje/tipo/temporizador 4–42; markup 45–53; estilos 55–94. |
| S-CSS | [global.css](../../public/global.css) | Base 1–32; controles/foco/disabled 47–141; scroll/utilidades 143–235. |

Las líneas sirven como localizadores de esta revisión; los enlaces de archivo son las referencias estables. No se usan datos provenientes de servicios ni configuraciones locales.

## Fundaciones existentes (RF-1–RF-3)

| ID / familia | Referencia e identidad observada | Variantes y particularidades |
| --- | --- | --- |
| F-COLOR / colores y significados | S-CSS, S-APP, S-DIR, S-CLI, S-ADD, S-PED, S-NOT | Primario global/nav `#007bff`; dirección/clientes `#3b82f6` y hover `#2563eb`; alta y cabecera degradado `#667eea` → `#764ba2`. Ubicación/alta flotante verde `#10b981` → `#059669`. Selección cliente `#dbeafe`; regalo pedido `#fef3c7`. Error local `#fef2f2`/`#dc2626`; éxito alta `#f0fdf4`/`#16a34a`; global éxito `#4CAF50`, error `#f44336`, otros `#333`. Warning usa otros, sin clase específica. No se decide una nueva paleta. |
| F-TYPE / tipografía | S-CSS 15–32; S-APP 788–794; S-ADD 263–268; títulos locales | Base sistema, 16 px y line-height 1.5; móvil body 14 px pero controles globales 16 px. App declara Arial; coordenadas Courier New. Títulos dirección/clientes/pedidos 1 rem/600 con variantes móviles; alta 1.5 rem/600; estadísticas 1.5 rem/600. Familia/altura efectivas pendientes de cascada. |
| F-SPACE / espaciado y dimensiones | S-CSS 54–84, 221–235; estilos locales | Utilidades 0.25/0.5/1/1.5 rem; padding y gaps locales hasta 2 rem. Botones globales min-height 44 px, móvil 48 px; cierres y flotantes declaran tamaños particulares; OL fuerza 30 px/28 px con `!important`. No se infiere tamaño interactivo efectivo. |
| F-BORDER / bordes y radios | S-CSS y estilos locales | Campos 1 px global/2 px local; neutros `#ccc`, `#d1d5db`, `#e5e7eb`. Radios 6/8/12 px, cierres redondos, alta flotante circular; ubicación borde discontinuo 2 px `#cbd5e1`. No hay escala común explícita. |
| F-ELEVATION / sombras y elevación | S-APP, S-DIR, S-CLI, S-ADD, S-PED, S-NOT | Sombras con negro/transparencia y verdes/violetas en hover. Fondos translúcidos/blur para paneles, tooltip y overlays. Nav/panel/flotantes z-index 1000; tres diálogos 1001; alta 1000; menú 999/overlay 998; notificación 2000; tooltip 10000. Convivencia efectiva pendiente. |
| F-ICON / iconografía | Markup S-APP y cuatro diálogos | Texto con emojis (búsqueda, cliente, pedido, ubicación, guardar), ×/✕, ▣ y hamburguesa CSS. Menú y cierres de diálogos tienen aria-label; flotantes/cierre capas tienen title. OL crea controles DOM. No se cambia simbología cartográfica. |
| F-MOTION / animaciones existentes | S-DIR 98–110, 327–335; S-CLI 236–248, 756–765; S-ADD 350–364; S-APP | Entrada dirección scale/translate 0.3 s; clientes/pedidos entrada 0.3 s; hover/active transform y transiciones 0.15–0.3 s; hamburguesa/menú; spinner alta 1 s infinito; scroll suave cliente y animaciones de mapa 1000 ms. Reduced-motion local solo dirección/clientes. Registro, no nueva política de movimiento. |

Identidad a contrastar posteriormente: azules actuales, verde de ubicación, marca RAWEB, iconos con texto y disposiciones particulares. Los cambios ya aprobados son unificación claro/oscuro y ajustes cromáticos, cabeceras compactas, selector y accesibilidad acotada de la spec; no se implementan ni se asignan valores en T1.

## Familias del catálogo y estados (RF-4, RF-6–RF-9)

| ID / familia | Experiencias y variantes E | Estados E y ausencia/no aplicabilidad | Referencias |
| --- | --- | --- | --- |
| C-BUTTON / botones | Navegación texto+emoji; Buscar/Guardar azules; alta violeta; Cancelar neutro; ubicación verde; icono cierre/capas/alta/Menú/OL | Normal, hover, active global/flotante, focus CSS; active selección nav. Disabled y carga: Guardar alta sin coordenadas o guardando; Cancelar alta al guardar. Búsqueda/guardado cliente no enlazan disabled a carga. No añadir disabled/carga a otros botones. | S-CSS; S-APP; S-DIR; S-CLI; S-ADD |
| C-FIELD / campos y áreas de texto | Texto búsquedas, altura de búsqueda como texto; number docenas/PAO/alta; tel alta; time alta; horario edición texto HH:MM:SS; textarea observaciones; readonly ID/nombre cliente | Normal, focus CSS, readonly; required/maxlength alta; mensajes de validación de cada formulario. CSS global input:disabled, sin binding disabled observado en estos campos. Carga/selección como estados propios del campo N/O; mantienen valores durante carga. | S-DIR; S-CLI; S-ADD; S-CSS |
| C-CHOICE / casillas y opciones exclusivas | Tiene pedido/regalo en alta/edición; Clientes/Pedidos capas; radio OSM/Satelital | Marcado/desmarcado; radio exclusivo, inicial OSM, Pedidos visible y Clientes oculto; hover contenedor capas y foco global de input. Disabled/carga/errores propios N/O. | S-APP 675–694; S-CLI 938–945; S-ADD 537–553 |
| C-THEME / selector de tema | N/O en UI actual; Claro/Oscuro/Sistema aprobado, no implementado | Estados/persistencia/seguimiento pendientes de tareas posteriores. No presentar el oscuro parcial como selector existente. | S-APP; S-CLI 767–807; spec RF-17/RF-18 |
| C-DIALOG / diálogos | Dirección, clientes, alta y pedidos; marcos distintos y overlay | Abierto/cerrado; cierre × y backdrop; Escape ligado al backdrop, con stopPropagation del contenido. Dirección maneja además Escape/Enter en input. Entrada animada salvo alta. Foco interior/retorno coordinados N/O. Reglas particulares en matriz de experiencias. | Cuatro diálogos; S-APP 366–411 |
| C-NAV / navegación desktop/móvil | Cuatro acciones desktop; Menú móvil hamburguesa/desplegable/overlay | Normal/hover/focus y acción active; menú abierto/cerrado, hamburguesa transformada. Abrir diálogo cierra menú y otros diálogos. Overlay móvil clic/Escape. Carga/disabled/mensajes propios N/O. | S-APP 593–657, 808–859, 1030–1130 |
| C-TABLE / tablas y filas accionables | Clientes: ID/nombre/dirección/calle/altura; pedidos: nueve columnas, normal/regalo | Hover; selected cliente; regalo amarillo pedido. Filas solo on:click, teclado/foco propio N/O. Tabla ausente sin resultados; mensajes carga/vacío/error fuera de tabla. Sin selección persistente en pedidos; clic con coordenadas hace zoom/cierra, sin ellas no hace acción. | S-CLI 445–491, 863–894; S-PED 191–229, 384–391, 419–462 |
| C-STATS / estadísticas | Cantidad Total, Cantidad Vendidas, Valor Total | Valores derivados presentes solo con pedidos.length > 0; normal y monetario verde. Foco/interacción/disabled N/A: tarjetas informativas. No indicador propio de carga/error. | S-PED 51–65, 255–291, 465–483 |
| C-NOTICE / notificaciones y mensajes | Global success/error/otros (warning usa otros); errores/carga clientes/pedidos; error/éxito alta; alertas nativas dirección | Visible/oculto; sustitución/temporización global; sin cierre manual. Validación/vacío usan error local; carga textual clientes/pedidos, Guardando+spinner alta. Normal/foco/selección/disabled N/A al mensaje informativo. Ver reglas y alertas abajo. | S-NOT; S-APP 81–91, 563–578; cuatro diálogos |
| C-PANEL / panel de capas | Abierto con dos grupos; cerrado reemplazado por botón ▣ | Toggle mostrar/cerrar, casillas/radios, hover y scroll vertical; sin carga/error propio. No cierre por fuera/Escape observado en panel. | S-APP 663–702, 861–996 |
| C-FLOAT / controles flotantes | Mostrar capas, alta circular, zoom +/−, atribución OL | Normal/hover/focus global o local; active alta. Abrir alta/capas, zoom/atribución nativos. Sin disabled/carga local; rotación desactivada. Contraste sobre OSM/satélite pendiente. | S-APP 220–226, 699–707, 971–1028, 1146–1246 |
| C-INFO / información del mapa | Elemento cliente o pedido, campos comunes y condicionales; fallback N/A | Visible/oculto por clic feature/fuera; click/keydown internos detienen propagación; sin cierre con botón, sin edición. Textos largos word-break; scroll vertical landscape. No carga/disabled/selección interna ni foco propio observado. | S-APP 240–337, 582–586, 742–781, 1371–1454 |

## Experiencias, mensajes, cierre y layout

| ID / experiencia RF-15 | Estados, validaciones y flujos existentes | Layout y relación con fondo / referencia ficticia |
| --- | --- | --- |
| X-NAV / desktop y móvil | Acciones excluyen otros diálogos y cierran menú. Menú alterna por botón, cierra por overlay clic/Escape. Estado active según diálogo visible. | Main flex 100vh/overflow hidden; navbar min-height declarado 60 px desktop/56 móvil, marca izquierda/acciones derecha. ≤768 móvil; ≤480 compacto; 769–1024 botones compactos. Menú fijo top 56/60 px, scroll landscape ≤768. Referencia R-NAV. |
| X-DIR / dirección | Input vacío trim → A-01; válido emite buscar y App cierra antes de POST. Éxito centra/marca mapa; falta coordenadas → A-02; fallo → A-03. Sin carga visible. Input Enter busca, Escape cierra; ×/backdrop cierra. No asumir Escape global desde otros controles. | Ancho máximo 500 px, 90vh, cuerpo scroll/footer centrado; tablet 400 px. Móvil arriba, padding/alturas según 768/480; landscape centrado. Cabecera min-height 40/36/32 px más cascada/padding, no medición RF-14. Referencia R-DIR. |
| X-CLI / búsqueda y edición | Tres búsquedas: vacío nombre/dirección/calle → mensajes «Por favor, ingrese…»; altura opcional. Carga «🔄 Cargando...» sin deshabilitar controles. Array vacío → «No se encontraron clientes…» como error; fallos muestran err.message. Selección rellena edición y scroll suave; guardar sin selección/horario inválido → error («No hay un cliente seleccionado para guardar.» / «Formato de horario inválido. Use HH:MM:SS.»). Éxito notifica/refresca/geocodifica/cierra; geocodificación puede warning. Sin alerta nativa. | Máx. 800 px/95vh; cuerpo vertical; tabla máx. 300 px/overflow auto, min-width 600 px (500 ≤480), thead sticky; dos columnas edición, una móvil, dos landscape ≤768. Tablet marco 90 %. Cabecera 40/36/32 px declarados. Oscuro automático parcial. Referencia R-CLI. |
| X-ADD / alta con ubicación | Sin coordenadas «No seleccionadas», Guardar disabled; seleccionar emite evento, App activa crosshair y acepta clic de mapa → prop {lat, lon}/marcador. Validaciones JS en orden: nombre, dirección, ubicación; errores exactos «El nombre del cliente es requerido.», «La dirección del cliente es requerida.», «Debe seleccionar una ubicación en el mapa.». Required nombre/dirección y maxlength 60/50/50/30/200 en campos correspondientes. Submit del form y botón exterior on:click usan handleSubmit: validación nativa efectiva depende de ruta, pendiente. Guardando+spinner, Cancelar disabled; ×/backdrop siguen habilitados. Fallo HTTP result.error o «Error al agregar el cliente.»; conexión «Error de conexión. Verifique su conexión a internet.». Éxito local/result.mensaje o fallback, evento padre cierra inmediatamente/notifica; timeout close local 2000 ms. | 90 %/máx.600 px/90vh; overlay completo permanece montado al pedir ubicación: no se observó ocultamiento/alternancia en fuente. Acceso efectivo al mapa pendiente; no corregido por T1. Cuerpo scroll, footer separado, grid dos columnas (una ≤640), secciones básico/ubicación/pedido. Cabecera degradada padding 1.5rem 2rem (1rem móvil), título 1.5rem: altura sin medir. Referencia R-ADD. |
| X-PED / pedidos, tabla y estadísticas | GET al crear componente; carga «🔄 Cargando pedidos...»; fallo err.message; array vacío → «No se encontraron clientes con pedidos.» como error. Asigna results y ejecuta forEach: respuesta objeto vacío admitida por contrato puede fallar antes del mensaje; hallazgo estático pendiente, no se corrige. Regalo requiere es_regalo === 1; clic con coordenadas emite zoom/cierra. Total suma todas las cantidades; vendidas excluye regalos; valor suma todas ×500, incluso regalo (registro, no cambio). | Máx.1000 px/95vh, cuerpo scroll; tabla máx.400 px/overflow auto, min-width 800 px (600 ≤480), nueve columnas/sticky. Tres tarjetas auto-fit mínimo 200 px, una columna ≤768; mensajes preceden sección. Cabecera 40/36/32 px declarados. Referencia R-PED. |
| X-NOT / notificación global | message no vacío muestra y reinicia timer anterior; vacío oculta. duration por defecto 3000 ms; al destruir limpia timer. App programa borrado message a 3500 ms por llamada sin cancelar timers previos: mensajes consecutivos pueden ocultarse por timeout anterior. Mismo mensaje repetido no tiene garantía de nueva reacción; requiere ejecución. Sin cola/cierre manual. success verde, error rojo; warning geocodificación usa fondo genérico oscuro y textos existentes. | Una instancia; overlay pantalla completa centrado z2000/pointer-events none, contenido auto, padding 15×30 px, min-width250 px/max-width80 %/pointer-events auto. No política adicional de convivencia. Referencia R-NOT. |
| X-MAP / capas, flotantes e información | Casillas cambian capas; radio OSM/satélite; panel toggle; alta flotante abre formulario. Clic feature muestra cliente/pedido, clic fuera/sin feature cierra tooltip; modo selección ubicación tiene prioridad. No indicador visible local de carga/fallo WFS observado. Panel/tooltip no se cierran explícitamente al abrir diálogo; tooltip z10000 puede convivir por encima. | Panel derecha arriba, width250 px, max-height calc(100vh − 200px), scroll; móvil280/260 px con max-width distinto. Flotantes44/40 px declarados; OL30/28 px forzados. Tooltip fijo180–250 px desktop; límites móviles, ajuste JS estima300×200 distinto del CSS; landscape scroll. Mapa permanece DOM. Referencia R-MAP. |

## Alertas nativas: exclusión visual aprobada

| ID | Disparador y mensaje existente | Fuente | Resultado T1 |
| --- | --- | --- | --- |
| A-01 | Buscar dirección vacía: «Por favor, ingrese una dirección.» | S-DIR 8–11 | Disparador inspeccionado; funcionamiento pendiente. |
| A-02 | Respuesta dirección sin latitud/longitud truthy: «No se recibieron coordenadas válidas del backend.» | S-APP 486–495 | Rama inspeccionada; funcionamiento pendiente. |
| A-03 | Catch búsqueda dirección: `Error al buscar dirección: ${error.message}` | S-APP 498–500 | Rama inspeccionada; funcionamiento pendiente; ejemplo ficticio: «Error al buscar dirección: Fallo ficticio». |

En A-01–A-03, apariencia/tema/contraste: **N/A — control del navegador**, conforme a Cobertura/RNF-2. No se sustituyen. No se observan otras llamadas alert en las seis fuentes Svelte inspeccionadas. Los mensajes nativos de validación HTML (required/tipos de campo) dependen del navegador y de la ruta de submit; se registran separados de estas tres llamadas, sin inventar su texto.

## Referencias con datos ficticios

Descripciones para comparación posterior con el código existente; **no son capturas, fixtures ejecutados ni requisitos nuevos**. Sin acceso a API ni escrituras. Los estados de ausencia/fallo ya existen en fuente.

| ID | Experiencia / familias | Escenario y contenido exclusivamente ficticios |
| --- | --- | --- |
| R-NAV | X-NAV; C-NAV/C-BUTTON | Marca RAWEB, cuatro acciones existentes, menú abierto/cerrado y acción activa al abrir cada diálogo. No datos personales. |
| R-DIR | X-DIR; C-DIALOG/C-FIELD/C-BUTTON/C-NOTICE | Dirección «CALLE FICTICIA 100»; entrada vacía para A-01; respuesta sin coordenadas para A-02; error «Fallo ficticio» para A-03. |
| R-CLI | X-CLI; C-DIALOG/C-FIELD/C-CHOICE/C-TABLE/C-NOTICE | Cliente ID9001 «Cliente Ficticio A», dirección «CALLE FICTICIA 100», calle «CALLE FICTICIA», altura100; docenas1.5, PAO101, horario14:30:00, observaciones «Ejemplo ficticio\nSegunda línea». Estado seleccionado, marcado/desmarcado y readonly; horario inválido «25:00:00»; arrays vacío/con fila y fallo ficticio. |
| R-ADD | X-ADD; C-DIALOG/C-FIELD/C-CHOICE/C-BUTTON/C-NOTICE | «Cliente Ficticio B», «CALLE DE EJEMPLO 200», teléfono vacío, cantidad2, PAO102, horario15:00, observación «Alta ficticia, no guardar». Sin coordenadas/con coordenadas ilustrativas lat−35/lon−58; carga y mensajes existentes solo como referencias. |
| R-PED | X-PED; C-DIALOG/C-TABLE/C-STATS/C-NOTICE | Dos pedidos ficticios IDs9001/9002, cantidades1.5/2, es_regalo0/1; teléfono/horario/observación ausentes para N/A; fila normal y regalo. Cálculos de referencia según fuente: total3.5, vendidas1.5, valor1750.00. Sin ejecución de cálculo ni GET. |
| R-NOT | X-NOT; C-NOTICE | «Cliente ficticio actualizado.» success; «Fallo ficticio.» error; warning con mensaje existente de geocodificación, sin datos personales. Mensajes consecutivos/largos y repetidos para comparación posterior de temporizadores. |
| R-MAP | X-MAP; C-PANEL/C-CHOICE/C-FLOAT/C-INFO | Panel con opciones actuales; información de cliente/pedido9001 «Cliente Ficticio A», «CALLE FICTICIA 100», resto ausente N/A, observación ficticia larga. Comparación sobre OSM/satélite sin cambiar cartografía o símbolos. |

## Registro preliminar de evidencias y limitaciones (RF-23)

| ID | Ámbito | Tema / viewport / texto | Resultado al 2026-10-06 | Evidencia o limitación |
| --- | --- | --- | --- | --- |
| E-STATIC | F-COLOR–F-MOTION, C-BUTTON–C-INFO, X-NAV–X-MAP, A-01–A-03 | CSS claro y oscuro parcial; viewport/texto N/A (lectura) | Inspección estática realizada | Fuentes enlazadas S-APP–S-CSS y escenarios R-NAV–R-MAP. No evidencia de cumplimiento renderizado. |
| E-BROWSER | Capturas, contraste efectivo, cabeceras, scroll, teclado, foco y convivencia | Claro/oscuro; 360×800, 800×360, 768×1024, 1366×768; texto200 % móvil vertical/escritorio | Bloqueado en esta sesión para evidencia visual | `chrome-devtools_list_pages` devolvió `Protocol error (Target.setDiscoverTargets): Target closed`. Sin capturas; no se creó evidence/ vacío. Ninguna medida tomada. |
| E-SERVICES | REST/WFS, búsquedas, edición, alta con mapa, pedidos y refresh | Matriz aprobada, pendiente | Pendiente; disponibilidad no comprobada | Sin navegador operativo; no se probaron API/GeoServer/base ni se configuró entorno local ficticio. No afirmar que los servicios estén caídos o accesibles. Sin mutaciones ni validación de flujos. |
| E-THEME | Selector, persistencia, seguimiento dispositivo y ambos temas completos | Claro/Oscuro/Sistema | Pendiente de implementación | Selector N/O, oscuro parcial no acredita RF-13/RF-17/RF-18. |

Esta matriz preliminar deja pendientes las capturas, mediciones y resultados funcionales de la entrega. No completa T40–T50 ni la aceptación de la spec. El inventario T1 se verifica por cobertura documental y enlaces, sin test rojo artificial ni build por no cambiar código.

## Comprobaciones de T1

- Integridad documental: 11 enlaces locales resuelven; IDs únicos: 7 fuentes, 7 fundaciones, 12 familias, 7 experiencias, 3 alertas, 7 referencias ficticias y 4 registros preliminares de evidencia. Sin enlaces ausentes ni IDs duplicados. Revisión manual contra Cobertura/RF-15 realizada.
- `node --test`, ejecutado desde raweb: código de salida **0**; tests **0**, suites **0**, pass **0**, fail **0**, cancelled **0**, skipped **0**, todo **0**; duration_ms **85.029307**. La ausencia de tests no constituye cobertura funcional.
- No se ejecutó build: T1 solo modifica documentación. Verificación renderizada/funcional pendiente según E-BROWSER/E-SERVICES; T1 documental completada, no aceptación de RF-23 completo.

## Evidencia incremental T9

| ID | Ámbito / RF | Tema / viewport | Resultado | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T9 | F-COLOR/F-TYPE/F-SPACE/F-BORDER/F-ELEVATION, clases C-BUTTON/C-FIELD/C-CHOICE y foco; RF-1, RF-2, RF-5, RF-13, RF-19 | Claro/oscuro; 360×800, 800×360, 768×1024, 1366×768; texto normal | Pasa criterio aislado T9 | [Rojo/verde, escalas, dimensiones y contraste renderizado](t9-verification.md). Carga global→DS→bundle comprobada; sin cambio de dimensiones/movimiento. No acredita migración ni matriz final; mensajes/tokens restantes, selección nativa, transparencias/degradados/mapa y servicios pendientes. |

## Evidencia incremental T10

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T10 | F-COLOR, paleta opaca; RF-13, RF-23; RNF-2 | Claro/oscuro; viewport/texto N/A (cálculo numérico) | Pasa criterio de lógica T10 | [Rojo/verde, 68 pares y listado de mediciones renderizadas pendientes](t10-verification.md). 23 tests pasan y build Windows código0. No hay ejecución navegador nueva ni integración; no acredita contraste efectivo completo ni aceptación de la spec. |

## Evidencia incremental T11

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T11 | X-NAV, C-NAV/C-THEME; RF-11, RF-15–RF-19 | Claro/oscuro; 360×800, 800×360, 768×1024, 1366×768; texto normal | Pasa criterio integrado T11 | [App real: rojo/verde, ubicación, altura previa/actual, teclado, persistencia y dispositivo](t11-verification.md). Tres opciones restauradas por recarga/reapertura; header sin fila nueva. Chrome Windows/CDP con WFS vacío y cartografía controlada; cero errores/mutaciones. No acredita servicios/flujos de negocio, retorno de foco, texto200 %, contraste completo ni aceptación final. Convivencia previa del menú/flotantes registrada como límite. |

## Evidencia incremental T12

Registro histórico T12; su mención «T13 no ejecutada» corresponde al cierre de esa tarea, actualizado por E-T13 abajo.

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T12 | X-NAV/X-DIR/X-CLI/X-ADD/X-PED, C-DIALOG; RF-9, RF-16, RF-21 | Claro/oscuro; 360×800, 800×360, 768×1024, 1366×768; texto normal | Pasa coordinación integrada T12 | [Rojo/verde real: disparador, retorno tras desmontaje, Menú cerrado y selección de punto sin retorno/reapertura](t12-verification.md). Cuatro diálogos/alta flotante y cierres adicionales; punto actualiza coordenadas con eventos DOM dirigidos al viewport real. Overlay previo no acredita clic físico mapa; alta integral pendiente T21/T46. Cero errores/escrituras persistentes; guardados/servicios reales no ejecutados. 23 tests y build Windows pasan. Foco interior/cabeceras/200 %/aceptación final pendientes; T13 no ejecutada. |

## Evidencia incremental T13

| ID | Ámbito / RF | Tema / viewport / texto | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T13 | X-DIR, C-DIALOG, A-01; RF-9, RF-14, RF-21 | Ambos temas; cuatro viewports; texto200 % de cabecera móvil vertical/desktop | Pasa criterio literal integrado T13 | [Rojo/verde real, cabecera41/45 px, ampliada49/89 px sin recorte, foco/retorno/cierres y dos alertas nativas](t13-verification.md). Cero errores/soloGET/sin mutaciones, 23 tests y build Windows pasan. A-01 funcionamiento pasa, apariencia/tema/contraste N/A navegador. Servicios/POST válido, colores/contraste y ampliación integral pendientes; no completa T14/T44 ni aceptación final. |

## Evidencia incremental T14

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T14 | X-DIR, C-FIELD/C-BUTTON/C-NOTICE; RF-4–RF-7, RF-11–RF-13, RF-19 | Claro/oscuro; 360×800, 800×360, 768×1024, 1366×768 | Pasa criterio literal integrado T14 | [Rojo/verde Chrome Windows, muestras de contraste/foco, Enter y Buscar, POST controlado, alertas/mensajes](t14-verification.md). Sin API/WFS reales ni escrituras; cero errores. No completa T44 ni aceptación final. |

## Evidencia incremental T51

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T51 | X-DIR, C-DIALOG/C-FIELD/C-BUTTON; RF-13, RF-14, RF-24; RNF-2 | Claro/Oscuro; estilos actuales aportados por usuario. Viewports/altura referidos solo a T14 | Pasa criterio literal integrado T51 | [Baseline y atribución de evidencia](t51-baseline.md): `getComputedStyle` actual aportado por usuario, pares de contraste calculados; capturas/mediciones Chrome automatizadas T14 reutilizadas. Capturas actuales con límites colapsados; no implican nuevos rectángulos/mediciones de altura. No completa RF-24 ni aceptación final. |

## Evidencia incremental T52

| ID | Ámbito / RF | Tema / viewport / texto | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T52 | X-CLI, C-DIALOG/C-FIELD/C-BUTTON/C-CHOICE/C-TABLE/C-NOTICE; RF-11, RF-13, RF-16, RF-24; RNF-2 | Claro/Oscuro; 360×800, 800×360, 768×1024, 1366×768 efectivos; texto 200 % móvil/escritorio | Pasa criterio visual T52 | [Capturas, corrección de foco/selección, contrastes y cabeceras](t52-implementation.md), [medidas crudas](t52-browser-evidence.json). Chrome DevTools real, cliente ficticio; cabeceras44/48 px, modal352 px a viewport360. Texto≥4.5 y controles/indicadores≥3. Búsqueda mock y capturas finales WFS vacío fetch/XHR; sin PUT real. Contratos/eventos T16/T18 reutilizados, negocio sin cambios. Consola final limpia; runner23/23 y build Windows0. No acredita integración real T45, T55 ni aceptación final; T53 no iniciada. |

## Evidencia incremental T15

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T15 | X-CLI, C-DIALOG; RF-9, RF-14, RF-21 | Claro/oscuro; 360×800, 800×360, 768×1024, 1366×768 | Pasa criterio literal integrado T15 | [Rojo/verde Chrome Windows, cabecera, foco/retorno, ancho/scroll/animación](t15-verification.md). No se ejecutaron búsquedas ni operaciones REST; capas/teselas externas interceptadas. No acredita T16 ni aceptación final. |

## Evidencia incremental T16

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T16 | X-CLI, campos y acciones C-FIELD/C-BUTTON; RF-4–RF-7, RF-11–RF-13, RF-19 | Claro/oscuro; 360×800, 800×360, 768×1024, 1366×768 | Pasa criterio literal de T16 | [Rojo/verde Chrome Windows, clases/tokens/foco, carga, validaciones vacías y tres payloads](t16-verification.md); [Claro](t16-light.png), [Oscuro](t16-dark.png). POST/WFS/teselas interceptados; sin escrituras ni servicios reales. No incluye la tabla/filas de T17 ni aceptación final. |

## Evidencia incremental T17

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T17 | X-CLI, tabla C-TABLE y filas; RF-4, RF-5, RF-19 | Claro; Chrome viewport escritorio, contenedor estrecho 258 px | Pasa criterio literal T17 | [Rojo/verde Chrome Windows: clic/Enter/Espacio una vez, descendiente, 5 columnas y overflow horizontal](t17-verification.md). Búsqueda REST ficticia interceptada; sin mutación. No cubre edición/PUT de T18 ni aceptación final. |

## Evidencia incremental T18

| ID | Ámbito / RF | Tema / viewport / texto | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T18 | X-CLI, campos/acciones de edición C-FIELD/C-CHOICE/C-BUTTON; RF-4–RF-7, RF-11–RF-13, RF-16, RF-19 | Claro/oscuro; 360×800, 800×360, 768×1024, 1366×768; texto normal | Pasa criterio literal T18 | [Rojo/verde Chrome Windows, bindings, PUT y eventos](t18-verification.md); [captura oscuro](t18-dark.png). POST búsqueda, PUT, geocodificación, WFS y teselas interceptados con datos ficticios; no se mutó backend real. La comprobación no sustituye T45 ni aceptación final. |

## Evidencia incremental T19

| ID | Ámbito / RF | Tema / viewport / texto | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T19 | X-ADD, cabecera/foco C-DIALOG; RF-9, RF-14, RF-21 | Claro/oscuro; 360×800, 800×360, 768×1024, 1366×768; texto normal | Pasa criterio literal T19 | [Rojo/verde Chrome Windows/CDP, mediciones y cierres](t19-verification.md); ocho capturas. Header 44–48 px; foco dentro al abrir, cierre Enter y retorno al disparador visibles. Mapa sigue en DOM; no se ejecutaron selección de ubicación ni guardado (T21/T46). WFS/teselas interceptados; cero mutaciones. No completa alta integral ni aceptación final. |

## Evidencia incremental T20

| ID | Ámbito / RF | Tema / viewport / texto | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T20 | X-ADD, campos básicos C-FIELD; RF-4, RF-5, RF-7, RF-11, RF-13 | Ambos temas previstos; viewport no comprobado | Bloqueado: falta verificación renderizada | [Cambios, auditoría de contratos y comprobaciones](t20-verification.md). Los cinco controles conservan tipo, asociación, binding y atributos/reglas existentes; clases y CSS aplican tokens comunes. `node --test` 23/23 y build Windows sin warnings. Chrome CDP no disponible (`Target closed`), por lo que no se marca pasa ni se cierra T20. Sin requests ni mutaciones ejecutadas. |

## Evidencia incremental T21

| ID | Ámbito / RF | Tema / viewport / texto | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T21 | X-ADD, campos de pedido C-FIELD/C-CHOICE/C-BUTTON/C-NOTICE y selección de ubicación; RF-4–RF-7, RF-9, RF-12, RF-16, RF-19–RF-21 | Claro/oscuro; Chrome viewport escritorio | Pasa criterio literal T21 | [Rojo/verde Chrome Windows/CDP](t21-verification.md): clic físico OpenLayers actualiza coordenadas sin cerrar el alta; cuatro campos renderizados en ambos temas; Cancelar sin POST y Guardar con payload/evento ficticio preservados. POST interceptado, sin mutaciones ni errores. No acredita servicios reales, matriz RNF-3 ni aceptación global. |

## Evidencia incremental T24

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T24 | X-PED, C-STATS/C-NOTICE; RF-4, RF-6, RF-11, RF-13, RF-16 | Tokens aplicables a claro/oscuro; viewport no medido | Implementación, runner y build pasan; navegador pendiente | [Cambio, referencia ficticia y comprobaciones](t24-verification.md). Fórmula y precio intactos; valores R-PED: 3.5, 1.5 y 1750.00. Fallo previo de respuesta `{message: ...}` queda registrado. El pase integrado T22–T24 no se declara verificado. |

## Evidencia incremental T25

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T25 | X-NOT, C-NOTICE; RF-6, RF-8, RF-11, RF-13, RF-16 | Claro/oscuro; viewport y render no medidos | Implementación, runner y build pasan; navegador pendiente | [Tokens semánticos y conservación de temporización/sustitución/cierre](t25-verification.md). Chrome bloqueado por `Target closed`; la variante warning/otros y las señales temporales no se declaran visualmente verificadas. |
| E-T26 | X-MAP, C-PANEL/C-CHOICE; RF-4, RF-5, RF-15, RF-16, RF-19, RF-20 | Claro/oscuro; Chrome Windows Headless 154, viewport por defecto | Pasa criterio literal T26 | [Rojo/verde integrado](t26-verification.md): superficies/acentos por tema, nombres AX, foco/teclado de casillas, radios y toggle; WFS/teselas de prueba controladas. WFS Clientes generó una solicitud GET adicional al activar su visibilidad; satélite activó su endpoint de teselas. Sin mutaciones ni errores. No verifica API/GeoServer reales, matriz completa RNF-3, coexistencia de paneles ni aceptación final. |
| E-T27 | X-MAP, C-FLOAT; RF-4, RF-5, RF-15, RF-19–RF-21; RNF-2 | Claro/Oscuro; 360×800 móvil y 1034×605 escritorio; OSM real | Pasa criterio literal T27 | [Corrección de foco y verificación real](t27-verification.md). Chrome DevTools página 1 midió píxeles del canvas OSM: Claro ≥3.2330:1; halo oscuro ≥8.5761:1. Posición/tamaño, zoom, nombres AX, foco/retorno y apertura/cierre verificados; Alta deja el mapa montado y no se guarda. Sólo GET WFS/OSM, sin mutaciones; 23/23 tests y build Windows pasan. Build WSL bloqueado por opcional de Rollup ausente. No completa T28 ni aceptación final. |
| E-T28 | X-MAP, C-INFO; RF-4, RF-15, RF-16, RF-19 | Claro/Oscuro; 360×800 y 800×360; fixtures ficticios | T28 completa; integración de Pedido pasa | [Rojo/verde, fixture WFS aislado y límites](t28-verification.md). Fixture DOM sintético: Claro #fff/#1f2937; Oscuro #1f2937/#f9fafb; scroll 306 px a 800×360. InitScript previo interceptó solo GetFeature WFS Clientes/Pedidos; una respuesta Pedido sintética fue renderizada por OpenLayers/App real. Clic marcador abrió `role=dialog` con nombre y contenido ficticios; clic interior conserva; clic exterior cierra; Enter/Espacio no generan selección. Oscuro medido #1f2937/#f9fafb. Cero solicitudes de Clientes en esta carga: esa variante no queda comprobada integradamente. Sin mutaciones/guardados ni lectura/transcripción de respuestas reales. Runner23/23, build Windows0 previos, sin cambios de código. |

## Pase integrado T22–T24

| ID | Ámbito | Tema / viewport | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T22-T24 | X-PED, cabecera/foco, filas/zoom/scroll, tarjetas/mensajes; RF-4–RF-6, RF-9, RF-11–RF-14, RF-16, RF-19, RF-21, RF-23 | Claro/Oscuro; medidas completas atribuidas a T54 | Bloqueo histórico superado para el pase RF-24 | [`T22–T24`](t22-t24-integration-verification.md) conserva el intento inicial bloqueado. El pase T55 con Chrome DevTools verificó superficies en ambos temas; medidas de teclado, filas, scroll, cálculos y texto200 se reutilizan de `t54-verification.md`. No se inspeccionaron respuestas WFS reales; T47 y aceptación final siguen pendientes. |

## Evidencia correctiva T53 — RF-24

| ID | Ámbito / RF | Tema / viewport / texto | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T53 | X-ADD, superficies/cabecera/secciones/labels/campos/acciones/casillas/footer/estados; RF-11, RF-13, RF-16, RF-24; RNF-2/RNF-3 | Claro/Oscuro; 360×800, 800×360, 768×1024, 1366×768; 200 % móvil vertical/escritorio | Pasa T53; parar antes de T54 | [Rojo/verde, contraste efectivo y flujos](t53-verification.md), [JSON](t53-browser-evidence.json), capturas. Sin degradados; header44/48 px normal, sin clipping; clic físico en mapa escritorio/móvil, Cancelar sin POST adicional, alta completa ficticia y cierre/foco. REST/WFS mock; sin escrituras reales. Success inline no visible por cierre inmediato existente; pares semánticos intactos. Runner exacto23/23 y build Windows0. No sustituye T46/T55 ni aceptación final. |

## Evidencia correctiva T54 — RF-24

| ID | Ámbito / RF | Tema / viewport / texto | Resultado al 2026-10-06 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T54 | X-PED, modal/cabecera/títulos/cierre/secciones/tabla/filas/estadísticas/carga/error; RF-11, RF-13, RF-16, RF-19, RF-21, RF-24; RNF-2/RNF-3 | Claro/Oscuro; 360×800, 800×360, 768×1024; 200 % móvil/escritorio | Pasa T54; hallazgo Enter resuelto | [Matriz/contraste y cierre autorizado](t54-verification.md), [JSON visual original](t54-browser-evidence.json), [rojo/verde teclado nativo](t54-keyboard-evidence.json), capturas. Evidencia visual anterior reutilizada, CSS intacto: cabecera41 px, texto≥4.5 y bordes/foco≥3; estadísticas/carga/vacío conservados. Corrección única preventDefault para Enter/Espacio aceptados: clic/teclado zoom/cierre una vez, un GET por apertura, foco Pedidos o Menú cerrado. Repeat/descendientes dirigidos sin interceptar. Runner exacto23/23 (340.006446 ms), build Windows0 (7.5 s); fixtures sin escrituras, ningún error y warning meta previo. Reload preparatorio GET WFS real sin inspección de cuerpos, init restaurado antes de casos verdes. Objeto vacío previo sin corregir; no acredita servicios/T47 ni aceptación final. |

## Evidencia integrada T55 — RF-24

| ID | Ámbito / RF | Tema / viewport | Resultado al 2026-10-07 | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T55 | Cuatro diálogos; superficies/títulos/campos/acciones/estados, contraste/cabeceras, conservación de flujos; RF-13–RF-16, RF-23–RF-24; RNF-1–RNF-3, RNF-6 | Claro/Oscuro; pase directo Chrome DevTools 1366×768 y Cliente 360×800; dimensiones completas/200 % reutilizadas de T52–T54 | Pasa matriz T55 | [Matriz integrada y procedencia de evidencias](t55-verification.md). Dirección baseline #fff/#1f2937 y #1f2937/#f9fafb; Cliente, Alta y Pedidos usan las mismas superficies/tokens; Alta sin degradado. Medidas completas anteriores enlazadas por diálogo, no atribuidas al pase directo. `node --test`23/23, build Windows0 (12.1s), consola inspeccionada limpia. Búsqueda ficticia solo lectura devolvió vacío; GET WFS/tiles iniciales no inspeccionados. Sin escrituras. T27 y T28–T50, servicios reales y aceptación final pendientes. |

## Evidencia incremental T29

| ID | Ámbito / RF | Tema / base / viewport | Resultado | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T29 | Controles DOM OpenLayers: zoom y atribución; RF-5, RF-13, RF-15, RF-19, RF-20 | Claro/Oscuro × OSM/Satelital; Chrome 800×360 | Pasa criterio literal T29 | [Rojo, build Windows y verificación final](t29-verification.md). Defecto rojo: enlace OSM en Oscuro 2,54:1; parche CSS local usa tokens. Runner 23/23 y build Windows0. Controles habilitados, nombres AX, foco/Enter; enlace OSM 5,1686:1 Claro y 8,1403:1 Oscuro. GET WFS sustituido por fixture vacío; sin mutaciones. El canvas no presentó cambio de tamaño/estilo durante cambios de tema/capa; no había features WFS para comparar geometrías/símbolos. |

## Evidencia incremental T30

| ID | Ámbito / RF | Tema / viewport / texto | Resultado | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T30 | Viewport, tipografía heredada, shell/nav/controles, cabeceras; RF-11, RF-14, RF-16, RF-19; RNF-3 | Claro/Oscuro; Chrome 360×800 móvil y 1366×768 desktop; texto ×2 aplicado con DevTools sin cambiar viewport/DPR | **Parcial; T30 sin marcar** | [Referencia, resultados y limitaciones](t30-verification.md). Rojo de fuente: viewport prohibía zoom, Arial anulaba el tema/herencia y shell era `overflow:hidden`. Verde: viewport sin restricciones, familia heredada, shell desplazable, acciones/selector accesibles y cabeceras/títulos/cierres contenidos en ambos temas. Nuevo intento CDP en `localhost:52948`: pinch 1.5× agotó 30 s y único reintento también; escala permaneció 1, DPR 1 y viewport restaurado. Solo metadatos de `GET /geoserver/ows?...` WFS, fallido sin status HTTP; no se leyeron respuestas/cuerpos. No se demuestra pinch ni aislamiento total de red. Runner/build previamente pasan y no se repitieron. La anotación original de T31 bloqueada quedó superada por la replanificación aprobada; E-T31 registra su contrato de datos completado sin alterar T30. |

## Evidencia incremental T31 — contrato de inventario

| ID | Ámbito / RF | Resultado | Evidencia y límite |
| --- | --- | --- | --- |
| E-T31 | 12 familias C-BUTTON–C-INFO; referencias RF y experiencias; variantes/estados; A-01–A-03; RF-1–RF-4, RF-10, RF-22, RF-23 | Pasa contrato de datos T31 | [Contrato, matrices rojo/verde y comandos](t31-verification.md). Módulo puro `src/design-system/catalog.mjs`; 12 IDs, 41 variantes, 48 estados aplicables, 34 no aplicables y 3 alertas nativas. Cada declaración remite al inventario T1; estados no aplicables tienen motivo. Apariencia/contraste de alertas N/A por control del navegador; disparador/mensaje/funcionamiento quedan verificables. No es catálogo visual ni aceptación RF-22/RF-23 completa. T30 sigue parcial. La referencia histórica de bloqueo de T32 fue reemplazada por la replanificación aprobada; ver E-T32. |

## Evidencia incremental T56 — cierres RF-24

| ID | Ámbito / RF | Tema / viewport | Resultado | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T56 | Cierres de los cuatro diálogos: caja, forma, color, hover/foco/cierre; RF-19, RF-20, RF-24; RNF-2/RNF-3 | Chrome sin Dark Reader; Claro/Oscuro; matriz previa de cuatro viewports, más Pedidos 1366×768 y 360×800 | **T56 completa** | [Mediciones, evidencia integrada y límites](t56-verification.md). Dirección/Cliente/Alta verificados previamente; Pedidos medido en desktop claro/oscuro (32×32) y móvil claro/oscuro (36×36), círculo completo, transparente, radios/colores/foco equivalentes; cierre y retorno de foco al disparador o a Menú con menú cerrado. App en `localhost:52948`; WFS `/geoserver/ows` 502 y OPTIONS/GET Pedidos `ERR_CONNECTION_REFUSED` prueban que no se recibieron registros. No se inspeccionaron headers/cuerpos/atributos ni contenido de tabla; OSM 200/304; sin mutaciones. Runner 26/26 y build Windows0 (7.4 s) reutilizados, sin repetirlos por no haber cambios de código. |
| E-T57 | Apertura/foco preferido Dirección, Cliente y Alta; RF-21 | Chrome sin Dark Reader; Claro/Oscuro; 1366×768 y móvil táctil 360×800 | **T57 completa** | [Rojo/verde, runner/build, foco/teclado, retorno y límites del teclado móvil](t57-verification.md). Tres IDs correctos y visibles con outline 3 px; cursor listo para escribir, recorrido Tab/Mayús+Tab y retorno comprobados; no hubo solicitudes REST nuevas al abrir/focalizar. WFS inicial GET continuó 502 y no se inspeccionaron cuerpos; cero mutaciones. La emulación táctil del host de escritorio no expone teclado virtual del sistema operativo: limitación no bloqueante, pues RF-21 requiere foco real en el input y el teclado móvil no se suprime. Una comprobación en dispositivo físico podría complementar evidencia, sin quedar como pendiente de tarea. |

## Evidencia incremental T32 — entrada del catálogo

| ID | Ámbito / RF | Tema / viewport | Resultado | Evidencia y límite |
| --- | --- | --- | --- | --- |
| E-T32 | Entrada aislada del catálogo; RF-10, RF-22 | Chrome en `localhost:52948`; catálogo directo/recarga; ruta normal 1366×768 y menú móvil 360×800 | **Pasa T32** | [Regresión roja, corrección y verificación](t32-verification.md). Roja normal: CSS de App ausente; navbar computaba `display:block`, transparente; grupo y cada botón medían 1358 px frente a `button {width:100%}` global. Verde tras import estático sin montar App en catálogo: CSS scoped presente; navbar `flex`, row/wrap, 68 px; grupo 743.56×44 px; cuatro botones `width:auto` en la misma fila que Tema; móvil muestra hamburguesa 44×48 y menú con cuatro acciones/Tema. Catálogo directo y recarga: título/inventario presentes, sin navbar/mapa/App en DOM; 6 GET locales cada carga y cero `/api`, `/buscar_direccion` u `/ows`. Ruta normal monta mapa; WFS inicial rechazado (`ERR_CONNECTION_REFUSED`) y teselas OSM; no se leyeron cuerpos ni hubo mutaciones o REST. Consola: warning de meta obsoleta y error WFS solo en ruta normal. Runner 33/33 y build Windows código 0 ejecutados tras el arreglo. T30 incompleta; T50 espera T30. |
| E-T33 | Fundaciones e identidad del catálogo; RF-1–RF-3, RF-13, RF-22; RNF-5 | Claro/Oscuro; Chrome 1366×768 y 360×800 | **Pasa T33** | [Referencia roja, ejemplos y verificación](t33-verification.md). Directo en query; valores/tokens, propósito, muestras de color/tipo/espacio/bordes/radios/sombras/iconografía y comparación con identidad actual visibles en ambos temas. Claro/Oscuro verificados por `data-theme` y valores computados; layout 336 px a 360 sin overflow horizontal y 960 px a 1366. Seis GET locales, cero API/búsqueda/WFS; consola sin errores (warning preexistente meta). Runner33/33 y build Windows código0. Catálogo no añade selector de tema; contraste visual integral de todos los estados permanece fuera de T33. T30 incompleta; T50 espera T30; T34 no iniciada. |
