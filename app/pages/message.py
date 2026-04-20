
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout, QLineEdit, QTextEdit, QSizePolicy
from PySide6.QtCore import Qt, Signal
from . import Page
from app.modules.logger import debug
from app.modules.messages import Message

class MessagePage(Page):
    def __init__(self, id, message, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.isNew = id == None
        self.id = id
        self.message = message

        # Instanciation du layout
        self.setLayout(QVBoxLayout(self))
        self.bottomRow = QHBoxLayout()

        # Instanciation des widgets
        self.subject = QLabel(message.subject)
        self.sender = QLabel(message.sender)
        self.content = QTextEdit(html=message.content)
        self.homeButton = QPushButton("retour") # A changer pour une icone
        self.respondButton = QPushButton("répondre")
        self.deleteButton = QPushButton("supprimer")

        self.content.setReadOnly(True)
        self.content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Connection des events
        self.homeButton.clicked.connect(lambda _: self.switch("messages"))

        self.layout().addWidget(self.subject)
        self.layout().addWidget(self.sender)
        self.layout().addWidget(self.content)
        self.bottomRow.addWidget(self.homeButton)
        self.bottomRow.addWidget(self.respondButton)
        self.bottomRow.addWidget(self.deleteButton)
        self.bottomRow.addStretch(1)
        self.layout().addLayout(self.bottomRow)