from PySide6.QtWidgets import QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal

class Button(QPushButton):
    onclick = Signal(str)

    def __init__(self, char:str, special:str | None=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shift = False
        self.special = False
        
        self.layout = QVBoxLayout(self)
        self.label = QLabel(char)
        self.layout.addWidget(self.label)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        self.character = char
        if special:
            self.specialCharacter = special
        else:
            self.specialCharacter = char
        self.current = char
        
        # Gestion par le bouton de l'évènement click
        super().clicked.connect(self.handleClick)
        

    # Un objet bouton gère lui-même ce qu'il renvoie quand il est cliqué en fonction des paramètres
    # Shift, Caps Lock et selon si le clavier est en mode caractères spéciaux.
    def handleClick(self):
        self.onclick.emit(self.current)


    def toggleShift(self):
        self.shift = not self.shift
        self.update()


    def toggleSpecial(self):
        self.special = not self.special
        self.update()


    def update(self):
        if self.special:
            self.current = self.specialCharacter
        elif self.shift:
            self.current = self.character.upper()
        else:
            self.current = self.character

        self.label.setText(self.current)