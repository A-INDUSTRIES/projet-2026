from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QObject
from ..modules.settings import SettingsManager

class Settings(QWidget):
    def __init__(self, parent):
        super().__init__()

        # Instanciation du layout
        self.layout = QVBoxLayout(self)

        # Instanciation des widgets
        self.homeButton = QPushButton("menu") # A changer pour une icone
        self.voiceChoice = Setting("voice", "Voix du text-to-speech", ["Femme", "Homme"], [0, 1])

        # Connection des events
        self.homeButton.clicked.connect(lambda _event: self.switch(parent))

        self.layout.addWidget(self.voiceChoice)
        self.layout.addStretch(1)
        self.layout.addWidget(self.homeButton)

    def switch(self, parent):
        from .menu import Menu

        parent.inner = Menu(parent)

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

    def updateButtons(self):
        currentSettingValue = SettingsManager().getSetting(self.name)

        for i, button in enumerate(self.buttons):
            if self.values[i] == currentSettingValue:
                button.setStyleSheet("color:red;")
            else:
                button.setStyleSheet("")