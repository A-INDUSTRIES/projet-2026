from PySide6.QtWidgets import QLabel, QSizePolicy
from PySide6.QtCore import QTimer
from PySide6.QtWebEngineWidgets import QWebEngineView
from ..widgets import LineEdit, TextDisplayWidget, KeyboardWidget, VBoxLayout, PushButton, HBoxLayout, GridLayout
from ..modules.mail import MailManager
from ..modules.settings import SettingsManager
from . import Page

class MessagePage(Page):
    def __init__(self, id, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.message = message

        # Instanciation du layout
        self.setLayout(VBoxLayout(self))
        self.bottomRow = HBoxLayout()

        # Instanciation des widgets
        self.subject = QLabel(message.subject)
        self.sender = QLabel(message.sender)
        self.content = QWebEngineView()
        self.homeButton = PushButton("retour") # A changer pour une icone
        self.respondButton = PushButton("répondre")
        self.deleteButton = PushButton("supprimer")

        #self.content.setReadOnly(True)
        self.content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content.setHtml(message.content)

        # Connection des events
        self.homeButton.clicked.connect(lambda _: self.switch("messages"))
        self.respondButton.clicked.connect(self.respond)

        self.layout().addWidget(self.subject)
        self.layout().addWidget(self.sender)
        self.layout().addWidget(self.content)
        self.bottomRow.addWidget(self.homeButton)
        self.bottomRow.addWidget(self.respondButton)
        self.bottomRow.addWidget(self.deleteButton)
        self.bottomRow.addStretch(1)
        self.layout().addLayout(self.bottomRow)

    def respond(self):
        page = NewMessagePage(subject=f"RE: {self.message.subject}", recepient=self.message.sender)
        self.switch(page)

class NewMessagePage(Page):
    def __init__(self, content="", subject="", recepient="",  *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Instanciation du layout
        self.grid = GridLayout(self)
        self.vbox = VBoxLayout()
        self.bottomRow = HBoxLayout()

        # Instanciation des widgets
        self.subject = LineEdit(placeholderText="Entrez un sujet", text=subject)
        self.subject.setPlaceholderText
        self.recepient = LineEdit(placeholderText="Entrez une adresse mail ou choisissez un contact", text=recepient)
        self.content = TextDisplayWidget(text=content)
        self.homeButton = PushButton("retour") # A changer pour une icone
        self.sendButton = PushButton("envoyer")
        self.keyboard = KeyboardWidget()

        self.content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Connection des events
        self.homeButton.clicked.connect(lambda _: self.switch("messages"))
        self.sendButton.clicked.connect(self.send)

        self.bottomRow.addWidget(self.homeButton)
        self.bottomRow.addWidget(self.sendButton)
        self.bottomRow.addStretch(1)

        self.vbox.addWidget(self.subject)
        self.vbox.addWidget(self.recepient)
        self.vbox.addWidget(self.content)
        self.vbox.addLayout(self.bottomRow)

        self.grid.addLayout(self.vbox, 0, 0, 5, 1)
        self.grid.addWidget(self.keyboard, 5, 0, 10, 1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.resetSendButton)

    def animateSend(self):
        self.sendButton.setText("envoyé!")
        self.sendButton.setFontColor("green")
        self.timer.start(SettingsManager().getSetting("animationSpeed"))

    def resetSendButton(self):
        self.sendButton.setText("envoyer")
        self.sendButton.setFontColor("black")

    def send(self):
        MailManager().send(self.recepient.toPlainText(), self.subject.toPlainText(), self.content.toPlainText())
        self.animateSend()