# Spec 003 — Búsqueda en el mapa

Estado: aprobada (el usuario pidió implementar el plan completo el 2026-11-21)

## Contexto y objetivo
Quien reparte o planifica necesita ubicar un cliente o un pedido sin abrir un diálogo ni recorrer el mapa. El objetivo es una caja sobre el mapa que, al escribir, proponga pedidos y clientes y lleve la vista al punto elegido.

## Usuarios
- Repartidor con el móvil.
- Operador en escritorio.

## Historias de usuario
- HU-1. Como operador, quiero escribir en una caja sobre el mapa y ver sugerencias debajo para no salir del mapa.
- HU-2. Como operador, quiero ver por separado los pedidos y los clientes para distinguir un reparto de un cliente sin pedido.
- HU-3. Como repartidor, quiero tocar un resultado y que el mapa se acerque a ese punto para llegar al lugar.

## Definiciones
- **Pedido activo:** un cliente con pedido vigente y el último pedido sin completar, el mismo conjunto que muestra la capa Pedidos del mapa.
- **Cliente:** cualquier cliente con ubicación, tenga o no pedido.

## Requisitos funcionales
- RF-1: EL SISTEMA muestra sobre el mapa una caja con el texto «Buscar cliente o pedido».
- RF-2: MIENTRAS el texto, sin espacios al inicio ni al final, tenga menos de 3 caracteres, EL SISTEMA no consulta y no muestra la lista.
- RF-3: CUANDO el texto llega a 3 caracteres y pasan 300 ms sin otro cambio, EL SISTEMA busca ese texto en pedidos activos y en clientes.
- RF-4: CUANDO llega una búsqueda más nueva, EL SISTEMA descarta el resultado de la anterior.
- RF-5: EL SISTEMA compara el texto sin distinguir mayúsculas ni acentos contra el nombre, la dirección y la calle.
- RF-6: EL SISTEMA muestra primero el grupo «Pedidos» y después el grupo «Clientes», como máximo 8 resultados en cada uno.
- RF-7: SI un grupo no tiene coincidencias, ENTONCES EL SISTEMA no muestra el título de ese grupo.
- RF-8: SI no hay coincidencias en ningún grupo, ENTONCES EL SISTEMA muestra «Sin resultados».
- RF-9: CUANDO el usuario elige un resultado con clic, Enter o la fila resaltada, EL SISTEMA centra el mapa en su ubicación, se acerca al nivel de zoom 18, deja una marca y cierra la lista.
- RF-10: CUANDO el usuario pulsa Escape o toca fuera de la caja y de la lista, EL SISTEMA cierra la lista.
- RF-11: MIENTRAS la lista está abierta, EL SISTEMA permite mover la fila resaltada con las flechas arriba y abajo.
- RF-12: SI la búsqueda falla, ENTONCES EL SISTEMA muestra que no se pudo buscar y no mueve el mapa.
- RF-13: EL SISTEMA mantiene las búsquedas de cliente y de dirección que ya existen en los diálogos.

## Requisitos no funcionales
- RNF-1: La caja y la lista usan los tokens de superficie, borde, radio, sombra y foco del design system, en tema claro y oscuro.
- RNF-2: En un ancho de 360 px la caja no tapa el zoom del mapa ni el botón de capas, y la lista se desplaza si no entra.
- RNF-3: Las coordenadas del resultado viajan en EPSG:4326. Cada resultado trae id, nombre, dirección, longitud y latitud. En un pedido, el id es el del pedido.
- RNF-4: La búsqueda de menos de 3 caracteres no llega a la base. Si llega igual, la API responde 400.

## Casos límite
- El mismo nombre coincide en un pedido y en un cliente: aparece en los dos grupos.
- Un pedido activo sin geometría o sin id de pedido no entra en la lista.
- Un cliente sin geometría no entra en la lista.
- El texto incluye `%` o `_`: se buscan como caracteres, no como comodines.

## Fuera de alcance
- Buscar calles, pedidos históricos o pedidos completados.
- Reemplazar los diálogos «Buscar cliente» y «Buscar dirección».
- Abrir la ficha del cliente o del pedido al elegirlo.

## Criterios de finalización
- `npm run build` y `node --test` del módulo de la regla de las 3 letras, sin errores.
- Con la API en marcha: dos letras no consultan; desde la tercera aparecen los grupos; elegir un pedido y un cliente acerca el mapa.

## Dudas abiertas
- Ninguna.
