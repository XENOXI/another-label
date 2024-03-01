from PyQt6.QtCore import QSize,QRect,Qt,QPoint
from PyQt6.QtGui import QPaintEvent, QPainter,QColor,QBrush,QShortcut,QKeyEvent,QLinearGradient,QMouseEvent
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
        self.selected_bbox = 0
        

        self.labels_color = [Qt.GlobalColor.magenta,Qt.GlobalColor.blue]
        self.selected_colors = [QColor(0,134,110),QColor(0,143,103)]


    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)

        
        

        for i in range(0,self.frame_cnt):
            painter.drawRect((i-self.frame)*self.frame_box_size, 10, self.frame_box_size, self.frame_box_size*self.unique_bbox.shape[0])

        brush = QBrush(self.selected_colors[0],Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)

        painter.drawRect(0, 10, self.frame_box_size, self.frame_box_size*self.unique_bbox.shape[0])

        brush = QBrush(self.selected_colors[1],Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        
        painter.drawRect(-self.frame*self.frame_box_size, 10+self.frame_box_size*self.selected_bbox, self.frame_box_size*self.frame_cnt, self.frame_box_size)

        grad = QLinearGradient(0,0,self.frame_box_size,0)
        brush = QBrush(Qt.GlobalColor.black,Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        painter.translate(self.frame_box_size/2-self.frame*self.frame_box_size,3+self.frame_box_size//2)

        
        for seq in self.sequences: 
            last_frame = int(seq.iloc[0]["frame"])
            last_cl = self.labels_color[int(seq.iloc[0]["label"])]
            painter.translate(self.frame_box_size*last_frame,0) 
            seq = seq[1:].iloc
            for dataframe in seq:
                cl = self.labels_color[int(dataframe["label"])]
                frame = int(dataframe["frame"])  
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