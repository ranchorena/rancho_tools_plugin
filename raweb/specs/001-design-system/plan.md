# Plan 001 — Design system de raweb

Estado: T31, T32, T56 y T57 completadas. Replanificación T32/T30/T50 aprobada explícitamente con respuesta exacta «si»; T32 verificada en navegador. T30 permanece incompleta y sin marcar; pinch físico/real diferido al usuario; T50 espera a T30.
Base: spec 001 y enmiendas aprobadas explícitamente, incluida RF-21. La revisión previa de T56 con dimensiones propuestas de 28×28 px escritorio/36×36 px móvil queda sustituida. La versión vigente fija el baseline medido de 32×32 px escritorio y 36×36 px hasta 768 px.

## 1. Inspección y restricciones

- Svelte 3.59, Rollup 4, OpenLayers 10; `package.json` es ESM. No hay suite ni script de test preexistente. Se usarán pruebas nativas de Node, sin dependencias nuevas.
- `src/main.js` monta `App.svelte`. Este conserva mapa, WFS, visibilidad de diálogos y sus suscripciones; cada formulario conserva sus llamadas REST y reglas de negocio.
- `public/global.css` y CSS local compiten por tipografía, colores, tamaños y foco. Hay temas parciales automáticos en BuscarCliente y reglas locales de reducción de movimiento; sustituir únicamente la resolución de colores por tema explícito y mantener las animaciones/preferencias existentes.
- Los formularios tienen marcos y anchuras diferentes. Compartir presentación y cabecera sin homogeneizar distribución, posición ni flujo. El alta sigue alternando con selección de ubicación y devuelve `{lat, lon}`.
- `public/index.html` limita zoom con `user-scalable=no,maximum-scale=1`. Retirar esas restricciones para poder verificar RNF-3; conservar las demás opciones de viewport. El cambio sirve al texto ampliado aprobado, no añade otra política de accesibilidad.
- Hay filas clicables sin teclado en BuscarCliente/Pedidos. Añadir activación equivalente sin alterar selección ni zoom. Las alertas nativas siguen intactas y se registran como exclusión visual.
- No se prevén cambios de API, configuración de URLs, backend, dependencias, cartografía ni simbología. No editar bundles ni publicar `.env` o datos reales.

## 2. Arquitectura propuesta y responsabilidades

Rutas relativas a `raweb/`. Los archivos nuevos son propuestas, no existen todavía.

| Archivos | Responsabilidad | Trazabilidad |
| --- | --- | --- |
| `public/design-system.css`, `public/global.css`, `public/index.html` | Variables semánticas por tema, escalas visuales, clases reutilizables para controles/campos/tablas/paneles/mensajes, foco; cargar CSS compartido después de global y antes del bundle. Reducir reglas duplicadas al migrar, conservando tamaños particulares. | RF-1–RF-8, RF-11, RF-13–RF-16, RF-19; RNF-1–RNF-4 |
| `src/design-system/theme.mjs`, `theme-controller.mjs` | Política pura y adaptador de preferencia, almacenamiento y `matchMedia`; aplicar `data-theme` al documento y suscribir/limpiar cambios del dispositivo. | RF-17, RF-18; RNF-4 |
| `src/design-system/focus-policy.mjs`, `dialog-focus.mjs`, `keyboard.mjs` | Elegir destino de retorno mediante hechos de visibilidad; acción de foco interior y coordinador de retorno; activación de filas por Enter/Espacio. Sin captura global de Tab ni bloqueo del mapa. | RF-9, RF-19–RF-21; RNF-6 |
| `src/design-system/Button.svelte`, `DialogHeader.svelte`, `ThemeSelector.svelte` | Primitivas Svelte 3: botón nativo, cabecera compacta con título/cierre y selector etiquetado «Tema». | RF-4, RF-5, RF-14, RF-17, RF-19, RF-20 |
| `src/App.svelte` | Integración tema en barra/menú; captura de disparador; retorno tras cierre; navegación, panel de capas, controles flotantes e información del mapa. Preservar instancia de mapa y eventos. | RF-9, RF-11–RF-21 |
| `src/BuscarDireccionDialog.svelte` | Migrar presentación/cabecera, foco interior; preservar evento `buscar`, `close`, Enter/Escape y alerta vacía. Constituye baseline visual de RF-24. | RF-4–RF-7, RF-9, RF-11–RF-16, RF-19–RF-21, RF-24 |
| `src/BuscarCliente.svelte` | Migrar búsqueda/edición, tabla y filas activables; no modificar `fetchData`, payloads ni eventos. Las superficies, títulos, campos, acciones y estados del diálogo siguen RF-24. | RF-4–RF-7, RF-9, RF-11–RF-16, RF-19–RF-21, RF-24 |
| `src/AgregarCliente.svelte` | Migrar campos/mensajes/cabecera; mantener prop coordenadas, selección de mapa, validaciones y cierre. Eliminar el degradado exclusivo y aplicar patrón RF-24, sin alterar estructura/tamaños. | RF-4–RF-7, RF-9, RF-11–RF-16, RF-19–RF-21, RF-24 |
| `src/Pedidos.svelte` | Migrar cabecera, tabla, filas y estadísticas; conservar cálculos, carga y `zoomToLocation`. Superficies/títulos/controles/estados del diálogo siguen RF-24. | RF-4–RF-6, RF-9, RF-11–RF-16, RF-19–RF-21, RF-24 |
| `src/GlobalNotification.svelte` | Solo presentación de variantes existentes; conservar mensaje, temporizadores, sustitución y ausencia de cierre manual. | RF-6, RF-8, RF-11, RF-13, RF-15, RF-16 |
| `src/design-system/catalog.mjs`, `Catalog.svelte`, `examples/*.svelte`, `src/main.js` | Inventario y ejemplos interactivos ficticios. Seleccionar catálogo mediante `?catalog=design-system` en el mismo entry; importar App pero no montarla en ese modo, sin consultas REST/WFS. | RF-1–RF-5, RF-10, RF-22; RNF-5 |
| `docs/design-system/guide.md`, `coverage.md`, `evidence/` | Guía, comparación de identidad, uso/variantes/no aplicables y registro de comprobaciones con IDs, tema, estado, viewport, resultado y limitaciones. | RF-1–RF-4, RF-6–RF-10, RF-22, RF-23; RNF-1–RNF-6 |
| `tests/design-system/*.test.mjs`, `tests/design-system/support/contrast.mjs` | Pruebas de políticas y contratos de catálogo/paleta; no simulan render real ni API. | RF-17–RF-21, RF-22, RF-23; RNF-1, RNF-2 |

### Responsabilidad de la tarea de seguimiento T56

T56 verificará/ajustará únicamente los cuatro botones `.close-button` de `BuscarDireccionDialog.svelte`, `BuscarCliente.svelte`, `AgregarCliente.svelte` y `Pedidos.svelte` para igualar el baseline renderizado documentado en T51: círculo completo, dimensiones renderizadas reales de 32×32 px en escritorio y 36×36 px hasta 768 px, colores y estados interactivos/de foco equivalentes. En cada viewport y tema el círculo debe verse completo, sin clipping ni sobresalir de forma inconsistente de la cabecera. Mantendrá nombre accesible, activación, handler, emisión/cierre, foco y flujo existente. No tocar Cancelar/Guardar ni otras reglas de diálogo.

### Responsabilidad propuesta para T57 — destino preferido de foco de apertura

T57 extenderá `src/design-system/dialog-focus.mjs` para aceptar un destino preferido mediante marcador/acción explícita y, tras `tick`, enfocarlo realmente si existe, está habilitado y visible; si falta, está oculto o deshabilitado, conservará el fallback actual al primer control habilitado y visible (o al contenido con `tabindex=-1`). Los formularios marcarán como preferidos exactamente `#direccion-input` en `BuscarDireccionDialog.svelte`, `#search-cliente` —búsqueda por nombre, no el campo Nombre de solo lectura— en `BuscarCliente.svelte`, y `#nombre` en `AgregarCliente.svelte`. No se alteran búsquedas, handlers, cierre/retorno, ni la selección de ubicación; el foco no enviará formularios ni solicitudes. Otros diálogos conservan el foco al interior mediante el comportamiento actual. La acción no atrapará Tab/Mayús+Tab ni suprimirá el teclado móvil nativo.

### Reutilización sin trasladar reglas de negocio

Campos, selecciones, tablas, mensajes, tarjetas y paneles reutilizan clases CSS explícitas sobre elementos nativos; se conservan `bind:value`, `bind:checked`, `bind:group`, IDs y asociaciones actuales. No crear wrappers para cada tipo de input ni una tabla genérica con callbacks nuevos. Button y DialogHeader se usan en producto y catálogo, sin extraer el marco de todos los diálogos ni cambiar su overlay. CSS local retiene solo disposición y particularidades necesarias; reemplazar colores literales por variables compartidas para evitar que el CSS del bundle anule los temas.

OpenLayers mantiene controles nativos, geometrías, fuentes y animaciones. Sus controles DOM usan variables y reglas acotadas `.ol-control` dentro del mapa; no recolorear canvas ni símbolos WFS.

## 3. Interfaces y funciones

Identificadores nuevos en inglés; textos/documentación/comentarios en español. Usar `export let`, slots, `on:click` reenviado y acciones `use:` de Svelte 3; no runas ni APIs Svelte 5.

### Políticas puras

- `normalizeThemePreference(value) -> 'light' | 'dark' | 'system'`: elección desconocida/ausente se interpreta como system; no almacena nada.
- `resolveTheme(preference, systemIsDark) -> 'light' | 'dark'`: elección explícita prevalece sobre dispositivo; system sigue el dispositivo.
- `chooseFocusReturn({ triggerPresent, triggerVisible, openedFromMobileMenu, menuButtonPresent, menuButtonVisible }) -> 'trigger' | 'menu' | null`: devolver disparador visible; si desapareció la acción móvil, usar Menú visible; no inventar otro destino ni reabrir el menú.
- `shouldActivateRow(key, isRepeat, targetIsRow) -> boolean`: Enter/Espacio en la propia fila, sin repetir activación ni interceptar controles descendientes; adaptador evita scroll al activar con Espacio.
- `contrastRatio(foreground, background) -> number` en soporte de pruebas: sRGB opaco para pares declarados en CSS; resultado sin redondear antes de comparar umbral. Para transparencias/degradados, composición y medición del render en navegador, no fingir equivalencia con pares opacos.

**T57 — extensión de dialogFocus:** resolver tras `tick` el destino preferido declarado por el diálogo y enfocarlo realmente solo si está presente, habilitado y visible. Si no es utilizable, aplicar sin cambios el fallback al primer control habilitado/visible y, como último recurso, al contenido `tabindex=-1`. Mantener cancelación al desmontar. Esta selección de destino no activa el control, no envía el formulario ni invoca handlers de búsqueda.

No se introducen reglas de fechas ni cálculo temporal. No hace falta parámetro `today`/«hoy» en estas funciones; si surgiera una función temporal legítima, recibirá fecha explícita y no leerá reloj global. No refactorizar temporizadores ni cálculos de negocio por este trabajo.

### Adaptadores con efectos

- `createThemeController({ storage, mediaQuery, applyTheme, onPreferenceChange }) -> { start, setPreference, destroy }`: almacenamiento local bajo clave versionada `raweb.theme.v1`, valores light/dark/system; textos Claro/Oscuro/Sistema. `storage` y `mediaQuery` inyectables. Lectura/escritura encapsuladas: si el navegador rechaza almacenamiento, mantener elección durante la sesión; documentar que no pudo verificarse persistencia allí, sin introducir mensajes nuevos.
- `dialogFocus(node) -> { destroy }`: foco a primer control habilitado del contenido después del montaje; si no hay control, contenido con tabindex -1. Sin focus trap, inert ni nuevas reglas Escape/backdrop. No restituir foco en destroy automáticamente: el padre distingue cierre final de cambios internos/selección de ubicación.
- Coordinación en App: conservar `event.currentTarget` y origen móvil antes de cerrar menú; tras cierre final y `tick()`, medir presencia/visibilidad y ejecutar destino elegido. Todas las rutas de cierre existentes pasan por ese retorno, incluidos guardado/búsqueda/selección de pedido. Selección de punto no es cierre final.

### Componentes

- `Button`: props `variant`, `type='button'`, `disabled`; slot para texto/icono; resto de atributos nativos y `on:click`, `on:keydown`, `on:focus` reenviados. Prop explícita para clase adicional si se necesita conservar disposición. En formularios existentes, especificar siempre type original para no provocar submit accidental.
- `DialogHeader`: `titleId`, slot título, slot acción de cierre. No conoce ni despacha operaciones de negocio; consume Button cuando corresponda. Altura natural con tipografía/padding calibrados: ≤48 px título de una línea y ≤64 px dos líneas móvil a tamaño normal; permitir crecer al ampliar texto, sin max-height/overflow que recorte. No medir texto para truncarlo.
- `ThemeSelector`: prop `value`, evento `change` con preferencia; select nativo y label «Tema», tres opciones. IDs distintos para escritorio/móvil si ambos están montados, sin dos selecciones independientes.
- `Catalog`: emplea las mismas primitivas/clases y un controlador de tema; navegación por secciones y ejemplos aislados sin API. Ejemplos de mensajes simulan estados existentes, no alteran políticas del producto. Alertas nativas se describen y, para verificar, se activan explícitamente con mensaje ficticio; no se intenta tematizarlas.

## 4. Algoritmos en pseudocódigo

```text
inicio tema:
  saved := leer storage (capturar rechazo)
  preference := normalizeThemePreference(saved)
  aplicar resolveTheme(preference, mediaQuery.matches)
  escuchar cambio dispositivo:
    aplicar resolveTheme(preference, nuevo valor)
elección manual:
  preference := normalizeThemePreference(valor)
  intentar guardar preference
  sincronizar selectores y aplicar tema
desmontaje:
  retirar escucha dispositivo

abrir diálogo(event, origen):
  guardar currentTarget y origen antes de desmontar menú
  ejecutar flujo existente de apertura y cierre de menú
  al montar contenido enfocar primer control habilitado
cierre final:
  ejecutar cierre existente
  esperar tick
  destino := chooseFocusReturn(hechos DOM actuales)
  enfocar destino si existe; nunca abrir menú
apertura de diálogo (T57):
  esperar tick
  si destino preferido existe y está habilitado y visible:
    enfocar realmente el destino
  si no:
    usar primer control habilitado y visible
    si no existe, enfocar contenido tabindex -1
  no activar el control ni ejecutar submit/búsqueda
selección de ubicación:
  continuar flujo existente; no atrapar Tab ni consumir clic mapa

activar fila(event):
  si shouldActivateRow(key, repeat, target == currentTarget):
    si Espacio impedir scroll de esa pulsación
    ejecutar mismo manejador del clic exactamente una vez

aceptación:
  para cada elemento/variante/estado aplicable y tema:
    vincular ejemplo de catálogo, experiencia y evidencia
    si alerta nativa: comprobar disparador/mensaje/funcionamiento;
       registrar exclusión de apariencia/tema/contraste
    en otro caso: medir pares/estados renderizados y cabecera aplicable
  recorrer experiencias en matriz RNF-3 y casos límite
  registrar fallos/bloqueos; no marcar verificado lo no ejecutado
```

## 5. Decisiones técnicas y alternativas descartadas

| Decisión propuesta | Motivo | Alternativa descartada |
| --- | --- | --- |
| Variables CSS semánticas en hoja compartida; tema explícito data-theme | Permite claro/oscuro/manual uniforme y revisión de la cascada | Solo media query: no respeta elección manual; framework CSS nuevo: dependencia innecesaria |
| Clases sobre inputs/tablas nativos + pocas primitivas Svelte | Mantiene bindings, DOM y eventos actuales; reutilización real de presentación | Wrappers de cada input/tabla o gran Dialog genérico: riesgo de cambiar distribución y contratos |
| Controlador de tema compartido con adaptadores inyectables | Política testeable, una preferencia para ambas ubicaciones | Llamadas a localStorage/matchMedia repetidas en cada componente |
| Retorno de foco coordinado por App y acción de entrada local | App conoce disparador, menú y cierre final; respeta alta con mapa | Trap modal/retorno automático en todo destroy: bloquea mapa o roba foco al alternar |
| T57: destino de foco preferido declarado por formulario, con fallback intacto | RF-21 requiere comenzar a escribir en tres campos concretos; fallback mantiene foco interior en otros diálogos y tolera targets no disponibles | Enfocar siempre el primer control (prioriza el cierre frente al campo de escritura) o elegir por etiqueta (puede tomar el Nombre de cliente solo lectura) |
| Activación de filas conservando su manejador de clic | Añade teclado aprobado sin cambiar tabla ni operación | Convertir tabla en lista/tarjetas o añadir una operación nueva |
| Catálogo por query en entry existente | Accesible mediante URL directa, usa Rollup sin nuevo router ni nuevo botón de negocio | Storybook/router/framework nuevo: dependencias y configuración no necesarias |
| Pruebas nativas Node + navegador real | No hay suite existente; políticas verificables sin instalar herramientas | Assertions de texto fuente como prueba funcional, jsdom o suite E2E nueva |
| Alertas nativas intactas y excluidas visualmente | Límite de spec aprobado por QA/usuario | Sustituirlas por toast: cambio no autorizado de interacción |

La paleta final partirá de azules actuales y semántica verde de ubicación; ajustar colores también en degradados donde existan. No fijar de antemano valores que no pasen contraste. Las dimensiones particulares se conservan, salvo ajustes de cabeceras/texto ampliado requeridos. RF-24 normaliza las superficies, títulos, campos, acciones y estados de los cuatro diálogos al patrón de Buscar Dirección en ambos temas y elimina el degradado exclusivo de Alta; además, los cierres comparten forma, dimensiones renderizadas reales (32×32 px escritorio/36×36 px hasta 768 px), apariencia y estados de interacción/foco. En cada viewport/tema el círculo completo no debe quedar recortado ni sobresalir de forma inconsistente de la cabecera. No homogeneiza otras dimensiones ni flujos. Antes de remover una regla existente, comprobar si contiene animación, breakpoint o disposición que debe mantenerse.

## 6. Pruebas y verificación previstas

### Automatizadas sin dependencias

Comando futuro desde `raweb/`: `node --test tests/design-system/*.test.mjs`. Usar Node con soporte estable del runner (comprobar versión antes de implementar). No crear por inferencia un script `npm test` ni instalar herramientas.

- Tema: matriz tres preferencias × dispositivo claro/oscuro, valor ausente/desconocido, cambio de sistema sin sobrescribir elección manual. Adaptador: storage falso, escritura/relectura de cada opción, excepción de almacenamiento, suscripción y limpieza. Los falsos prueban coordinación, no comportamiento real del navegador.
- Foco: disparador visible, desaparecido/oculto, menú visible y origen móvil; no escoger menú para origen escritorio ni afirmar foco correcto basándose solo en política. Acción/DOM se valida aparte en navegador.
- T57, selección/action: target preferido válido prevalece; ausente/oculto/deshabilitado usa primer control habilitado/visible y, de no haberlo, contenido `tabindex=-1`; comprobar limpieza al desmontar. No usar tests de strings fuente como sustituto del DOM real.
- Filas: Enter/Espacio, otras teclas, repeat y descendientes; browser verifica activación real y scroll.
- Contraste: casos conocidos negro/blanco (21:1), iguales (1:1) y umbrales; extraer variables hex opacas de los dos bloques de tema del CSS y comprobar pares declarados. No cubrir transparencias, CSS computado ni todos los estados con este test.
- Catálogo/matriz: unicidad de IDs, elementos inventariados enlazados a RF, estados aplicables o no aplicables y clasificación de alertas nativas. Es verificación de integridad de datos de documentación, no de producto.

En tareas de lógica, escribir primero el caso significativo y ejecutar rojo, implementar y obtener verde. En tareas CSS/componentes, registrar primero el fallo observable o la captura/medición de referencia; no fabricar un test Node que inspeccione strings del componente. Ejecutar tests Node existentes, build y comprobación de navegador afectada. Documentación/evidencias se comprueban por enlaces e integridad y no necesitan un rojo artificial.

### Compilación y navegador

- `npm run build` por tarea de código; `npm run dev` sirve y recompila en 8080. `npm start` solo sirve salida existente. No ejecutar estos comandos en esta fase documental.
- Revisar consola y requests: búsqueda dirección POST `/buscar_direccion`; clientes POST búsqueda en tres criterios; PUT actualización (docenas/observaciones); POST alta (cantidad/observacion y latitud/longitud); GET pedidos; WFS Clientes/Pedidos en EPSG:3857 y refresh tras mutaciones.
- Comparar comportamiento antes/después sin guardar datos reales; usar datos ficticios en entorno local de prueba. No modificar QA/UAT sin autorización. API/GeoServer y base con PostGIS son requisitos externos de verificación, no tareas de cambiar infraestructura.
- Cubrir éxito, carga, ausencia y fallo existentes sin cambiar su clasificación. GET pedidos vacío puede devolver objeto HTTP 200: registrar cualquier fallo previo observado, no arreglarlo silenciosamente ni considerar completo ese flujo con mocks. Una corrección de negocio requeriría decisión aparte.
- Matriz visual completa: claro/oscuro en 360×800, 800×360, 768×1024, 1366×768; texto al 200 % en 360×800 y 1366×768. Medir ampliación de texto real (preferencia del navegador o método documentado que duplique fuente sin cambiar viewport), no solo DPR ni asumir que zoom de página equivale a texto al 200 %.
- Recorrer navegación, cuatro diálogos, tablas/estadísticas, mensajes y elementos de mapa. Comprobar scroll, acciones accesibles, títulos/cierres, Tab/Mayús+Tab, teclas de tipo nativo, filas, botones icono, foco interior y retorno (incluido Menú cerrado), persistencia/recarga y cambios del dispositivo en Sistema.
- T57: en Chrome, Claro/Oscuro y escritorio/móvil, comprobar que abrir Buscar Dirección activa `#direccion-input`; Buscar Cliente activa `#search-cliente` de búsqueda por nombre (no el Nombre de cliente seleccionado readonly); Agregar Cliente activa `#nombre`. Confirmar cursor listo para escribir, Tab/Mayús+Tab, retorno al cerrar y, en móvil, teclado/scroll nativos como posible consecuencia del foco real. La apertura no debe autoenviar ni producir búsqueda/REST/WFS; en Alta debe seguir siendo posible seleccionar ubicación. No suprimir el teclado móvil nativo.
- Medir cabecera mediante caja renderizada: una línea ≤48 px; dos líneas móvil ≤64 px; texto ampliado crece sin recorte. Medir texto grande con criterio WCAG correspondiente y anotar tamaño/peso; pares normales ≥4,5, grandes ≥3, controles/estados ≥3. Incluir hover/foco/selección/deshabilitado cuando corresponda según criterio, texto/bordes contra fondo efectivo, degradados/transparencias y controles sobre fondos OSM/satelital. No declarar certificación total.
- RF-24: comparar los cuatro diálogos lado a lado en Claro/Oscuro, registrando para cada superficie (marco/cuerpo), título/cabecera, campos, acciones y estados existentes captura y estilos renderizados contra el patrón de Buscar Dirección. Confirmar ausencia de degradado exclusivo en Alta; comprobar contraste aplicable RNF-2 y que estructura, tamaños, cabeceras y flujos no hayan cambiado. Las capturas aportadas por el usuario sirven como referencia del defecto, no como evidencia de que la corrección pase.
- T56: con Dark Reader desactivado, comprobar en Chrome Claro/Oscuro y en escritorio/móvil que los cuatro cierres renderizan un círculo completo de 32×32/36×36 px (36 px hasta 768 px), sin clipping ni sobresalir de forma inconsistente de la cabecera en cada viewport/tema; verificar colores y estados interactivos/foco equivalentes a Buscar Dirección, nombre accesible y activación/cierre/handler de cada uno. Comparar con T51 y la matriz integrada T55/evidencia pertinente. Ejecutar el runner y build previstos, pero ninguno ni sus resultados sustituyen la verificación de navegador.
- Disponibilidad de QA: no asumir acceso desde WSL al CDP de Windows:9222. No aplicar portproxy ni abrir puertos como parte de estas tareas. UI/integración requiere navegador accesible y app servida; si no está disponible, registrar bloqueo y solicitar evidencia accesible para cada tema/diálogo. Build/tests por sí solos no completan una tarea visual.
- Mantener animaciones, temporizadores y reglas de reducción existentes; comparar sin introducir preferencias nuevas. Verificar alertas del navegador por mensaje/disparador/funcionamiento; marcar medidas visuales «no aplica — control navegador».

### Evidencias

`coverage.md`: filas por ID de componente/estado/experiencia y referencias a evidencia, RF/RNF, tema, viewport, ampliación, fecha de ejecución, resultado (pendiente/pasa/falla/bloqueado), limitaciones y exclusiones. La fecha es metadato aportado, no cálculo de negocio. Capturas de datos ficticios y resultados resumidos sin credenciales ni cuerpos REST con datos reales. Separar evidencia de catálogo aislado de integración con servicios reales; si falta un servicio, marcar bloqueado, nunca pasa.

## 7. Dependencias y límites de ejecución

- Aprobación del plan/tareas anterior y ejecución por bloques registrada con respuesta exacta «si». La enmienda RF-24 y la revisión vigente de plan/tareas T56 están aprobadas explícitamente con respuesta «si». T56 queda autorizada para ejecución, pero sigue sin implementar y sin marcar; verificar y marcar conforme a SDD solo después de completar sus criterios.
- Node/npm disponibles; dependencias existentes instaladas desde raweb (`npm ci` solo si faltan); API/GeoServer accesibles desde navegador y datos locales ficticios para mutaciones.
- Árbol de trabajo con muchas modificaciones anteriores: inspeccionar diff del archivo antes de cada tarea y conservarlas; sin commits ni restauraciones por inferencia.
- Una discrepancia que obligue a alterar distribución/interacción o criterios aprobados se eleva como hallazgo; no ampliar la spec mediante decisiones técnicas.

## 8. Organización de ejecución anterior

El desglose completo tiene **50 tareas de 20–30 minutos**, agrupadas en cinco bloques de diez aprobados. El tiempo total orientativo es 17–25 horas, sujeto a hallazgos y disponibilidad de servicios. No representa cinco tareas gigantes ni promete cerrar toda la validación en una sola sesión.

La propuesta de división exigida por la skill se resolvió con aprobación de la ejecución en cinco bloques: A fundaciones/infraestructura UI, B navegación/búsquedas/inicio alta, C alta/pedidos/mapa, D catálogo/guía, E evidencias de aceptación. Se conserva 001 como contrato íntegro de alcance y se mantienen las dependencias de tareas salvo la propuesta de secuenciación puntual descrita a continuación. No se crean ni renumeran specs derivadas.

Decisión anterior: respuesta exacta «si» aprobó plan/tareas de 50 tareas en cinco bloques; T1–T26 completadas y T27 implementada con verificación UI bloqueada. Por la necesidad explícita de resolver primero la inconsistencia RF-24, T51–T55 tienen prioridad sobre reanudar T27–T50. Sus predecesoras están cumplidas: T51 depende de T14; T52–T54 de T51; T55 de T52–T54. Al cerrar T55 se reanuda T27 (sin saltarla) y después T28–T50. No se reinicia ni cambia el estado histórico de tareas.

### Replanificación aprobada antes de implementar T31

T31 es un contrato de inventario expresable y verificable como datos/lógica pura: unicidad de IDs, referencias a RF, declaración de estados aplicables/no aplicables y clasificación de alertas nativas. Sus criterios no dependen de la configuración de viewport, el pinch ni la disponibilidad del shell, y se pueden cubrir con los tests Node ya previstos sin modificar UI. Se desacopla únicamente T31 de T30 y puede ejecutarse tras T1. Esta secuencia no satisface ni reduce ningún criterio de T30, que permanece incompleta.

T32 conserva el catálogo como tarea de UI y queda explícitamente dependiente de T30 además de T31. En consecuencia, T32 y las tareas que dependen de ella no se inician hasta completar T30; T40 puede preparar documentación solo conforme a sus dependencias existentes, sin convertirlo en autorización para adelantar la UI. Aprobación explícita del usuario: respuesta exacta «si». T31 sigue pendiente de ejecución; esta aprobación no marca tareas completas ni cambia el alcance. **Registro histórico: esta dependencia queda reemplazada por la propuesta de replanificación pendiente de aprobación registrada abajo.**

## 9. Revisión prioritaria por RF-24 (T51–T56 aprobadas y ejecutadas)

T51–T55 se agregan al final del historial, pero se ejecutan antes de reanudar T27–T50: cinco tareas de 20–30 minutos, sin marcar y con dependencias explícitas. Orden: T51 baseline Buscar Dirección; T52 Buscar Cliente/edición; T53 Agregar Cliente sin degradado; T54 Pedidos; T55 comparación integrada/matriz. T51 depende de T14 completada y T52–T54 dependen de T51, de modo que pueden preceder T27 (cuya dependencia T26 también está completada). Tras validar T55, retomar T27 pendiente de verificación UI y seguir T28–T50 en su orden original. RF-24 no cambia estructura/tamaños, interacciones ni contratos.

Cada tarea ejecuta `node --test tests/design-system/*.test.mjs` y `npm run build`; si Node falla, detener y no avanzar a la siguiente. Build fallido también bloquea la tarea hasta resolverlo. Las tareas UI además requieren browser y evidencia del criterio en Claro/Oscuro. Si el browser no es accesible, marcar bloqueo real y no declarar concluida la tarea ni avanzar como si estuviera validada. No se permite portproxy ni apertura de puertos para alcanzar CDP.

Registro de aprobación: el usuario aprobó explícitamente la revisión del plan/tareas RF-24 con respuesta exacta «si» y la prioridad T51→T55 antes de T27→T28–T50. También aprobó desacoplar únicamente T31 de T30: T31 puede ejecutarse tras T1; T32 y su cadena UI esperan a que T30 esté completa. La enmienda RF-24 de dimensiones y no-clipping y la revisión vigente de plan/tareas T56 fueron aprobadas explícitamente con «si»; T56 y T57 están completadas según la evidencia registrada. T30 permanece incompleta; T31 y T56/T57 conservan sus estados completados. **La dependencia T32→T30 aquí descrita es histórica y queda sujeta a la propuesta de replanificación pendiente de aprobación al final de este plan.**

### T56 — Igualar botones de cierre con el baseline (revisión vigente aprobada; implementación pendiente)

T56 es seguimiento incremental del alcance aprobado en RF-24; conserva intacto el historial T51–T55 y no declara que la corrección se haya realizado. La propuesta anterior de 28×28 px escritorio/36×36 px móvil quedó sustituida por la enmienda aprobada: igualar únicamente los cuatro controles de cierre al baseline renderizado de Buscar Dirección, forma circular y dimensiones reales 32×32 px escritorio y 36×36 px hasta 768 px. En cada viewport y tema el círculo se verá completo, sin clipping ni sobresalir de forma inconsistente de la cabecera; igualar colores y estados interactivos/foco. Mantener nombre accesible, activación, cierre, handlers y flujos actuales. No cambiar Cancelar/Guardar ni otros estilos. Verificación: en Chrome sin Dark Reader, Claro/Oscuro, comprobar dimensiones renderizadas, forma/encaje en cabecera, colores/estados, foco y contraste aplicable según RNF-2; comprobar cada nombre accesible y flujo de cierre. Comparar/documentar contra baseline T51 y evidencia integrada T55, y ejecutar `node --test tests/design-system/*.test.mjs` y `npm run build`; registrar evidencia y resultado solo tras ejecución.

Dependencias de T56: T51, T52, T53, T54 y T55 (todas completadas). Orden aprobado: después de T55 y antes de reanudar la secuencia restante; T56 no depende de T30, no adelanta T32 ni modifica dependencias existentes. La versión previa de T56 y su orden fue aprobada, pero sus dimensiones 28×28/36×36 quedan reemplazadas. El usuario aprobó explícitamente esta revisión corregida de plan/tareas con «si»; T56 está completada según el registro de verificación. **Registro histórico anterior a esta propuesta:** T30 permanece incompleta y T32 conserva su bloqueo hasta completar T30.

### T57 — Foco preferido de apertura para tres formularios (plan/tareas aprobados; implementación pendiente)

RF-21 está aprobada. T57 aplicará foco DOM real tras `tick` al campo de dirección `#direccion-input`, a la búsqueda por nombre `#search-cliente` (no al campo Nombre del cliente seleccionado, que es readonly) y a `#nombre` en Agregar Cliente. La apertura de otros diálogos conserva el foco interior actual. El target preferido debe ser comprobado como presente, visible y habilitado; si falta, está oculto o deshabilitado, se mantiene el fallback de T6: primer control habilitado/visible, y luego contenido enfocable. No cambiar retorno al disparador/Menú cerrado, flujo de selección de ubicación, validación ni handlers; no auto-submit ni llamadas API/REST/WFS. En móvil se acepta el teclado nativo como consecuencia de foco real y no se suprime.

Responsabilidades: `src/design-system/dialog-focus.mjs` recibe/resuelve el destino preferido con fallback; `src/BuscarDireccionDialog.svelte`, `src/BuscarCliente.svelte`, `src/AgregarCliente.svelte` declaran los selectores exactos sin modificar los handlers; añadir `tests/design-system/dialog-focus.test.mjs` para probar selección/fallback/desmontaje mediante la acción, no inspección de strings; registrar evidencia de navegador en `docs/design-system/` al ejecutar.

Dependencias: T6, T12, T13, T15, T19 y T56, todas completadas. Orden propuesto: después de T56 y antes de T30, conforme a la ubicación aprobada por el usuario. No depende de viewport/zoom/datos, no modifica estado ni criterios de T30 (sigue incompleta), y no inicia T32 (registro histórico sujeto a la propuesta de replanificación al final de este plan).

Verificación prevista: `node --test tests/design-system/*.test.mjs`; `npm run build` desde `raweb/` (usar el build disponible en Windows si WSL carece del Rollup opcional); navegador Chrome Claro/Oscuro, escritorio/móvil, foco activo/cursor en cada target, escritura, Tab/Mayús+Tab, retorno al cerrar, teclado/scroll móvil nativo si aparece y selección de ubicación en Alta. Confirmar cero submit y cero requests/búsqueda al abrir/focalizar. Dejar incompleta con bloqueo específico si falta cualquier comprobación exigida. El plan/tareas está aprobado; T57 queda autorizada y pendiente de implementación.

### Replanificación aprobada — T30 diferida y T32 habilitada

El usuario respondió exactamente «si», aprobando esta replanificación. T32 dependerá únicamente de T31; la entrada `?catalog=design-system` y el catálogo aislado no requieren pinch, API ni WFS. La revisión de T33–T49 no detectó dependencia funcional de T30: T36 cubre el ejemplo adaptable/móvil, T42 verifica texto ampliado al 200 % (distinto de pinch), y las demás tareas mantienen sus dependencias de cadena actuales. No se elimina ni rebaja ningún criterio de RF/RNF.

Secuencia aprobada: ejecutar T32–T49 respetando la cadena de dependencias ya aprobada; el pinch manual en dispositivo físico/real de T30 queda expresamente diferido al usuario. T30 permanece `[ ]`, con sus criterios viewport y RF/RNF intactos; las verificaciones ya registradas no se convierten en cumplimiento del pinch. T50 depende explícitamente de T30 además de T49 y no puede marcarse ni aceptarse hasta que T30 esté completa y el resto de criterios verificados. T31, T32 y T56/T57 están completas. Tras reportarse una regresión de CSS en T32, se volvió a verificar la entrada normal y el catálogo después de corregir el empaquetado en `src/main.js`; evidencia actualizada en `docs/design-system/t32-verification.md`. T33 no se ha iniciado.
