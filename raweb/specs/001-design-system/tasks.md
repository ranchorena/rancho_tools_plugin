# Tareas 001 — Design system de raweb

Estado: propuestas; pendientes de aprobación del plan/tareas y división. Ninguna tarea ejecutada.

50 tareas, cada una estimada en 20–30 minutos. Los cinco bloques de diez son una propuesta de división, no specs nuevas ni una reducción del alcance aprobado. Si una tarea excede 30 minutos por hallazgos, detener y proponer subdivisión; no ocultar trabajo bajo «migrar todo».

## Protocolo común

- Antes de tocar un archivo, revisar sus cambios previos. Implementar una tarea y parar tras verificar/marcar.
- **L:** lógica: test significativo primero, `node --test tests/design-system/*.test.mjs` rojo → implementación → verde, `npm run build` y navegador si tiene integración.
- **UI:** registrar primero caso fallido/medición de referencia; no simular render con tests de strings. Tras cambio, runner Node existente en verde, build y flujo afectado en navegador. Toda comprobación faltante se registra bloqueada, no completa.
- **D:** documentación: integridad/enlaces y datos ficticios; runner si hay contratos de datos. No inventar tests para cambios documentales triviales.
- **V:** verificación: medir y registrar ejecución real; runner y build como base, sin repetirlos por cada captura si no cambió código. El «hecho cuando» de cada tarea se añade a este protocolo.
- Dependencias por número; dentro de cada bloque se sigue el orden listado. Todos los pasos de código requieren antes aprobación global de este plan/tareas.

## A — Fundaciones e infraestructura UI (T1–T10)

- [ ] **T1. Inventariar variantes/estados y referencias visuales existentes.** RF-1–RF-4, RF-6–RF-9, RF-23. D; sin dependencias.
  - Hecho cuando: coverage preliminar relaciona cada familia/experiencia de spec con estados existentes, alertas nativas y particularidades de layout; referencias con datos ficticios, sin añadir reglas.
- [ ] **T2. Política pura de tema.** RF-17, RF-18. L; depende T1.
  - Hecho cuando: tests cubren las tres preferencias, ambos dispositivos y valores ausentes/desconocidos; ninguna lectura global de navegador en la política.
- [ ] **T3. Adaptador de tema y almacenamiento.** RF-17, RF-18. L; depende T2.
  - Hecho cuando: tests de lectura/escritura, rechazo y limpieza de suscripción pasan; dispositivo no sobreescribe elección explícita.
- [ ] **T4. Selector nativo compartido «Tema».** RF-4, RF-17, RF-19. UI; depende T3.
  - Hecho cuando: selector aislado muestra tres opciones, etiqueta/ID, evento de preferencia y teclado nativo; no tiene preferencia independiente.
- [ ] **T5. Política pura de retorno de foco y activación de filas.** RF-19, RF-21. L; depende T1.
  - Hecho cuando: tests discriminan disparador visible/oculto/desmontado, origen móvil/Menú y Enter/Espacio/descendientes/repeat.
- [ ] **T6. Acción de foco interior sin trap.** RF-9, RF-21. UI; depende T5.
  - Hecho cuando: ejemplo aislado enfoca contenido/control y permite salir con Tab; desmontaje no restituye foco prematuramente ni altera cierre.
- [ ] **T7. Botón reutilizable nativo.** RF-4, RF-5, RF-19, RF-20. UI; depende T1.
  - Hecho cuando: type, disabled, nombre accesible y eventos reenviados funcionan en ejemplo aislado; no submit accidental.
- [ ] **T8. Cabecera reutilizable de altura natural.** RF-4, RF-14, RF-20. UI; depende T7.
  - Hecho cuando: ejemplo una línea/dos líneas móvil cumple 48/64 px; a texto 200 % título y cierre no se recortan.
- [ ] **T9. Fundaciones y clases de controles/campos/foco.** RF-1, RF-2, RF-5, RF-13, RF-19. UI; depende T7, T8.
  - Hecho cuando: hoja compartida cargada, variables claro/oscuro y escalas definidas; controles nativos mantienen dimensiones particulares y foco visible sin reglas globales de movimiento nuevas.
- [ ] **T10. Verificador de contraste opaco de la paleta.** RF-13, RF-23; RNF-2. L; depende T9.
  - Hecho cuando: tests 21:1/1:1/umbrales y pares opacos de ambas paletas pasan; listado deja explícitos los pares que necesitan medición renderizada.

## B — Navegación, búsqueda e inicio de alta (T11–T20)

- [ ] **T11. Integrar tema en navegación desktop/móvil.** RF-11, RF-15–RF-19. UI; depende T3, T4, T9.
  - Hecho cuando: selector al final de barra y debajo de acciones móvil; elegir/recargar/cambiar dispositivo funciona sin añadir fila en cabecera móvil.
- [ ] **T12. Capturar disparador y coordinar retorno de foco en App.** RF-9, RF-16, RF-21. UI; depende T5, T6, T11.
  - Hecho cuando: cierre final tras tick retorna a disparador visible o Menú cerrado; selección de punto no provoca retorno ni reapertura.
- [ ] **T13. Cabecera/foco del diálogo de dirección.** RF-9, RF-14, RF-21. UI; depende T8, T12.
  - Hecho cuando: cabecera/foco y cierres anteriores funcionan; alerta de entrada vacía sigue nativa.
- [ ] **T14. Campos/acciones del diálogo de dirección.** RF-4–RF-7, RF-11–RF-13, RF-19. UI; depende T13.
  - Hecho cuando: campo, Enter y Buscar mantienen evento/dirección y `/buscar_direccion`; ambos temas legibles, mismos mensajes.
- [ ] **T15. Cabecera/foco de búsqueda de clientes.** RF-9, RF-14, RF-21. UI; depende T12, T14.
  - Hecho cuando: diálogo mantiene ancho/scroll/animación y recibe/restaura foco conforme RF-21; retirar solo reglas cromáticas automáticas conflictivas.
- [ ] **T16. Migrar controles de los tres criterios de clientes.** RF-4–RF-7, RF-11–RF-13, RF-19. UI; depende T15.
  - Hecho cuando: nombre/dirección/calle-altura conservan payloads/validaciones/loading y presentación común.
- [ ] **T17. Tabla de resultados y activación por teclado.** RF-4, RF-5, RF-19. UI; depende T5, T16.
  - Hecho cuando: clic y Enter/Espacio seleccionan una vez el mismo cliente, no interceptan descendientes; scroll horizontal y columnas se conservan.
- [ ] **T18. Campos y acciones de edición de clientes.** RF-4–RF-7, RF-11–RF-13, RF-16, RF-19. UI; depende T17.
  - Hecho cuando: bindings y PUT docenas/observaciones mantienen contrato y eventos de notificación/refresco/geocodificación; no hay reglas nuevas.
- [ ] **T19. Cabecera/foco del alta.** RF-9, RF-14, RF-21. UI; depende T8, T12, T18.
  - Hecho cuando: título/cierre y retorno de foco cumplen; el marco conserva disposición y relación actual con el mapa.
- [ ] **T20. Campos básicos de alta.** RF-4, RF-5, RF-7, RF-11, RF-13. UI; depende T19.
  - Hecho cuando: nombre/dirección/calle/altura/teléfono conservan inputs, asociaciones y bindings con colores compartidos, sin cambiar validaciones.

## C — Alta, pedidos e interfaz del mapa (T21–T30)

- [ ] **T21. Campos de pedido, ubicación y mensajes de alta.** RF-4–RF-7, RF-9, RF-12, RF-16, RF-19–RF-21. UI; depende T20.
  - Hecho cuando: cantidad/regalo/horario/observación, selección de coordenadas y guardar/cancelar preservan eventos/payload y no bloquean clic de ubicación.
- [ ] **T22. Cabecera/foco de pedidos.** RF-9, RF-14, RF-21. UI; depende T12, T21.
  - Hecho cuando: cabecera/título/cierre y retorno funcionan conservando carga/distribución.
- [ ] **T23. Tabla/filas de pedidos.** RF-4–RF-6, RF-12, RF-16, RF-19. UI; depende T5, T22.
  - Hecho cuando: clic/teclado emiten zoomToLocation igual y cierran; columnas/scroll y cálculo de datos no cambian.
- [ ] **T24. Estadísticas y mensajes de pedidos.** RF-4, RF-6, RF-11, RF-13, RF-16. UI; depende T23.
  - Hecho cuando: tarjetas/mensajes usan fundaciones en ambos temas y cálculos conservan resultados de referencia; fallos previos se registran, no se corrigen por inferencia.
- [ ] **T25. Presentación de notificación global.** RF-6, RF-8, RF-11, RF-13, RF-16. UI; depende T9, T24.
  - Hecho cuando: success/error/otros tipos existentes conservan temporización y sustitución; no se añade cierre ni nueva política.
- [ ] **T26. Panel de capas y selecciones.** RF-4, RF-5, RF-15, RF-16, RF-19, RF-20. UI; depende T11, T25.
  - Hecho cuando: checkbox/radio, mostrar/cerrar y nombres icono funcionan con teclado y fondos propios sin alterar visibilidad de fuentes.
- [ ] **T27. Controles flotantes de App.** RF-4, RF-5, RF-15, RF-19–RF-21. UI; depende T26.
  - Hecho cuando: abrir alta/capas mantiene posición/tamaño particular, foco/nombres y flujo; contraste contra fondo efectivo en ambos temas.
- [ ] **T28. Información del elemento seleccionado.** RF-4, RF-15, RF-16, RF-19. UI; depende T27.
  - Hecho cuando: información/scroll/cierre y acciones que ya existan conservan contenido y disparadores; no se introduce selección cartográfica por teclado.
- [ ] **T29. Estilos de controles DOM de OpenLayers.** RF-5, RF-13, RF-15, RF-19, RF-20. UI; depende T28.
  - Hecho cuando: controles DOM legibles/activables en OSM y satélite ambos temas; canvas, símbolos y geometrías sin cambios.
- [ ] **T30. Habilitar ampliación y revisar cascada del shell.** RF-11, RF-14, RF-16, RF-19; RNF-3. UI; depende T29.
  - Hecho cuando: viewport permite ampliación, tipografía heredada no queda anulada por Arial local, shell conserva acciones accesibles con scroll y cabeceras no recortadas a 200 %.

## D — Catálogo y guía (T31–T40)

- [ ] **T31. Contrato de inventario del catálogo.** RF-1–RF-4, RF-10, RF-22, RF-23. L; depende T1, T30.
  - Hecho cuando: tests de IDs/referencias/estados/no aplicables cubren todas las familias y clasificación de alertas nativas; no crean estados nuevos.
- [ ] **T32. Entrada aislada del catálogo.** RF-10, RF-22. UI; depende T31.
  - Hecho cuando: URL `?catalog=design-system` monta catálogo y no App ni requests REST/WFS; entrada normal conserva aplicación.
- [ ] **T33. Ejemplos de fundaciones e identidad.** RF-1–RF-3, RF-13, RF-22. UI; depende T32.
  - Hecho cuando: valores/propósito/muestra y comparación documentada con identidad actual visibles en ambos temas, sin datos reales.
- [ ] **T34. Ejemplos interactivos de botones.** RF-4, RF-5, RF-19, RF-20, RF-22. UI; depende T33.
  - Hecho cuando: mismos Button/clases demuestran variantes/estados aplicables e iconos con nombre, incluyendo teclado/foco.
- [ ] **T35. Ejemplos de campos/selecciones/tema.** RF-4, RF-5, RF-17–RF-19, RF-22. UI; depende T34.
  - Hecho cuando: tipos existentes y opciones exclusivas/casillas/selector emplean clases del producto y datos ficticios; no se presenta validación nueva como requisito.
- [ ] **T36. Ejemplos de diálogos y navegación.** RF-4, RF-9, RF-14, RF-19–RF-22. UI; depende T35.
  - Hecho cuando: ejemplo demuestra entrada/retorno foco, cabeceras y versión móvil sin cambiar reglas de producto.
- [ ] **T37. Ejemplos de tablas y estadísticas.** RF-4, RF-5, RF-19, RF-22. UI; depende T36.
  - Hecho cuando: datos ficticios/filas activables/scroll/estados usan estilos compartidos y no alteran cálculos del producto.
- [ ] **T38. Ejemplos de mensajes y elementos del mapa.** RF-4, RF-6, RF-8, RF-15, RF-22. UI; depende T37.
  - Hecho cuando: clases de panel/control/información y mensajes existentes demostradas; alerta nativa identificada como exclusión visual, no sustitución.
- [ ] **T39. Guía de uso en español.** RF-1–RF-4, RF-6–RF-10, RF-22. D; depende T38.
  - Hecho cuando: guía enlaza cada familia/ejemplo, explica variantes, estados no aplicables, identidad y límites; incluye reglas existentes de mensajes/animaciones/diálogos.
- [ ] **T40. Estructura definitiva de matriz/evidencias.** RF-23; RNF-1–RNF-6. D; depende T31, T39.
  - Hecho cuando: inventario enlazado a RF/RNF y casos RNF-3 con campos resultado/evidencia/limitación; nada marcado pasa sin ejecución.

## E — Verificación y evidencias (T41–T50)

Para T43–T48, usar ambos temas y los cuatro viewports de RNF-3 más texto 200 % en móvil vertical/escritorio. Cada tarea cubre una experiencia acotada y reutiliza captura/medición ya registrada al migrar. Si la matriz real excede 30 minutos, proponer tareas adicionales por viewport antes de marcar; no aceptar cobertura parcial como completa.

- [ ] **T41. Medir paleta y estados renderizados de controles/mensajes.** RF-5, RF-13, RF-23; RNF-2. V; depende T40.
  - Hecho cuando: mediciones opacas y efectivas (degradados/transparencias/foco/selección) en catálogo registradas con fondo/tamaño/peso/umbral; alertas nativas no medidas.
- [ ] **T42. Medir cabeceras y contraste de paneles/mapa.** RF-14, RF-15, RF-23; RNF-2, RNF-3. V; depende T41.
  - Hecho cuando: 48/64 px y ampliación comprobados, paneles/controles sobre OSM/satélite medidos en ambos temas; ninguna excepción implícita.
- [ ] **T43. Verificar navegación y ciclo completo de tema.** RF-15–RF-19, RF-21, RF-23. V; depende T42.
  - Hecho cuando: matriz navegación/menú/selector pasa; persistencia tres opciones, recarga y cambio de sistema comprobados, retorno Menú sin reabrir.
- [ ] **T44. Verificar búsqueda de dirección y alertas nativas.** RF-6, RF-7, RF-9, RF-12, RF-19–RF-21, RF-23. V; depende T43.
  - Hecho cuando: matriz de diálogo/teclado/scroll y POST real comprobados; validación/alertas mantienen disparador/mensaje/funcionamiento, con exclusión visual registrada.
- [ ] **T45. Verificar búsquedas y edición de cliente.** RF-4–RF-7, RF-12, RF-19–RF-21, RF-23. V; depende T44.
  - Hecho cuando: matriz visual/teclado, tres búsquedas, selección y PUT local ficticio pasan; refresh WFS/geocodificación/eventos revisados en consola/red.
- [ ] **T46. Verificar alta con ubicación.** RF-7, RF-9, RF-12, RF-19–RF-21, RF-23. V; depende T45.
  - Hecho cuando: matriz alta, selección de punto sin bloqueo y POST ficticio local pasan; coordenadas/ejes/refresco/cierre comprobados.
- [ ] **T47. Verificar pedidos y estadísticas.** RF-4–RF-6, RF-12, RF-19–RF-21, RF-23. V; depende T46.
  - Hecho cuando: matriz tabla/tarjetas/scroll, GET real, selección/zoom y cálculos conservados; respuesta vacía y fallos existentes registrados sin aprobación falsa.
- [ ] **T48. Verificar capas, información y notificación global.** RF-8, RF-12, RF-15, RF-16, RF-19, RF-20, RF-23. V; depende T47.
  - Hecho cuando: matriz interfaz mapa/mensajes pasa con fuentes reales; overlay/convivencia y duración preservados; sin cambio de cartografía/simbología.
- [ ] **T49. Verificar catálogo/guía y privacidad de evidencias.** RF-1–RF-4, RF-10, RF-22, RF-23; RNF-5. V/D; depende T48.
  - Hecho cuando: todas las familias/estados y exclusiones están enlazadas y navegables; ejemplos sin API ni datos reales, enlaces/capturas/mediciones identificables.
- [ ] **T50. Reconciliar cobertura y preparar validación de entrega.** RF-11, RF-12, RF-23; RNF-1–RNF-6. V/D; depende T49.
  - Hecho cuando: runner/build finales y evidencias tienen resultados veraces; cada requisito tiene evidencia o bloqueo explícito, hallazgos resueltos/autorizados. Solo si todo incluido pasa se solicita aceptación; no marcar spec implementada por completar este checklist sin validación.

## Decisión pendiente

Por superar diez tareas, se propone dividir ejecución en cinco specs derivadas/bloques de diez, con 001 como contrato de alcance. No se han creado specs derivadas ni se ha cambiado la spec aprobada. Usuario debe aprobar división y plan/tareas o indicar otra organización antes de implementar.
