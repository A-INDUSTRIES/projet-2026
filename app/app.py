from PySide6.QtGui import Qt, QShortcut, QKeySequence, QCursor, QPainter, QBrush, QPen
from PySide6.QtWidgets import QMainWindow, QStackedLayout, QWidget
from app.pages import *
from app.modules.tts import VoiceEngine
from app.modules.logger import *
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

        self.container = Container()
        self.stack = QStackedLayout(self.container)
        self.stack.setStackingMode(QStackedLayout.StackingMode.StackAll)
        
        self.setCentralWidget(self.container)

        self.eye = Eye()
        self.eye.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents) 

        self.switch("menu")
        self.stack.insertWidget(1, self.eye)
        self.stack.setCurrentIndex(1)

        self.updateStyle()

        self.setMouseTracking(True)

        # On montre la fenêtre quand elle est prête
        self.show()

        self.timer = QTimer()
        self.timer.setInterval(int(1/60))
        self.timer.timeout.connect(self.eyeEvent)
        self.timer.start()

    def switch(self, page: str | Page | None=None):
        current = self.stack.widget(0)

        if current:
            self.stack.removeWidget(current)

        if current and current in self.static_pages.values():
            current.setParent(None)

        if isinstance(page, Page):
            self.stack.insertWidget(0, page)
        elif isinstance(page, str):
            if page in self.static_pages:
                self.stack.insertWidget(0, self.static_pages[page])
            else:
                match page:
                    case "menu":
                        self.stack.insertWidget(0, Menu())
                    case "contacts":
                        self.stack.insertWidget(0, Contacts())
                    case "messages":
                        self.stack.insertWidget(0, Messages())
                    case "settings":
                        self.stack.insertWidget(0, Settings())
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

    def eyeEvent(self):
        mouse = QCursor()
        self.stack.widget(0).eyeEvent(self.mapFromGlobal(mouse.pos()))
        self.eye.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        brush = QBrush("red")

        pen = QPen("black")

        painter.setBrush(brush)
        painter.setPen(pen)
        painter.setOpacity(0.2)

        center = self.mapFromGlobal(QCursor().pos())

        painter.drawEllipse(center, 20, 20)
        return super().paintEvent(event)

class Container(QWidget):
    def switch(self, page):
        self.parent().switch(page)

    def close(self):
        self.parent().close()

    def updateStyle(self):
        self.parent().updateStyle()

class Eye(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)

        brush = QBrush("gray")

        pen = QPen("black")

        painter.setBrush(brush)
        painter.setPen(pen)
        painter.setOpacity(0.2)

        center = self.mapFromGlobal(QCursor().pos())

        painter.drawEllipse(center, 20, 20)
        return super().paintEvent(event)