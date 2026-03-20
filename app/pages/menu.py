from PySide6.QtWidgets import QHBoxLayout, QWidget, QPushButton
from .keyboard import Keyboard
from .messages import Messages
from .contacts import Contacts
from .settings import Settings

class Menu(QWidget):
    def __init__(self, parent):
        super().__init__()

        # Instanciation du layout du menu
        self.layout = QHBoxLayout(self)

        # Instanciation des boutons 
        self.keyboardButton = QPushButton("Clavier")
        self.messagesButton = QPushButton("Messages")
        self.contactsButton = QPushButton("Contacts")
        self.settingsButton = QPushButton("Paramètres")

        # Connection des events
        self.keyboardButton.clicked.connect(lambda _event: self._switch(parent, Keyboard(parent)))
        self.messagesButton.clicked.connect(lambda _event: self._switch(parent, Messages(parent)))
        self.contactsButton.clicked.connect(lambda _event: self._switch(parent, Contacts(parent)))
        self.settingsButton.clicked.connect(lambda _event: self._switch(parent, Settings(parent)))

        # Ajout des boutons dans le layout
        self.layout.addWidget(self.keyboardButton)
        self.layout.addWidget(self.messagesButton)
        self.layout.addWidget(self.contactsButton)
        self.layout.addWidget(self.settingsButton)

    def _switch(self, parent, page):
        parent.inner = page