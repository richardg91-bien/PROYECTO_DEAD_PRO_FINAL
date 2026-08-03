@echo off
setlocal
set "ROOT=%~dp0"
set "BACKEND_PORT=%FLASK_PORT%"
if "%BACKEND_PORT%"=="" set "BACKEND_PORT=5000"
set "FRONTEND_PORT=%VITE_PORT%"
if "%FRONTEND_PORT%"=="" set "FRONTEND_PORT=5173"

echo Iniciando PROYECTO_DEAD_PRO_FINAL...

if not exist "%ROOT%venv\Scripts\activate" (
    echo ERROR: No se encontro el entorno virtual. Ejecuta primero:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist "%ROOT%frontend-react\node_modules" (
    echo Instalando dependencias del frontend...
    cd /d "%ROOT%frontend-react" && npm install
)

echo Iniciando backend en http://127.0.0.1:%BACKEND_PORT%
start "Backend Flask" cmd /k "cd /d "%ROOT%" && call venv\Scripts\activate && set FLASK_ENV=development && python run.py"

echo Iniciando frontend en http://127.0.0.1:%FRONTEND_PORT%
start "Frontend React" cmd /k "cd /d "%ROOT%frontend-react" && set VITE_API_URL=http://127.0.0.1:%BACKEND_PORT% && npm run dev -- --host 127.0.0.1 --port %FRONTEND_PORT%"

echo Listo. Abre http://127.0.0.1:%FRONTEND_PORT% en tu navegador.
endlocal
