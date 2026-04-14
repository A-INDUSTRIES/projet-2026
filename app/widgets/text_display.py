from PySide6.QtCore import QSize, QTimer
from PySide6.QtGui import QIcon, QTextCursor, QPainter, QColor
from PySide6.QtWidgets import QTextEdit, QScrollBar

class TextDisplayWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        
        self.setPlaceholderText("Ecrivez quelque chose")
        self.setTextCursor(self.textCursor())
        self.ensureCursorVisible()
        
    
    # Modifier la scroll bar et la rendre utilisable avec les yeux
        self.scrollbar = QScrollBar()
        self.setVerticalScrollBar(self.scrollbar)
        self.scrollVal = self.scrollbar.value()
        
    # Pour avoir un curseur visible en permanence, même lorsque le focus est sur le clavier
        self.setCursorWidth(0)
        self.cursorVisible = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.blinkCursor)
        self.timer.start(500)
        
        
    def scrollText(self, type):
        match type:
            case "up":
                self.scrollVal = min(self.scrollbar.value(), max(abs(self.scrollbar.value() - self.scrollbar.minimum())//3, self.scrollbar.maximum()//4))
                self.scrollbar.setValue(self.scrollVal)
            case "down":
                self.scrollVal = max(self.scrollbar.value(), max(abs(self.scrollbar.value() - self.scrollbar.maximum())//3, self.scrollbar.maximum()//4))
                self.scrollbar.setValue(self.scrollVal)
            case _:
                pass
    
    
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
                
            case _:
                self.insertPlainText(char)
    
        self.cursorVisible = True
        self.timer.start()