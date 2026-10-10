const t1 = 'docs/design-system/coverage.md — inventario T1';
const variantsByFamily = {
  'C-BUTTON': ['navegación texto+emoji', 'primario', 'secundario/neutro', 'ubicación', 'cierre/icono'],
  'C-FIELD': ['texto', 'número', 'teléfono', 'hora', 'área de texto', 'solo lectura'],
  'C-CHOICE': ['casilla', 'radio exclusivo'],
  'C-THEME': ['Claro', 'Oscuro', 'Sistema'],
  'C-DIALOG': ['Buscar Dirección', 'Buscar Cliente/edición', 'Agregar Cliente', 'Pedidos'],
  'C-NAV': ['escritorio', 'móvil'],
  'C-TABLE': ['clientes', 'pedidos', 'fila normal', 'fila de regalo'],
  'C-STATS': ['Cantidad Total', 'Cantidad Vendidas', 'Valor Total'],
  'C-NOTICE': ['global success/error/otros', 'error/carga local', 'éxito local', 'alerta nativa'],
  'C-PANEL': ['panel de capas abierto', 'disparador cerrado'],
  'C-FLOAT': ['capas', 'alta', 'zoom', 'atribución'],
  'C-INFO': ['información de cliente', 'información de pedido']
};

function entry(id, name, requirements, experiences, applicable, notApplicable) {
  return {
    id,
    name,
    variants: variantsByFamily[id],
    requirements,
    experiences,
    states: {
      applicable: applicable.map(([stateId, detail]) => ({ id: stateId, source: t1, detail })),
      notApplicable: notApplicable.map(([stateId, reason]) => ({ id: stateId, source: t1, reason }))
    }
  };
}

// El inventario describe estados y variantes observados o aprobados; no crea estados de producto.
export const catalog = [
  entry('C-BUTTON', 'Botones', ['RF-1', 'RF-2', 'RF-4'], ['X-NAV', 'X-DIR', 'X-CLI', 'X-ADD', 'X-PED', 'X-MAP'],
    [['normal', 'Botones de acción y navegación existentes.'], ['hover', 'Hover CSS existente.'], ['active', 'Active CSS y selección de navegación existentes.'], ['focus', 'Foco CSS declarado.'], ['disabled', 'Guardado/Cancelación de alta cuando corresponde.'], ['loading', 'Guardando con indicador existente en Alta.']],
    [['selected', 'Solo la acción de navegación refleja el diálogo activo; no es aplicable a los demás botones.'], ['message', 'Los botones no son mensajes.']]),
  entry('C-FIELD', 'Campos y áreas de texto', ['RF-1', 'RF-2', 'RF-4'], ['X-DIR', 'X-CLI', 'X-ADD'],
    [['normal', 'Campos editables y de solo lectura existentes.'], ['focus', 'Foco CSS declarado.'], ['disabled', 'CSS global existe; no se observó binding disabled en estos campos.']],
    [['hover', 'No se declara un estado hover específico del campo; coverage describe foco/solo lectura y validaciones existentes.'], ['selected', 'La selección pertenece a resultados/filas, no a campos.'], ['loading', 'La carga no cambia el estado del campo observado.']]),
  entry('C-CHOICE', 'Casillas y opciones exclusivas', ['RF-1', 'RF-2', 'RF-4'], ['X-CLI', 'X-ADD', 'X-MAP'],
    [['checked', 'Marcado y desmarcado en casillas; selección exclusiva en radios.'], ['unchecked', 'Casillas y opción inicial de capas según T1.'], ['focus', 'Foco nativo/CSS declarado.'], ['hover', 'Hover de contenedor de capas observado.']],
    [['disabled', 'No se observaron estados disabled, carga ni error propios de estas opciones.'], ['loading', 'No se observaron estados de carga propios.'], ['message', 'Las opciones no son mensajes.']]),
  entry('C-THEME', 'Selector de tema', ['RF-4', 'RF-10', 'RF-22'], ['X-NAV'],
    [['normal', 'Opciones Claro, Oscuro y Sistema aprobadas por RF-17.'], ['selected', 'La preferencia elegida se conserva según RF-17/RF-18.'], ['focus', 'Control select nativo; comportamiento de foco propio del control.']],
    [['disabled', 'No definido ni observado para el selector.'], ['loading', 'No definido ni observado para el selector.']]),
  entry('C-DIALOG', 'Diálogos', ['RF-1', 'RF-2', 'RF-4'], ['X-DIR', 'X-CLI', 'X-ADD', 'X-PED'],
    [['open', 'Diálogo visible.'], ['closed', 'Diálogo cerrado por sus reglas existentes.'], ['focus', 'Foco interior/retorno coordinado N/O en el inventario T1.']],
    [['disabled', 'No es un estado del marco de diálogo.'], ['loading', 'La carga corresponde a contenido de algunos diálogos, no al marco.']]),
  entry('C-NAV', 'Navegación de escritorio y móvil', ['RF-1', 'RF-2', 'RF-4'], ['X-NAV'],
    [['normal', 'Acciones de navegación existentes.'], ['hover', 'Hover CSS existente.'], ['focus', 'Foco CSS declarado.'], ['active', 'Acción correspondiente al diálogo activo.'], ['open', 'Menú móvil desplegado.'], ['closed', 'Menú móvil cerrado.']],
    [['disabled', 'No se observaron estados disabled propios de navegación.'], ['loading', 'No se observaron estados de carga propios.']]),
  entry('C-TABLE', 'Tablas y filas accionables', ['RF-1', 'RF-2', 'RF-4'], ['X-CLI', 'X-PED'],
    [['normal', 'Filas de clientes y pedidos existentes.'], ['hover', 'Hover de fila observado.'], ['selected', 'Fila de cliente seleccionada.'], ['focus', 'Foco/teclado propio de fila N/O en T1; no afirmar implementación previa.']],
    [['disabled', 'No se observaron filas deshabilitadas.'], ['loading', 'Carga y mensajes se presentan fuera de la tabla.'], ['message', 'Vacío/carga/error se presentan fuera de la tabla.']]),
  entry('C-STATS', 'Estadísticas', ['RF-1', 'RF-2', 'RF-4'], ['X-PED'],
    [['normal', 'Tarjetas informativas cuando hay pedidos.']],
    [['focus', 'Tarjetas informativas sin foco propio.'], ['active', 'No son controles accionables.'], ['selected', 'No son elementos seleccionables.'], ['disabled', 'No son controles.'], ['loading', 'No hay indicador propio de carga/error en tarjetas.']]),
  entry('C-NOTICE', 'Notificaciones y mensajes', ['RF-1', 'RF-2', 'RF-4'], ['X-CLI', 'X-ADD', 'X-PED', 'X-NOT', 'X-DIR'],
    [['visible', 'Mensajes locales/globales y alertas existentes.'], ['hidden', 'Mensajes no visibles cuando no hay contenido/estado que mostrar.'], ['loading', 'Carga de clientes/pedidos y guardado de alta existentes.'], ['success', 'Éxito local de alta y notificación global existentes.'], ['error', 'Errores locales/globales existentes.'], ['message', 'Contenido textual conservado; warning usa la variante genérica existente.']],
    [['focus', 'Los mensajes informativos no reciben foco propio en el inventario T1.'], ['selected', 'Los mensajes no tienen selección propia.'], ['disabled', 'Los mensajes no son controles.']]),
  entry('C-PANEL', 'Panel de capas', ['RF-1', 'RF-2', 'RF-4'], ['X-MAP'],
    [['open', 'Panel visible.'], ['closed', 'Panel cerrado y sustituido por su disparador.'], ['checked', 'Casillas/radios reflejan selección de capas.'], ['hover', 'Hover de opciones de capa observado.'], ['scroll', 'Desplazamiento vertical existente.']],
    [['loading', 'No se observó estado de carga/error propio del panel.'], ['message', 'No se observó estado de mensaje propio.']]),
  entry('C-FLOAT', 'Controles flotantes', ['RF-1', 'RF-2', 'RF-4'], ['X-MAP'],
    [['normal', 'Controles de capas, alta y OpenLayers existentes.'], ['hover', 'Hover CSS declarado.'], ['focus', 'Foco global/local declarado.'], ['active', 'Estado activo existente del control de alta.']],
    [['disabled', 'No se observó disabled local; rotación del mapa desactivada en la configuración existente.'], ['loading', 'No se observaron estados de carga propios.'], ['message', 'No son elementos de mensaje.']]),
  entry('C-INFO', 'Información del mapa', ['RF-1', 'RF-2', 'RF-4'], ['X-MAP'],
    [['visible', 'Información mostrada tras interacción existente con una entidad del mapa.'], ['hidden', 'Información cerrada por clic fuera/sin feature.'], ['scroll', 'Scroll vertical ante contenido largo en landscape.']],
    [['focus', 'No se observó foco propio.'], ['selected', 'No hay selección interna de la información.'], ['disabled', 'No es un control editable.'], ['loading', 'No se observó carga propia.']])
];

export const nativeAlerts = [
  {
    id: 'A-01',
    trigger: 'Buscar dirección con entrada vacía',
    message: 'Por favor, ingrese una dirección.',
    requirements: ['RF-6', 'RF-7', 'RF-23'],
    presentation: 'native-browser-excluded',
    behavior: 'verify-trigger-message-function'
  },
  {
    id: 'A-02',
    trigger: 'Respuesta de búsqueda de dirección sin latitud/longitud truthy',
    message: 'No se recibieron coordenadas válidas del backend.',
    requirements: ['RF-6', 'RF-23'],
    presentation: 'native-browser-excluded',
    behavior: 'verify-trigger-message-function'
  },
  {
    id: 'A-03',
    trigger: 'Catch de la búsqueda de dirección',
    message: 'Error al buscar dirección: ${error.message}',
    requirements: ['RF-6', 'RF-23'],
    presentation: 'native-browser-excluded',
    behavior: 'verify-trigger-message-function'
  }
];
