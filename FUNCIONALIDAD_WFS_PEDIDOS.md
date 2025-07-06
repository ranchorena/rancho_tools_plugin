# Funcionalidad WFS para Pedidos

## Descripción General

Se ha implementado una nueva funcionalidad en el plugin **RAncho Tools** que permite usar una capa WFS (Web Feature Service) para el manejo de pedidos, reemplazando la funcionalidad original que dependía de capas locales.

## Características Principales

### 1. Capa WFS de Pedidos
- **Conexión a servicios WFS externos**: Permite conectarse a servidores WFS como GeoServer, MapServer, etc.
- **Configuración flexible**: Soporte para autenticación con usuario/contraseña
- **Compatibilidad con múltiples versiones WFS**: Soporte para versiones 1.0.0, 1.1.0 y 2.0.0

### 2. Herramienta de Click Interactiva
- **Identificación por click**: Haga click en cualquier pedido para ver su información
- **Información detallada**: Muestra ID, nombre, dirección, cantidad, fecha y observaciones
- **Interfaz amigable**: Diálogo emergente con información clara y organizada

### 3. Configuración Avanzada
- **Diálogo de configuración**: Interface gráfica para configurar la conexión WFS
- **Auto-carga**: Opción para cargar automáticamente la capa al iniciar QGIS
- **Personalización visual**: Configuración del tamaño de símbolos
- **Prueba de conexión**: Verificación de conectividad antes de usar

## Instalación y Configuración

### Paso 1: Configurar el Servicio WFS

1. Abra QGIS con el plugin RAncho Tools instalado
2. En la barra de herramientas RAncho, haga click en **"Configurar WFS Pedidos"** 
3. Complete los campos requeridos:

   - **URL del Servidor WFS**: `http://su-servidor.com:8080/geoserver/wfs`
   - **Nombre de la Capa**: `workspace:pedidos`
   - **Versión WFS**: `1.1.0` (recomendado)
   - **Usuario/Contraseña**: Si su servidor requiere autenticación

4. Configure las opciones de visualización:
   - **Cargar automáticamente al inicio**: Para auto-cargar la capa
   - **Tamaño del símbolo**: Tamaño de los puntos de pedidos
   - **Activar herramienta click automáticamente**: Para activar la herramienta al cargar

5. Haga click en **"Probar Conexión"** para verificar que la configuración es correcta
6. Haga click en **"Guardar"** para guardar la configuración

### Paso 2: Cargar la Capa WFS

1. Una vez configurado, haga click en **"Cargar Pedidos WFS"** en la barra de herramientas
2. La capa se agregará automáticamente al panel de capas de QGIS
3. Los pedidos aparecerán como puntos rojos en el mapa

### Paso 3: Activar la Herramienta de Click

1. Haga click en **"Activar Click Pedidos"** en la barra de herramientas
2. El cursor cambiará a una cruz
3. Haga click en cualquier pedido para ver su información

## Estructura de Datos Requerida

Para que la funcionalidad WFS funcione correctamente, la capa de pedidos debe contener los siguientes campos:

### Campos Obligatorios
- `id` o `id_pedido`: Identificador único del pedido
- `nombre`: Nombre del cliente
- `direccion`: Dirección del pedido

### Campos Opcionales
- `cantidad`: Cantidad de productos pedidos
- `fecha`: Fecha del pedido
- `observaciones`: Observaciones adicionales
- `telefono`: Teléfono del cliente
- `horario`: Horario preferido de entrega

### Geometría
- **Tipo**: Point (Punto)
- **Sistema de coordenadas**: Cualquier SRC válido (se reprojectará automáticamente)

## Ejemplos de Configuración

### GeoServer Local
```
URL: http://localhost:8080/geoserver/wfs
Capa: pedidos:pedidos_activos
Versión: 1.1.0
```

### GeoServer con Autenticación
```
URL: https://mi-servidor.com/geoserver/wfs
Capa: empresa:pedidos
Versión: 1.1.0
Usuario: admin
Contraseña: mi_password
```

### MapServer
```
URL: http://servidor.com/cgi-bin/mapserv?map=/path/to/map.map
Capa: pedidos
Versión: 1.0.0
```

## Funciones Avanzadas

### Filtrado por Atributos
El servicio WFS permite filtrar pedidos usando expresiones CQL. Ejemplos:

- Pedidos de hoy: `fecha = '2024-01-15'`
- Pedidos pendientes: `estado = 'pendiente'`
- Cantidad mayor a 5: `cantidad > 5`

### Actualización en Tiempo Real
Si el servidor WFS soporta transacciones (WFS-T), los cambios se reflejarán automáticamente en QGIS al refrescar la capa.

## Solución de Problemas

### Error: "No se pudo cargar la capa WFS"
**Posibles causas:**
- URL incorrecta del servidor WFS
- Nombre de capa incorrecto
- Servidor WFS no accesible
- Problemas de autenticación

**Soluciones:**
1. Verificar que el servidor WFS esté funcionando
2. Usar "Probar Conexión" en el diálogo de configuración
3. Verificar las credenciales de acceso
4. Comprobar la conectividad de red

### Error: "No se encontró ningún pedido"
**Posibles causas:**
- Capa sin datos
- Filtros aplicados que ocultan todos los pedidos
- Problemas de proyección de coordenadas

**Soluciones:**
1. Verificar que la capa tenga datos usando un cliente WFS externo
2. Revisar y remover filtros aplicados
3. Verificar el sistema de coordenadas de la capa

### Rendimiento Lento
**Optimizaciones:**
- Usar filtros espaciales para limitar el área de consulta
- Implementar paginación en el servidor WFS
- Usar cache del lado del servidor
- Limitar el número de features retornadas

## Archivos de Configuración

La configuración se guarda en el archivo `pedidos_wfs_config.ini` en el directorio del plugin:

```ini
[WFS]
url = http://localhost:8080/geoserver/wfs
layer_name = pedidos:pedidos_activos
version = 1.1.0
usuario = 
password = 

[DISPLAY]
auto_cargar = True
symbol_size = 8
auto_click_tool = False
```

## Compatibilidad

### Versiones QGIS Soportadas
- QGIS 3.16 LTR o superior
- QGIS 3.22 LTR (recomendado)
- QGIS 3.28 LTR

### Servidores WFS Compatibles
- GeoServer 2.18+
- MapServer 7.0+
- QGIS Server 3.16+
- ArcGIS Server 10.8+

### Formatos de Datos Soportados
- GeoJSON
- GML 2.0, 3.1, 3.2
- KML (solo lectura)

## Migración desde Capas Locales

Para migrar de la funcionalidad anterior basada en capas locales:

1. **Preparar datos**: Exporte sus datos de pedidos a PostGIS o publíquelos en un servidor WFS
2. **Configurar WFS**: Use el nuevo diálogo de configuración
3. **Probar conexión**: Verifique que todos los datos se muestren correctamente
4. **Actualizar flujo de trabajo**: Adapte sus procesos para usar la nueva herramienta de click

## Soporte y Contacto

Para reportar errores o solicitar nuevas funcionalidades, contacte al equipo de desarrollo del plugin RAncho Tools.

## Registro de Cambios

### Versión 2.0
- ✅ Implementación de capa WFS para pedidos
- ✅ Herramienta de click interactiva
- ✅ Diálogo de configuración WFS
- ✅ Auto-carga de capas
- ✅ Soporte para autenticación
- ✅ Prueba de conexión integrada