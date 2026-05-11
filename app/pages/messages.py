from PySide6.QtWidgets import QLabel, QSizePolicy, QStyleOption, QStyle
from PySide6.QtCore import Qt, Signal, QThread, Slot
from PySide6.QtGui import QPainter
from ..widgets import VBoxLayout, HBoxLayout, PushButton, ScrollArea, Widget
from ..modules.mail import MailManager
from ..modules.messages import Message as M
from . import MessagePage, NewMessagePage, Page

class Messages(Page):
    def __init__(self, *args):
        super().__init__(*args)

        # Instanciation du layout
        self.setLayout(VBoxLayout(self))

        # Instanciation des widgets
        self.title = QLabel("Messages")
        self.homeButton = PushButton("menu") # A changer pour une icone
        self.bottomRow = HBoxLayout()
        self.messages = ScrollArea()
        self.messagesContent = Widget()
        self.messagesLayout = VBoxLayout(self.messagesContent)

        self.title.setObjectName("title")
        self.messagesContent.setObjectName("messages")
        self.messagesLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages.setWidget(self.messagesContent)
        self.messages.setWidgetResizable(True)
        self.messages.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)

        # Connection des events
        self.homeButton.clicked.connect(lambda _: self.switch("menu"))

        self.layout().addWidget(self.title)
        self.layout().addWidget(self.messages)
        self.bottomRow.addWidget(self.homeButton)
        self.bottomRow.addStretch(1)
        self.layout().addLayout(self.bottomRow)

        self.loader = Worker()
        self.loader.loaded.connect(self.loadMessages)
        self.loader.start()

    def loadMessages(self, messages):
        for message in messages:
            widget = Message(message)
            widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            widget.openView.connect(self.openMessage)
            widget.deleted.connect(lambda widget=widget: self.deleteMail(widget))
            widget.respondView.connect(self.respondMessage)
            self.messagesLayout.addWidget(widget)

    def deleteMail(self, widget):
        self.messagesLayout.removeWidget(widget)
        widget.deleteLater()

    def openMessage(self, message):
        page = MessagePage(message)
        self.switch(page)
    
    def respondMessage(self, message):
        page = NewMessagePage(subject=f"RE: {message.subject}", recepient=message.sender)
        self.switch(page)

class Message(Widget):
    openView = Signal(M)
    respondView = Signal(M)
    deleted = Signal()

    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

        self.subject = QLabel(message.subject)
        self.sender = QLabel(f"de: {message.sender}")
        self.openButton = PushButton("lire")
        self.respondButton = PushButton("répondre")
        self.deleteButton = PushButton("supprimer")

        self.setLayout(HBoxLayout(self))
        self.info = VBoxLayout()

        self.openButton.clicked.connect(self.open)
        self.deleteButton.clicked.connect(self.delete)
        self.respondButton.clicked.connect(self.respond)

        self.info.addWidget(self.subject)
        self.info.addWidget(self.sender)
        self.layout().addLayout(self.info)
        self.layout().addStretch(1)
        self.layout().addWidget(self.openButton)
        self.layout().addWidget(self.respondButton)
        self.layout().addWidget(self.deleteButton)

    def open(self):
        self.openView.emit(self.message)

    def delete(self):
        MailManager().delete(self.message.id())
        self.deleted.emit()

    def respond(self):
        self.respondView.emit(self.message)

    def paintEvent(self, _):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

class Worker(QThread):
    loaded = Signal(list)

    @Slot()
    def run(self):
        result = MailManager().receive()
        self.loaded.emit(result)