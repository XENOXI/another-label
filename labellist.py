from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget,QLabel, QVBoxLayout
from PyQt6.QtGui import QFont,QPaintEvent,QPainter,QColor

class LabelList(QWidget):
    def __init__(self):
        super().__init__()
        self.bbox_cnt = 0
        self.selected_bbox = 0
        self.frame_box_size = 0
        self.selected_color = QColor(200,200,200)

    
        

    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)
        self.setFixedHeight(15+self.frame_box_size//2+self.bbox_cnt*self.frame_box_size)
        painter.fillRect(0,self.frame_box_size//2+self.selected_bbox*self.frame_box_size,25,self.frame_box_size,self.selected_color)
        for i in range(self.bbox_cnt):
            painter.drawText(10,15+self.frame_box_size//2+i*self.frame_box_size,f"{i}")

    def set_frame_box_size(self,bbox_cnt,frame_box_size):
        self.bbox_cnt = bbox_cnt
        self.frame_box_size = frame_box_size
        self.repaint()
    
    def set_bboxes_cnt(self,bbox_cnt):
        self.bbox_cnt = bbox_cnt
        self.repaint()
    
    def set_selected_bbox(self,box):
        self.selected_bbox = box
        self.repaint()

    def sizeHint(self) -> QSize:
        return QSize(25, 300)
    
