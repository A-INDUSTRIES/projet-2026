from PySide6.QtWidgets import QWidget, QStyleOption, QStyle
from PySide6.QtGui import QPainter
from PySide6.QtCore import QPoint
from enum import Enum

class EyeAction(Enum):
    NONE = 1
    CLICK = 2
    GAZE = 3

class Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def paintEvent(self, _):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def eyeEvent(self, position: QPoint):
        for object in self.layout().children():
            if isinstance(object, Widget):
                rect = object.geometry()
                if rect.contains(position):
                    return object.eyeEvent(position)
        return EyeAction.NONE