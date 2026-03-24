import sounddevice as sd
import requests
from zipfile import ZipFile
from io import BytesIO
from kokoro import KPipeline, KModel
from pathlib import Path
from threading import Thread

MODEL_PATH = Path(__file__).parent / "voice_model"
MODEL_URL = "https://cloud.aindustries.be/public.php/dav/files/Paik9imyoMJjsLK/?accept=zip"

# Si le modèle n'a pas été téléchargé
# Sert durant le dev: pour la release on installera ces fichiers durant l'installation
if not MODEL_PATH.exists():
    print("Téléchargement du modèle pour la voix en cours.")
    response = requests.get(MODEL_URL)

    with ZipFile(BytesIO(response.content)) as zip:
        zip.extractall(MODEL_PATH.parent)


model = KModel(repo_id="hexgrad/Kokoro-82M", 
               model=MODEL_PATH / "kokoro-v1_0.pth",
               config=MODEL_PATH / "config.json")

class VoiceEngine():
    def __init__(self):
        self.voice = KPipeline(repo_id="hexgrad/Kokoro-82M",
                               lang_code="f",
                               model=model)
        self.stream = sd.OutputStream(samplerate=24000, channels=1, dtype='float32')
        self.stream.start()

    def __del__(self):
        self.stream.stop()

    def read(self, text):
        self.thread = Thread(target=self._thread, args=[text])
        self.thread.start()

    def _thread(self, text):
        voice = MODEL_PATH / "voices" / "ff_siwis.pt"
        generator = self.voice(text, voice=voice.as_posix())
        for _, _, data in generator:
            self.stream.write(data)