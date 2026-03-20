from PySide6.QtWidgets import QGridLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt
from . import menu # Import du package menu entier pour éviter une erreur d'import circulaire

class Settings(QWidget):
    def __init__(self, parent):
        super().__init__()

        # Instanciation du layout
        self.layout = QGridLayout(self)

        # Instanciation des widgets
        self.homeButton = QPushButton("menu") # A changer pour une icone

        self._test = QLabel("Paramètres")
        self._test.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connection des events
        self.homeButton.clicked.connect(lambda _event: self.switch(parent, menu.Menu(parent)))

        self.layout.addWidget(self._test, 0, 0)
        self.layout.addWidget(self.homeButton, 1, 0)

    def switch(self, parent, page):
        parent.inner = page