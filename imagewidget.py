from PyQt6.QtCore import Qt, QRect, QPoint, QSize
from PyQt6.QtGui import QMouseEvent, QPaintEvent, QImage, QPainter
from PyQt6.QtWidgets import QWidget
from PyQt6 import QtGui
import cv2


class ImageWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.start_frame = None
        self.selected_id = None
        self.labels = None
        self.shape = None
        self.frame = None
        self.cap = None

    def set_labels(self, labels):
        self.labels = labels        

    def set_video(self, filepath):
        self.cap = cv2.VideoCapture(filepath)
        self.frame = 0

    def set_frame(self, frame):
        self.frame = frame
        self.repaint()

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            pass
        if e.button() == Qt.MouseButton.RightButton:
            for r in self.labels[self.labels['frame'] == self.frame].iloc:
                x1 = int((r['x'] - r['w']/2))
                x2 = int((r['x'] + r['w']/2))

                y1 = int((r['y'] - r['h']/2))
                y2 = int((r['y'] + r['h']/2))

                if x1 <= e <= x2 and y1 <= e.y() <= y2:
                    self.selected_id = self.labels['track_id']
                    break

    def mouseReleaseEvent(self, a0: QMouseEvent | None) -> None:
        return super().mouseReleaseEvent(a0)
    
    def mouseMoveEvent(self, a0: QMouseEvent | None) -> None:
        pass
    
    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)
        print(self.width(), self.height())
        if not self.cap:
            brush = QtGui.QBrush()
            brush.setColor(QtGui.QColor('black'))
            brush.setStyle(Qt.BrushStyle.SolidPattern)
            rect = QRect(0, 0, painter.device().width(), painter.device().height())
            painter.fillRect(rect, brush)
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame)
        ret, image = self.cap.read()
        if not ret:
            print("FRAME READ FAILURE")
        for r in self.labels[self.labels['frame'] == self.frame].iloc:
            color = (0, 255, 0)
            if r['label'] == 1:
                color = (255, 0, 0)
            if r['track_id'] == self.selected_id:
                color = (255, 255, 0)

            x1 = int((r['x'] - r['w']/2))
            x2 = int((r['x'] + r['w']/2))

            y1 = int((r['y'] - r['h']/2))
            y2 = int((r['y'] + r['h']/2))
            image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        height, width, _ = image.shape
        bytesPerLine = width*3
        size = QSize(width, height)
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format.Format_BGR888)
        painter.drawImage(QRect(QPoint(0, 0), size), qImg)
