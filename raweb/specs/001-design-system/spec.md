# Spec 001 — Design system de raweb

Estado: aprobada

QA: LISTA PARA APROBACIÓN tras las dos correcciones aceptadas. Aprobación global del usuario: respuesta exacta «si». Autoriza preparar plan y tareas; su aprobación separada sigue siendo necesaria antes de implementar.

## Contexto y objetivo

Petición original exacta del usuario: «construir el design system de raweb».

El objetivo es disponer de un lenguaje de interfaz compartido que mantenga coherencia entre las experiencias de raweb y reduzca decisiones de presentación repetidas. La entrega incluye fundaciones visuales, componentes reutilizables, documentación/ejemplos y migración de la interfaz existente. Conserva y unifica la identidad actual en claro y oscuro, con ajustes cromáticos, cabeceras compactas, selector de tema y accesibilidad acotada. Se preservan flujos, distribución y comportamiento salvo las excepciones expresamente aprobadas en RF-16. Los requisitos siguientes constituyen la spec aprobada globalmente tras QA.

### Estado existente observado

Inspección estática de la interfaz y sus estilos; estas observaciones no constituyen una validación visual o funcional en navegador.

- La experiencia principal gira alrededor de un mapa, con navegación de escritorio y móvil, búsqueda de direcciones, búsqueda y edición de clientes, alta de clientes y consulta de pedidos.
- Hay botones con texto, símbolos y emojis; campos de texto, número, teléfono y horario; áreas de texto, casillas y opciones exclusivas; diálogos, tablas con filas accionables, tarjetas de estadísticas, panel de capas, controles flotantes, información del elemento seleccionado y notificaciones.
- Existen reglas base de tipografía, espaciado, foco, botones y adaptación móvil, junto con variantes específicas de cada experiencia. No se identificó un catálogo explícito de reglas y componentes con sus contratos de uso.
- Las acciones primarias usan azules diferentes y, en el alta, un degradado violeta. Las acciones de ubicación usan verde. Los diálogos varían en encabezados, dimensiones, espaciado y acciones de cierre; las diferencias podrían ser intencionales y necesitan evaluación.
- La tipografía base combina una familia de sistema y Arial. Hay bordes, radios, sombras y animaciones repetidos con variaciones.
- Las reglas base proponen botones táctiles de al menos 44 píxeles, o 48 en móvil, mientras controles del mapa se declaran de 28–30 píxeles y algunos cierres de 24–36. No se ha medido el área interactiva efectiva.
- El modo oscuro solo tiene reglas parciales en búsqueda de clientes. La reducción de movimiento está contemplada en dos diálogos, sin una política transversal identificada.
- La comunicación mezcla alertas del navegador, mensajes dentro de diálogos y notificaciones temporales. El estado vacío se presenta como error en algunas consultas. Las advertencias globales no tienen una variante visual específica.
- Las tablas contemplan desplazamiento horizontal y los diálogos desplazamiento vertical. El alta requiere alternar entre formulario y selección de una ubicación en el mapa.

### Registro de decisiones de clarificación

- **Confirmado por la petición:** el producto destinatario es raweb y se solicita construir su design system.
- **Restricciones vigentes:** respetar la constitución del proyecto, documentar en español y no exponer datos personales ni credenciales.
- **Decisión confirmada de alcance:** a la pregunta sobre los bloques de la primera entrega, el usuario respondió exactamente «los cuatro bloques». Se incluyen fundaciones visuales, componentes reutilizables, documentación y ejemplos de uso, y migración de la UI existente.
- **Respuesta exacta sobre identidad:** «A pero si hay que modificar colores por ejemplo de los botones para que se vea mejor en oscuro cambiarlos, verificar combinacion de colores para oscuro y claro. El header de los formularios no debe ser muy alto ya que ocuparia mucha pantalla».
- **Decisiones confirmadas de identidad y presentación:** conservar y unificar la identidad actual (opción A); permitir cambios de colores, incluidos botones, para mejorar legibilidad y coherencia; requerir ambos temas, claro y oscuro, y verificar sus combinaciones cromáticas; mantener compactas las cabeceras de los formularios para no consumir excesiva pantalla.
- **Respuesta exacta sobre cobertura:** «si confirmo esta entrega», en respuesta a la propuesta de migración de navegación de escritorio/móvil; formularios de búsqueda de dirección, búsqueda/edición de clientes y alta; tablas/estadísticas de pedidos; notificaciones; paneles, controles flotantes e información del mapa. Se confirma la unificación visual claro/oscuro y cabeceras compactas conservando los flujos actuales, sin rediseñar distribución o interacción salvo los ajustes necesarios en las cabeceras.
- **Alcance de esta confirmación:** aprueba esa cobertura y sus límites, no la spec completa ni el paso a plan o implementación. No incluye por inferencia cambios de simbología o cartografía base.
- **Respuesta exacta sobre contraste y altura:** «si», en respuesta a los criterios propuestos. Quedan aprobados, en claro y oscuro, contraste de texto normal ≥ 4,5:1, texto grande ≥ 3:1 y elementos necesarios para identificar controles/estados ≥ 3:1, tomando como referencia los criterios correspondientes de WCAG AA, sin certificación total de la aplicación. Cabeceras de formularios de máximo 48 px con título de una línea y hasta 64 px con título de dos líneas en móvil; con texto ampliado se permite crecer para no recortar título ni cierre.
- **Respuesta exacta sobre elección de tema:** «Automático con selector manual». Se confirma seguir la preferencia claro/oscuro del dispositivo por defecto y permitir elegir Claro, Oscuro o Sistema dentro de raweb. Sistema sigue la preferencia del dispositivo; Claro y Oscuro permiten elegir el tema independientemente de ella. Se autoriza este control adicional, sin fijar su ubicación ni la conservación de la elección entre visitas.
- **Respuesta exacta sobre persistencia del tema:** «si», a recordar Claro/Oscuro/Sistema al recargar o volver a abrir raweb en el mismo navegador; sin elección guardada, usar Sistema. Se aprueba esta persistencia entre visitas, sin presuponer sincronización entre dispositivos ni cuentas. La ubicación se confirmó en la decisión posterior.
- **Respuesta exacta sobre ubicación del selector:** «si». Se confirma el selector etiquetado «Tema» al final de las acciones de la barra superior en escritorio y dentro del menú desplegable móvil, debajo de sus acciones, manteniendo compacta la cabecera móvil.
- **Respuesta exacta sobre teclado y foco:** «estoy de acuerdo continua». Se aprueban recorrido Tab/Mayús+Tab y activación por teclado según el tipo de control, foco visible en ambos temas, nombres accesibles en botones solo con iconos, foco al interior al abrir un diálogo y retorno al disparador al cerrar, sin trampas ni bloqueo de selección de ubicación en el mapa. Se excluyen selección de coordenadas por teclado y certificación total de accesibilidad. «continua» permite continuar la clarificación; no aprueba globalmente la spec, el plan ni decisiones pendientes.
- **Respuesta exacta sobre verificación y consulta:** «si continua». Se aprueba verificar las experiencias incluidas en ambos temas a 360×800, 800×360, 768×1024 y 1366×768 px de área visible; texto ampliado al 200 % en móvil vertical y escritorio, con contenido y acciones accesibles mediante desplazamiento cuando sea necesario y conservando desplazamiento horizontal de tablas; guía en español y catálogo visual interactivo con variantes, estados aplicables y ejemplos ficticios en ambos temas; matriz de cobertura con capturas, mediciones de contraste/cabeceras y resultados de teclado, foco, temas y flujos. No es aprobación global de spec/plan.
- **Respuesta exacta sobre inventario y límite de entrega:** «si continua». Se confirman las fundaciones y el catálogo de la sección Cobertura, con variantes existentes y estados aplicables. Se conservan mensajes, animaciones, cierre, convivencia de paneles, tamaños interactivos y reglas de funcionamiento salvo tema, accesibilidad y cabeceras aprobados; sin nuevas validaciones, estados funcionales ni políticas de notificaciones. RF-6 a RF-9 se acotan a ese límite.
- **Alcance de las aprobaciones:** decisiones particulares de clarificación; no aprobación global de spec/plan. Los valores visuales y las soluciones técnicas podrán definirse dentro de estos criterios en el futuro plan.
- **Aprobación global posterior:** respuesta exacta «si» tras el veredicto QA LISTA PARA APROBACIÓN. Las decisiones particulares anteriores quedan consolidadas; no implica aprobación del plan ni de las tareas.

## Usuarios

Destinatarios derivados de los flujos y entregables incluidos; no se introducen perfiles ni permisos nuevos.

- Personas que consultan y actualizan clientes y pedidos, y ubican información en el mapa, desde escritorio o móvil.
- Personas que diseñan y mantienen la interfaz y necesitan criterios compartidos para elegir y utilizar sus elementos.
- Personas que revisan la coherencia de las experiencias y las evidencias. La aprobación final corresponde al usuario.

## Historias de usuario

Historias que resumen los requisitos consolidados y aprobados globalmente.

- HU-1. Como persona que mantiene la interfaz, quiero consultar reglas visuales comunes para presentar acciones e información sin redefinirlas en cada experiencia.
- HU-2. Como persona que mantiene la interfaz, quiero consultar los estados y usos de cada componente incluido para elegir el patrón apropiado.
- HU-3. Como persona usuaria de raweb, quiero reconocer acciones, selección, validación y resultados en las experiencias adoptadas para comprender qué ocurre y cómo continuar.
- HU-4. Como persona usuaria móvil o de teclado, quiero acceder al contenido y a las acciones de las experiencias adoptadas para completar los flujos incluidos.
- HU-5. Como persona que revisa el producto, quiero comparar ejemplos y cobertura con criterios acordados para aceptar el design system sin depender solo de apreciaciones subjetivas.

## Definiciones

- **Design system:** conjunto de reglas visuales, elementos de interfaz y guías de uso para la cobertura definida abajo, documentando el comportamiento existente y las excepciones aprobadas.
- **Fundaciones:** reglas de color y significado, tipografía, espaciado, dimensiones, bordes, radios, elevación, iconografía y movimiento.
- **Componente:** elemento de interfaz con propósito, variantes y estados definidos; por ejemplo, botón o campo.
- **Patrón:** combinación de elementos para una situación repetida; por ejemplo, un formulario con validación o un diálogo con acciones.
- **Adopción o migración de UI:** aplicación del design system a experiencias existentes, distinta de definirlo y ejemplificarlo.
- **Cobertura:** inventario delimitado en la sección siguiente, experiencias de RF-15 y matriz de RNF-3.

## Cobertura

- **Fundaciones:** colores semánticos, tipografía, espaciado y dimensiones, bordes y radios, sombras/elevación e iconografía. Documentar las animaciones existentes sin introducir una política nueva de movimiento.
- **Catálogo:** botones; campos y áreas de texto; casillas y opciones exclusivas; selector de tema; diálogos; navegación de escritorio/móvil; tablas y filas accionables; estadísticas; notificaciones; paneles, controles flotantes e información del mapa presentes en las experiencias de RF-15.
- **Variantes y estados:** variantes existentes y estados aplicables de normal, foco, interacción, selección, deshabilitado, carga y mensajes existentes, además del selector y las mejoras aprobadas. La guía identifica los estados no aplicables; no se crean estados funcionales nuevos para completar el catálogo.
- **Temas y ejemplos:** todo elemento incluido se documenta y ejemplifica en claro y oscuro con datos ficticios.
- **Comportamiento:** se conserva conforme a RF-16. Las reglas de notificación, animación, cierre y convivencia se documentan tal como existen; no se normalizan mediante nuevas políticas.
- **Límite de presentación — alertas nativas:** los mensajes mediante alertas nativas del navegador conservan su mensaje, disparador y comportamiento. Su apariencia, tema y contraste son controlados por el navegador y quedan fuera de la unificación visual y de las mediciones. La guía y la matriz de cobertura identificarán esos casos y verificarán su funcionamiento, sin exigir sustituir las alertas. Los requisitos de presentación y temas se aplican a los elementos controlados por raweb conforme a este límite. Corrección del segundo hallazgo QA aprobada con respuesta exacta «si».

## Requisitos funcionales

Requisitos consolidados y aprobados globalmente. No añaden comportamientos fuera de la Cobertura y RF-16.

### Fundaciones

- RF-1: EL SISTEMA ofrecerá, para cada fundación incluida en la cobertura aprobada, una definición con nombre, propósito, valores permitidos y un ejemplo de uso.
- RF-2: EL SISTEMA distinguirá los significados visuales incluidos —como acción principal, acción secundaria, selección, éxito, advertencia y error— mediante reglas documentadas que indiquen cuándo utilizar cada uno.
- RF-3: CUANDO se consulte una regla de identidad visual, EL SISTEMA identificará los elementos que deben conservarse de la UI actual y los cambios aprobados, con ejemplos comparables de ambos.

### Componentes y patrones

- RF-4: CUANDO se consulte un componente o patrón incluido, EL SISTEMA mostrará su propósito, variantes permitidas, estados aplicables, reglas de interacción y ejemplos que cubran cada variante y estado declarado.
- RF-5: CUANDO un control incluido reciba foco, se active, se seleccione o se deshabilite, EL SISTEMA presentará el estado correspondiente conforme a su definición; los estados no aplicables se identificarán expresamente en su guía.
- RF-6: CUANDO una experiencia incluida presente carga, ausencia de resultados o fallo mediante un estado existente, EL SISTEMA conservará su comportamiento y contenido y unificará su presentación visual conforme a las fundaciones. La guía documentará esos estados sin exigir nuevos indicadores ni reclasificar mensajes existentes.
- RF-7: CUANDO un formulario incluido presente una validación existente, EL SISTEMA conservará su regla y mensaje y aplicará la presentación visual común; no añadirá validaciones ni cambiará su momento de ejecución.
- RF-8: CUANDO se presente una notificación incluida, EL SISTEMA conservará su mensaje y reglas actuales de permanencia, sustitución, convivencia y cierre, aplicando las fundaciones visuales. La guía documentará las variantes existentes sin introducir una nueva política de notificaciones.
- RF-9: CUANDO se abra o cierre un diálogo incluido, EL SISTEMA conservará sus reglas de cierre y relación con el fondo, salvo el tratamiento de foco aprobado en RF-21; durante la selección de ubicación permitirá la interacción existente con el mapa.

### Documentación y adopción

- RF-10: CUANDO una persona consulte la guía de uso, EL SISTEMA permitirá identificar qué elementos están incluidos, elegir entre sus variantes mediante criterios documentados y consultar ejemplos con datos ficticios.
- RF-11: CUANDO una experiencia existente forme parte de la adopción aprobada, EL SISTEMA utilizará en ella las reglas, variantes y estados acordados para los elementos incluidos; las excepciones aprobadas se identificarán con su motivo.
- RF-12: CUANDO una persona realice un flujo existente incluido en la adopción, EL SISTEMA conservará sus operaciones de negocio, datos de entrada y resultados esperados, salvo los cambios de interacción aprobados expresamente en esta spec.

### Identidad, temas y cabeceras — decisiones confirmadas

- RF-13: EL SISTEMA conservará y unificará la identidad visual actual en los elementos incluidos y ofrecerá sus variantes claro y oscuro; los ajustes cromáticos permitidos responderán a legibilidad y coherencia entre ambos temas, y sus combinaciones de texto, fondo y estados se verificarán en ambos conforme a RNF-2. No se fija una paleta concreta.
- RF-14: CUANDO se muestre un formulario incluido con título de una línea, EL SISTEMA limitará su cabecera a un máximo de 48 px; CUANDO el título ocupe dos líneas en móvil, EL SISTEMA permitirá una altura de hasta 64 px; SI el texto está ampliado, ENTONCES EL SISTEMA permitirá que la cabecera crezca lo necesario para no recortar el título ni el cierre.

### Cobertura de migración — decisión confirmada

- RF-15: EL SISTEMA aplicará la unificación visual en claro y oscuro a la navegación de escritorio y móvil; los formularios de búsqueda de dirección, búsqueda/edición de clientes y alta; las tablas y estadísticas de pedidos; las notificaciones; y los paneles, controles flotantes e información del mapa, con cabeceras compactas en los formularios.
- RF-16: CUANDO se utilice cualquiera de las experiencias migradas, EL SISTEMA conservará sus flujos, distribución e interacciones actuales, salvo los ajustes de cabecera necesarios para cumplir RF-14, la selección de tema aprobada en RF-17 y las mejoras acotadas de teclado, foco y nombres accesibles de RF-19 a RF-21. La migración visual no autoriza otros rediseños ni cambios de negocio.

### Elección de tema — decisión confirmada

- RF-17: EL SISTEMA seguirá por defecto la preferencia claro/oscuro del dispositivo y ofrecerá dentro de raweb un selector manual con las opciones Claro, Oscuro y Sistema; CUANDO se elija Claro u Oscuro, EL SISTEMA aplicará el tema elegido independientemente de la preferencia del dispositivo; MIENTRAS esté seleccionada la opción Sistema, EL SISTEMA seguirá la preferencia del dispositivo. El selector llevará la etiqueta «Tema» y se ubicará al final de las acciones de la barra superior en escritorio y dentro del menú desplegable móvil, debajo de sus acciones, manteniendo compacta la cabecera móvil.
- RF-18: CUANDO se elija Claro, Oscuro o Sistema, EL SISTEMA recordará esa opción al recargar o volver a abrir raweb en el mismo navegador; SI no existe una elección guardada, ENTONCES EL SISTEMA utilizará Sistema. No se presupone sincronización entre dispositivos ni cuentas.

### Teclado, foco y nombres accesibles — decisión confirmada

- RF-19: CUANDO una persona utilice Tab o Mayús+Tab en la interfaz incluida, EL SISTEMA permitirá recorrer los controles habilitados sin trampas de teclado y activarlos con las teclas correspondientes a su tipo; MIENTRAS un control tenga foco, EL SISTEMA mostrará un indicador de foco visible en claro y oscuro.
- RF-20: EL SISTEMA proporcionará un nombre accesible que describa la acción de cada botón incluido representado solo mediante iconos.
- RF-21: CUANDO se abra un diálogo incluido, EL SISTEMA llevará el foco a su interior; CUANDO se cierre un diálogo incluido, EL SISTEMA devolverá el foco al control que lo abrió si sigue presente y visible; SI se abrió desde una acción del menú móvil que desaparece al cerrarse dicho menú, ENTONCES EL SISTEMA devolverá el foco al botón «Menú», manteniendo el menú cerrado. EL SISTEMA permitirá la selección de ubicación en el mapa durante el alta sin que estas reglas la bloqueen. Se excluye de esta entrega la selección de coordenadas mediante teclado; estas mejoras no implican certificación total de accesibilidad.

### Consulta y evidencias — decisión confirmada

- RF-22: EL SISTEMA ofrecerá una guía en español y un catálogo visual interactivo de los elementos incluidos, con sus variantes y estados aplicables y ejemplos ficticios en claro y oscuro.
- RF-23: EL SISTEMA contará con una matriz de cobertura que relacione los elementos y experiencias incluidos con capturas, mediciones de contraste y cabeceras y resultados de verificación de teclado, foco, temas y flujos.

## Requisitos no funcionales

Criterios consolidados para la cobertura incluida. La referencia a WCAG AA se limita a los criterios de contraste indicados; no se acuerda conformidad total.

- RNF-1 — Consistencia verificable: todos los ejemplos y experiencias adoptadas se podrán contrastar con una matriz de cobertura; cada diferencia respecto de la definición deberá corresponder a una excepción aprobada.
- RNF-2 — Contraste: en la presentación controlada por raweb, en ambos temas, texto normal ≥ 4,5:1, texto grande ≥ 3:1 y elementos necesarios para identificar controles y estados ≥ 3:1, conforme a los criterios correspondientes de WCAG AA. Verificar las combinaciones aplicables con sus fondos y estados conforme al límite de presentación de la sección Cobertura; la apariencia, tema y contraste de las alertas nativas del navegador quedan fuera de estas mediciones. Esta referencia no implica certificación o conformidad total de la aplicación. La accesibilidad adicional se limita a RF-19 a RF-21; no se añaden otros requisitos de etiquetas, comunicación o tamaños interactivos.
- RNF-3 — Adaptación y verificación aprobadas: verificar las experiencias incluidas en claro y oscuro a 360×800, 800×360, 768×1024 y 1366×768 px de área visible; verificar además texto ampliado al 200 % en móvil vertical (360×800) y escritorio (1366×768). Todo el contenido y las acciones serán accesibles, mediante desplazamiento cuando sea necesario, sin recortes que impidan su uso. Se conserva el desplazamiento horizontal de tablas y su distribución actual.
- RNF-4 — Temas y movimiento: claro y oscuro cubrirán las variantes y estados aplicables de todo elemento incluido, con verificación cromática, selector y ubicación de RF-17 y persistencia de RF-18. Se conservan las animaciones y el soporte de preferencias de movimiento existentes, sin introducir una política transversal nueva.
- RNF-5 — Idioma y privacidad: la documentación y los textos nuevos estarán en español; los ejemplos no incluirán credenciales ni datos personales reales.
- RNF-6 — Compatibilidad funcional: la adopción incluida se verificará en los flujos acordados de búsqueda, edición, alta con ubicación, consulta de pedidos y navegación del mapa, sin alterar cálculos ni persistencia por una decisión de presentación.

## Casos límite

Casos de verificación, no autorización para añadir reglas de negocio o interacción.

- Textos largos, observaciones multilínea, datos ausentes, pantallas estrechas, orientación horizontal y tablas anchas: comprobar acceso a contenido y acciones conforme a RNF-3, con desplazamiento cuando sea necesario.
- Carga, resultados vacíos, errores y validación existentes: verificar conservación de comportamiento/mensajes y presentación visual conforme a RF-6/RF-7.
- Diálogo, menú, paneles e información del mapa simultáneos; notificaciones consecutivas o extensas: preservar cierre, convivencia y permanencia conforme a RF-8/RF-9/RF-16.
- Alta con ubicación: verificar que el foco de diálogos no bloquea la selección en el mapa.
- Cierre de formulario/diálogo abierto desde el menú móvil: verificar que el foco vuelve al botón «Menú» sin reabrir el menú; si el control que abrió el diálogo sigue presente y visible, verificar el retorno a ese control. Corrección del primer hallazgo QA aprobada con respuesta exacta «si».
- Controles y filas accionables, botones con iconos: verificar recorrido y activación por teclado, foco y nombres conforme a RF-19 a RF-21.
- Tema: verificar seguimiento del dispositivo en Sistema, elección manual, restauración de cada opción entre visitas y Sistema sin elección guardada; comprobar acceso al selector en escritorio/móvil.
- Cabeceras: medir RF-14 en la matriz RNF-3 y con texto ampliado sin recortar título ni cierre. No se añaden límites o excepciones para otros casos; una incompatibilidad observada con títulos reales deberá señalarse en QA, sin resolverla por inferencia.
- Fondos cartográficos claros y satelitales: comprobar lectura de controles/paneles incluidos; conservar simbología y cartografía base.

## Límites y fuera de alcance

- **Separación de fases:** la spec fija alcance y comportamiento; las soluciones técnicas y tareas se documentan aparte y requieren aprobación antes de implementar.
- **Fuera del alcance delimitado:** nuevas operaciones de negocio, validaciones, políticas de mensajes/notificaciones o movimiento; cambios de datos, cálculos o permisos; rediseño de otros productos; reemplazo de cartografía base o simbología del mapa.
- **Alcance confirmado por bloques:** fundaciones visuales, componentes reutilizables, documentación y ejemplos de uso, y migración de la UI existente.
- **Presentación confirmada:** conservar y unificar la identidad actual con ajustes cromáticos permitidos; ambos temas claro/oscuro y revisión de sus combinaciones; cabeceras compactas de formularios.
- **Criterios aprobados:** contraste según RNF-2 y altura de cabeceras según RF-14, incluidas las excepciones expresamente aceptadas. No se extiende esta aprobación a conformidad completa con WCAG.
- **Migración confirmada:** las experiencias enumeradas en RF-15; mantener flujos, distribución e interacción salvo las excepciones de RF-16: cabeceras, selección de tema y mejoras acotadas de teclado, foco y nombres accesibles. Otros rediseños quedan fuera del alcance confirmado.
- **Accesibilidad acotada confirmada:** RF-19 a RF-21; se excluyen selección de coordenadas por teclado y certificación total de accesibilidad.
- **Elección de tema confirmada:** automático con selector manual Claro/Oscuro/Sistema dentro de raweb, siguiendo el dispositivo por defecto; recordar la opción entre visitas en el mismo navegador y usar Sistema sin elección guardada (RF-18). Selector «Tema» al final de acciones de barra superior en escritorio y debajo de acciones dentro del menú desplegable móvil (RF-17).
- **Consulta y verificación confirmadas:** guía en español, catálogo visual interactivo y evidencias de RF-22/RF-23; pantallas y texto ampliado de RNF-3.
- **Inventario confirmado:** la sección Cobertura. Se conservan reglas de funcionamiento, animaciones y mensajes salvo las excepciones expresamente aprobadas. No se solicitan nuevos recursos de marca.
- Los comportamientos existentes descritos son contexto, no aprobación de su diseño actual ni autorización para corregir cualquier defecto encontrado.

## Criterios de finalización

### Para aprobar la spec

- Revisar en QA consistencia, trazabilidad de las decisiones, cobertura y verificabilidad de los requisitos consolidados. El reviewer solo detecta hallazgos; no aprueba ni añade requisitos.
- Resolver los hallazgos reales que impidan la aprobación, consultando al usuario si afectan alcance o comportamiento. No reabrir decisiones particulares resueltas.
- Obtener aprobación explícita del usuario. **Completado:** respuesta exacta «si» tras QA LISTA PARA APROBACIÓN; plan y tareas requieren aprobación separada.

### Para aceptar la futura entrega

- Cada fundación, componente y patrón aprobado cuenta con su definición y con los ejemplos exigidos por RF-1 a RF-10 que resulten aplicables.
- La matriz de cobertura relaciona cada elemento y estado aprobado con una evidencia de aceptación; no quedan casos incluidos sin comprobar.
- Las experiencias seleccionadas para adopción cumplen RF-11 y RF-12, con excepciones expresamente aceptadas.
- Todas las experiencias enumeradas en RF-15 tienen evidencia de unificación visual en ambos temas y de conservación de flujos, distribución e interacción según RF-16.
- Se cumple RNF-3 en ambos temas y se entregan la guía, el catálogo y la matriz de evidencias aprobados en RF-22/RF-23, incluyendo las comprobaciones de texto ampliado al 200 %.
- Se registran las mediciones de contraste de las combinaciones aplicables en claro y oscuro conforme a RNF-2, y las alturas de cabeceras y los casos de texto ampliado conforme a RF-14.
- Se verifica el seguimiento del tema del dispositivo por defecto y en Sistema, y la selección manual de Claro y Oscuro según RF-17. Se verifica para cada opción su conservación al recargar y volver a abrir raweb en el mismo navegador, y Sistema sin elección guardada según RF-18; el selector «Tema» es accesible al final de las acciones de la barra superior en escritorio y debajo de las acciones dentro del menú desplegable móvil.
- La persona responsable de aceptación confirma los entregables y la cobertura aprobados.
- Se verifica recorrido y activación por teclado, foco visible en ambos temas, nombres accesibles de botones con iconos y foco al abrir/cerrar diálogos según RF-19 a RF-21; se comprueba que el alta permite seleccionar ubicación en el mapa.

## Dudas abiertas

Los dos hallazgos bloqueantes de la revisión QA recibieron aprobación particular «si» y sus correcciones están aplicadas: retorno de foco desde el menú móvil (RF-21/casos límite) y límite de presentación de alertas nativas (Cobertura/RNF-2). No quedan decisiones pendientes sobre esos hallazgos.

**QA completada tras las correcciones:** LISTA PARA APROBACIÓN, sin nuevos bloqueantes ni contradicciones detectadas. Aprobación global posterior del usuario: «si». Si aparece una incompatibilidad que requiera cambiar un criterio aprobado, se consultará al usuario; no se añadirá una excepción automáticamente.

**Aprobaciones pendientes:** plan y tareas, incluida la organización por bloques propuesta para la entrega. No se autoriza implementación hasta obtenerlas.

**Detalles para el futuro plan:** valores visuales dentro de los criterios acordados, organización técnica de componentes/catálogo, almacenamiento de preferencia y herramientas de verificación. No constituyen dudas independientes de alcance.
