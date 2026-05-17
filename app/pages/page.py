from PySide6.QtWidgets import QStyleOption, QStyle
from PySide6.QtGui import QPainter
from ..widgets import Widget

class Page(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def showEvent(self, event):
        self.layout().setContentsMargins(100, 100, 100, 100)
        return super().showEvent(event)

    def paintEvent(self, _):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def switch(self, page):
        self.parent().switch(page)