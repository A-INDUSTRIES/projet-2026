from PySide6.QtWidgets import QGridLayout, QPushButton, QLabel
from PySide6.QtCore import Qt
from . import Page

class ContactPage(Page):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Instanciation du layout
        self.layout = QGridLayout(self)

        # Instanciation des boutons
        self.homeButton = QPushButton("retour") # A changer pour une icone
        
        self._test = QLabel("Contact")
        self._test.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Connection des events
        self.homeButton.clicked.connect(lambda _: self.switch("contacts"))

        self.layout.addWidget(self._test, 0, 0)
        self.layout.addWidget(self.homeButton, 1, 0)