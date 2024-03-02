from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QSizePolicy

class LabelList(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def sizeHint(self) -> QSize:
        return QSize(300, 400)