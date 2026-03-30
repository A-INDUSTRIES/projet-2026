from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import Qt
from app.pages import *
from app.modules.tts import VoiceEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Définition des propiétés de la fenêtre
        self.setWindowTitle("Communiquer avec les yeux")
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setStyleSheet(open("app/style.css").read())

        self.switch("menu")

        # On montre la fenêtre quand elle est prête
        self.show()

    def switch(self, page="", instance=None):
        match page:
            case "menu":
                self.setCentralWidget(Menu(self))
            case "contacts":
                self.setCentralWidget(Contacts(self))
            case "keyboard":
                self.setCentralWidget(Keyboard(self))
            case "messages":
                self.setCentralWidget(Messages(self))
            case "settings":
                self.setCentralWidget(Settings(self))
            case "":
                self.setCentralWidget(instance)

    def showEvent(self, event):
        VoiceEngine()
        return super().showEvent(event)

    def closeEvent(self, event):
        VoiceEngine().stop()
        return super().closeEvent(event)