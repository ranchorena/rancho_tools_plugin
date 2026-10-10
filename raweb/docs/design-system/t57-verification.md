# T57 — Foco preferido al abrir tres diálogos

Fecha: 2026-10-07. RF-21. **Estado: T57 completa.**

## Implementación

`dialogFocus` prioriza el descendiente marcado `data-dialog-initial-focus` después de `tick`, solo si está conectado, visible y habilitado. Si no es utilizable, conserva la selección anterior del primer control habilitado/visible y, como último recurso, enfoca el contenido con `tabindex=-1`. La acción sigue cancelando el foco pendiente al desmontarse y no captura Tab ni devuelve foco automáticamente.

Los únicos destinos declarados son `#direccion-input`, `#search-cliente` y `#nombre` en sus formularios respectivos. BuscarCliente enfoca el input editable de búsqueda por nombre, no el Nombre de cliente seleccionado de solo lectura. No cambiaron handlers, validaciones, eventos, contratos, coordenadas ni llamadas de búsqueda.

## Pruebas automatizadas rojo/verde

- Antes de implementar, `node --test tests/design-system/*.test.mjs` falló en la prueba de foco preferido: 33 contabilizadas, 32 pasaron y 1 falló (objetivo preferido con 0 focos frente a 1 esperado). El fallback, contenido enfocable y cancelación ya pasaban; el rojo aisló la falta de priorización del destino.
- Después del cambio, el mismo comando terminó con código 0: 33 tests, 33 pass, 0 fail/cancelled/skipped/todo (344.410501 ms, ejecución final). Los casos de `dialog-focus.test.mjs` comprueban foco preferido en el núcleo de la acción después de tick; targets ausente/oculto/deshabilitado; fallback al control usable/contenido; y cancelación del foco pendiente al desmontar.
- Build exacto `cmd.exe /c "cd /d C:\GIT\github\rancho_tools_plugin\raweb && npm run build"`: código 0, bundle creado por Rollup en 8.5 s, sin warnings de compilación.

## Verificación Chrome

Aplicación `http://localhost:52948/` (Chrome sin Dark Reader), viewport de escritorio 1366×768 y emulación móvil táctil 360×800. Tema seleccionado manualmente Claro/Oscuro. Las cajas de los tres campos tuvieron dimensiones positivas y el foco computado mostró outline sólido de 3 px.

| Tema | Viewport | Buscar Dirección | Buscar Cliente (nombre) | Agregar Cliente | Cierre/retorno |
|---|---|---|---|---|---|
| Claro | 1366×768 | `direccion-input`, editable/visible | `search-cliente`, editable/visible | `nombre`, editable/visible | En escritorio volvió al disparador correspondiente |
| Oscuro | 1366×768 | `direccion-input`, editable/visible | `search-cliente`, editable/visible | `nombre`, editable/visible | En escritorio volvió al disparador correspondiente |
| Oscuro | 360×800 táctil | `direccion-input`, visible, outline 3 px | `search-cliente`, visible, outline 3 px | `nombre`, visible, outline 3 px; cuerpo desplazable | Menú cerrado; foco volvió a «Menú» |
| Claro | 360×800 táctil | `direccion-input`, visible, outline 3 px | `search-cliente`, visible, outline 3 px | `nombre`, visible, outline 3 px; cuerpo desplazable | Menú cerrado; foco volvió a «Menú» |

En escritorio se usaron pulsaciones Tab/Mayús+Tab reales: Dirección recorrió campo→Buscar→campo y Mayús+Tab desde el campo alcanzó «Cerrar»; Cliente recorrió `search-cliente`→Buscar→`search-cliente`; Alta recorrió `nombre`→`telefono`→`nombre`. El botón Cerrar está en el recorrido y permanece alcanzable. El foco inicial no pulsó los botones ni envió los formularios.

En la emulación móvil el scroll del cuerpo del alta respondió; los cuerpos de Dirección y Buscar Cliente no necesitaban desplazamiento en esa apertura. El Chrome/DevTools disponible simula viewport táctil pero corre sobre host de escritorio y no presenta un teclado virtual del sistema operativo. Los destinos son inputs `type=text`, no readonly, sin `inputmode` que suprima el teclado; el foco nativo real quedó aplicado y el cursor queda listo para escribir. La ausencia de teclado virtual visible es una limitación del emulador, no un criterio fallido: RF-21 se acredita por el foco real al campo de escritura y no se deshabilitó ni suprimió el teclado móvil. La observación en un dispositivo físico podría complementar la evidencia, pero no queda como pendiente ni bloquea T57.

## Red y consola

Se consultó únicamente la lista de solicitudes por método/recurso/URL/estado, sin inspeccionar cuerpos, cabeceras ni respuestas. Comparación de metadatos antes/después de abrir los tres formularios: no hubo solicitudes nuevas atribuibles a la apertura o al foco, ni búsquedas REST. Permaneció visible un GET WFS Pedidos de carga inicial, con HTTP 502 en `/geoserver/ows`; coincide con GeoServer detenido, informado previamente por el usuario. No hubo solicitudes API ni mutaciones POST/PUT/DELETE. No se levantaron servicios.

Consola: error de recurso HTTP 502 correspondiente al WFS inicial; aviso previo de `apple-mobile-web-app-capable` obsoleto; un issue de DevTools sobre un campo de formulario sin id/name. No se registraron errores JS generados al abrir/focalizar los formularios.

No se pulsó Buscar/Guardar, no se enviaron datos, y no se hizo clic en el mapa ni se cambiaron coordenadas. La acción de diálogo para Pedidos conserva su comportamiento anterior por no declarar un destino preferido.

## Estado

La implementación, runner, build, foco de los tres campos, fallback/desmontaje automatizados, Tab/Mayús+Tab, retorno de foco y ausencia de solicitudes causadas por apertura pasan. La falta de teclado virtual visible se registra como limitación no bloqueante del emulador: en móvil puede aparecer y no se suprime. **T57 queda completada `[x]`.** No se modificó el estado de T30 (incompleta), T31 (completa) ni T32 (bloqueada); no se inició otra tarea.
