# ra-mcp

Servidor MCP, construido con FastMCP, para que un agente busque clientes y registre un pedido delegando la persistencia en `raapi`.

## Objetivo

Permitir prompts como:

```text
Agregar un pedido al cliente Silvia, 2 docenas nro_pao 3
```

El agente busca por nombre, distingue una coincidencia de varias y solo registra el pedido cuando el cliente está identificado por `id_cliente`. Si hay varias personas con ese nombre, no se modifica ninguna hasta que el usuario elija.

## Arquitectura

```text
Agente
   │
   ▼
ra-mcp (FastMCP)
   │ HTTP
   ▼
raapi
   │
   ▼
Base de datos
```

`ra-mcp` no abre la base, no importa Flask y no replica el SQL de `raapi`.

La búsqueda reutiliza `POST /api/clientes/buscar`. El pedido reutiliza `PUT /api/clientes/actualizar/<id>`. No se agregó un endpoint nuevo para registrar: ese `PUT` ya acepta un cuerpo parcial y `actualizarCliente` solo escribe los campos presentes. El MCP envía únicamente:

```json
{
  "docenas": 2,
  "nro_pao": 3,
  "tiene_pedido": true
}
```

`raapi` traduce `docenas` a la columna `cantidad`, convierte `tiene_pedido: true` en `1` y guarda `nro_pao` como entero. La transacción es la de `Session.begin()`: un solo `UPDATE` y commit al salir sin error. No se reenvían horario, observaciones ni `es_regalo`, porque la búsqueda no los devuelve y volver a mandarlos en blanco los pisaría.

El historial reutiliza `GET /api/pedidos/historico`. Sin fechas, `raapi` devuelve el día del pedido más reciente. Con `desde` y `hasta`, el rango incluye ambos días. Las estadísticas las calcula el tool con la misma regla del formulario: la cantidad total suma todos los pedidos, y la cantidad vendida y el valor total excluyen los regalos. El valor de cada pedido es su cantidad por el precio unitario.

Tampoco hay un tool `listar_clientes`. `POST /api/clientes/buscar` ya devuelve todas las coincidencias del nombre.

## Requisitos

- Python 3.10 o superior.
- `raapi` en ejecución y accesible por HTTP.
- Variable `RA_API_BASE_URL` definida en el proceso del servidor. El código no trae una URL de desarrollo por defecto.

## Instalación

Desde `ra-mcp`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Configuración de RA_API_BASE_URL

Copiá `.env.example` solo como referencia. El servidor lee el entorno del proceso; no carga un archivo `.env` por su cuenta.

PowerShell:

```powershell
$env:RA_API_BASE_URL = "http://localhost:5000"
```

Opcional: `RA_API_TIMEOUT` en segundos. Si no está, el tiempo de espera es 30.

Ejemplo para Cursor. El uso normal es HTTP y OAuth; no hace falta usuario ni contraseña en este archivo:

```json
{
  "mcpServers": {
    "ra-mcp": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

El servidor tiene que estar levantado con `RA_MCP_TRANSPORT=http` antes de conectar Cursor. La primera vez el cliente abre el navegador contra el realm `rancho`.

## Modo no autenticado

STDIO no exige OAuth. Sirve para la suite de tests y para desarrollo interno del proceso. No es la configuración de Cursor:

```powershell
$env:RA_MCP_TRANSPORT = "stdio"
$env:RA_API_BASE_URL = "http://localhost:5000"
python -m ra_mcp.server
```

## Ejecución

El uso normal es Streamable HTTP con OAuth:

```powershell
$env:RA_MCP_TRANSPORT = "http"
$env:RA_API_BASE_URL = "http://localhost:5000"
$env:RA_MCP_PUBLIC_URL = "http://localhost:8000"
$env:KEYCLOAK_ISSUER = "http://localhost:8081/realms/rancho"
$env:KEYCLOAK_JWKS_URL = "http://127.0.0.1:8081/realms/rancho/protocol/openid-connect/certs"
$env:KEYCLOAK_CLIENT_ID = "ra-mcp"
$env:KEYCLOAK_CLIENT_SECRET = "<secreto local>"
$env:RA_API_AUDIENCE = "raapi"
$env:RA_MCP_JWT_SIGNING_KEY = "<secreto local>"
$env:RA_MCP_OAUTH_STORAGE_KEY = "<secreto local>"
python -m ra_mcp.server
```

El endpoint autenticado es `http://localhost:8000/mcp`. Los tokens upstream quedan cifrados en `%USERPROFILE%\.ra-mcp\oauth`.

`ra-mcp` no manda a `raapi` el JWT interno de FastMCP. Con el access token de Keycloak del usuario hace Standard Token Exchange V2 (`audience=raapi`) y usa solo ese resultado.

## Tools disponibles

### buscar_cliente

Busca clientes por nombre antes de realizar operaciones que requieren identificar a un cliente. Puede devolver múltiples coincidencias y, en ese caso, el agente debe pedir al usuario que seleccione el cliente correcto antes de efectuar cambios.

| Parámetro | Tipo | Descripción |
| --- | --- | --- |
| `nombre` | string | Nombre o fragmento. `raapi` busca con `LIKE` parcial, sin distinguir mayúsculas, y solo incluye clientes con geometría. |

Estados: `NO_MATCH`, `ONE_MATCH`, `MULTIPLE_MATCHES`. Un fallo de red o de `raapi` vuelve como `status: ERROR` y no como ausencia de clientes.

Los campos de cada coincidencia son los que realmente devuelve la búsqueda: `id` (expuesto como `id_cliente`), `nombre`, `direccion`, `calle`, `altura`, `longitud` y `latitud`. No hay apellido, teléfono ni localidad en esa respuesta.

Ejemplo con varias coincidencias:

```json
{
  "status": "MULTIPLE_MATCHES",
  "success": true,
  "requiere_seleccion": true,
  "clientes": [
    {
      "id_cliente": 145,
      "nombre": "Silvia Gómez",
      "direccion": "San Martín 100",
      "calle": "San Martín",
      "altura": 100,
      "longitud": -58.41,
      "latitud": -34.61
    }
  ],
  "message": "Hay varias coincidencias. Pedí al usuario que elija un id_cliente antes de registrar un pedido. No elijas automáticamente."
}
```

Sin coincidencias, `clientes` es un array vacío y `status` es `NO_MATCH`. Con una sola, el resultado incluye además `id_cliente` en la raíz.

### agregar_pedido

Registra un pedido para un cliente previamente identificado mediante su id_cliente. No debe utilizarse si la búsqueda previa devolvió múltiples clientes y el usuario todavía no seleccionó uno.

| Parámetro | Tipo | Descripción |
| --- | --- | --- |
| `id_cliente` | entero positivo | Identificador devuelto por `buscar_cliente`. No se acepta el nombre. |
| `cantidad_docenas` | número mayor que cero | Docenas pedidas. Se envía como `docenas` y `raapi` la guarda en `cantidad`. Se admiten fracciones, como `1.5`, igual que el formulario web. |
| `nro_pao` | entero positivo | Número de PaO. `raapi` lo persiste con `int()` en la columna `nro_pao`. El tool rechaza cero, negativos y valores que no son enteros antes de llamar a `raapi`. |

`raapi` no valida hoy un rango para `nro_pao` ni que la cantidad sea positiva. Esa comprobación de entrada vive en el tool para no confirmar un pedido con datos que el agente no debería enviar. La escritura sigue siendo exclusiva de `raapi`.

Respuesta correcta:

```json
{
  "success": true,
  "id_cliente": 145,
  "cantidad_docenas": 2,
  "nro_pao": 3,
  "tiene_pedido": 1,
  "mensaje": "Cliente actualizado correctamente."
}
```

El `PUT` actual no devuelve el nombre del cliente. El nombre queda en la respuesta previa de `buscar_cliente`.

Error:

```json
{
  "success": false,
  "error_code": "CLIENT_NOT_FOUND",
  "message": "No existe el cliente indicado.",
  "id_cliente": 999,
  "detalle": "Cliente con ID 999 no encontrado."
}
```

Otros códigos: `INVALID_ID_CLIENTE`, `INVALID_CANTIDAD`, `INVALID_NRO_PAO`, `RAAPI_REJECTED`, `RAAPI_ERROR`, `RAAPI_UNAVAILABLE`, `RAAPI_NOT_CONFIGURED`.

Si la validación local falla, no hay llamada HTTP. Si `raapi` responde 4xx o 5xx, `success` es `false`.

### pedidos_historico

Devuelve los pedidos históricos de un período y las estadísticas totales. Si no se envían fechas, trae los pedidos del día del pedido más reciente, igual que el formulario Pedidos histórico.

| Parámetro | Tipo | Descripción |
| --- | --- | --- |
| `desde` | `YYYY-MM-DD`, opcional | Fecha inicial inclusive. Hay que enviarla junto con `hasta`. |
| `hasta` | `YYYY-MM-DD`, opcional | Fecha final inclusive. Hay que enviarla junto con `desde`. |

Sin `desde` ni `hasta`, el tool llama a `GET /api/pedidos/historico` sin consulta. `raapi` usa el día de la fecha máxima de la tabla `pedido`.

`cantidad_total` suma la cantidad de todos los pedidos. `cantidad_vendida` y `valor_total` dejan afuera los que tienen `es_regalo` en 1. El valor de cada pedido vendido es `cantidad * precio_unitario`.

```json
{
  "success": true,
  "fecha_desde": "2026-10-11",
  "fecha_hasta": "2026-10-11",
  "pedidos": [],
  "estadisticas": {
    "cantidad_total": 3.5,
    "cantidad_vendida": 2.5,
    "valor_total": 12500.0
  },
  "message": "Pedidos históricos del período indicado."
}
```

Si no hay ningún pedido cargado, `fecha_desde` y `fecha_hasta` vienen vacías y el mensaje es `No hay pedidos registrados.` Si el período no tiene filas, el mensaje es `No se encontraron pedidos para las fechas indicadas.`

Una sola fecha, un formato distinto de `YYYY-MM-DD` o un desde posterior al hasta responden `INVALID_FECHA` y no llaman a `raapi`.

## Manejo de múltiples clientes

```text
Encontré 3 clientes llamados Silvia:

1. Silvia Gómez — Cliente 145 — San Martín 100
2. Silvia Pérez — Cliente 327 — Belgrano 200
3. Silvia Rodríguez — Cliente 401 — Mitre 300

¿Cuál querés usar?
```

Hasta esa respuesta el MCP solo ejecutó la búsqueda. Después de la elección:

```text
agregar_pedido(id_cliente=145, cantidad_docenas=2, nro_pao=3)
```

## Ejemplos de prompts para agentes

```text
Agregar un pedido al cliente Silvia, 2 docenas nro_pao 3
```

```text
Agregar un pedido al cliente Marta, 1 docena nro_pao 5
```

Flujo que debe seguir el agente:

1. Extraer nombre, cantidad de docenas y `nro_pao`.
2. Llamar a `buscar_cliente`.
3. `NO_MATCH`: informar que no hay coincidencia.
4. `ONE_MATCH`: usar ese `id_cliente`.
5. `MULTIPLE_MATCHES`: mostrar candidatos y esperar. No crear el pedido.
6. Llamar a `agregar_pedido` con el `id_cliente` elegido.
7. Informar el resultado de `raapi`.

El servidor publica estas instrucciones para el cliente MCP.

## Pruebas

```powershell
python -m pytest
python scripts/flujo_silvia.py
```

`scripts/flujo_silvia.py` reproduce, contra un `raapi` simulado en memoria:

```text
Agregar un pedido al cliente Silvia, 2 docenas nro_pao 3
```

Comprueba que, con tres Silvias, no hay ningún `PUT` hasta que se selecciona un `id_cliente`, y que el `PUT` final apunta solo a ese cliente. No toca la base de datos.
