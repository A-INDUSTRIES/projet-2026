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

    def switch(self, page: str| Page | None=None ):
        if isinstance(page, str):
            match page:
                case "menu":
                    self.setCentralWidget(Menu())
                case "contacts":
                    self.setCentralWidget(Contacts())
                case "keyboard":
                    self.setCentralWidget(Keyboard())
                case "messages":
                    self.setCentralWidget(Messages())
                case "settings":
                    self.setCentralWidget(Settings())
                case _:
                    print(f"Warn: Page {page} does not exists")
        elif isinstance(page, Page):
            self.setCentralWidget(page)
        else:
            print("Warn: switch called without an argument")


    def showEvent(self, event):
        VoiceEngine()
        return super().showEvent(event)

    def closeEvent(self, event):
        VoiceEngine().stop()
        return super().closeEvent(event)