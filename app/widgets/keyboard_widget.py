from PySide6.QtWidgets import QWidget, QPushButton, QGridLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from ..modules.tts import VoiceEngine
from .button import Button
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
        
        # Gestion du toggle du clavier de caractères spéciaux
        self.specialCharactersToggled = False
        
        # Récupération des icones à display sur le bouton shift        
        imgPath = (Path(__file__).parent.parent / "assets" / "shift_off.png").as_posix()    
        self.shiftOFF = QIcon(imgPath)
        imgPath = (Path(__file__).parent.parent / "assets" / "shift_on.png").as_posix()
        self.shiftON = QIcon(imgPath)
                
        # Grandes lignes principales du clavier : 10 x 4
        self.firstLine = list("1234567890")
        self.secondLine = list("azertyuiop")
        self.thirdLine = list("qsdfghjklm")
        self.fourthLine = list("wxcvbn,.:'")
        self.lines = [self.firstLine, self.secondLine, self.thirdLine, self.fourthLine]
        self.keyboardButtons = [] # Pour garder chaque bouton accessible pour la modification (shift, capslock...)
        
        for n in range(len(self.lines)):
            for i in range(len(self.lines[n])):              
                self.lowerLetter = Button(self.lines[n][i])
                self.layout.addWidget(self.lowerLetter, n+1, 3+2*i, 1, 2)
                self.lowerLetter.clicked.connect(lambda _event, char=self.lines[n][i]: self.handleCharacterButton(char))
                self.keyboardButtons.append(self.lowerLetter)
        
        # Lignes de caractères spéciaux
        self.secondSpecial = list("@#€_&-+()/")
        self.thirdSpecial = list('*";!?=~£¥$')
        self.fourthSpecial = list("^°{") + list("}[]\\%<>")
        self.specialLines = self.secondSpecial + self.thirdSpecial + self.fourthSpecial

        # Boutons spéciaux
        # Retour au menu
        self.homeButton = Button("menu") # A changer pour une icone
        self.homeButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.homeButton, 5, 3, 1, 4)
        
        # Text-to-Speech
        # NE RESTERA PAS DANS LE CLAVIER, FONCTIONNALITE TEST
        self.tts = Button("Text-to\nSpeech")
        self.layout.addWidget(self.tts, 0, 22, 1, 3)
        self.tts.clicked.connect(lambda _event: self.handleTextToSpeech())
        
        # Espace
        self.space = Button(" ")
        self.space.clicked.connect(lambda _event, char=" ": self.handleCharacterButton(char))
        self.layout.addWidget(self.space, 5, 7, 1, 10)
        
        # Back Space
        self.backSpace = Button("Back\nSpace")
        self.backSpace.clicked.connect(lambda _event: self.handleBackSpace())
        self.layout.addWidget(self.backSpace, 1, 23, 1, 2)
        
        # Bouton effacer tout le texte
        self.eraseText = Button("Effacer\ntout le\ntexte")
        self.eraseText.clicked.connect(lambda _event: self.handleTextErasion())
        self.layout.addWidget(self.eraseText, 2, 23, 1, 2)
        
        # Flèche gauche
        self.leftArrow = Button("<")
        self.leftArrow.clicked.connect(lambda _event: self.handleLeftArrow())
        self.layout.addWidget(self.leftArrow, 5, 17, 1, 3)
        
        # Flèche droite
        self.rightArrow = Button(">")
        self.rightArrow.clicked.connect(lambda _event: self.handleRightArrow())
        self.layout.addWidget(self.rightArrow, 5, 20, 1, 3)
        
        # Shift
        self.shiftKey = Button(self.shiftOFF, "Shift")
        self.shiftKey.setIconSize(QSize(48, 48))
        self.shiftKey.clicked.connect(lambda _event: self.handleShift())
        self.layout.addWidget(self.shiftKey, 4, 0, 1, 2)
        
        # Caps Lock
        self.capsLock = Button("verr\nmaj\noff")
        self.capsLock.clicked.connect(lambda _event: self.handleCapsLock())
        self.layout.addWidget(self.capsLock, 3, 0, 1, 2)
        
        # Bouton caractères spéciaux
        self.special = Button("?!&")
        self.special.clicked.connect(lambda _event: self.toggleSpecialCharacters())
        self.layout.addWidget(self.special, 5, 0, 1, 2)
        
        # Bouton Gaze Typing ON / OFF
        self.gazeTyping = Button(" Gaze\nTyping\nON/OFF")
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
        if self.specialCharactersToggled:
            return
        
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
        
        
    def toggleSpecialCharacters(self):
        self.specialCharactersToggled = not self.specialCharactersToggled
        
        if self.specialCharactersToggled:
            for n in range(len(self.specialLines)):
                self.keyboardButtons[n+10].setText(self.specialLines[n])
        
        else:
            self.updateCharactersCase()
        
        
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