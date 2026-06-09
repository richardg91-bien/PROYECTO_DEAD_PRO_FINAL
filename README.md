# PROYECTO_DEAD_PRO_FINAL

Aplicacion web con backend Flask y frontend React para guardar experiencias, imagenes, codigos QR y conversaciones asistidas por IA.

## Estructura principal

- `app/`: backend Flask.
- `frontend-react/`: frontend React/Vite.
- `static/`: archivos generados por el backend en ejecucion local.
- `tests/`: pruebas automatizadas del backend.

La carpeta React valida es `frontend-react/`. Si aparecen copias internas como `frontend-react/frontend-react/`, no deben usarse como proyecto principal.

## Configuracion

1. Copia `.env.example` a `.env`.
2. Completa `SUPABASE_URL`, `SUPABASE_KEY`, `SECRET_KEY` y opcionalmente `DEEPSEEK_API_KEY`.
3. Para produccion, define `FLASK_DEBUG=0` y limita `CORS_ORIGINS` al dominio real del frontend.

## Ejecutar backend

```powershell
venv\Scripts\activate
python run.py
```

Backend local: `http://127.0.0.1:5000`

## Ejecutar frontend

```powershell
cd frontend-react
npm install
npm run dev
```

Frontend local: `http://127.0.0.1:5173`

Para apuntar el frontend a otro backend, crea `frontend-react/.env` con:

```text
VITE_API_URL=http://127.0.0.1:5000
```

## Pruebas

```powershell
pytest -q
```

Si el entorno virtual esta roto, recrealo:

```powershell
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Git

No se deben versionar bases de datos locales, imagenes subidas, QR generados, `node_modules`, `venv` ni copias duplicadas del proyecto.
