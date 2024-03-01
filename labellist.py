from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget

class LabelList(QWidget):
    def __init__(self):
        super().__init__()

    def sizeHint(self) -> QSize:
        return QSize(300, 300)