from PySide6.QtWidgets import QGridLayout, QPushButton, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from ..widgets.keyboard_widget import KeyboardWidget
from ..widgets.text_display import TextDisplayWidget
from . import Page
from pathlib import Path

class Keyboard(Page):
    def __init__(self, *args):
        super().__init__(*args)

        # Instanciation du layout
        self.layout = QGridLayout(self)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 4)
        
        # Instanciation du widget d'affichage du texte
        self.textDisplay = TextDisplayWidget()
        self.textDisplay.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.MinimumExpanding)
        self.layout.addWidget(self.textDisplay, 0, 0, 2, 8)
        
        # Instanciation du widget clavier
        self.keyboard = KeyboardWidget()
        # Sous le display
        self.keyboard.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.MinimumExpanding)
        self.layout.addWidget(self.keyboard, 2, 0, 4, 10)
        
        # Modification du texte affiché quand interaction avec le clavier
        self.keyboard.textUpdated.connect(self.textDisplay.updateText)
        
        # Boutons supplémentaires : Text-to-Speech, Envoi par mail, scroll le text (haut / bas)
        # TTS
        self.tts = QPushButton("Text to\nSpeech")
        self.tts.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.MinimumExpanding)
        self.layout.addWidget(self.tts, 0, 9, 1, 1)
        
        # Mail
        self.mail = QPushButton("Envoyer\npar mail")
        self.mail.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.MinimumExpanding)
        self.layout.addWidget(self.mail, 1, 9, 1, 1)
        
        # Images pour les boutons de scroll
        imgPath = (Path(__file__).parent.parent / "assets" / "chevron-up.png").as_posix()
        print(imgPath)
        self.up = QIcon(imgPath)
        imgPath = (Path(__file__).parent.parent / "assets" / "chevron-down.png").as_posix()
        self.down = QIcon(imgPath)
        
        # Scroll vers le haut
        self.scrollUp = QPushButton()
        self.scrollUp.setIcon(self.up)
        self.scrollUp.setIconSize(QSize(100, 100))
        self.scrollUp.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.MinimumExpanding)
        self.scrollUp.clicked.connect(self.scrollTextUp)
        self.layout.addWidget(self.scrollUp, 0, 8, 1, 1)
        
        # Scroll vers le bas
        self.scrollDown = QPushButton()
        self.scrollDown.setIcon(self.down)
        self.scrollDown.setIconSize(QSize(100, 100))
        self.scrollDown.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.MinimumExpanding)
        self.scrollDown.clicked.connect(self.scrollTextDown)
        self.layout.addWidget(self.scrollDown, 1, 8, 1, 1)
        
    def scrollTextUp(self):
        print("scrollign up")
        self.textDisplay.scrollText("up")
        
    def scrollTextDown(self):
        print("scrolling down")
        self.textDisplay.scrollText("down")