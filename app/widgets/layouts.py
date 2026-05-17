from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QScrollArea, QLayout
from PySide6.QtCore import QPoint
from typing import override
from . import EyeWidget, EyeAction

class HBoxLayout(QHBoxLayout, EyeWidget):
    @override 
    def eyeEvent(self, position: QPoint):
        return layoutEyeEvent(self, position)

class VBoxLayout(QVBoxLayout, EyeWidget):
    @override 
    def eyeEvent(self, position: QPoint):
        return layoutEyeEvent(self, position)

class GridLayout(QGridLayout, EyeWidget):
    @override 
    def eyeEvent(self, position: QPoint):
        return layoutEyeEvent(self, position)
    
class ScrollArea(QScrollArea, EyeWidget):
    @override
    def eyeEvent(self, position):
        widget = self.widget()
        if isinstance(widget, EyeWidget):
            return widget.eyeEvent(position)
        return EyeAction.NONE
    
def layoutEyeEvent(self: QLayout, position):
    for i in range(self.count()):
        object = self.itemAt(i)
        if (widget:=object.widget()) and isinstance(widget, EyeWidget):
            rect = widget.rect().translated(widget.mapTo(self.parentWidget().window(), QPoint(0, 0)))
            if rect.contains(position):
                ret = widget.eyeEvent(position)
                if not ret == EyeAction.NONE:
                    return ret
        elif (layout:=object.layout()) and isinstance(layout, EyeWidget):
            rect = layout.geometry()
            if rect.contains(position):
                ret = layout.eyeEvent(position)
                if not ret == EyeAction.NONE:
                    return ret
    return EyeAction.NONE