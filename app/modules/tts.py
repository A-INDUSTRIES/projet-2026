import sounddevice as sd
from piper.voice import PiperVoice
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
        for chunk in self.voice.synthesize(text):
            sd.play(chunk.audio_int16_array, samplerate=self.voice.config.sample_rate)
            sd.wait()


if __name__ == "__main__":
    from time import sleep

    text = "Bonjour, c'est une belle journée aujourd'hui!"
    voiceEngine = VoiceEngine()
    voiceEngine.read(text)
    sleep(10)