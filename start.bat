@echo off
start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python run.py"
start cmd /k "cd /d %~dp0\frontend-react && npm run dev"