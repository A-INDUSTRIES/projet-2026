from PySide6.QtWidgets import QStyleOption, QStyle, QWidget
from PySide6.QtGui import QPainter
from ..widgets import EyeWidget

class Page(QWidget, EyeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paintEvent(self, _):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def switch(self, page):
        self.parent().switch(page)