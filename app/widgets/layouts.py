from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PySide6.QtCore import QPoint
from typing import override
from . import EyeWidget, EyeAction

class HBoxLayout(QHBoxLayout, EyeWidget):
    @override 
    def eyeEvent(self, position: QPoint):
        for i in range(self.count()):
            object = self.itemAt(i).widget()
            if isinstance(object, EyeWidget):
                rect = object.geometry()
                if rect.contains(position):
                    return object.eyeEvent(position)
        return EyeAction.NONE

class VBoxLayout(QVBoxLayout, EyeWidget):
    @override 
    def eyeEvent(self, position: QPoint):
        for i in range(self.count()):
            object = self.itemAt(i).widget()
            if isinstance(object, EyeWidget):
                rect = object.geometry()
                if rect.contains(position):
                    return object.eyeEvent(position)
        return EyeAction.NONE

class GridLayout(QGridLayout, EyeWidget):
    @override 
    def eyeEvent(self, position: QPoint):
        for i in range(self.count()):
            object = self.itemAt(i).widget()
            if isinstance(object, EyeWidget):
                rect = object.geometry()
                if rect.contains(position):
                    return object.eyeEvent(position)
        return EyeAction.NONE