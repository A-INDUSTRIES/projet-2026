from PySide6.QtWidgets import QGridLayout
from ..widgets.keyboard_widget import KeyboardWidget
from . import Page

class Keyboard(Page):
    def __init__(self, *args):
        super().__init__(*args)

        # Instanciation du layout
        self.layout = QGridLayout(self)
        
        # Instanciation du widget clavier
        self.keyboard = KeyboardWidget()
        
        self.layout.addWidget(self.keyboard, 0, 0)