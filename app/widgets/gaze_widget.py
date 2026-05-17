from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QPen
from typing import override
from threading import Thread
from ..modules.gaze import GazeTyping
from . import Widget, EyeAction

class GazeWidget(Widget):
    words = Signal(list)

    def __init__(self):
        super().__init__()
        self.toggled = False
        self.anchorPoint = None
        self.inputs = False

        self.points = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.toggleInput)

        self.toggle()

    @override
    def eyeEvent(self, position):
        if not self.toggled:
            return super().eyeEvent(position)

        pos = self.mapFrom(self.window(), position)

        self.anchor(pos)

        if self.inputs:
            self.points.append(pos)
            pos = [pos.x()/self.width(), pos.y()/self.height()]
            GazeTyping().point(pos)

        return EyeAction.GAZE
    
    def anchor(self, position):
        if self.anchorPoint == None or (position - self.anchorPoint).manhattanLength() >= 50:
            self.anchorPoint = position
            self.timer.start(1000)

    def toggleInput(self):
        if self.inputs:
            self.timer.stop()
            self.input()
        self.inputs = not self.inputs
        self.anchorPoint = None
        
    def input(self):
        self.points = []
        words = GazeTyping().end()
        self.words.emit(words)
    
    def toggle(self):
        self.toggled = not self.toggled
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=self.toggled) 
        return self.toggled
    
    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen("gray")
        pen.setWidth(10)
        painter.setPen(pen)

        painter.drawPoints(self.points)
        return super().paintEvent(event)