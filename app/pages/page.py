from PySide6.QtWidgets import QWidget, QStyleOption, QStyle
from PySide6.QtGui import QPainter

class Page(QWidget):
    def __init__(self):
        super().__init__()

    def switch(self, page):
        self.parent().switch(page)
    
    def paintEvent(self, _):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)