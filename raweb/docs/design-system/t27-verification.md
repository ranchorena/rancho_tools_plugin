# Verificación T27 — Controles flotantes de App

Fecha: 2026-10-07. RF-4, RF-5, RF-15, RF-19–RF-21; RNF-2.

## Corrección

En `src/App.svelte`, el foco visible de los botones flotantes de Capas y Alta conserva el contorno blanco de 3 px con separación de 2 px en tema oscuro y añade un halo exterior opaco `#111827` de 5 px. La doble banda mantiene el foco distinguible sobre los píxeles claros de OSM, sin cambiar markup, nombres, posición, dimensiones, comportamiento ni colores de negocio. Claro conserva el contorno azul existente. Los controles OpenLayers no se modifican.

## Verificación en Chrome DevTools

- Aplicación real `http://localhost:8080/`, página 1; mosaicos OSM cargados y canvas del mapa presente. Se verificó en Claro y Oscuro. Contraste calculado en JavaScript usando los píxeles RGB leídos de `.ol-layer canvas` alrededor del contorno y luminancia sRGB.
- Contraste mínimo del foco claro (azul `#1d4ed8`) contra muestras del mapa: **3.2330:1** para Capas en 360×800; **3.2399:1** para Alta en 360×800; **3.3810:1** para Capas en 1034×605. Todas las muestras superan 3:1.
- En Oscuro, el halo exterior `#111827` contra las muestras OSM: **8.5761:1** mínimo en 360×800 para ambos botones; **8.9497:1** mínimo para Capas en 1034×605. Se tomaron 160–176 muestras perimetrales por elemento según viewport. El contorno blanco se mantiene como banda interior complementaria.
- Medidas verificadas: en escritorio 1034×605, Capas y Alta permanecen en x=974, y=84/148, 44×44 px. En móvil táctil 360×800, x=312, y=88/144, 40×48 px. Zoom OpenLayers mantiene 30×30 px en escritorio y 28×28 px en móvil; el canvas del mapa continúa montado.
- Nombres AX: «Mostrar panel de capas» y «Agregar nuevo cliente». En móvil oscuro, Tab/Enter abre Capas y enfoca «Clientes» sin marcarlo; Mayús+Tab/Enter cierra y devuelve foco al botón. Tab/Enter abre Alta y enfoca «Cerrar»; Enter cierra, devuelve foco al botón y mantiene el mapa montado. No se guardó.
- Red observada: solicitudes GET de la aplicación, WFS Pedidos y mosaicos OSM. No hubo POST, PUT ni DELETE. Consola: sin errores; warning existente de `apple-mobile-web-app-capable` y warning Canvas2D generado por las lecturas `getImageData` de la medición.

## Comprobaciones automatizadas

- Desde `raweb/`, `node --test tests/design-system/*.test.mjs`: código **0**; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; **235.307901 ms**.
- `npm run build` en WSL: bloqueado, falta el opcional `@rollup/rollup-linux-x64-gnu`; no se instalaron dependencias.
- `npm run build` en Windows PowerShell/Node: código **0**; Rollup generó `public/build/bundle.js` en **7.8 s**.
- La página 1 se recargó sin caché tras el build Windows y cargó el bundle actualizado.

## Resultado

T27 cumple el criterio de posición/tamaño, foco y nombres, apertura/cierre y contraste ≥3:1 contra el fondo cartográfico muestreado en Claro y Oscuro. La implementación se limita al indicador de foco CSS de los dos controles flotantes. No se ejecutó el test previo de Pedidos como evidencia de T27. **T27 completa; detener aquí, sin iniciar T28.**
