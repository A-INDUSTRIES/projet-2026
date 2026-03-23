from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt
from ..widgets.keyboard_widget import KeyboardWidget


class Keyboard(QWidget):
    def __init__(self, parent):
        super().__init__()

        # Instanciation du layout
        self.layout = QGridLayout(self)
        
        # Instanciation du widget clavier
        self.keyboard = KeyboardWidget(parent)
        
        self.layout.addWidget(self.keyboard, 0, 0)

    def switch(self, parent):
        from .menu import Menu

        parent.inner = Menu(parent)