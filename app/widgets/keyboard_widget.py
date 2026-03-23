from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from ..modules.tts import VoiceEngine

class KeyboardWidget(QWidget):    
    def __init__(self, parent):
        super().__init__()
        
        # Texte écrit sur le clavier
        self.text = ""
        
        # Gestion des majuscules avec Caps Lock et Shift
        self.cpslock = False
        self.shift = False
        
        # Initialisation du layout en grille
        self.layout = QGridLayout(self)
                
        # Grandes lignes principales du clavier : 10 x 4
        first_line = list('1234567890')
        second_line = list("azertyuiop")
        third_line = list("qsdfghjklm")
        fourth_line = list("wxcvbn,.:=")
        lines = [first_line, second_line, third_line, fourth_line]
        
        for n in range(len(lines)):
            for i in range(len(lines[n])):
                self.lowerLetter = QPushButton(lines[n][i])
                self.lowerLetter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.layout.addWidget(self.lowerLetter, n+1, 3+2*i, 1, 2)
                self.lowerLetter.clicked.connect(lambda _event, char=lines[n][i]: self.handleCharacterButton(char))

        # Boutons spéciaux
        # Retour au menu
        self.homeButton = QPushButton("menu") # A changer pour une icone
        self.homeButton.clicked.connect(lambda _event: self.switch(parent))
        self.homeButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.homeButton, 5, 3, 1, 4)
        
        # Text-to-Speech
        # NE RESTERA PAS DANS LE CLAVIER, FONCTIONNALITE TEST
        self.tts = QPushButton("Text-to\nSpeech")
        self.tts.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.tts, 0, 22, 1, 4)
        self.tts.clicked.connect(lambda _event: self.handleTextToSpeech())
        
        # Espace
        self.space = QPushButton(" ")
        self.space.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.space.clicked.connect(lambda _event, char=" ": self.handleCharacterButton(char))
        self.layout.addWidget(self.space, 5, 7, 1, 10)
        
        # Back Space
        self.backSpace = QPushButton("Back\nSpace")
        self.backSpace.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.backSpace.clicked.connect(lambda _event: self.handleBackSpace())
        self.layout.addWidget(self.backSpace, 1, 23, 1, 3)
        
        # Caps Lock
        self.capsLock = QPushButton("Verr.\n Maj")
        self.capsLock.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.capsLock.clicked.connect(lambda _event: self.handleCapsLock())
        self.layout.addWidget(self.capsLock, 3, 0, 1, 2)
        
        # Flèche gauche
        self.leftArrow = QPushButton("<")
        self.leftArrow.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.leftArrow.clicked.connect(lambda _event: self.handleLeftArrow())
        self.layout.addWidget(self.leftArrow, 5, 17, 1, 3)
        
        # Flèche droite
        self.rightArrow = QPushButton(">")
        self.rightArrow.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.rightArrow.clicked.connect(lambda _event: self.handleRightArrow())
        self.layout.addWidget(self.rightArrow, 5, 20, 1, 3)
        
        # Bouton Gaze Typing ON / OFF
        self.gazeTyping = QPushButton(" Gaze\nTyping\nON/OFF")
        self.gazeTyping.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.gazeTyping.clicked.connect(lambda _event: self.handleGazeTyping())
        self.layout.addWidget(self.gazeTyping, 1, 0, 2, 2)
        
        # Shift
        self.shiftKey = QPushButton("Shift")
        self.shiftKey.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.shiftKey.clicked.connect(lambda _event: self.handleShift())
        self.layout.addWidget(self.shiftKey, 4, 0, 1, 2)
        
        # Bouton caractères spéciaux
        self.special = QPushButton("?!&")
        self.special.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.special.clicked.connect(lambda _event: self.toggleSpecialCharacters())
        self.layout.addWidget(self.special, 5, 0, 1, 2)
        
    
    def handleCapsLock(self):
        self.cpslock = not self.cpslock
        
        
    def handleShift(self):
        self.shift = not self.shift
            
        
    def handleTextToSpeech(self):
        tts = VoiceEngine()
        tts.read(self.text)
        
        
    def handleGazeTyping(self):
        print("Not yet implemented duh")
        
        
    def handleCharacterButton(self, character):
        if self.cpslock ^ self.shift:
            self.text += character.upper()
        else:
            self.text += character
        
        if self.shift:
            self.shift = False
            
        print(self.text)
        
        
    def toggleSpecialCharacters():
        print("Not yet implemented")
        
        
    def handleBackSpace(self):
        self.text = self.text[:-1]
        
        
    def handleLeftArrow(self):
        print("Left Arrow pressed, not implemented yet.")
        
        
    def handleRightArrow(self):
        print("Right Arrow pressed, not implemented yet.")
        
        
    def switch(self, parent):
        from ..pages.menu import Menu

        parent.inner = Menu(parent)