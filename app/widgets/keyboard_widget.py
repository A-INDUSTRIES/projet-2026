from PySide6.QtWidgets import QSizePolicy, QWidget
from PySide6.QtCore import QSize, Signal, Qt
from PySide6.QtGui import QIcon
from ..modules.logger import *
from . import Button, EyeWidget, GridLayout, PushButton, Widget, GazeWidget


class KeyboardWidget(QWidget, EyeWidget):    
    textUpdated = Signal(str)
    
    def __init__(self):
        super().__init__()
        
        # Initialisation du layout en grille
        self.setLayout(GridLayout(self))
        
        # Gestion des majuscules avec Caps Lock et Shift
        self.cpsLock = False
        self.shift = False
        
        # Gestion du toggle du clavier de caractères spéciaux
        self.specialCharactersToggled = False
        
        # Récupération des icones à display sur le bouton shift        
        self.shiftOFF = QIcon(":/icons/shift_off")
        self.shiftON = QIcon(":/icons/shift_on")
                
        # Grandes lignes principales du clavier : 10 x 4
        self.firstLine = list("1234567890")
        self.secondLine = list("azertyuiop")
        self.thirdLine = list("qsdfghjklm")
        self.fourthLine = list("wxcvbn,.:'")
        self.lines = self.firstLine + self.secondLine + self.thirdLine + self.fourthLine
        
        # Equivalent caractères spéciaux aux touches de base
        self.firstSpecial = ["1/2", "1/3", "é", "è", "à", "²", "³", "⁴", "≠", "..."]
        self.secondSpecial = list("@#€_&-+()/")
        self.thirdSpecial = list('*";!?=~£¥$')
        self.fourthSpecial = list("^°{") + list("}[]\\%<>")
        self.specialLines = self.firstSpecial + self.secondSpecial + self.thirdSpecial + self.fourthSpecial
        
        self.keyboardButtons = [] # Pour garder chaque bouton accessible pour la modification (shift, capslock...)

        self.gazeWidget = GazeWidget()
        self.gazeWidget.words.connect(self.handleGaze)
        self.layout().addWidget(self.gazeWidget, 1, 2, 3, 20)
        
        for n in range(len(self.lines)):
            self.lowerLetter = Button(self.lines[n], self.specialLines[n])
            self.lowerLetter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.layout().addWidget(self.lowerLetter, n//10, 2+2*(n%10), 1, 2)
            self.lowerLetter.onclick.connect(self.handleCharacterButton)
            self.keyboardButtons.append(self.lowerLetter)

        # Boutons spéciaux
        # Retour au menu
        self.homeButton = PushButton("menu") # A changer pour une icone
        self.homeButton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.homeButton.clicked.connect(lambda _event: self.parent().switch("menu"))
        self.layout().addWidget(self.homeButton, 4, 2, 1, 4)
                
        # Espace
        self.space = Button(" ")
        self.space.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.space.onclick.connect(lambda _event, char=" ": self.handleCharacterButton(char))
        self.layout().addWidget(self.space, 4, 6, 1, 10)
        
        # Back Space
        self.backSpace = PushButton("Back\nSpace")
        self.backSpace.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.backSpace.clicked.connect(lambda _event: self.handleBackSpace())
        self.layout().addWidget(self.backSpace, 0, 22, 1, 2)
        
        # Touche Enter
        self.enter = PushButton("Enter")
        self.enter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.enter.clicked.connect(lambda _event: self.handleEnter())
        self.layout().addWidget(self.enter, 1, 22, 1, 2)
        
        # Bouton effacer tout le texte
        self.eraseText = PushButton("Effacer\ntout le\ntexte")
        self.eraseText.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.eraseText.clicked.connect(lambda _event: self.handleTextErasion())
        self.layout().addWidget(self.eraseText, 2, 22, 2, 2)
        
        # Flèche gauche
        self.leftArrow = PushButton("<")
        self.leftArrow.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.leftArrow.clicked.connect(lambda _event: self.handleLeftArrow())
        self.layout().addWidget(self.leftArrow, 4, 16, 1, 3)
        
        # Flèche droite
        self.rightArrow = PushButton(">")
        self.rightArrow.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.rightArrow.clicked.connect(lambda _event: self.handleRightArrow())
        self.layout().addWidget(self.rightArrow, 4, 19, 1, 3)
        
        # Shift
        self.shiftKey = Button("")
        self.shiftKey.setIcon(self.shiftOFF)
        self.shiftKey.setIconSize(QSize(48, 48))
        self.shiftKey.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.shiftKey.onclick.connect(lambda _event: self.handleShift())
        self.layout().addWidget(self.shiftKey, 3, 0, 1, 2)
        
        # Caps Lock
        self.capsLock = Button("")
        self.capsLock.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.capsLock.onclick.connect(lambda _event: self.handleCapsLock())
        self.layout().addWidget(self.capsLock, 2, 0, 1, 2)
        self.updateCapsLockDisplay()
        
        # Bouton caractères spéciaux
        self.special = Button("")
        self.special.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.special.onclick.connect(lambda _event: self.toggleSpecialCharacters())
        self.layout().addWidget(self.special, 4, 0, 1, 2)
        self.updateSpecialCharactersDisplay()
        
        # Bouton Gaze Typing ON / OFF
        self.gazeTyping = PushButton("Gaze\nTyping\nOFF")
        self.gazeTyping.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.gazeTyping.clicked.connect(self.toggleGazeTyping)
        self.layout().addWidget(self.gazeTyping, 0, 0, 2, 2)

        self.gazeWidget.raise_()
        
    def debug_pos(self):
        poses = {}
        for i in range(self.layout().count()):
            object = self.layout().itemAt(i).widget()
            if isinstance(object, PushButton):
                pos = self.gazeWidget.mapFromGlobal(object.mapToGlobal(object.rect().center()))
                poses[object.text()] = {
                    "x": pos.x()/self.gazeWidget.width(),
                    "y": pos.y()/self.gazeWidget.height()
                }

        with open("coords.json", 'w') as f:
            import json
            json.dump(poses, f, indent=4)
    
    def handleCapsLock(self):
        self.cpsLock = not self.cpsLock
        self.updateCharactersCase()
        self.updateCapsLockDisplay()
        
    
    def updateCapsLockDisplay(self):
        if self.cpsLock:
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
        for key in self.keyboardButtons:
            key.toggleShift()

    def handleGaze(self, words):
        if len(words) == 0:
            return
        print(words[:10])
        self.textUpdated.emit(words[0][0] + " ")

    def toggleGazeTyping(self):
        if self.gazeWidget.toggle():
            self.gazeTyping.setText("Gaze\nTyping\nON")
        else:
            self.gazeTyping.setText("Gaze\nTyping\nOFF")
        
    def toggleSpecialCharacters(self):
        self.specialCharactersToggled = not self.specialCharactersToggled
        for key in self.keyboardButtons:
            key.toggleSpecial()  
        self.updateSpecialCharactersDisplay()
            
            
    def updateSpecialCharactersDisplay(self):
        if self.specialCharactersToggled:
            self.special.setText("abc")
        else:
            self.special.setText("?!&&")
            
              
    def handleCharacterButton(self, character):       
        if self.shift:
            self.shift = False
            self.updateCharactersCase()
            self.updateShiftKeyDisplay()
        
        self.emitSignal(character)
        
    
    def handleBackSpace(self):
        self.emitSignal("backspace")
        
    
    def handleTextErasion(self):
        self.emitSignal("reset")
        
    
    def handleEnter(self):
        self.emitSignal("enter")
        
        
    def emitSignal(self, txt):
        self.textUpdated.emit(txt)
        
        
    def handleLeftArrow(self):
        self.textUpdated.emit("left")
        
        
    def handleRightArrow(self):
        self.textUpdated.emit("right")