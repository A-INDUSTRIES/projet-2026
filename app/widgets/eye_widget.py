from PySide6.QtCore import QPoint
from enum import Enum

class EyeAction(Enum):
    NONE = 1
    CLICK = 2
    GAZE = 3

class EyeWidget():
    def eyeEvent(self, position: QPoint):
        for object in self.children():
            if isinstance(object, EyeWidget):
                rect = object.geometry()
                print(position, rect)
                if rect.contains(position):
                    print("contains")
                    return object.eyeEvent(position)
        return EyeAction.NONE