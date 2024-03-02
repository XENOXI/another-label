from PyQt6.QtCore import QSize,QRect,Qt,QPoint, pyqtSignal
from PyQt6.QtGui import QPaintEvent, QPainter,QColor,QBrush,QShortcut,QKeyEvent,QLinearGradient,QMouseEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy
import pandas as pd
import numpy as np

class KeypointsDisplay(QWidget):
    def __init__(self):
        super().__init__()
        # SETTINGS
        self.frame_box_size = 20
        self.frame_rhomb_size = 10
        self.connection_heigth = 4


        self.frame_selected = 0
        self.labels = None
        self.frame_cnt = 0
        self.bbox_cnt = 10
        self.unique_bbox = np.empty(0)
        self.sequences = []
        self.selected_bbox = 0
        self.first_frame_to_render = 0
        self.last_frame_to_render = 0
        self.width_per_box = 0
        

        self.labels_color = [Qt.GlobalColor.magenta,Qt.GlobalColor.blue]
        self.selected_colors = [QColor(200,200,200),QColor(180,180,180),QColor(230,230,230)]
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)

        self.width_per_box = self.width()//self.frame_box_size

        self.middle_frame_to_render = self.first_frame_to_render + self.width_per_box // 2

        if self.frame_selected >= self.width_per_box//2 and self.frame_selected < self.frame_cnt - self.width_per_box//2:
            self.first_frame_to_render =  self.frame_selected - self.width_per_box//2
        
        print(self.width())
    

        self.last_frame_to_render = self.width_per_box + self.first_frame_to_render

        for i in range(0,self.width()//self.frame_box_size+1):
            painter.drawRect(i*self.frame_box_size, 10, self.frame_box_size, self.frame_box_size*self.unique_bbox.shape[0])

        brush = QBrush(self.selected_colors[0],Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)

        painter.drawRect(self.frame_box_size*(self.frame_selected-self.first_frame_to_render), 10, self.frame_box_size, self.frame_box_size*self.unique_bbox.shape[0])

        brush = QBrush(self.selected_colors[1],Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        
        painter.drawRect(0, 10+self.frame_box_size*self.selected_bbox, self.width(), self.frame_box_size)

        grad = QLinearGradient(0,0,self.frame_box_size,0)
        brush = QBrush(Qt.GlobalColor.black,Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        painter.translate(self.frame_box_size/2,3+self.frame_box_size//2)
        
        
        for seq in self.sequences:
            last_frame = int(seq.iloc[0]["frame"])           
            if last_frame > self.last_frame_to_render or seq.iloc[-1]["frame"] < self.first_frame_to_render:
                continue
            last_cl = self.labels_color[int(seq.iloc[0]["label"])]
            i = 0
            while frame < self.first_frame_to_render:
                dataframe = seq[i]
                last_cl = self.labels_color[int(dataframe["label"])]
                last_frame = int(dataframe["frame"])
                i+=1
                
            
            seq = seq[1:].iloc
            for dataframe in seq:
                cl = self.labels_color[int(dataframe["label"])]
                frame = int(dataframe["frame"])
                if frame > self.last_frame_to_render or frame < self.first_frame_to_render: 
                    painter.translate(self.frame_box_size*(frame-last_frame),0) 
                    last_frame = frame
                    last_cl = cl
                    if frame > self.last_frame_to_render:
                        break
                    continue
                grad.setColorAt(0.0,last_cl)
                grad.setColorAt(1.0,cl)
                painter.fillRect(0, (self.frame_rhomb_size)//2, self.frame_box_size*(frame-last_frame),self.connection_heigth,grad)

                brush.setColor(last_cl)
                painter.setBrush(brush)
                painter.rotate(45)
                painter.drawRect(0, 0, self.frame_rhomb_size, self.frame_rhomb_size)
                painter.rotate(-45)
                painter.translate(self.frame_box_size*(frame-last_frame),0)
                last_frame = frame
                last_cl = cl
            brush.setColor(last_cl)
            painter.setBrush(brush)
            painter.rotate(45)
            painter.drawRect(0, 0, self.frame_rhomb_size, self.frame_rhomb_size)
            painter.rotate(-45)
            painter.translate(-self.frame_box_size*last_frame,self.frame_box_size)
        painter.end()

    


    def set_frame(self,frame):
        self.frame_selected = frame
        self.repaint()

    def set_frame_cnt(self,frame_cnt):
        self.frame_cnt = frame_cnt
        self.repaint()
    
    def set_labels(self, labels:pd.DataFrame):
        self.unique_bbox = pd.unique(labels["track_id"])
        for i in self.unique_bbox:
            self.sequences.append(labels[labels["track_id"]==i].copy().sort_values(by="frame",ascending=True))

    def sizeHint(self) -> QSize:
        return QSize(1000,10*self.frame_box_size)
    
    def keyPressEvent(self, event):
        print(self.keyevent_to_string(event))
        

        if self.keyevent_to_string(event) == "Control+Q":
            self.close()
    
    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            point = e.pos()
            if point.y() > 10:
                point.x()//self.frame_box_size
                self.selected_bbox = (point.y()-10)//self.frame_box_size               
                self.repaint()