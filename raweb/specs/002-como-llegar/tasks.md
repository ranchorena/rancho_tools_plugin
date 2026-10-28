# Tareas 002 — Cómo llegar

Estado: aprobadas junto con la spec. T1–T4 completas; T5 parcial (falta el navegador).

- [x] **T1. Endpoint de recorrido en raapi.** RF-10–RF-13
- Hecho cuando: `POST /api/rutas/calcular` devuelve la misma secuencia de tramos que `pgr_dijkstra` para un par de cruces conocido y rechaza coordenadas inválidas.
- Resultado 2026-10-27: pgRouting 3.6.0 instalado en `public` de la base local con autorización del usuario. `API.calcularRuta` coincide con `pgr_dijkstra` en tramos y metros: 157→37 (10 tramos, 891 m), 37→157 (17, 1526 m) y 269→34 (35, 3332 m). Ningún tramo a contramano. Mismo cruce y punto a más de 300 m verificados.
- Enmienda RF-16 2026-10-27: conexión con `pgr_withPoints` al punto más cercano del tramo. Verificado: la línea empieza en el origen y termina en el destino. Con los puntos del usuario da 1087 m y 13 tramos (antes 1162 m). Sobre un mismo tramo de mano única, a favor da 70 m y 1 tramo; en contra da 418 m y 7 tramos, dando la vuelta. Mismo punto: 0 m.
- [x] **T2. Funciones puras del planificador.** RF-8, RF-9, RF-10
- Hecho cuando: `node --test tests/route-planner.test.mjs` pasa.
- Resultado: rojo inicial sin módulo; luego 45/45 con el resto de los tests.
- [x] **T3. Diálogo Cómo llegar.** RF-2–RF-9, RF-15
- Hecho cuando: `npm run build` compila y el diálogo muestra origen, destino, intercambiar y Ver recorrido.
- Resultado: `npm run build` sin advertencias.
- [x] **T4. Integración en el mapa.** RF-1, RF-6, RF-7, RF-10, RF-11, RF-14
- Hecho cuando: el recorrido se dibuja en rojo, el click de selección no abre tooltips y Limpiar lo borra.
- Resultado: implementado y compilado; comprobación visual pendiente en T5.
- [x] **T6. Pedido más cercano por recorrido.** RF-17, RF-18, RF-19
- Hecho cuando: `/api/pedidos/cercano` elige el pedido de menor recorrido y devuelve la ruta, y el mapa la dibuja.
- Resultado 2026-10-27: `pgr_withPoints` de uno a muchos sobre los 39 pedidos activos, en 0,19 s. Desde 10 posiciones coincidió con calcular la ruta a cada pedido en los 8 casos con recorrido; en 2 de ellos el elegido no es el más cercano en línea recta. Los otros 2 están en partes desconectadas del callejero y dan 404. Build y tests 45/45; desplegado en `raweb-qa`/`raapi-qa`. Falta el navegador (T5).
- [ ] **T5. Verificación.** Criterios de finalización
- Hecho cuando: build, tests y flujo en navegador (escritorio y 360 px) verificados o requisitos faltantes informados.
- Bloqueo 2026-10-27: el navegador de Cursor queda en «Comprobando sesión…» porque el check-sso de Keycloak no vuelve para `localhost:8080` ni `localhost:52948`. Chrome DevTools MCP está ocupado por otra instancia. El puerto 5000 lo usa `raapi-qa`; no se tocó. Falta la prueba en navegador con sesión iniciada.
