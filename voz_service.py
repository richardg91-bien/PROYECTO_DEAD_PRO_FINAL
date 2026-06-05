import subprocess

def generar_audio(texto):
    try:
        result = subprocess.run(
            [
                "venv_voice\\Scripts\\python",
                "voz.py",
                texto
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("❌ ERROR VOZ:", result.stderr)
            return None

        # ⚡ devuelve la ruta del audio generada en voz.py
        ruta_audio = result.stdout.strip()

        return ruta_audio

    except Exception as e:
        print("❌ ERROR VOZ:", e)
        return None