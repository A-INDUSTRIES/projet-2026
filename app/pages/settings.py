from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout
from ..modules.settings import SettingsManager
from . import Page

class Settings(Page):
    def __init__(self, *args):
        super().__init__(*args)

        # Instanciation du layout
        self.layout = QVBoxLayout(self)

        # Instanciation des widgets
        self.homeButton = QPushButton("menu") # A changer pour une icone
        self.voiceChoice = Setting("fontSize", "Taille de la police d'écriture", ["Très petite", "Petite", "Normale", "Grande", "Très grande"], [10, 12, 16, 20, 22])

        # Connection des events
        self.homeButton.clicked.connect(lambda _event: self.switch("menu"))

        self.layout.addWidget(self.voiceChoice)
        self.layout.addStretch(1)
        self.layout.addWidget(self.homeButton)
    
    def updateStyle(self):
        self.parent().updateStyle()

class Setting(QWidget):
    def __init__(self, name, description, options, values):
        super().__init__()
        self.name = name
        self.values = values

        self.layout = QHBoxLayout(self)

        self.description = QLabel(description)

        self.layout.addWidget(self.description)
        self.layout.addStretch(1)

        self.buttons = []
        for i, option in enumerate(options):
            button = QPushButton(option)
            button.clicked.connect(lambda _event, value=values[i]: self.setValue(value))
            self.layout.addWidget(button)
            self.buttons.append(button)
        
        self.updateButtons()

    def setValue(self, value):
        SettingsManager().setSetting(self.name, value)
        self.updateButtons()
        self.parent().updateStyle()

    def updateButtons(self):
        currentSettingValue = SettingsManager().getSetting(self.name)

        for i, button in enumerate(self.buttons):
            if self.values[i] == currentSettingValue:
                button.setStyleSheet("color:red;")
            else:
                button.setStyleSheet("")