from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QPushButton, QSizePolicy
from . import Page

class Menu(Page):
    def __init__(self, *args):
        super().__init__(*args)

        # Instanciation du layout du menu
        self.layout = QVBoxLayout(self)
        self.buttons = QHBoxLayout()

        # Instanciation des boutons 
        self.keyboardButton = QPushButton("Clavier")
        self.messagesButton = QPushButton("Messages")
        self.contactsButton = QPushButton("Contacts")
        self.settingsButton = QPushButton("Paramètres")
        self.exitButton     = QPushButton("Quitter l'application")

        # Connection des events
        self.keyboardButton.clicked.connect(lambda _event: self.switch("keyboard"))
        self.messagesButton.clicked.connect(lambda _event: self.switch("messages"))
        self.contactsButton.clicked.connect(lambda _event: self.switch("contacts"))
        self.settingsButton.clicked.connect(lambda _event: self.switch("settings"))
        self.exitButton.clicked.connect(lambda _event: self.parent().close())

        # Modifier les boutons pour qu'ils s'agrandissent
        self.keyboardButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.messagesButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contactsButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.settingsButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.exitButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Ajout des boutons dans le layout
        self.buttons.addWidget(self.keyboardButton)
        self.buttons.addWidget(self.messagesButton)
        self.buttons.addWidget(self.contactsButton)
        self.buttons.addWidget(self.settingsButton)
        self.buttons.addWidget(self.exitButton)

        self.layout.addStretch(1)
        self.layout.addLayout(self.buttons, 1)
        self.layout.addStretch(1)