from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPaintEvent, QPainter
from PyQt6.QtWidgets import QWidget

class PersonTimeline(QWidget):
    def __init__(self):
        super().__init__()

    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)
        painter.drawRect(10, 10, 20, 20)

    def sizeHint(self) -> QSize:
        return QSize(100, 100)