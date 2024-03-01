from PyQt6.QtCore import QSize,QRect,Qt
from PyQt6.QtGui import QPaintEvent, QPainter,QColor,QBrush
from PyQt6.QtWidgets import QWidget
import pandas as pd

class PersonTimeline(QWidget):
    def __init__(self):
        super().__init__()
        # SETTINGS
        self.frame_box_size = 20
        self.frame_rhomb_size = 10
        self.connection_heigth = 4


        self.frame = 0
        self.labels = None
        self.frame_cnt = 0
        self.bbox_cnt = 10
        self.unique_bbox = 0
        self.sequences = []


    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)


        for i in range(0,self.frame_cnt):
            painter.drawRect((i-self.frame)*self.frame_box_size, 10, self.frame_box_size, 100)

        if self.labels is None:
            return

        brush = QBrush(Qt.GlobalColor.magenta,Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        painter.translate(self.frame_box_size/2-self.frame*self.frame_box_size,5+self.frame_box_size//2)

        for seq in self.sequences: 
            size = seq.shape[0]     
            for i in range(0,size):
                painter.fillRect(0, (self.frame_rhomb_size)//2, self.frame_rhomb_size*2,self.connection_heigth,QBrush(QColor(200,0,200)))
                painter.rotate(45)
                painter.drawRect(0, 0, self.frame_rhomb_size, self.frame_rhomb_size)
                painter.rotate(-45)
                painter.translate(self.frame_box_size,0)
            painter.translate(self.frame_box_size*size,self.frame_box_size)


    def set_frame(self,frame):
        self.frame = frame
        self.repaint()

    def set_frame_cnt(self,frame_cnt):
        self.frame_cnt = frame_cnt
        self.repaint()
    
    def set_labels(self, labels:pd.DataFrame):
        self.labels = labels  
        self.unique_bbox = pd.unique(labels["track_id"])
        self.sequences = []
        for i in range(self.unique_bbox):
            self.sequences.append(labels[labels["track_id"]==i].copy().sort_index("frame",ascending=True))

    def sizeHint(self) -> QSize:
        return QSize(1000, self.bbox_cnt*self.frame_box_size+20)