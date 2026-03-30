from PySide6.QtWidgets import QWidget, QStyleOption, QStyle
from PySide6.QtGui import QPainter

class Page(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def switch(self, page: str | QWidget):
        if isinstance(page, str):
            self.parent.switch(page)
        else:
            self.parent.switch(instance=page)
    
    def paintEvent(self, _event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)