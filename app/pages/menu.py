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
        self.exitButton     = QPushButton("Quitter l'application")

        # Connection des events
        self.keyboardButton.clicked.connect(lambda _event: self._switch(parent, Keyboard(parent)))
        self.messagesButton.clicked.connect(lambda _event: self._switch(parent, Messages(parent)))
        self.contactsButton.clicked.connect(lambda _event: self._switch(parent, Contacts(parent)))
        self.settingsButton.clicked.connect(lambda _event: self._switch(parent, Settings(parent)))
        self.exitButton.clicked.connect(lambda _event: parent.close())

        # Ajout des boutons dans le layout
        self.layout.addWidget(self.keyboardButton)
        self.layout.addWidget(self.messagesButton)
        self.layout.addWidget(self.contactsButton)
        self.layout.addWidget(self.settingsButton)
        self.layout.addWidget(self.exitButton)

    def _switch(self, parent, page):
        parent.inner = page