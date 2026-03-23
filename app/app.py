from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import Qt
from app.pages.menu import Menu

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._inner = None

        # Définition des propiétés de la fenêtre
        self.setWindowTitle("Communiquer avec les yeux")
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        # La page par défaut est le Menu
        menu = Menu(self)
        self.inner = menu

        # On montre la fenêtre quand elle est prête
        self.show()

    @property
    def inner(self):
        """ Inner est une propriété de la fenêtre pour
        permettre de changer facilement de 'page'.

        Exemple de Menu: parent.inner = Keyboard()
        """
        return self._inner
    
    @inner.setter
    def inner(self, inner):
        self._inner = inner
        self.setCentralWidget(self._inner)