from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import QTimer, QPropertyAnimation, Property
from typing import override
from . import EyeWidget, EyeAction

class PushButton(QPushButton, EyeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._value = 0
        
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)

        self.timer = QTimer()
        self.timer.timeout.connect(self.stopAnimation)

    @Property(int)
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
        self.updateStyle()

    def updateStyle(self):
        if self._value == 0:
            self.setStyleSheet("")
        else:
            self.setStyleSheet(f"""
            PushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                            stop:0 #ADB5BD,
                            stop:{self.value/100} #ADB5BD,
                            stop:{self.value/100 + 0.01} #CED4DA,
                            stop:1 #CED4DA);
            }}
            """)
        
    def stopAnimation(self):
        self.animation.stop()
        self._value = 0
        self.updateStyle()

    @override
    def eyeEvent(self, _position):
        if self.animation.state() == QPropertyAnimation.State.Stopped:
            self.animation.start()

        if self._value >= 99:
            self.timer.stop()
            self.stopAnimation()
            self.click()
            return EyeAction.CLICK
        
        self.timer.start(100)
        return EyeAction.GAZE