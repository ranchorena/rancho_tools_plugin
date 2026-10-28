# Spec 002 — Cómo llegar

Estado: aprobada (el usuario pidió implementar el plan completo el 2026-10-27)

## Contexto y objetivo
Quien reparte necesita saber por qué calles ir desde donde está, o desde un punto cualquiera, hasta un cliente o una dirección. El callejero ya tiene la red de calles con su sentido de circulación. El objetivo es mostrar en el mapa el recorrido más corto que respeta las manos de las calles.

## Usuarios
- Repartidor con el móvil y la ubicación activada.
- Operador en escritorio que planifica un reparto.

## Historias de usuario
- HU-1. Como repartidor, quiero que el origen sea mi ubicación actual para no tener que escribirla.
- HU-2. Como operador, quiero indicar origen y destino con una dirección o tocando el mapa para planificar recorridos.
- HU-3. Como repartidor, quiero ver el recorrido en rojo sobre el mapa sin ir nunca a contramano.

## Definiciones
- **Punto:** un par latitud/longitud con un texto que lo describe (dirección, «Mi ubicación» o coordenadas).
- **Recorrido:** sucesión de tramos del callejero, cada uno recorrido en un sentido permitido, que empieza y termina en el punto del tramo más cercano al origen y al destino (los tramos extremos se recortan), más un segmento recto corto desde el origen hasta ese punto y desde el último punto hasta el destino.
- **Sentido de un tramo:** 0 solo de inicio a fin, 1 solo de fin a inicio, 2 o vacío doble mano.

## Requisitos funcionales
- RF-1: EL SISTEMA ofrece la acción «Cómo llegar» en la barra de escritorio y en la barra inferior móvil.
- RF-2: CUANDO se abre el diálogo y la ubicación del móvil está activa con una posición recibida, EL SISTEMA completa el origen con «Mi ubicación».
- RF-3: MIENTRAS la ubicación del móvil no esté activa, EL SISTEMA deshabilita el botón «Mi ubicación» y deja el origen vacío para ingresar una dirección o elegir en el mapa.
- RF-4: CUANDO el usuario ingresa una dirección en origen o destino y pide buscarla, EL SISTEMA la geocodifica con la búsqueda de direcciones existente y fija ese punto.
- RF-5: SI la dirección no se encuentra o tiene formato inválido, ENTONCES EL SISTEMA muestra el mensaje del servidor y no cambia el punto.
- RF-6: CUANDO el usuario pulsa «Elegir en el mapa» de origen o destino, EL SISTEMA oculta el diálogo, toma el siguiente click del mapa como ese punto, muestra sus coordenadas y vuelve a mostrar el diálogo.
- RF-7: MIENTRAS se elige un punto en el mapa, EL SISTEMA no abre la información de pedidos o clientes con ese click.
- RF-8: CUANDO el usuario pulsa «Intercambiar», EL SISTEMA intercambia origen y destino.
- RF-9: MIENTRAS falte el origen o el destino, EL SISTEMA deshabilita «Ver recorrido».
- RF-10: CUANDO el usuario pulsa «Ver recorrido», EL SISTEMA dibuja en rojo el recorrido de menor longitud en metros, sin recorrer ningún tramo en contra de su sentido, marca origen y destino, encuadra el recorrido y muestra la distancia total.
- RF-11: SI no hay recorrido posible entre los puntos, ENTONCES EL SISTEMA avisa «No hay recorrido posible entre los puntos elegidos.» y no dibuja nada.
- RF-12: SI un punto está a más de 300 m de la red de calles, ENTONCES EL SISTEMA avisa que está fuera del callejero.
- RF-13: SI origen y destino quedan sobre el mismo tramo, ENTONCES EL SISTEMA recorre solo la parte del tramo entre ambos si el sentido lo permite, o da la vuelta por las calles si no.
- RF-16: EL SISTEMA dibuja el recorrido empezando en el punto de origen y terminando en el de destino, sin pasar dos veces por la cuadra del origen o del destino por ir hasta una esquina.
- RF-14: CUANDO el usuario pulsa «Limpiar» en el mapa, EL SISTEMA borra el recorrido y sus marcas.
- RF-15: SI la ubicación se desactiva con el diálogo abierto y el origen era «Mi ubicación», ENTONCES EL SISTEMA vacía el origen.

- RF-17: CUANDO el usuario pulsa «Marcar el pedido más cercano» con la posición del móvil activa, EL SISTEMA elige el pedido activo con el recorrido más corto en metros por las calles respetando el sentido, no el más cercano en línea recta.
- RF-18: CUANDO encuentra ese pedido, EL SISTEMA lo resalta como hasta ahora, dibuja en rojo el recorrido desde la posición actual, encuadra el recorrido y muestra la distancia.
- RF-19: SI ningún pedido activo es alcanzable por el callejero o la posición está a más de 300 m de la red, ENTONCES EL SISTEMA avisa y no marca ningún pedido.

## Requisitos no funcionales
- RNF-1: El diálogo usa los componentes y tokens del design system de raweb (cabecera, campos, botones, foco, temas claro y oscuro).
- RNF-2: El diálogo entra en un ancho de 360 px sin desplazamiento horizontal.
- RNF-3: Las coordenadas viajan en EPSG:4326 entre web y API.

## Casos límite
- Ubicación activada pero sin posición recibida todavía: «Mi ubicación» deshabilitado.
- Grafo con tramos sin salida por sentido: sin recorrido (RF-11).
- Coordenadas fuera de rango: error de validación.
- El usuario cierra el diálogo mientras elige en el mapa: se cancela la elección.

## Fuera de alcance
- Indicaciones paso a paso, tiempo estimado y rutas alternativas.
- Modificar las tablas `callejero` o `callejero_vertices_pgr`.

## Criterios de finalización
- `npm run build` y `node --test` sin errores.
- Recorrido calculado por la API igual al de pgRouting para un par de cruces conocido.
- Flujo verificado en navegador en escritorio y en 360 px, o requisitos faltantes informados.

## Dudas abiertas
- Ninguna. Enmienda 2026-10-27 a pedido del usuario: el pedido más cercano se mide por recorrido y marca la ruta (RF-17 a RF-19). Costo en metros decidido por el usuario. Enmienda 2026-10-27 a pedido del usuario («la línea debería empezar en el punto de origen»): conexión al punto más cercano del tramo en lugar del cruce (RF-13 y RF-16).
