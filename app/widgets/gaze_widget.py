from PySide6.QtCore import Qt, QTimer, Signal
from typing import override
from threading import Thread
from ..modules.gaze import GazeTyping
from . import Widget, EyeAction

class GazeWidget(Widget):
    words = Signal(list)

    def __init__(self):
        super().__init__()
        self.toggled = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.input)

        self.toggle()

    @override
    def eyeEvent(self, position):
        if self.toggled:
            pos = self.mapFrom(self.window(), position)
            pos = [pos.x()/self.width(), pos.y()/self.height()]
            GazeTyping().point(pos)
            self.timer.start(500)
            return EyeAction.GAZE
        else:
            return super().eyeEvent(position)
        
    def input(self):
        self.timer.stop()
        words = GazeTyping().end()
        self.words.emit(words)

    def toggle(self):
        self.toggled = not self.toggled
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, on=self.toggled) 
        return self.toggled