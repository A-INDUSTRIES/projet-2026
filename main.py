from PySide6.QtWidgets import QApplication
from app.app import MainWindow
from app.modules.logger import setLogLevel, debug
from ctypes.util import find_library
import os
import app.modules.assets

if __name__ == "__main__":
    setLogLevel("debug")
    espeak_path = find_library("espeak-ng") or find_library("espeak")
    debug(espeak_path)
    if espeak_path:
        os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = espeak_path
    app = QApplication()
    main_window = MainWindow()
    app.exec()