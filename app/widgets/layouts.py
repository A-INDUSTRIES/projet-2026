from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from . import EyeWidget

class HBoxLayout(QHBoxLayout, EyeWidget):
    pass

class VBoxLayout(QVBoxLayout, EyeWidget):
    pass

class GridLayout(QGridLayout, EyeWidget):
    pass