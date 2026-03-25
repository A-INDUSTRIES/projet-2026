import sounddevice as sd
import requests
from zipfile import ZipFile
from io import BytesIO
from pathlib import Path
from threading import Thread, Event
from queue import Queue

MODEL_PATH = Path(__file__).parent / "voice_model"
MODEL_URL = "https://cloud.aindustries.be/public.php/dav/files/Paik9imyoMJjsLK/?accept=zip"

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class VoiceEngine(metaclass=Singleton):
    def __init__(self):
        self.queue = Queue()
        self.thread = Thread(target=self._thread)
        self.thread.start()
        self.instance = self

    def stop(self):
        self.queue.put(None)
        self.thread.join()

    def read(self, text):
        self.queue.put(text)

    def _thread(self):
        print("Démarrage du VoiceEngine")
        from kokoro import KPipeline, KModel

        # Si le modèle n'a pas été téléchargé
        # Sert durant le dev: pour la release on installera ces fichiers durant l'installation
        if not MODEL_PATH.exists():
            print("Téléchargement du modèle pour la voix en cours.")
            response = requests.get(MODEL_URL)

            with ZipFile(BytesIO(response.content)) as zip:
                zip.extractall(MODEL_PATH.parent)

        print("Initialisation du modèle")
        model = KModel(repo_id="hexgrad/Kokoro-82M", 
                    model=MODEL_PATH / "kokoro-v1_0.pth",
                    config=MODEL_PATH / "config.json")

        voice = KPipeline(repo_id="hexgrad/Kokoro-82M",
                               lang_code="f",
                               model=model)

        stream = sd.OutputStream(samplerate=24000, channels=1, dtype='float32')
        stream.start()

        voice_path = MODEL_PATH / "voices" / "ff_siwis.pt"

        print("Chargement du modèle terminé")

        while True:
            print("En attente d'une demande")
            text = self.queue.get(block=True, timeout=None)
            if text==None:
                break
            generator = voice(text, voice=voice_path.as_posix())
            for _, _, data in generator:
                stream.write(data)

        stream.stop()
        print("VoiceEngine arrêté")