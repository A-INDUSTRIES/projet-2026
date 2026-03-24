from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from ..modules.tts import VoiceEngine
from pathlib import Path

class KeyboardWidget(QWidget):    
    def __init__(self, parent):
        super().__init__()
        
        # Initialisation du layout en grille
        self.layout = QGridLayout(self)
        
        # Texte écrit sur le clavier (se réinitialise à chaque ouverture du clavier, peut-être changer ?)
        self.text = ""
        
        # Gestion des majuscules avec Caps Lock et Shift
        self.cpslock = False
        self.shift = False
        
        # Récupération des icones à display sur le bouton shift        
        imgPath = (Path(__file__).parent.parent / "assets" / "shift_off.png").as_posix()    
        self.shiftOFF = QIcon(imgPath)
        imgPath = (Path(__file__).parent.parent / "assets" / "shift_on.png").as_posix()
        self.shiftON = QIcon(imgPath)
                
        # Grandes lignes principales du clavier : 10 x 4
        self.first_line = list("1234567890")
        self.second_line = list("azertyuiop")
        self.third_line = list("qsdfghjklm")
        self.fourth_line = list("wxcvbn,.:=")
        self.lines = [self.first_line, self.second_line, self.third_line, self.fourth_line]
        self.keyboardButtons = [] # Pour garder chaque bouton accessible pour la modification (shift, capslock...)
        
        for n in range(len(self.lines)):
            for i in range(len(self.lines[n])):
                self.lowerLetter = QPushButton(self.lines[n][i])
                self.lowerLetter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.layout.addWidget(self.lowerLetter, n+1, 3+2*i, 1, 2)
                self.lowerLetter.clicked.connect(lambda _event, char=self.lines[n][i]: self.handleCharacterButton(char))
                self.keyboardButtons.append(self.lowerLetter)

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
        self.layout.addWidget(self.tts, 0, 22, 1, 3)
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
        self.layout.addWidget(self.backSpace, 1, 23, 1, 2)
        
        # Bouton effacer tout le texte
        self.eraseText = QPushButton("Effacer\ntout le\ntexte")
        self.eraseText.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.eraseText.clicked.connect(lambda _event: self.handleTextErasion())
        self.layout.addWidget(self.eraseText, 2, 23, 1, 2)
        
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
        
        # Shift
        self.shiftKey = QPushButton(self.shiftOFF ,"Shift")
        self.shiftKey.setIconSize(QSize(48, 48))
        self.shiftKey.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.shiftKey.clicked.connect(lambda _event: self.handleShift())
        self.layout.addWidget(self.shiftKey, 4, 0, 1, 2)
        
        # Caps Lock
        self.capsLock = QPushButton("verr\nmaj\noff")
        self.capsLock.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.capsLock.clicked.connect(lambda _event: self.handleCapsLock())
        self.layout.addWidget(self.capsLock, 3, 0, 1, 2)
        
        # Bouton caractères spéciaux
        self.special = QPushButton("?!&")
        self.special.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.special.clicked.connect(lambda _event: self.toggleSpecialCharacters())
        self.layout.addWidget(self.special, 5, 0, 1, 2)
        
        # Bouton Gaze Typing ON / OFF
        self.gazeTyping = QPushButton(" Gaze\nTyping\nON/OFF")
        self.gazeTyping.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.gazeTyping.clicked.connect(lambda _event: self.handleGazeTyping())
        self.layout.addWidget(self.gazeTyping, 1, 0, 2, 2)
               
    
    def handleCapsLock(self):
        self.cpslock = not self.cpslock
        self.updateCharactersCase()
        self.updateCapsLockDisplay()
    
    def updateCapsLockDisplay(self):
        if self.cpslock:
            self.capsLock.setText("VERR\nMAJ\nON")
        else:
            self.capsLock.setText("verr\nmaj\noff")
        
        
    def handleShift(self):
        self.shift = not self.shift
        self.updateCharactersCase()
        self.updateShiftKeyDisplay()
            
    def updateShiftKeyDisplay(self):
        if self.shift:
            self.shiftKey.setIcon(self.shiftON)
        else:
            self.shiftKey.setIcon(self.shiftOFF) 
        
        
    def updateCharactersCase(self):
        if self.cpslock ^ self.shift:
            for n in range(len(self.keyboardButtons)):
                self.keyboardButtons[n].setText(self.lines[n//10][n%10].upper())
        
        else:
            for n in range(len(self.keyboardButtons)):
                self.keyboardButtons[n].setText(self.lines[n//10][n%10].lower())
        
            
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
            self.updateCharactersCase()
            self.updateShiftKeyDisplay()
        
        print(self.text)
        
        
    def toggleSpecialCharacters():
        print("Not yet implemented")
        
        
    def handleBackSpace(self):
        self.text = self.text[:-1]
        print(self.text)
        
    
    def handleTextErasion(self):
        self.text = ""
        print(self.text)
        
        
    def handleLeftArrow(self):
        print("Left Arrow pressed, not implemented yet.")
        
        
    def handleRightArrow(self):
        print("Right Arrow pressed, not implemented yet.")
        
        
    def switch(self, parent):
        from ..pages.menu import Menu

        parent.inner = Menu(parent)