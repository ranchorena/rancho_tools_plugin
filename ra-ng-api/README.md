# ra-ng-api

API de clientes, pedidos, direcciones y rutas. El contrato está en `/api/v1`. raweb arma las llamadas sobre `API_URL`, que ya termina en `/api/v1`.

La audiencia de Keycloak sigue siendo el clientId `raapi`. raweb y ra-mcp emiten ese `aud`.

## Entorno virtual

Desde `ra-ng-api`, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Las variables salen de `.env` en esta carpeta. Una variable ya definida en el proceso tiene prioridad, así que Docker no toma el `DB_HOST=localhost` de ese archivo.

- Salud: `http://localhost:8000/health`
- Documentación: `http://localhost:8000/docs`
- Contrato: `openapi.yaml` (OpenAPI 3.1)

Para regenerar el contrato, con el entorno activo y `PyYAML` instalado (`python -m pip install PyYAML`):

```powershell
python -m scripts.export_openapi
```

## Docker Compose

El servicio publica el puerto **5001** del host hacia el **8000** del contenedor. ra-proxy envía `/api/` y `/health` a este servicio. Por el proxy, raweb llama `http://localhost:8088/api/v1/...`.

```powershell
docker compose up -d --build ra-ng-api proxy frontend
```

## CORS

Quien entra por `http://localhost:8088` comparte origen con la API y no necesita CORS. Sí hace falta para `npm run dev` en el puerto 8080 y para el frontend publicado en el 8082, porque llaman a otro origen. `CORS_ORIGINS` cubre esos tres.
