import subprocess
import sys
import os

def generar_audio(texto):
    """Genera audio usando gTTS a través de voz.py"""
    try:
        # Usar el Python del venv actual
        python_exe = sys.executable
        voz_script = os.path.join(os.path.dirname(__file__), "..", "voz.py")

        result = subprocess.run(
            [
                python_exe,
                voz_script,
                texto
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("❌ ERROR VOZ:", result.stderr)
            return None

        # Devuelve la ruta del audio generada por voz.py
        ruta_audio = result.stdout.strip()
        return ruta_audio

    except Exception as e:
        print("❌ ERROR VOZ:", e)
        return None
