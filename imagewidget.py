from PyQt6.QtCore import Qt, QRect, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPaintEvent, QImage, QPainter, QResizeEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6 import QtGui
import cv2
from pandas import Series

class BBox:
    def __init__(self, row: Series) -> None:
        self.r = row

    def lt_corner(self):
        x = int((self.r['x'] - self.r['w']/2))
        y = int((self.r['y'] - self.r['h']/2))
        return (x, y)
    
    def lb_corner(self):
        x = int((self.r['x'] - self.r['w']/2))
        y = int((self.r['y'] + self.r['h']/2))
        return (x, y)
    
    def rt_corner(self):
        x = int((self.r['x'] + self.r['w']/2))
        y = int((self.r['y'] - self.r['h']/2))
        return (x, y)
    
    def rb_corner(self):
        x = int((self.r['x'] + self.r['w']/2))
        y = int((self.r['y'] + self.r['h']/2))
        return (x, y)
    
    def r_middle(self):
        return (int(self.r['x']+self.r['w']/2), int(self.r['y']))
    
    def l_middle(self):
        return (int(self.r['x']-self.r['w']/2), int(self.r['y']))
    
    def t_middle(self):
        return (int(self.r['x']), int(self.r['y'] - self.r['h']/2))
    
    def b_middle(self):
        return (int(self.r['x']), int(self.r['y'] + self.r['h']/2))
    
class ImageWidget(QWidget):
    frameSelected = pyqtSignal(int)
    def __init__(self) -> None:
        super().__init__()
        
        self.selectedId = None
        self.labels = None
        self.shape = None
        self.frame = None
        self.cap = None

        self.aspectRatio = 360/640

        # self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def setLabels(self, labels):
        self.labels = labels        

    def setVideo(self, filepath):
        self.cap = cv2.VideoCapture(filepath)
        width  = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
        self.shape = (height, width)
        self.aspectRatio = width/height
        self.frame = 0

    def setFrame(self, frame):
        self.frame = frame
        self.repaint()

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            pass
        if e.button() == Qt.MouseButton.RightButton:
            height, width = self.shape
            x = e.pos().x() / self.width() * width
            y = e.pos().y() / self.height() * height
            print(x, y, self.width(), self.height(), width, height)
            for r in self.labels[self.labels['frame'] == self.frame].iloc:
                bbox = BBox(r)
                lt = bbox.lt_corner()
                rb = bbox.rb_corner()

                if lt[0] <= x <= rb[0] and lt[1] <= y <= rb[1]:
                    self.selectedId = int(r['track_id'])
                    self.frameSelected.emit(self.selectedId)
                    print(f"Selected {self.selectedId}")
                    self.repaint()
                    return
            self.repaint()
            self.selectedId = None

    def mouseReleaseEvent(self, a0: QMouseEvent | None) -> None:
        return super().mouseReleaseEvent(a0)
    
    def mouseMoveEvent(self, e: QMouseEvent | None) -> None:
        if self.selectedId and e.button() == Qt.MouseButton.LeftButton:
            height, width = self.shape
            x = e.pos().x() / self.width() * width
            y = e.pos().y() / self.height() * height


            
    
    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)
        
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
            return
        for r in self.labels[self.labels['frame'] == self.frame].iloc:
            color = (0, 255, 0)
            if r['label'] == 1:
                color = (255, 0, 0)
            if int(r['track_id']) == self.selectedId:
                color = (255, 255, 0)
                bbox = BBox(r)
                cv2.circle(image, bbox.lt_corner(), 10, color, -1)
                cv2.circle(image, bbox.t_middle(), 10, color, -1)
                cv2.circle(image, bbox.rt_corner(), 10, color, -1)
                cv2.circle(image, bbox.l_middle(), 10, color, -1)
                cv2.circle(image, bbox.r_middle(), 10, color, -1)
                cv2.circle(image, bbox.lb_corner(), 10, color, -1)
                cv2.circle(image, bbox.b_middle(), 10, color, -1)
                cv2.circle(image, bbox.rb_corner(), 10, color, -1)

            bbox = BBox(r)
            image = cv2.rectangle(image, bbox.lt_corner(), bbox.rb_corner(), color, 2)
        image = cv2.resize(image, (640, 360))
        height, width, _ = image.shape
        bytesPerLine = width*3
        size = QSize(width, height)
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format.Format_BGR888)
        painter.drawImage(QRect(QPoint(0, 0), size), qImg)

    def sizeHint(self) -> QSize:
        return QSize(640, 360)
    
    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        w = self.width()
        h = self.height()
        aspect = h/w

        if(aspect < self.aspectRatio):
            targetWidth = int(h/self.aspectRatio)
            self.setMaximumWidth(targetWidth)
            self.setMaximumHeight(h)
        else:
            targetHeigth = int(w*self.aspectRatio)
            self.setMaximumHeight(targetHeigth)
            self.setMaximumWidth(w)
