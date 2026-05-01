from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QScrollArea, QSizePolicy, QStyle, QStyleOption, QVBoxLayout
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter
from ..modules.contacts import ContactsManager, Contact as C
from ..widgets import Widget
from . import ContactPage, Page

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
        self.contactsContent = Widget()
        self.contactsLayout = QVBoxLayout(self.contactsContent)
        self.createContactButton = QPushButton("Ajouter un contact")

        self.title.setObjectName("title")
        self.contactsContent.setObjectName("contacts")
        self.contactsLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.contacts.setWidget(self.contactsContent)
        self.contacts.setWidgetResizable(True)
        self.contacts.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)

        # Connection des events
        self.homeButton.clicked.connect(lambda _: self.switch("menu"))
        self.createContactButton.clicked.connect(self.createContact)

        for id, contact in ContactsManager().getContacts().items():
            widget = Contact(id, contact)
            widget.openEdit.connect(self.editContact)
            widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            widget.deleted.connect(lambda widget=widget: self.deleteContact(widget))
            self.contactsLayout.addWidget(widget)

        self.layout.addWidget(self.title)
        self.contactsLayout.addWidget(self.createContactButton)
        self.layout.addWidget(self.contacts)
        self.bottomRow.addWidget(self.homeButton)
        self.bottomRow.addStretch(1)
        self.layout.addLayout(self.bottomRow)

    def createContact(self):
        page = ContactPage(parent = self.parent())
        self.switch(page)

    def editContact(self, id, contact):
        page = ContactPage(id=id, name=contact.name, email=contact.email, parent = self.parent())
        self.switch(page)

    def deleteContact(self, widget):
        self.contactsLayout.removeWidget(widget)
        widget.deleteLater()

class Contact(Widget):
    openEdit = Signal(int, C)
    deleted = Signal()

    def __init__(self, id, contact, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = id
        self.contact = contact

        self.name = QLabel(contact.name)
        self.email = QLabel(contact.email)
        self.editButton = QPushButton("modifier")
        self.deleteButton = QPushButton("supprimer")

        self.layout = QHBoxLayout(self)
        self.info = QVBoxLayout()

        self.editButton.clicked.connect(self.edit)
        self.deleteButton.clicked.connect(self.delete)

        self.info.addWidget(self.name)
        self.info.addWidget(self.email)
        self.layout.addLayout(self.info)
        self.layout.addStretch(1)
        self.layout.addWidget(self.editButton)
        self.layout.addWidget(self.deleteButton)

    def edit(self):
        self.openEdit.emit(self.id, self.contact)

    def delete(self):
        ContactsManager().deleteContact(self.id)
        self.deleted.emit()

    def paintEvent(self, _):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)