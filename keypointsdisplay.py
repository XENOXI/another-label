from PyQt6.QtCore import QSize,QRect,Qt,QPoint, pyqtSignal
from PyQt6.QtGui import QPaintEvent, QPainter,QColor,QBrush,QShortcut,QKeyEvent,QLinearGradient,QMouseEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy
import pandas as pd
import numpy as np

class KeypointsDisplay(QWidget):
    boxCountUpdated = pyqtSignal(int, int)
    selectedBboxUpdate = pyqtSignal(int)
    imageWidgetRepaint = pyqtSignal()
    setFrame = pyqtSignal(int)

    tableUpdate = pyqtSignal()
    def __init__(self):
        super().__init__()
        # SETTINGS
        self.frame_box_size = 20
        self.frame_rhomb_size = 10
        self.connection_heigth = 4

        self.first_selected_frame = 0
        self.last_selected_frame = 0
        self.mode = "one-select"
        self.labels = None
        self.frame_cnt = 0
        self.bbox_cnt = 0
        self.sequences = []
        self.sequences = []
        self.selectBBox(0)
        self.first_frame_to_render = 0
        self.last_frame_to_render = 0
        self.width_per_box = 0
  
        self.select_last_side = True

        self.labels_color = [Qt.GlobalColor.magenta,Qt.GlobalColor.blue]
        self.selected_colors = [QColor(180,180,180),QColor(150,150,150),QColor(230,230,230)]
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)

        if len(self.sequences)==0:
            painter.translate(self.width()//2,30)
            painter.drawText(0,0,"HEHE")
            painter.end()
            return
        

        self.width_per_box = self.width()//self.frame_box_size-1


        self.last_frame_to_render = self.width_per_box + self.first_frame_to_render

        if self.select_last_side:
            if self.last_selected_frame >= self.last_frame_to_render:
                self.last_frame_to_render = self.last_selected_frame +  1
                self.first_frame_to_render = self.last_frame_to_render-self.width_per_box
            elif self.last_selected_frame < self.first_frame_to_render:
                self.first_frame_to_render = self.last_selected_frame
                self.last_frame_to_render = self.first_frame_to_render + self.width_per_box
        else:
            if self.first_selected_frame >= self.last_frame_to_render:
                self.last_frame_to_render = self.first_selected_frame +  1
                self.first_frame_to_render = self.last_frame_to_render-self.width_per_box
            elif self.first_selected_frame < self.first_frame_to_render:
                self.first_frame_to_render = self.first_selected_frame
                self.last_frame_to_render = self.first_frame_to_render + self.width_per_box

        

        

        for i in range(0,self.width_per_box):
            painter.drawRect(i*self.frame_box_size, 10, self.frame_box_size, self.frame_box_size*len(self.sequences))

        

        brush = QBrush(self.selected_colors[0],Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        for i in range(max(self.first_selected_frame,self.first_frame_to_render),self.last_selected_frame+1):
            painter.drawRect(self.frame_box_size*(i-self.first_frame_to_render), 10, self.frame_box_size, self.frame_box_size*len(self.sequences))

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

            if seq.shape[0] == 0 or int(frames[0]) > self.last_frame_to_render or int(frames[frames.shape[0]-1]) < self.first_frame_to_render:
                painter.translate(0,self.frame_box_size)
                continue
            
            i = 0
            if seq.shape[0] == 1:
                painter.translate(self.frame_box_size*(frames[i]-self.first_frame_to_render),0) 
                brush.setColor(last_cl)
                painter.setBrush(brush)
                painter.rotate(45)
                painter.drawRect(0, 0, self.frame_rhomb_size, self.frame_rhomb_size)
                painter.rotate(-45)
                painter.translate(0,self.frame_box_size)
                continue
            
            



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

        painter.fillRect(self.width_per_box*self.frame_box_size-self.frame_box_size//2 + 1, -len(self.sequences)*self.frame_box_size-3, self.frame_box_size*2, self.frame_box_size*len(self.sequences),self.palette().color(self.backgroundRole()))
        painter.end()

    


    def set_frame(self,frame):
        if self.mode == "one-select":
            self.last_selected_frame = frame
            self.first_selected_frame = frame
        elif frame>self.last_selected_frame:
            if not self.select_last_side:
                self.first_selected_frame = self.last_selected_frame
                self.select_last_side = True
            self.last_selected_frame = frame

        elif frame<self.first_selected_frame:
            if self.select_last_side:
                self.last_selected_frame = self.first_selected_frame
                self.select_last_side = False
            self.first_selected_frame = frame

        elif self.select_last_side:
            self.last_selected_frame = frame
        else:
            self.first_selected_frame = frame
        self.repaint()

    def set_frame_cnt(self,frame_cnt):
        self.frame_cnt = frame_cnt
        self.repaint()
    
    def set_sequences(self, sequences: list[pd.DataFrame]):
        self.boxCountUpdated.emit(len(sequences),self.frame_box_size)
        self.sequences = sequences




    

    def sizeHint(self) -> QSize:
        return QSize(1000,10*self.frame_box_size)
    
    
    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            point = e.pos()
            if point.y() > 10 and point.y()<10 + self.frame_box_size*len(self.sequences) and point.x()<self.frame_box_size*self.width_per_box:
                self.selected_bbox = (point.y()-10)//self.frame_box_size   
                self.selectedBboxUpdate.emit(self.selected_bbox)          

                self.mode = "one-select"
                self.setFrame.emit(point.x()//self.frame_box_size+self.first_frame_to_render)  
                self.repaint()
                
    
    def mouseMoveEvent(self, a0: QMouseEvent | None) -> None:
        now_pos = a0.pos()
        self.mode = "multiselect"

        pos_per_box = now_pos.x()//self.frame_box_size
        self.setFrame.emit(pos_per_box+self.first_frame_to_render)        

    
    def selectBBox(self, bbox_id):
        self.selected_bbox = bbox_id
        self.selectedBboxUpdate.emit(self.selected_bbox)
        self.repaint()

    def draw_class(self,cls):
        if cls >= len(self.labels_color):
            return
        
        self.tableUpdate.emit()
        frames = self.sequences[self.selected_bbox]["frame"]
        self.sequences[self.selected_bbox].loc[np.bitwise_and(frames >= self.first_selected_frame, frames <= self.last_selected_frame),"label"] = cls    
        self.imageWidgetRepaint.emit()
        self.repaint()
        
    
    def add_new_keypoint(self): 
        if self.mode != "one-select" and np.any(sq["frame"]==self.last_selected_frame):
            return
        
        self.tableUpdate.emit()
        
        sq = self.sequences[self.selected_bbox]
        
        
        if not sq.shape[0] == 0 and sq["frame"].iloc[0]<self.last_selected_frame<sq["frame"].iloc[sq.shape[0]-1]:
            
            i = np.argwhere(sq["frame"]<self.last_selected_frame)[-1,0]
            frame_before = sq.iloc[i]
            frame_after = sq.iloc[i+1]

            min_x1,min_x2,max_x1,max_x2 =  sq['x'].iloc[i],sq['x'].iloc[i+1],sq['h'].iloc[i],sq['h'].iloc[i+1]
            min_y1,min_y2,max_y1,max_y2 = sq['y'].iloc[i],sq['y'].iloc[i+1],sq['w'].iloc[i],sq['w'].iloc[i+1]
            
            div = (self.last_selected_frame-int(frame_before["frame"]))/(int(frame_after["frame"]-frame_before["frame"]))
    
            buff = pd.DataFrame({"frame":[self.last_selected_frame],"track_id":[0], "x":[(min_x2-min_x1)*div + min_x1], "y":[(min_y2-min_y1)*div + min_y1],
                                    "h":[(max_x2-max_x1)*div + max_x1], "w":[(max_y2-max_y1)*div + max_y1],"label":[sq['label'].iloc[i]]})
            
            buff = pd.concat([sq,buff],ignore_index=True).sort_values("frame",ascending=True)
        elif sq.shape[0]==0:
            buff = pd.DataFrame({"frame":[self.last_selected_frame],"track_id":[0], "x":[0], "y":[0],
                                    "h":[30], "w":[40],"label":[0]})
        else: 
            if self.last_selected_frame < sq["frame"].iloc[0]:
                buff = sq[0:1].copy()
            else:
                buff = sq[sq.shape[0]-1:sq.shape[0]].copy()
            buff.loc[:,"frame"] = self.last_selected_frame            
            buff = pd.concat([buff,sq],ignore_index=True)              
                  
        self.sequences[self.selected_bbox] = buff.sort_values("frame",ascending=True)
        self.imageWidgetRepaint.emit()
        self.repaint()

    def delete_keypoint(self):
        self.tableUpdate.emit()
        frames = self.sequences[self.selected_bbox]["frame"]
        self.sequences[self.selected_bbox] = self.sequences[self.selected_bbox].drop(frames.index[np.bitwise_and(frames >= self.first_selected_frame, frames <= self.last_selected_frame)])
        self.imageWidgetRepaint.emit()
        self.repaint()
    
    def delete_sequance(self):
        self.tableUpdate.emit()
        self.sequences.pop(self.selected_bbox)
        self.boxCountUpdated.emit(len(self.sequences),self.frame_box_size)
        if self.selected_bbox >= len(self.sequences) and len(self.sequences) != 0:
            self.selected_bbox -= 1

        self.imageWidgetRepaint.emit()
        self.repaint()
    
    def add_sequance(self):
        self.tableUpdate.emit()
        self.sequences.append(pd.DataFrame({"frame":[self.last_selected_frame],"track_id":[0], "x":[0], "y":[0],
                                    "h":[100], "w":[200],"label":[0]}))
        self.selected_bbox = len(self.sequences)-1
        self.imageWidgetRepaint.emit()
        self.boxCountUpdated.emit(len(self.sequences),self.frame_box_size)
        self.repaint()


        