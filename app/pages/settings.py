from PySide6.QtWidgets import QLabel, QStyleOption, QStyle
from PySide6.QtGui import QPainter
from ..widgets import Widget, PushButton, HBoxLayout, VBoxLayout
from ..modules.settings import SettingsManager
from . import Page

class Settings(Page):
    def __init__(self, *args):
        super().__init__(*args)

        # Instanciation du layout
        self.setLayout(VBoxLayout(self))

        # Instanciation des widgets
        self.homeButton = PushButton("menu") # A changer pour une icone
        self.calibrate = PushButton("Recalibrer le tracking")
        self.fontSize = Setting("fontSize", "Taille de la police d'écriture", ["Très petite", "Petite", "Normale", "Grande", "Très grande"], [10, 18, 24, 32, 40])
        self.animationSpeed = Setting("animationSpeed", "Vitesse des animations", ["Lent", "Normal", "Rapide"], [2000, 1000, 500])
        self.inputSpeed = Setting("inputSpeed", "Délai d'activation des touches", ["Long", "Normal", "Rapide"], [2000, 1000, 500])
        self.bottomRow = HBoxLayout()

        # Connection des events
        self.homeButton.clicked.connect(lambda _event: self.switch("menu"))

        self.layout().addWidget(self.fontSize)
        self.layout().addWidget(self.animationSpeed)
        self.layout().addWidget(self.inputSpeed)
        self.layout().addStretch(1)
        self.bottomRow.addWidget(self.homeButton)
        self.bottomRow.addWidget(self.calibrate)
        self.bottomRow.addStretch(1)
        self.layout().addLayout(self.bottomRow)
    
    def updateStyle(self):
        self.parent().updateStyle()

    def updateInputSpeed(self):
        self.fontSize.updateInputSpeed()
        self.animationSpeed.updateInputSpeed()
        self.inputSpeed.updateInputSpeed()
        self.homeButton.updateInputSpeed()
        self.calibrate.updateInputSpeed()

class Setting(Widget):
    def __init__(self, name, description, options, values):
        super().__init__()
        self.name = name
        self.values = values

        self.setLayout(HBoxLayout(self))

        self.description = QLabel(description)

        self.layout().addWidget(self.description)
        self.layout().addStretch(1)

        self.buttons = []
        for i, option in enumerate(options):
            button = PushButton(option)
            button.clicked.connect(lambda _event, value=values[i]: self.setValue(value))
            self.layout().addWidget(button)
            self.buttons.append(button)
        
        self.updateButtons()

    def setValue(self, value):
        SettingsManager().setSetting(self.name, value)
        self.updateButtons()
        self.parent().updateStyle()
        self.parent().updateInputSpeed()

    def updateButtons(self):
        currentSettingValue = SettingsManager().getSetting(self.name)

        for i, button in enumerate(self.buttons):
            if self.values[i] == currentSettingValue:
                button.setFontColor("red")
            else:
                button.setFontColor("black")
    
    def updateInputSpeed(self):
        for button in self.buttons:
            button.updateInputSpeed()

    def paintEvent(self, _):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)