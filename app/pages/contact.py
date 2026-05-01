from PySide6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGridLayout
from PySide6.QtCore import Signal
from ..modules.contacts import ContactsManager, Contact
from ..widgets.keyboard_widget import KeyboardWidget
from ..widgets.line_edit import LineEdit
from ..modules.logger import debug
from ..widgets import Widget
from . import Page

class ContactPage(Page):
    def __init__(self, *args, id=None, name="", email="", **kwargs):
        super().__init__(*args, **kwargs)

        self.isNew = id == None
        self.id = id
        self.name = name
        self.email = email

        # Instanciation du layout
        self.grid = QGridLayout(self)
        self.vbox = QVBoxLayout()
        self.bottomRow = QHBoxLayout()

        # Instanciation des widgets 
        self.homeButton = QPushButton("retour") # A changer pour une icone
        self.title = QLabel("Contact")
        self.nameEdit = Value("Nom", name, "Ecrivez un nom")
        self.emailEdit = Value("Email", email, "Ecrivez une adresse mail")
        self.saveButton = QPushButton("sauvegarder")
        self.keyboard = KeyboardWidget()

        self.title.setObjectName("title")

        # Connection des events
        self.homeButton.clicked.connect(lambda _: self.switch("contacts"))
        self.saveButton.clicked.connect(self.save)
        self.nameEdit.valueChanged.connect(self.setName)
        self.emailEdit.valueChanged.connect(self.setEmail)
        self.keyboard.textUpdated.connect(self.nameEdit.updateText)
        self.keyboard.textUpdated.connect(self.emailEdit.updateText)
        
        self.bottomRow.addWidget(self.homeButton)
        self.bottomRow.addWidget(self.saveButton)
        self.bottomRow.addStretch(1)

        self.vbox.addWidget(self.title)
        self.vbox.addWidget(self.nameEdit)
        self.vbox.addWidget(self.emailEdit)
        self.vbox.addStretch(1)
        self.vbox.addLayout(self.bottomRow)

        self.grid.addLayout(self.vbox, 0, 0, 5, 1)
        self.grid.addWidget(self.keyboard, 5, 0, 10, 1)

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

class Value(Widget):
    valueChanged = Signal(str)

    def __init__(self, name, value, placeholder):
        super().__init__()
        self.editing = False

        self.setLayout(QHBoxLayout(self))

        self.vbox = QVBoxLayout()
        self.nameLabel = QLabel(name)
        self.valueLabel = LineEdit(value)
        self.editButton = QPushButton("modifier")

        self.valueLabel.setPlaceholderText(placeholder)
        self.valueLabel.textChanged.connect(self.valueChange)
        self.editButton.clicked.connect(self.toggleEdit)

        self.vbox.addWidget(self.nameLabel)
        self.vbox.addWidget(self.valueLabel)
        self.layout().addLayout(self.vbox)
        self.layout().addWidget(self.editButton)

    def valueChange(self):
        self.valueChanged.emit(self.valueLabel.toPlainText())

    def toggleEdit(self):
        self.editing = not self.editing
        debug(f"{self.nameLabel.text()} - {self.editing}")

    def updateText(self, text):
        if self.editing:
            self.valueLabel.updateText(text)