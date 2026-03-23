from PySide6.QtWidgets import QApplication
from app.app import MainWindow

if __name__ == "__main__":
    app = QApplication()
    main_window = MainWindow()
    app.exec()