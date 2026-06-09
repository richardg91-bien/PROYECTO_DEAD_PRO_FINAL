from gtts import gTTS
import sys, uuid, os

texto = sys.argv[1]

os.makedirs("static/audio", exist_ok=True)

filename = f"{uuid.uuid4()}.mp3"
ruta = f"static/audio/{filename}"

tts = gTTS(text=texto, lang="es")
tts.save(ruta)

# ⚡ esto lo lee voz_service.py
print(ruta)