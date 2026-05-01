import sounddevice as sd
import requests
from zipfile import ZipFile
from io import BytesIO
from threading import Thread
from queue import Queue
from .utils import Singleton, getUserDataPath
from .logger import *

MODEL_PATH = getUserDataPath() / "voice_model"
MODEL_URL = "https://cloud.aindustries.be/public.php/dav/files/Paik9imyoMJjsLK/?accept=zip"

class VoiceEngine(metaclass=Singleton):
    def __init__(self):
        self.queue = Queue()
        self.thread = Thread(target=self._thread, daemon=True)
        self.thread.start()

    def stop(self):
        # On ne join pas le thread, il se coupera directement même s'il est en train de charger.
        self.queue.put(None)

    def read(self, text):
        self.queue.put(text)

    def _thread(self):
        info("Démarrage du VoiceEngine")
        from kokoro import KPipeline, KModel

        # Si le modèle n'a pas été téléchargé
        # Sert durant le dev: pour la release on installera ces fichiers durant l'installation
        if not MODEL_PATH.exists():
            info("Téléchargement du modèle pour la voix en cours.")
            response = requests.get(MODEL_URL)

            with ZipFile(BytesIO(response.content)) as zip:
                zip.extractall(MODEL_PATH.parent)

        debug("Initialisation du modèle")
        model = KModel(repo_id="hexgrad/Kokoro-82M", 
                    model=MODEL_PATH / "kokoro-v1_0.pth",
                    config=MODEL_PATH / "config.json")

        voice = KPipeline(repo_id="hexgrad/Kokoro-82M",
                               lang_code="f",
                               model=model)

        stream = sd.OutputStream(samplerate=24000, channels=1, dtype='float32')
        stream.start()

        voice_path = MODEL_PATH / "voices" / "ff_siwis.pt"

        info("Chargement du modèle terminé")

        while True:
            debug("En attente d'une demande")
            text = self.queue.get(block=True, timeout=None)
            if text==None:
                break
            generator = voice(text, voice=voice_path.as_posix())
            for _, _, data in generator:
                stream.write(data)

        stream.stop()
        info("VoiceEngine arrêté")