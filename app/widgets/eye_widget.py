from PySide6.QtCore import QPoint
from enum import Enum

class EyeAction(Enum):
    NONE = 1
    CLICK = 2
    GAZE = 3

class EyeWidget():
    def eyeEvent(self, position: QPoint):
        for i in range(self.layout().count()):
            object = self.layout().itemAt(i)
            if isinstance(object, EyeWidget):
                rect = object.geometry()
                if rect.contains(position):
                    return object.eyeEvent(position)
        return EyeAction.NONE