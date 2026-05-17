from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from ..widgets import VBoxLayout, PushButton
from . import Page

from time import sleep

class Calibration(Page):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vlayout = VBoxLayout(self)
        self.instruction = QLabel("")
        self.begin = PushButton("Commencer la calibration")
        self.homeButton = PushButton("menu")

        self.step = 0
        self.begin.clicked.connect(self.startCalibration)
        self.homeButton.clicked.connect(lambda _: self.switch("menu"))
        self.instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.vlayout.addWidget(self.instruction)
        self.vlayout.addWidget(self.begin)
        self.vlayout.addWidget(self.homeButton)

    def startCalibration(self):
        positions = ["haut à gauche", "haut à droite", "bas à droite", "bas à gauche"]
        self.begin.setText("Calibration en cours")

        for i in range(4):
            self.instruction.setText(f"Regardez le point rouge en {positions[i]}")
            self.window().setPoint(i)
            # Faire les appels vers le module eye_tracking

        self.begin.setText("Calibration finie")