# T21 — Campos de pedido, ubicación y mensajes de alta

Fecha: 2026-10-06. **T21 completada.** RF-4–RF-7, RF-9, RF-12, RF-16, RF-19–RF-21; depende de T20.

> Hecho cuando: cantidad/regalo/horario/observación, selección de coordenadas y guardar/cancelar preservan eventos/payload y no bloquean clic de ubicación.

## Cambio

- En `AgregarCliente.svelte`, cantidad, horario, número PAO y observación usan `ds-field`; las casillas de pedido y regalo usan `ds-choice`. Guardar y Cancelar adoptan los estilos primario/secundario compartidos. Mensajes existentes de error/éxito utilizan los tokens semánticos de ambos temas.
- La prop `seleccionandoUbicacion` enlaza el estado de selección de App al formulario. Mientras está activo, el diálogo se oculta y el backdrop deja pasar los eventos de puntero; el mapa queda accesible. El clic de OpenLayers termina el modo y actualiza las coordenadas, haciendo reaparecer el mismo formulario.
- Se conservan tipos, IDs, labels, bindings, eventos `seleccionarUbicacion`, `close` y `clienteAgregado`, validaciones y traducción/payload existente del alta. No se cambió API ni lógica de negocio.

## Rojo/verde en navegador real

- Rojo previo a editar: Chrome Windows 154.0.8037.95, Node Windows 22.17.1, CDP nativo, App real en `http://192.168.0.102:8080/`. Tras activar «Seleccionar en Mapa», un clic CDP físico sobre el viewport de OpenLayers cerró el diálogo (`dialog:false`); esperado, formulario abierto y coordenadas fijadas. Aserción falló con código 1. WFS y teselas controlados antes de navegar.
- Verde final: código 0. Clic físico sobre el viewport real seleccionó coordenadas EPSG:4326 y mantuvo el formulario abierto. Se comprobó que Cancelar cierra sin enviar POST.
- Los campos de pedido conservaron etiqueta/tipo y clases compartidas: cantidad number, horario time, PAO number, observación textarea; casillas con `ds-choice`. Chrome verificó texto, fondo y borde renderizados para los cuatro campos en claro y oscuro; la observación también usa el borde compartido.
- Un alta completamente ficticia conservó el payload esperado: cantidad `2.5`, horario `15:30`, PAO `921`, observación ficticia, casillas seleccionadas y coordenadas numéricas latitud/longitud. El POST `/api/clientes/agregar` fue interceptado y contestado localmente con éxito ficticio; se observó cierre y notificación correspondiente. Ninguna escritura llegó a API/base de datos. Cero errores de consola/CDP.

## Comprobaciones

- `node --test` exacto final desde `raweb/`: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; `duration_ms 361.671446`.
- `npm run build` final en Windows PowerShell/Node: código 0; bundle compilado en 9.3 s, sin warnings.
- Navegador Chrome Windows/CDP: rojo código 1 antes del cambio; verde código 0 tras el cambio. Requests externos WFS/teselas controlados; POST de alta interceptado, sin mutaciones reales.

T21 cumple su criterio literal. La verificación usa respuestas locales ficticias; no acredita disponibilidad de API/GeoServer ni completa la aceptación global. Detener antes de T22.
