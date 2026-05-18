from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer
from ..widgets import VBoxLayout, PushButton
from ..modules.eye_tracking import EyeTracking
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

        self.current = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.nextPoint)
        self.timer.setInterval(5000)

    def startCalibration(self):
        self.begin.setText("Calibration en cours")
        self.timer.start()
    
    def nextPoint(self):
        if self.current == 4:
            self.stopCalibration()
            return
        
        positions = ["haut à gauche", "haut à droite", "bas à droite", "bas à gauche"]
        self.instruction.setText(f"Regardez le point rouge en {positions[self.current]}")
        self.window().setPoint(self.current)
        
        QTimer.singleShot(2000, lambda current=self.current: EyeTracking().calibratePoint(current))
        self.current += 1

    def stopCalibration(self):
        self.timer.stop()
        self.current = 0
        self.begin.setText("Calibration terminée")
        self.instruction.setText("")
        self.window().setPoint(-1)