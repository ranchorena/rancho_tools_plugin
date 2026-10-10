# Verificación T29 — Controles DOM de OpenLayers

Fecha: 2026-10-07. RF-5, RF-13, RF-15, RF-19, RF-20.

## Referencia roja en navegador

Chrome DevTools página 1, `http://localhost:8080/`, viewport emulado 800×360. Se inspeccionó solo DOM/CSS de `.ol-control`; no se consultaron cuerpos REST/WFS.

| Tema | Base | Control DOM observado | Medición roja/operación |
| --- | --- | --- | --- |
| Oscuro | OSM | Zoom +/−, atribución y enlace OpenStreetMap | Zoom: texto `#f9fafb` sobre superficie `#1f2937`; borde `#9ca3af`. Enlace de atribución heredaba `rgb(0,100,200)` sobre `#1f2937` (contraste calculado 2,54:1, inferior a 4,5:1 para texto normal). Árbol accesible: «Zoom in», «Zoom out», «Attributions» y enlace «OpenStreetMap». |
| Claro | Satelital | Zoom +/−; atribución sin contenido mientras la capa satelital estaba activa | Zoom: texto `#1f2937` sobre `#fff`; borde `#6b7280`. Botones nativos habilitados. La atribución colapsó a 0×0/sin contenido en esta carga satelital. |
| Claro | OSM | Zoom +/− y atribución expandida | Zoom: texto `#1f2937` sobre `#fff`; borde `#6b7280`. Atribución 165×41 px, texto de atribución 11,2 px. |
| Oscuro | OSM | Zoom +/− y atribución expandida | Zoom: texto `#f9fafb` sobre `#1f2937`; borde `#9ca3af`. Enlace azul global `rgb(0,100,200)`; defecto rojo anterior. |

La activación real por teclado de Tab enfocó «Zoom in»; el foco computado era contorno sólido de 3 px, azul `rgb(29,78,216)`, offset −3 px. El árbol accesible proporcionó nombres a partir de los títulos nativos de OpenLayers. El botón de zoom se activó mediante clic; no se guardaron datos. No se pudieron verificar todos los controles tras compilar la corrección.

## Cambio acotado

En `src/App.svelte`, únicamente `a` y `a:hover` descendientes de `.ol-attribution` usan `--ds-primary` y `--ds-primary-hover`. El enlace deja de heredar el azul global en Oscuro y conserva la semántica visual del tema. No se tocaron capas, renderizado de canvas, simbología, features, fuentes ni geometrías.

## Estado inicial de verificación

El entorno browser mostró OSM y Satelital en el viewport 800×360 y los dos temas. La matriz previa al cambio detectó el defecto citado. La verificación posterior quedó inicialmente **bloqueada** porque el build WSL falló antes de recompilar/servir el CSS. El bloqueo se resolvió con el runtime Windows existente; resultados finales más abajo.

## Solicitudes y consola

- Durante la inspección interactiva se usaron controles de capas base reales OSM/Satelital, tema Claro/Oscuro, Tab y clic en zoom. La carga incluyó las solicitudes GET habituales de mapa/WFS. No se inspeccionaron cuerpos de respuesta ni datos/atributos de registros; no se enviaron POST/PUT/DELETE ni se guardó información.
- No se registraron errores de consola durante las mediciones iniciales. La inspección final se documenta abajo.

## Comprobaciones automatizadas

- `node --test tests/design-system/*.test.mjs`: código **0**; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; **354.475843 ms**.
- No se encontró `pwsh` ni `powershell` en PATH.
- `npm run build` desde `raweb/`: código **1**. Rollup no puede cargar `@rollup/rollup-linux-x64-gnu` (dependencia opcional ausente). No se reinstalaron dependencias ni se modificó la configuración.

## Cierre final — 2026-10-07

- **Build Windows existente:** `cmd.exe /c "cd /d C:\GIT\github\rancho_tools_plugin\raweb && npm run build"`, desde `raweb/`; código **0**. Rollup creó `public/build/bundle.js` en 8 s. No se instalaron paquetes ni se modificaron configuración o lockfile.
- **Runner:** `node --test tests/design-system/*.test.mjs`; código **0**, 23 tests, 23 pass, 0 fail/cancelled/skipped/todo, 224.304726 ms.
- **Chrome DevTools:** página 1, `http://localhost:8080/`, bundle recompilado cargado mediante recarga. `initScript` sustituyó las solicitudes WFS GetFeature por FeatureCollection vacía; no se inspeccionaron respuestas WFS reales. Viewport 800×360.
- **Controles DOM:** zoom habilitado, 30×30 px, con nombres «Zoom in» y «Zoom out» en OSM y Satelital, Claro y Oscuro. Atribución con botón habilitado/nombre «Attributions»; en Satelital no presenta contenido/enlace y su caja mide 0×0 px. En OSM, expandida, mide 165×41 px.
- **Contraste del enlace OpenStreetMap:** Claro `rgb(37,99,235)` sobre `rgb(255,255,255)`: **5,1686:1**; Oscuro `rgb(147,197,253)` sobre `rgb(31,41,55)`: **8,1403:1**. Ambos superan 4,5:1.
- **Teclado/activación:** Tab dejó foco visible de 3 px en Zoom out; Enter produjo una activación. El botón de atribución recibió foco visible de 3 px y Enter lo colapsó, cambiando `aria-expanded`. No se guardaron datos ni se enviaron mutaciones.
- **Consola:** un aviso de Chrome por `apple-mobile-web-app-capable` obsoleto; ningún error de consola durante la comprobación.
- **Alcance e invariancia:** la contribución de T29 en `src/App.svelte` se limita a reglas CSS para `.ol-attribution a` y `:hover` enlazadas a los tokens de tema. No modifica HTML/JS, capas, fuentes, renderizador, símbolos ni geometrías. El canvas observado conservó 800×292 y el mismo estilo/transform durante cambios de tema/capa. Como WFS se sustituyó por colección vacía, no había símbolos/feature geometries que comparar píxel a píxel; la invariancia se acredita por el alcance CSS-only del cambio, no por comparación de features reales.

**Estado final: T29 completa. T30 no iniciada.**

## Estado

**T29 completa** tras build Windows y verificación posterior en Chrome. T30 no iniciada.
