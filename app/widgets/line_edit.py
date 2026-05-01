from PySide6.QtGui import QPainter, QColor, QTextCursor
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QTextEdit

class LineEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.ensureCursorVisible()
    
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        metrics = self.fontMetrics()
        lineHeight = metrics.lineSpacing()
        margin = self.document().documentMargin()

        self.setFixedHeight(int(lineHeight + margin * 2))
        
        self.setCursorWidth(0)
        self.cursorVisible = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.blinkCursor)
        self.timer.start(500)
   
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
                pass
            case _:
                self.insertPlainText(char)
    
        self.cursorVisible = True
        self.timer.start()

    # Overload de l'event pour ignorer les 'enter'
    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Return or e.key() == Qt.Key.Key_Enter:
            return
        return super().keyPressEvent(e)