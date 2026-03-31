from PySide6.QtWidgets import QApplication
from app.app import MainWindow
from app.modules.logging import setLogLevel

if __name__ == "__main__":
    setLogLevel("debug")
    app = QApplication()
    main_window = MainWindow()
    app.exec()