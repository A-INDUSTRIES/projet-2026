from PySide6.QtGui import QTextCursor, QPainter, QColor
from PySide6.QtWidgets import QTextEdit, QScrollBar
from PySide6.QtCore import QTimer
from ..modules.logger import warn

class TextDisplayWidget(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.setPlaceholderText("Ecrivez quelque chose")
        self.setTextCursor(self.textCursor())
        self.ensureCursorVisible()
        
    
    # Modifier la scroll bar et la rendre utilisable avec les yeux
        self.scrollbar = QScrollBar()
        self.setVerticalScrollBar(self.scrollbar)
        
    # Pour avoir un curseur visible en permanence, même lorsque le focus est sur le clavier
        self.setCursorWidth(0)
        self.cursorVisible = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.blinkCursor)
        self.timer.start(500)
        
        
    def scrollText(self, type):
        min_step = (self.scrollbar.maximum() - self.scrollbar.minimum())//10
        match type:
            case "up":
                step = abs(self.scrollbar.value() - self.scrollbar.minimum())//3
                step = max(min_step, step)
                new_val = max(self.scrollbar.minimum(), self.scrollbar.value() - step)
                self.scrollbar.setValue(new_val)
            case "down":
                step = abs(self.scrollbar.maximum() - self.scrollbar.value())//3
                step = max(min_step, step)
                new_val = min(self.scrollbar.maximum(), self.scrollbar.value() + step)
                self.scrollbar.setValue(new_val)
            case _:
                warn("Invalid scroll type for TextDisplayWidget")
    
    
    def blinkCursor(self):
        self.cursorVisible = not self.cursorVisible
        self.viewport().update()
        
    
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.cursorVisible:
            return
        
        cursor = self.textCursor()
        rect = self.cursorRect(cursor)
        
        painter = QPainter(self.viewport())
        painter.fillRect(rect.x(), rect.y(), 2, rect.height(), QColor("black"))
    
    
    # Gestion des inputs clavier
    def updateText(self, char):
        match char:
            case "backspace":
                self.textCursor().deletePreviousChar()
                
            case "reset":
                self.setText("")
                
            case "left":
                self.moveCursor(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor)
            
            case "right":
                self.moveCursor(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor)
                
            case "enter":
                self.insertPlainText("\n")
                
            case _:
                self.insertPlainText(char)
    
        self.cursorVisible = True
        self.timer.start()