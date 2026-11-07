# ra-ng-api

API que reemplaza a `raapi` manteniendo el contrato que ya consume raweb.

Las operaciones viven en `/api/v1/...`. El mismo router está montado en `/api/...`, que es la base que raweb llama a través de ra-proxy. La audiencia de Keycloak sigue siendo `raapi`.

## Entorno virtual

Desde `ra-ng-api`, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Variables del proceso (la aplicación no lee un archivo `.env`):

```powershell
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "postgres"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_NAME = "postgres"
$env:DB_SCHEMA = "generalbelgrano"
$env:KEYCLOAK_ISSUER = "http://localhost:8088/realms/rancho"
$env:KEYCLOAK_JWKS_URL = "http://127.0.0.1:8081/realms/rancho/protocol/openid-connect/certs"
$env:RA_API_AUDIENCE = "raapi"
$env:CORS_ORIGINS = "http://localhost:8088,http://localhost:8082,http://localhost:8080"
```

Arranque:

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- Salud: `http://localhost:8000/health`
- Documentación: `http://localhost:8000/docs`
- Contrato: `openapi.yaml` (OpenAPI 3.1)

Para regenerar el contrato, con el entorno activo y `PyYAML` instalado (`python -m pip install PyYAML`):

```powershell
python -m scripts.export_openapi
```

## Docker Compose

El servicio `ra-ng-api` publica el puerto **5001** del host hacia el **8000** del contenedor. ra-proxy envía `/api/` y `/health` a este servicio. `raapi` sigue en el puerto 5000.

```powershell
docker compose up -d --build ra-ng-api proxy
```

Para volver el proxy a la API Flask, en `ra-proxy/nginx.conf` las dos variables `$raapi` deben apuntar a `backend:5000` y hay que recrear el contenedor `proxy`.
