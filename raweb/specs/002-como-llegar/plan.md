# Plan 002 — Cómo llegar

Estado: aprobado junto con la spec.

## Archivos y responsabilidades
- `raapi/API.py` — `API.calcularRuta(session, origen, destino)`: cruces más cercanos, `pgr_dijkstra` dirigido y armado de la línea. RF-10–RF-13.
- `raapi/server.py` — `POST /api/rutas/calcular`: validación de coordenadas y códigos HTTP. RF-10–RF-12.
- `raweb/src/route-planner.mjs` — funciones puras: `isValidPoint`, `buildRoutePayload`, `formatDistance`, `swapPoints`, `formatCoordinates`. RF-8, RF-9, RF-10.
- `raweb/src/ComoLlegarDialog.svelte` — presentación, geocodificación y llamada a `/api/rutas/calcular` (como el resto de los diálogos); emite `seleccionarPunto`, `mostrarRuta` y `close`. RF-2–RF-9, RF-11–RF-13, RF-15.
- `raweb/src/App.svelte` — acción de navegación, modo de selección en el mapa, capa de recorrido, aviso con la distancia, encuadre y limpieza. Recuerda los últimos puntos para reabrir el diálogo. RF-1, RF-6, RF-7, RF-10, RF-14.
- `raweb/src/design-system/Icon.svelte` — iconos `route` y `swap`.

## Algoritmo (API)
```
para cada punto p en (origen, destino):
  g = ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 5347)
  t = tramo de callejero más cercano a g (operador <->), f = ST_LineLocatePoint(t, g)
  si distancia(g, t) > 300 -> out_of_network
aristas = id, source, target,
          cost = -1 si sentido = 1 sino ST_Length
          reverse_cost = -1 si sentido = 0 sino ST_Length
puntos = (pid 1, t_origen, f_origen), (pid 2, t_destino, f_destino)
camino = pgr_withPoints(aristas, puntos, -1, -2, directed, driving_side 'b')
si vacío y no es el mismo lugar -> not_found
cada fila va de node a LEAD(node): fracción 0 (source), 1 (target) o f del punto;
  ST_LineSubstring entre ambas fracciones, invertida si desde > hasta
línea = ST_MakeLine(origen, subtramos en orden seq, destino)
devolver GeoJSON EPSG:4326 y distancia en metros
```

## Interfaz
- Request: `{origen: {latitud, longitud}, destino: {latitud, longitud}}`.
- 200: `{geometria: GeoJSON LineString, distancia_m: int, tramos: int}`.
- 400: coordenadas inválidas. 404: `{error}` sin recorrido o fuera del callejero.

## Decisiones
- Costo en la consulta a partir de `ST_Length` y `sentido`, descartando `cost_len`/`rcost_len` porque `rcost_len` está multiplicado por 1000 en las calles doble mano.
- `pgr_withPoints` sobre el punto más cercano del tramo (enmienda RF-16). Se descartó el cruce más cercano con `pgr_dijkstra` porque la línea iba en diagonal hasta la esquina y volvía por la misma cuadra.
- Botón en la barra inferior móvil como sexta columna, en lugar de reemplazar una acción existente.

## Tests
- `node --test tests/route-planner.test.mjs` para las funciones puras.
- API: comparación manual con `pgr_dijkstra` en la base local.
