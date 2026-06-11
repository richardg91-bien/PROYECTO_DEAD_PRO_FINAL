@echo off
echo Iniciando PROYECTO_DEAD_PRO_FINAL...

if not exist venv\Scripts\activate (
    echo ERROR: No se encontro el entorno virtual. Ejecuta primero:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

if not exist frontend-react\node_modules (
    echo Instalando dependencias del frontend...
    cd frontend-react && npm install && cd ..
)

echo Iniciando backend en http://127.0.0.1:5000
start "Backend Flask" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python run.py"

echo Iniciando frontend en http://127.0.0.1:5173
start "Frontend React" cmd /k "cd /d %~dp0\frontend-react && npm run dev"

echo Listo. Abre http://127.0.0.1:5173 en tu navegador.
