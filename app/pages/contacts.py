from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QStyle, QStyleOption, QVBoxLayout, QWidget
from app.modules.contacts import Contact as C
from app.modules.contacts import ContactsManager
from . import Page

class Contacts(Page):
    def __init__(self, *args):
        super().__init__(*args)

        # Instanciation du layout
        self.layout = QVBoxLayout(self)

        # Instanciation des widgets
        self.title = QLabel("Contacts")
        self.homeButton = QPushButton("menu") # A changer pour une icone
        self.bottomRow = QHBoxLayout()
        self.contacts = QScrollArea()

        self.contacts.setLayout(QVBoxLayout())
        self.contacts.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)

        # Connection des events
        self.homeButton.clicked.connect(lambda _event: self.switch("menu"))

        test = Contact(C({"name": "test", "email": "test@gmail.com"}))
        self.contacts.layout().addWidget(test)

        for contact in ContactsManager().getContacts():
            widget = Contact(contact)
            self.contacts.layout().addWidget(widget)

        self.createContact = QPushButton("Ajouter un contact")
        self.contacts.layout().addWidget(self.createContact)
        self.contacts.layout().addStretch(1)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.contacts)
        self.bottomRow.addWidget(self.homeButton)
        self.bottomRow.addStretch(1)
        self.layout.addLayout(self.bottomRow)

class Contact(QWidget):
    def __init__(self, contact):
        super().__init__()
        self.name = QLabel(contact.name)
        self.email = QLabel(contact.email)
        self.edit = QPushButton("modifier")
        self.delete = QPushButton("supprimer")

        self.layout = QHBoxLayout(self)
        self.info = QVBoxLayout()

        self.info.addWidget(self.name)
        self.info.addWidget(self.email)
        self.layout.addLayout(self.info)
        self.layout.addStretch(1)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.delete)

    def paintEvent(self, _):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)