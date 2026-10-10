# Verificación T26 — Panel de capas y selecciones

Fecha: 2026-10-06. RF-4, RF-5, RF-15, RF-16, RF-19, RF-20.

## Cambio realizado

- `App.svelte` aplica `--ds-surface`, `--ds-background`, `--ds-text`, `--ds-text-muted`, `--ds-border`, `--ds-secondary-hover` y `--ds-focus` al panel, su cabecera, etiquetas, hover y cierre.
- Casillas y radios usan `ds-choice`, conservando inputs nativos, labels, valores y bindings existentes.
- Los botones icono de mostrar/cerrar declaran sus nombres accesibles y `type="button"`. Al abrir el panel el foco pasa a la primera selección; al cerrarlo vuelve al botón que queda visible.
- Se conservaron las reacciones existentes `osmLayer.setVisible`, `satelliteLayer.setVisible`, `pedidosLayer.setVisible` y `clientesLayer.setVisible`, sus fuentes y visibilidades iniciales.

## Verificación integrada real

Chrome Windows Headless 154.0.8037.95, con WebSocket/CDP nativo de Node y la App compilada. WFS y teselas se interceptaron y respondieron con fixtures vacíos/transparentes; no se usaron datos reales ni se enviaron mutaciones.

- **Rojo previo:** en tema oscuro el panel tenía `rgba(255, 255, 255, 0.95)` en lugar de la superficie del tema (`#1f2937`); los botones icono carecían de `aria-label` explícito.
- **Verde visual/tema:** panel oscuro medido como `rgb(31, 41, 55)`, texto `rgb(249, 250, 251)`, cabecera `rgb(17, 24, 39)` y acento de selección `rgb(147, 197, 253)`. En claro: superficie `rgb(255, 255, 255)`, texto `rgb(31, 41, 55)`, cabecera `rgb(248, 249, 250)` y acento `rgb(37, 99, 235)`.
- **Teclado y foco:** Enter abre; foco visible de 3 px en la casilla; Espacio activa/desactiva Clientes; Flecha abajo/arriba cambia Satelital/OpenStreetMap manteniendo exclusividad; Enter cierra y devuelve foco al botón Mostrar; Espacio vuelve a abrir.
- **Nombres accesibles:** árbol de accesibilidad confirmó nombres de Clientes, Pedidos, OpenStreetMap, Satelital, Cerrar panel de capas y Mostrar panel de capas.
- **Visibilidad/fuentes:** al activar Clientes aumentó de 1 a 2 el número de solicitudes WFS controladas; el input volvió a desmarcarse con Espacio. La selección Satelital generó solicitudes de teselas `/vt/lyrs=s`; volver a OpenStreetMap dejó el radio exclusivo en su valor inicial. Los requests fueron solo GET.
- Consola sin errores. No se midieron los cuatro viewports RNF-3 ni se probaron servicios reales; esto no sustituye T48 ni la aceptación final.

## Comprobaciones de código

- `node --test tests/design-system/*.test.mjs`: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; 319.86771 ms.
- `npm run build` en Windows PowerShell desde `raweb/`: código 0; Rollup generó `public/build/bundle.js` en 8.6 s.
- `git diff --check -- raweb/src/App.svelte`: código 0.

T26 satisface su criterio literal. No se inició T27.
