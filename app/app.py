from PySide6.QtWidgets import QMainWindow, QApplication, QLabel
from pages.menu import Menu

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._inner = None

        self.setWindowTitle("Communiquer avec les yeux")

        menu = Menu()
        self.inner = menu

        self.show()

    @property
    def inner(self):
        return self._inner
    
    @inner.setter
    def inner(self, inner):
        self._inner = inner
        self.setCentralWidget(self._inner)

if __name__ == "__main__":
    app = QApplication()
    main_window = MainWindow()
    app.exec()