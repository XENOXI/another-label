from PyQt6.QtCore import QSize,QRect,Qt,QPoint
from PyQt6.QtGui import QPaintEvent, QPainter,QColor,QBrush,QShortcut,QKeyEvent,QLinearGradient
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

        self.labels_color = [Qt.GlobalColor.magenta,Qt.GlobalColor.blue]
        


    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)


        for i in range(0,self.frame_cnt):
            painter.drawRect((i-self.frame)*self.frame_box_size, 10, self.frame_box_size, self.frame_box_size*self.unique_bbox.shape[0])
        
        grad = QLinearGradient(0,0,self.frame_box_size,0)
        brush = QBrush(Qt.GlobalColor.black,Qt.BrushStyle.SolidPattern)
        Qt.BrushStyle.LinearGradientPattern
        painter.setBrush(brush)
        painter.translate(self.frame_box_size/2-self.frame*self.frame_box_size,5+self.frame_box_size//2)

        
        for seq in self.sequences: 
            # f_df = seq.iloc[0]
            
            # brush.setColor(self.labels_color[int(f_df["label"])])
            # painter.setBrush(brush)

            # last_frame = int(f_df["frame"])
            # painter.translate(self.frame_box_size*last_frame,0) 
            # painter.rotate(45)
            # painter.drawRect(0, 0, self.frame_rhomb_size, self.frame_rhomb_size)
            # painter.rotate(-45)
            last_frame = int(seq.iloc[0]["frame"])
            last_label = int(seq.iloc[0]["label"])
            painter.translate(self.frame_box_size*last_frame,0) 
            seq = seq[1:].iloc
            for dataframe in seq:
                label = int(dataframe["label"])
                frame = int(dataframe["frame"])  
                grad.setColorAt(0.0,self.labels_color[last_label])
                grad.setColorAt(1.0,self.labels_color[label])
                painter.setBrush(grad)
                painter.fillRect(0, (self.frame_rhomb_size)//2, self.frame_box_size*(frame-last_frame),self.connection_heigth,QBrush(QColor(200,0,200)))
                
                             
                brush.setColor(self.labels_color[int(dataframe["label"])])
                painter.setBrush(brush)
                painter.rotate(45)
                painter.drawRect(0, 0, self.frame_rhomb_size, self.frame_rhomb_size)
                painter.rotate(-45)
                painter.translate(self.frame_box_size*(frame-last_frame),0) 
                last_frame = frame
            painter.rotate(45)
            painter.drawRect(0, 0, self.frame_rhomb_size, self.frame_rhomb_size)
            painter.rotate(-45)
            painter.translate(-self.frame_box_size*last_frame,self.frame_box_size)
        painter.end()

    


    def set_frame(self,frame):
        self.frame = frame
        self.repaint()

    def set_frame_cnt(self,frame_cnt):
        self.frame_cnt = frame_cnt
        self.repaint()
    
    def set_labels(self, labels:pd.DataFrame):
        self.unique_bbox = pd.unique(labels["track_id"])
        for i in self.unique_bbox:
            self.sequences.append(labels[labels["track_id"]==i].copy().sort_values(by="frame",ascending=True))

    def sizeHint(self) -> QSize:
        return QSize(1000, self.unique_bbox.shape[0]*self.frame_box_size+20)