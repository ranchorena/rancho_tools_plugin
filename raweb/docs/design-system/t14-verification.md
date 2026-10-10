# T14 — Campos/acciones del diálogo de dirección

Fecha: 2026-10-06. **Pasa el criterio literal de T14**. RF-4–RF-7, RF-11–RF-13, RF-19; depende de T13.

## Alcance verificado

- El campo conserva su asociación con la etiqueta y su binding; el botón Buscar conserva su acción. Los estilos adoptan `ds-field`, `ds-button` y variables semánticas de ambos temas, sin alterar validación ni mensajes.
- El componente conserva `dispatch('buscar', { direccion: direccionInput.trim() })`. Enter desde el campo y clic en Buscar mantienen el evento y la dirección normalizada; App mantiene el POST a `/buscar_direccion` y cierra el diálogo con el retorno de foco ya coordinado por T12/T13.
- La entrada vacía conserva la alerta nativa «Por favor, ingrese una dirección.»; se mantienen los mensajes existentes para respuesta sin coordenadas y fallo de búsqueda.

## Rojo y verde en navegador

- Chrome Windows 154.0.8037.95, Node Windows 22.17.1, App real servida en `http://192.168.0.102:8080/`, control CDP nativo. El harness temporal `/tmp/opencode/t14-browser.cjs` deriva del usado en T11 y registra estilos calculados, teclas, diálogos JavaScript y solicitudes.
- **Rojo previo: código 1**, antes de la corrección temática: con tema Oscuro, `.modal-content` seguía en superficie blanca (`rgb(255, 255, 255)`). El resto del diálogo provenía de una composición cromática clara; el contraste medido del texto principal fue insuficiente frente al tema esperado.
- **Verde final: código 0** tras ajustar la expectativa defectuosa del harness (el criterio pide Enter en el campo y clic en Buscar; no requiere Enter adicional sobre el botón). Se ejecutaron las comprobaciones completas del guion.

| Comprobación real | Resultado |
| --- | --- |
| Campo, foco, etiqueta, acción Buscar | Conservados; label asociado al ID `direccion-input`, foco visible; botón y campo legibles en ambos temas. |
| Tema y tamaños | Claro/Oscuro en 360×800, 800×360, 768×1024 y 1366×768. Cabecera 41–45 px. Texto/placeholder/acción/cierre ≥4,5:1; borde y foco ≥3:1 en las muestras medidas. |
| Enter en campo | Una solicitud POST controlada a `/buscar_direccion`, cuerpo `{"direccion":"CALLE FICTICIA 100"}` tras recortar espacios; diálogo cierra y foco vuelve al disparador. |
| Clic en Buscar | Una solicitud POST controlada a `/buscar_direccion`, con la misma dirección ficticia normalizada; cierre/retorno conservados. |
| Mensajes | Vacío: alerta nativa exacta al usar Enter y clic Buscar. Respuesta simulada sin coordenadas: alerta existente. Respuesta simulada inválida: mensaje de error existente. |
| Consola/red | Cero excepciones/logs de error CDP. WFS, teselas y POST REST interceptados localmente por CDP antes de llegar a servicios; no se guardaron ni enviaron datos reales. |

La cobertura reporta únicamente lo ejecutado. No se afirma disponibilidad o comportamiento de API/GeoServer reales. Alertas: apariencia/tema/contraste N/A por ser UI nativa del navegador.

## Capturas

- [Diálogo en tema Claro, 1366×768](t14-light.png)
- [Diálogo en tema Oscuro, 1366×768](t14-dark.png)

## Verificación de proyecto

- `node --test` exacto desde `raweb/`: código 0; **23 tests**, suites 0, pass 23, fail 0, cancelled 0, skipped 0, todo 0; 556.000798 ms.
- `npm run build` desde `raweb/` en Windows: código 0; Rollup generó `public/build/bundle.js` en 9.6 s.
- Sin instalación de dependencias. No se ejecutó T15.
