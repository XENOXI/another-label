from PyQt6.QtCore import QSize,QRect,Qt,QPoint, pyqtSignal
from PyQt6.QtGui import QPaintEvent, QPainter,QColor,QBrush,QShortcut,QKeyEvent,QLinearGradient,QMouseEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy
import pandas as pd
import numpy as np

class KeypointsDisplay(QWidget):
    boxCountUpdated = pyqtSignal(int, int)
    selectedBboxUpdate = pyqtSignal(int)
    def __init__(self):
        super().__init__()
        # SETTINGS
        self.frame_box_size = 20
        self.frame_rhomb_size = 10
        self.connection_heigth = 4


        self.selected_frame = 0
        self.labels = None
        self.frame_cnt = 0
        self.bbox_cnt = 10
        self.unique_bbox = np.empty(0)
        self.sequences = []
        self.selectBBox(0)
        self.first_frame_to_render = 0
        self.last_frame_to_render = 0
        self.width_per_box = 0
        

        self.labels_color = [Qt.GlobalColor.magenta,Qt.GlobalColor.blue]
        self.selected_colors = [QColor(200,200,200),QColor(180,180,180),QColor(230,230,230)]
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)

        self.width_per_box = self.width()//self.frame_box_size-1


        self.last_frame_to_render = self.width_per_box + self.first_frame_to_render

        if self.selected_frame >= self.last_frame_to_render:
            self.last_frame_to_render = self.selected_frame+1
            self.first_frame_to_render = self.last_frame_to_render-self.width_per_box
        elif self.selected_frame < self.first_frame_to_render:
            self.first_frame_to_render = self.selected_frame
            self.last_frame_to_render = self.first_frame_to_render + self.width_per_box

        

        

        for i in range(0,self.width_per_box):
            painter.drawRect(i*self.frame_box_size, 10, self.frame_box_size, self.frame_box_size*self.unique_bbox.shape[0])

        

        brush = QBrush(self.selected_colors[0],Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)

        painter.drawRect(self.frame_box_size*(self.selected_frame-self.first_frame_to_render), 10, self.frame_box_size, self.frame_box_size*self.unique_bbox.shape[0])

        brush = QBrush(self.selected_colors[1],Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        
        painter.drawRect(0, 10+self.frame_box_size*self.selected_bbox, self.width_per_box * self.frame_box_size , self.frame_box_size)

        grad = QLinearGradient(0,0,self.frame_box_size,0)
        brush = QBrush(Qt.GlobalColor.black,Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        painter.translate(self.frame_box_size/2,3+self.frame_box_size//2)
        
        for seq in self.sequences:  
            classes = seq["label"].to_numpy()
            frames = seq["frame"].to_numpy()
 
            if int(frames[0]) > self.last_frame_to_render or int(frames[frames.shape[0]-1]) < self.first_frame_to_render:
                painter.translate(0,self.frame_box_size)
                continue
            
            i = 0
            if seq.shape[0] == 1:
                painter.translate(self.frame_box_size*(frames[i]-self.first_frame_to_render),0) 
            
            



            while int(frames[i+1]) < self.first_frame_to_render:
                i+=1
            
            last_cl = self.labels_color[int(classes[i])]

            painter.translate(self.frame_box_size*(frames[i]-self.first_frame_to_render),0) 
           

            while i + 1 < frames.shape[0] and int(frames[i]) <= self.last_frame_to_render-1:
                cl = self.labels_color[int(classes[i+1])]
                grad.setColorAt(0.0,last_cl)
                grad.setColorAt(1.0,cl)
                painter.fillRect(0, (self.frame_rhomb_size)//2, self.frame_box_size*(frames[i+1]-frames[i]),self.connection_heigth,grad)

                brush.setColor(last_cl)
                painter.setBrush(brush)
                painter.rotate(45)
                painter.drawRect(0, 0, self.frame_rhomb_size, self.frame_rhomb_size)
                painter.rotate(-45)
                painter.translate(self.frame_box_size*(frames[i+1]-frames[i]),0)
                last_cl = cl
                i+=1
            

            brush.setColor(last_cl)
            painter.setBrush(brush)
            painter.rotate(45)
            painter.drawRect(0, 0, self.frame_rhomb_size, self.frame_rhomb_size)
            painter.rotate(-45)
                
            painter.translate(self.frame_box_size*(self.first_frame_to_render - frames[i]),self.frame_box_size)

        painter.fillRect(self.width_per_box*self.frame_box_size-self.frame_box_size//2 + 1, -self.unique_bbox.shape[0]*self.frame_box_size-3, self.frame_box_size, self.frame_box_size*self.unique_bbox.shape[0],self.palette().color(self.backgroundRole()))
        painter.end()

    


    def set_frame(self,frame):
        self.selected_frame = frame
        self.repaint()

    def set_frame_cnt(self,frame_cnt):
        self.frame_cnt = frame_cnt
        self.repaint()
    
    def set_labels(self, labels:pd.DataFrame):
        
        self.unique_bbox = pd.unique(labels["track_id"])
        self.boxCountUpdated.emit(self.unique_bbox.shape[0],self.frame_box_size)
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
                self.selectedBboxUpdate.emit(self.selected_bbox)            
                self.repaint()
    
    def selectBBox(self, bbox_id):
        self.selected_bbox = bbox_id-1
        self.selectedBboxUpdate.emit(self.selected_bbox)
        self.repaint()