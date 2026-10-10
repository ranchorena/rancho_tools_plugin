# T52 — Implementación visual de Buscar Cliente/edición

Fecha: 2026-10-06. RF-11, RF-13, RF-16, RF-24; RNF-2. **T52 completada** tras verificación Chrome DevTools de búsqueda, tabla y edición en Claro y Oscuro, y corrección CSS del foco/indicador de selección de filas. T53 no iniciada.

## Referencia y cambio

- El baseline es [T51](t51-baseline.md), sustentado por evidencia Chrome actual aportada para Buscar Dirección y mediciones/capturas históricas T14 expresamente atribuidas.
- Antes de este cambio, las reglas locales de `BuscarCliente.svelte` fijaban el marco en blanco; títulos, etiquetas y secciones en colores claros; la tabla, hover/selección, casillas, solo lectura, carga y error también tenían colores literales. Estos estilos locales podían prevalecer sobre el tema.
- Se cambiaron exclusivamente reglas CSS de presentación y la clase visual de la nota de scroll horizontal. Ahora el marco/cabecera, secciones y campos consumen superficie/texto/borde semánticos; etiquetas y título heredan texto del tema; botón de cierre y acciones emplean tokens secundarios/primarios; solo lectura, casillas, cabeceras de tabla, hover, selección y estados de error/carga emplean variables semánticas, incluyendo foco.
- Los pares existentes son los tokens compartidos: Claro `--ds-surface #fff`, `--ds-text #1f2937`, `--ds-border #6b7280`, acción `--ds-primary #2563eb`/`--ds-on-primary #fff`; Oscuro `--ds-surface #1f2937`, `--ds-text #f9fafb`, `--ds-border #9ca3af`, acción `--ds-primary #93c5fd`/`--ds-on-primary #111827`. Los pares opacos de paleta pasan el soporte automatizado; esto no es medición del CSS renderizado del diálogo.
- No se cambiaron operaciones, funciones, eventos, payloads, mensajes, DOM estructural, anchura, alto máximo, scroll, tabla/columnas, padding, breakpoints, animación ni dimensiones de controles. Se preserva el trabajo anterior de T15–T18 (cabecera/foco, clases de campos/acciones, bindings, filas accesibles).

## Comprobaciones iniciales de implementación (históricas)

- `node --test tests/design-system/*.test.mjs`: código 0; 23 tests, 23 pass, 0 fail/cancelled/skipped/todo; 251.824729 ms.
- `npm run build` desde Windows PowerShell en `raweb/`: código 0; Rollup creó `public/build/bundle.js` en 9.6 s, sin warnings Svelte.
- No se pudo ejecutar inspección del diálogo en navegador en esta sesión. No se afirma que T52 pase visualmente, que los contrastes renderizados cumplan, ni que se hayan verificado dimensiones o estados después del cambio.

## Protocolo de inspección utilizado

Solicitar capturas y salida de estilos computados del diálogo real en **Claro y Oscuro**. Para cubrir la superficie de búsqueda y el flujo de edición, cargar resultados ficticios y seleccionar una fila; mostrar también captura/inspección con el estado de mensaje existente si está disponible, sin ejecutar guardados reales. Repetir al menos a 1366×768 y 360×800. No hace falta exponer datos reales.

En la consola de Chrome, con el diálogo abierto, ejecutar el siguiente código en cada tema y copiar la salida completa:

```js
(() => {
  const selectors = {
    dialog: '.modal-content',
    header: '.modal-header',
    title: '#modal-title',
    section: '.search-section',
    label: '.search-section label',
    field: '.search-section .ds-field',
    primary: '.search-section .ds-button--primary',
    table: '.table-container',
    tableHeader: '.table-container th',
    row: '.table-container tbody tr',
    selectedRow: '.table-container tbody tr.selected',
    editSection: '.selected-client-section',
    checkbox: '.checkbox-group',
    loading: '.loading-indicator',
    error: '.error-message'
  };
  const properties = [
    'color', 'backgroundColor', 'borderTopColor', 'borderRightColor',
    'borderBottomColor', 'borderLeftColor', 'outlineColor', 'boxShadow'
  ];
  return Object.fromEntries(Object.entries(selectors).map(([name, selector]) => {
    const element = document.querySelector(selector);
    if (!element) return [name, null];
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return [name, {
      text: element.innerText?.trim().slice(0, 100) ?? '',
      styles: Object.fromEntries(properties.map((property) => [property, style[property]])),
      rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
      scroll: { clientWidth: element.clientWidth, scrollWidth: element.scrollWidth,
        clientHeight: element.clientHeight, scrollHeight: element.scrollHeight }
    }];
  }));
})()
```

La salida de fila seleccionada, carga y error será `null` si esos estados no estaban activos; no se los debe simular alterando el código para completar la evidencia. Comparar superficies/título/campos/acción con [T51](t51-baseline.md), calcular contraste de texto contra su fondo efectivo y de bordes/foco/estados contra su superficie, y reportar viewport/tema. Confirmar visualmente que se conservan ancho/scroll, dimensiones y disposición.

La falta de navegador de la implementación inicial queda superada por la ejecución registrada a continuación.

## Verificación y corrección de esta sesión

Chrome DevTools respondió a `list_pages` y se creó una pestaña en contexto aislado `t52-ficticio`, sobre `http://localhost:8080/`. Chrome Windows 154; user agent, viewport efectivo, cajas, scroll, colores y ratios constan en [mediciones completas](t52-browser-evidence.json). Las medidas iniciales y las muestras `final-*` se distinguen explícitamente.

- Búsqueda REST interceptada en `window.fetch`, con cliente **9001 / Cliente Ficticio T52**, cantidad 1.5, PaO 123, horario 14:30:00 y observación ficticia. Se comprobó POST de nombre con `{criterio:"nombre", nombre_cliente:"Cliente Ficticio T52"}`. No se pulsó Guardar ni se enviaron PUT/altas.
- La inspección inicial de red detectó que WFS usa **XMLHttpRequest**, que no cubría el primer interceptor fetch. Hubo GET WFS iniciales sin inspeccionar sus cuerpos. Se añadió interceptación XHR exclusivamente a la pestaña, se recargó y se reemplazaron **todas** las capturas por imágenes finales con FeatureCollection vacío. REST/WFS finales son simulados; teselas OSM públicas reales. La lista de red final de fetch/XHR está vacía y el registro local acredita las respuestas simuladas; no es evidencia de integración real con servicios.
- Defecto observado tras CSS T52: foco nativo de fila `rgb(16,16,16) auto 1px` sobre selección azul oscura, insuficiente. Corrección exclusiva en `BuscarCliente.svelte`: outline 3 px con `--ds-focus`, offset interior −3 px para evitar recorte en el contenedor, y marca de selección `box-shadow: inset 3px 0 var(--ds-on-selected)`. No cambia cajas ni manejadores. Recarga completa del bundle recompilado: foco/selección medidos en ambos temas; fila de escritorio conserva 692×49 px.
- Enter seleccionó la fila antes de la corrección; Espacio la seleccionó tras la corrección y clic volvió a mostrar la edición. Tab desde fila lleva al ID de solo lectura y Mayús+Tab retorna a fila; Espacio cambia Tiene Pedido de true a false, sin guardar. Foco inicial en Cerrar. Cierre vuelve a Buscar Cliente en escritorio y al botón con `aria-label="Menú"` en móvil, con menú cerrado. Foco de campo/casilla/Guardar usa outline 3 px y tokens del tema.
- La preservación de los tres criterios y PUT/eventos se respalda además con [T16](t16-verification.md) y [T18](t18-verification.md): las modificaciones de T52 y esta corrección son de presentación, sin cambios a funciones, bindings, payloads ni eventos. No se repitió el guardado ni se acredita persistencia real en este cierre visual.

### Contraste renderizado

Se compusieron los fondos transparentes recorriendo los ancestros con alpha y se calculó luminancia sRGB WCAG sobre el fondo efectivo. Cabecera/cuerpo/títulos transparentes usan la superficie heredada. Los controles nativos checkbox se inspeccionan visualmente y por accent/foco; su `color` CSS no se presenta como color del glifo interno. Los ratios de bordes se aplican a trazos presentes; el borde azul de acción se compara contra la superficie **exterior**, no contra su propio relleno.

| Par renderizado | Claro | Oscuro | Resultado |
| --- | ---: | ---: | --- |
| Texto de marco/cabecera/secciones/campos/edición | 14.68 | 14.05 | ≥4.5 |
| Texto cabecera de tabla y etiquetas de casillas | 13.93 | 16.98 | ≥4.5 |
| Solo lectura: texto sobre fondo propio | 7.17 | 12.04 | ≥4.5 |
| Texto selección / marca interior de selección | 7.15 | 8.72 | ≥4.5 texto; ≥3 indicador |
| Buscar/Guardar normal | 5.17 | 9.84 | ≥4.5 |
| Buscar hover real | 6.70 | 12.48 | ≥4.5 |
| Texto mensaje de validación vacío | 5.91 | 6.93 | ≥4.5 |
| Texto carga con respuesta retenida | 7.17 | 12.04 | ≥4.5 |
| Borde campo/sección/tabla contra superficie | 4.83 | 5.78 | ≥3 |
| Borde solo lectura contra fondo propio | 4.59 | 6.99 | ≥3 |
| Foco campo/acción contra superficie | 6.70 | 8.14 | ≥3 |
| Foco casilla contra su grupo | 6.36 | 9.84 | ≥3 |
| Foco fila seleccionada contra fila | 5.49 | 4.84 | ≥3 |

La acción Oscuro usa el token común actual `#93c5fd/#111827`. T51 registra una muestra aportada anterior azul `#2563eb`; el código actual de Buscar Dirección también consume `--ds-primary/--ds-on-primary`. La uniformidad se aplica al patrón/token compartido vigente, sin restaurar literales de esa captura histórica. Marco/secciones/títulos/campos comparten las superficies/texto del baseline.

### Viewports efectivos y scroll

Emulación de **área visible en CSS px**, DPR 1 y modo desktop, también para tamaños móviles; no se afirma prueba de hardware táctil. Cada tamaño se comprobó en los dos temas. `innerWidth/innerHeight` se verificaron, sin inferirlos del nombre de una captura.

| Viewport efectivo | Marco (ancho×alto con edición) | Cabecera | Cuerpo clientHeight / scrollHeight | Resultado |
| --- | --- | ---: | --- | --- |
| 360×800 | 352×784 | 48 px | 736 / 1909 | Sin overflow horizontal del cuerpo; tabla 288 / 500 px, desplazamiento horizontal real 212 px |
| 800×360 | 691.19×342 | 44 px | 298 / 1606 | Guardar accesible por scroll vertical |
| 768×1024 | 752×992 | 48 px | 944 / 1975 | Formulario de una columna; Guardar accesible |
| 1366×768 | 800×729.59 | 44 px | 686 / 1574 | Dos columnas de edición y cinco columnas de tabla conservadas |

En 360 px el modal es **352 px**, no 392 px: queda corregida la atribución anterior de un viewport 400 como 360. Los controles y Guardar se alcanzaron mediante scroll; no se cambiaron anchuras, padding, breakpoints, animación ni distribución.

Texto 200 %: se duplicó la **fuente computada de cada elemento del modal** mediante estilos temporales de la pestaña, manteniendo viewport/DPR; campo 16→32 px. No se usó zoom de página como sustituto. Ambos temas a 360×800 y 1366×768: cabecera 48/44 px, título 40 px de alto contenido en cabecera, cierre visible, scroll ampliado 2904/2113 px y Guardar accesible. La fuente temporal se restauró; no hay cambio de producto. La matriz de tamaños/texto se midió antes de corregir foco de filas; esa corrección no altera dimensiones. Recarga final confirma cajas y scroll móvil/escritorio.

### Capturas finales con datos ficticios

| Estado | Claro | Oscuro |
| --- | --- | --- |
| Búsqueda escritorio | [captura](t52-light-search.png) | [captura](t52-dark-search.png) |
| Tabla seleccionada + entrada de edición | [captura](t52-light-table.png) | [captura](t52-dark-table.png) |
| Edición escritorio completa | [captura](t52-light-edit.png) | [captura](t52-dark-edit.png) |
| Búsqueda móvil efectiva 360×800 | [captura](t52-light-mobile-search.png) | [captura](t52-dark-mobile-search.png) |
| Edición móvil desplazada hasta Guardar | [captura](t52-light-mobile-edit.png) | [captura](t52-dark-mobile-edit.png) |
| Texto 200 % escritorio, desplazado al final | Medidas en JSON | [captura](t52-dark-text200.png) |

### Comprobaciones finales y veredicto

- Tras la corrección: `node --test tests/design-system/*.test.mjs`, código 0, **23/23 pass**, 0 fail/cancelled/skipped/todo, 332.552869 ms.
- `npm run build` desde Windows PowerShell en `raweb/`, código 0; Rollup genera bundle en **7.8 s**, sin warnings Svelte. Sin instalaciones de dependencias.
- Consola DevTools final: **cero warnings/errores**. Ninguna mutación de backend. Integración REST/WFS real y repetición completa del guardado quedan para sus tareas de aceptación; no son resultados simulados presentados como reales.
- `git diff --check` devuelve código 2 por finales CRLF/espacios existentes de `BuscarCliente.svelte` frente a HEAD, visibles ya en el diff previo. Se preservaron; las reglas nuevas de foco/marca no aparecen en esos avisos. No se declara este chequeo limpio.
- **Pasa el criterio visual T52**: búsqueda, tabla y edición inspeccionadas en ambos temas, contraste y cabeceras conformes, estructura/dimensiones/flujos preservados. T52 marcada y parada; T53 no iniciada. No equivale a aceptación final de RF-24 o de la entrega.
