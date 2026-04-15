from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import Qt, QShortcut, QKeySequence
from app.pages import *
from app.modules.tts import VoiceEngine
from app.modules.logging import *
from app.modules.settings import SettingsManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.static_pages = {
            "keyboard": Keyboard()
        }

        # Définition des propiétés de la fenêtre
        self.setWindowTitle("Communiquer avec les yeux")
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        self.refreshShortcut = QShortcut(QKeySequence('r'), self)
        self.refreshShortcut.activated.connect(self.updateStyle)

        self.switch("menu")

        self.updateStyle()

        # On montre la fenêtre quand elle est prête
        self.show()

    def switch(self, page: str | Page | None=None):
        current = self.centralWidget()
        if current and current in self.static_pages.values():
            current.setParent(None)

        if isinstance(page, Page):
            self.setCentralWidget(page)
        elif isinstance(page, str):
            if page in self.static_pages:
                self.setCentralWidget(self.static_pages[page])
            else:
                match page:
                    case "menu":
                        self.setCentralWidget(Menu())
                    case "contacts":
                        self.setCentralWidget(Contacts())
                    case "messages":
                        self.setCentralWidget(Messages())
                    case "settings":
                        self.setCentralWidget(Settings())
                    case _:
                        warn(f"Page {page} does not exists.")
        else:
            warn("Switch called with no argument or of wrong type.")
        
    def showEvent(self, event):
        VoiceEngine()
        return super().showEvent(event)

    def closeEvent(self, event):
        VoiceEngine().stop()
        return super().closeEvent(event)
    
    def updateStyle(self):
        info("Mise à jour du style")
        stylesheet = open("app/style.css").read()
        fontSize = SettingsManager().getSetting("fontSize")
        stylesheet = stylesheet.replace("var(base)", f"{fontSize}px")
        stylesheet = stylesheet.replace("var(large)", f"{fontSize+12}px")
        stylesheet = stylesheet.replace("var(extra-large)", f"{fontSize+20}px")
        self.setStyleSheet(stylesheet)