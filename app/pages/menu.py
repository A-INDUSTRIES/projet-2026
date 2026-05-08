from PySide6.QtWidgets import QSizePolicy
from ..widgets import PushButton, HBoxLayout, VBoxLayout
from . import Page

class Menu(Page):
    def __init__(self, *args):
        super().__init__(*args)

        # Instanciation du layout du menu
        self.vlayout = VBoxLayout(self)
        self.buttons = HBoxLayout()

        # Instanciation des boutons 
        self.keyboardButton = PushButton("Clavier")
        self.messagesButton = PushButton("Messages")
        self.contactsButton = PushButton("Contacts")
        self.settingsButton = PushButton("Paramètres")
        self.exitButton = PushButton("Quitter l'application")

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

        self.vlayout.addStretch(1)
        self.vlayout.addLayout(self.buttons, 1)
        self.vlayout.addStretch(1)