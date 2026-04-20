from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget, QHBoxLayout, QLineEdit
from PySide6.QtCore import Qt, Signal
from . import Page
from app.modules.logger import debug
from app.modules.contacts import ContactsManager, Contact

class ContactPage(Page):
    def __init__(self, *args, id=None, name="", email="", **kwargs):
        super().__init__(*args, **kwargs)

        self.isNew = id == None
        self.id = id
        self.name = name
        self.email = email

        # Instanciation du layout
        self.setLayout(QVBoxLayout(self))
        self.bottomRow = QHBoxLayout()

        # Instanciation des widgets 
        self.homeButton = QPushButton("retour") # A changer pour une icone
        self.title = QLabel("Contact")
        self.nameEdit = Value("Nom", name, "Ecrivez un nom")
        self.emailEdit = Value("Email", email, "Ecrivez une adresse mail")
        self.saveButton = QPushButton("sauvegarder")

        self.title.setObjectName("title")

        # Connection des events
        self.homeButton.clicked.connect(lambda _: self.switch("contacts"))
        self.saveButton.clicked.connect(self.save)
        self.nameEdit.valueChanged.connect(self.setName)
        self.emailEdit.valueChanged.connect(self.setEmail)

        self.layout().addWidget(self.title)
        self.layout().addWidget(self.nameEdit)
        self.layout().addWidget(self.emailEdit)
        self.layout().addStretch(1)
        self.bottomRow.addWidget(self.homeButton)
        self.bottomRow.addWidget(self.saveButton)
        self.bottomRow.addStretch(1)
        self.layout().addLayout(self.bottomRow)

    def save(self):
        contact = Contact(name=self.name, email=self.email)
        if self.isNew:
            ContactsManager().createContact(contact)
        else:
            ContactsManager().editContact(self.id, contact)

    def setName(self, text):
        self.name = text

    def setEmail(self, text):
        self.email = text

class Value(QWidget):
    valueChanged = Signal(str)

    def __init__(self, name, value, placeholder):
        super().__init__()
        self.setLayout(QHBoxLayout(self))

        self.vbox = QVBoxLayout()
        self.nameLabel = QLabel(name)
        self.valueLabel = QLineEdit(value)
        self.editButton = QPushButton("modifier")

        self.valueLabel.setPlaceholderText(placeholder)
        self.valueLabel.textChanged.connect(self.valueChange)

        self.vbox.addWidget(self.nameLabel)
        self.vbox.addWidget(self.valueLabel)
        self.layout().addLayout(self.vbox)
        self.layout().addWidget(self.editButton)

    def valueChange(self, text):
        self.valueChanged.emit(text)