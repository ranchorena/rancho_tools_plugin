# Plan 001 — Design system de raweb

Estado: propuesto, pendiente de aprobación junto con tareas y división de trabajo.
Base: `spec.md` aprobada globalmente con respuesta exacta «si», tras QA LISTA PARA APROBACIÓN. Este documento no modifica su alcance.

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
| `src/BuscarDireccionDialog.svelte` | Migrar presentación/cabecera, foco interior; preservar evento `buscar`, `close`, Enter/Escape y alerta vacía. | RF-4–RF-7, RF-9, RF-11–RF-16, RF-19–RF-21 |
| `src/BuscarCliente.svelte` | Migrar búsqueda/edición, tabla y filas activables; no modificar `fetchData`, payloads ni eventos. | RF-4–RF-7, RF-9, RF-11–RF-16, RF-19–RF-21 |
| `src/AgregarCliente.svelte` | Migrar campos/mensajes/cabecera; mantener prop coordenadas, selección de mapa, validaciones y cierre. | RF-4–RF-7, RF-9, RF-11–RF-16, RF-19–RF-21 |
| `src/Pedidos.svelte` | Migrar cabecera, tabla, filas y estadísticas; conservar cálculos, carga y `zoomToLocation`. | RF-4–RF-6, RF-9, RF-11–RF-16, RF-19–RF-21 |
| `src/GlobalNotification.svelte` | Solo presentación de variantes existentes; conservar mensaje, temporizadores, sustitución y ausencia de cierre manual. | RF-6, RF-8, RF-11, RF-13, RF-15, RF-16 |
| `src/design-system/catalog.mjs`, `Catalog.svelte`, `examples/*.svelte`, `src/main.js` | Inventario y ejemplos interactivos ficticios. Seleccionar catálogo mediante `?catalog=design-system` en el mismo entry; importar App pero no montarla en ese modo, sin consultas REST/WFS. | RF-1–RF-5, RF-10, RF-22; RNF-5 |
| `docs/design-system/guide.md`, `coverage.md`, `evidence/` | Guía, comparación de identidad, uso/variantes/no aplicables y registro de comprobaciones con IDs, tema, estado, viewport, resultado y limitaciones. | RF-1–RF-4, RF-6–RF-10, RF-22, RF-23; RNF-1–RNF-6 |
| `tests/design-system/*.test.mjs`, `tests/design-system/support/contrast.mjs` | Pruebas de políticas y contratos de catálogo/paleta; no simulan render real ni API. | RF-17–RF-21, RF-22, RF-23; RNF-1, RNF-2 |

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
| Activación de filas conservando su manejador de clic | Añade teclado aprobado sin cambiar tabla ni operación | Convertir tabla en lista/tarjetas o añadir una operación nueva |
| Catálogo por query en entry existente | Accesible mediante URL directa, usa Rollup sin nuevo router ni nuevo botón de negocio | Storybook/router/framework nuevo: dependencias y configuración no necesarias |
| Pruebas nativas Node + navegador real | No hay suite existente; políticas verificables sin instalar herramientas | Assertions de texto fuente como prueba funcional, jsdom o suite E2E nueva |
| Alertas nativas intactas y excluidas visualmente | Límite de spec aprobado por QA/usuario | Sustituirlas por toast: cambio no autorizado de interacción |

La paleta final partirá de azules actuales y semántica verde de ubicación; ajustar colores también en degradados donde existan. No fijar de antemano valores que no pasen contraste. Las dimensiones particulares se conservan, salvo ajustes de cabeceras/texto ampliado requeridos. Antes de remover una regla existente, comprobar si contiene animación, breakpoint o disposición que debe mantenerse.

## 6. Pruebas y verificación previstas

### Automatizadas sin dependencias

Comando futuro desde `raweb/`: `node --test tests/design-system/*.test.mjs`. Usar Node con soporte estable del runner (comprobar versión antes de implementar). No crear por inferencia un script `npm test` ni instalar herramientas.

- Tema: matriz tres preferencias × dispositivo claro/oscuro, valor ausente/desconocido, cambio de sistema sin sobrescribir elección manual. Adaptador: storage falso, escritura/relectura de cada opción, excepción de almacenamiento, suscripción y limpieza. Los falsos prueban coordinación, no comportamiento real del navegador.
- Foco: disparador visible, desaparecido/oculto, menú visible y origen móvil; no escoger menú para origen escritorio ni afirmar foco correcto basándose solo en política. Acción/DOM se valida aparte en navegador.
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
- Medir cabecera mediante caja renderizada: una línea ≤48 px; dos líneas móvil ≤64 px; texto ampliado crece sin recorte. Medir texto grande con criterio WCAG correspondiente y anotar tamaño/peso; pares normales ≥4,5, grandes ≥3, controles/estados ≥3. Incluir hover/foco/selección/deshabilitado cuando corresponda según criterio, texto/bordes contra fondo efectivo, degradados/transparencias y controles sobre fondos OSM/satelital. No declarar certificación total.
- Mantener animaciones, temporizadores y reglas de reducción existentes; comparar sin introducir preferencias nuevas. Verificar alertas del navegador por mensaje/disparador/funcionamiento; marcar medidas visuales «no aplica — control navegador».

### Evidencias

`coverage.md`: filas por ID de componente/estado/experiencia y referencias a evidencia, RF/RNF, tema, viewport, ampliación, fecha de ejecución, resultado (pendiente/pasa/falla/bloqueado), limitaciones y exclusiones. La fecha es metadato aportado, no cálculo de negocio. Capturas de datos ficticios y resultados resumidos sin credenciales ni cuerpos REST con datos reales. Separar evidencia de catálogo aislado de integración con servicios reales; si falta un servicio, marcar bloqueado, nunca pasa.

## 7. Dependencias y límites de ejecución

- Aprobación del plan/tareas y decisión de división antes de implementación. Trabajar una tarea, verificar, marcarla y parar conforme a SDD.
- Node/npm disponibles; dependencias existentes instaladas desde raweb (`npm ci` solo si faltan); API/GeoServer accesibles desde navegador y datos locales ficticios para mutaciones.
- Árbol de trabajo con muchas modificaciones anteriores: inspeccionar diff del archivo antes de cada tarea y conservarlas; sin commits ni restauraciones por inferencia.
- Una discrepancia que obligue a alterar distribución/interacción o criterios aprobados se eleva como hallazgo; no ampliar la spec mediante decisiones técnicas.

## 8. División propuesta (requiere decisión)

El desglose completo tiene **50 tareas de 20–30 minutos**, agrupadas provisionalmente en cinco bloques de diez. El tiempo total orientativo es 17–25 horas, sujeto a hallazgos y disponibilidad de servicios. No representa cinco tareas gigantes ni promete cerrar toda la validación en una sola sesión.

La skill pide proponer división de la spec cuando hay más de diez tareas: **se propone conservar 001 como contrato de alcance y, con autorización, dividir la ejecución en cinco specs derivadas/bloques aprobables**: A fundaciones/infraestructura UI, B navegación/búsquedas/inicio alta, C alta/pedidos/mapa, D catálogo/guía, E evidencias de aceptación. Cada derivada referenciaría RF/RNF de 001 sin cambiar requisitos; D/E dependen de migraciones anteriores. No se han creado ni renumerado specs derivadas.

Decisión pendiente del usuario: aprobar esta división de ejecución preservando íntegra la spec 001, o pedir otra organización. Aprobar únicamente un bloque no acepta como terminada la entrega global de cuatro bloques. Plan y tareas siguen propuestos hasta la aprobación explícita.
