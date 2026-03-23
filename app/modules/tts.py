import sounddevice as sd
from piper.voice import PiperVoice
from piper.config import SynthesisConfig
from pathlib import Path
from threading import Thread

MODEL_PATH = Path(__file__).parent / "fr_FR-upmc-medium.onnx" 

class VoiceEngine():
    def __init__(self):
        self.voice = PiperVoice.load(MODEL_PATH)

    def read(self, text):
        self.thread = Thread(target=self._thread, args=[text])
        self.thread.run()

    def _thread(self, text):
        # Paramètre de l'application
        config = SynthesisConfig(1) # 0 = Caro | 1 = Mohammed
        for chunk in self.voice.synthesize(text, config):
            sd.play(chunk.audio_int16_array, samplerate=self.voice.config.sample_rate)
            sd.wait()


if __name__ == "__main__":
    from time import sleep

    text = "Bonjour, c'est une belle journée aujourd'hui!"
    voiceEngine = VoiceEngine()
    voiceEngine.read(text)
    sleep(10)