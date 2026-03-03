from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget

class Menu(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        
        self.test = QLabel("MENU")
        self.layout.addWidget(self.test)