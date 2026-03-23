from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt

class KeyboardWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        
        self.layout = QGridLayout(self)
        
        # Instanciation des boutons
        self.homeButton = QPushButton("menu") # A changer pour une icone

        # Connection des events
        self.homeButton.clicked.connect(lambda _event: self.switch(parent))

        self.layout.addWidget(self.homeButton, 20, 1, 5, 2)
        
        first_line = list('1234567890')
        second_line = list("azertyuiop")
        third_line = list("qsdfghjklm")
        fourth_line = list("wxcvbn,.:=")
        
        lines = [first_line, second_line, third_line, fourth_line]
        
        for n in range(len(lines)):
            for i in range(len(lines[n])):
                self.lowerLetter = QPushButton(lines[n][i])
                self.lowerLetter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.layout.addWidget(self.lowerLetter, 5*n, i+1, 5, 1)
                self.lowerLetter.clicked.connect(lambda _event, char=lines[n][i]: print(char))
                
        
    def switch(self, parent):
        from ..pages.menu import Menu

        parent.inner = Menu(parent)