from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QPoint
from enum import Enum

class EyeAction(Enum):
    NONE = 1
    CLICK = 2
    GAZE = 3

class EyeWidget():
    def eyeEvent(self, position: QPoint):
        if isinstance(self.layout(), EyeWidget):
            return self.layout().eyeEvent(position)
        return EyeAction.NONE
    
class Widget(QWidget, EyeWidget):
    pass