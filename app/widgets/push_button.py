from PySide6.QtWidgets import QPushButton
from typing import override
from . import EyeWidget, EyeAction

class PushButton(QPushButton, EyeWidget):
    @override
    def eyeEvent(self, position):
        print("CLICK")
        self.click()
        return EyeAction.CLICK