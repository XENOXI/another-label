from PyQt6.QtCore import QSize,QRect,Qt,QPoint, pyqtSignal
from PyQt6.QtGui import QPaintEvent, QPainter,QColor,QBrush,QShortcut,QKeyEvent,QLinearGradient,QMouseEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy
import pandas as pd
import numpy as np

class KeypointsDisplay(QWidget):
    boxCountUpdated = pyqtSignal(int, int)
    selectedBboxUpdate = pyqtSignal(int)
    classUpdate = pyqtSignal(int,int,int)
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
        self.seqs_copy = []
        self.sequences = []
        self.selectBBox(0)
        self.first_frame_to_render = 0
        self.last_frame_to_render = 0
        self.width_per_box = 0
        

        self.labels_color = [Qt.GlobalColor.magenta,Qt.GlobalColor.blue]
        self.selected_colors = [QColor(180,180,180),QColor(150,150,150),QColor(230,230,230)]
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)
        

        self.width_per_box = self.width()//self.frame_box_size-1


        self.last_frame_to_render = self.width_per_box + self.first_frame_to_render

        if self.last_selected_frame >= self.last_frame_to_render:
            self.last_frame_to_render = self.last_selected_frame+1
            self.first_frame_to_render = self.last_frame_to_render-self.width_per_box
        elif self.first_selected_frame < self.first_frame_to_render:
            self.first_frame_to_render = self.first_selected_frame
            self.last_frame_to_render = self.first_frame_to_render + self.width_per_box

        

        

        for i in range(0,self.width_per_box):
            painter.drawRect(i*self.frame_box_size, 10, self.frame_box_size, self.frame_box_size*len(self.seqs_copy))

        

        brush = QBrush(self.selected_colors[0],Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        for i in range(max(self.first_selected_frame,self.first_frame_to_render),self.last_selected_frame+1):
            painter.drawRect(self.frame_box_size*(i-self.first_frame_to_render), 10, self.frame_box_size, self.frame_box_size*len(self.seqs_copy))

        brush = QBrush(self.selected_colors[1],Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        
        painter.drawRect(0, 10+self.frame_box_size*self.selected_bbox, self.width_per_box * self.frame_box_size , self.frame_box_size)

        grad = QLinearGradient(0,0,self.frame_box_size,0)
        brush = QBrush(Qt.GlobalColor.black,Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)
        painter.translate(self.frame_box_size/2,3+self.frame_box_size//2)
        
        for seq in self.seqs_copy:  
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

        painter.fillRect(self.width_per_box*self.frame_box_size-self.frame_box_size//2 + 1, -len(self.seqs_copy)*self.frame_box_size-3, self.frame_box_size*2, self.frame_box_size*len(self.seqs_copy),self.palette().color(self.backgroundRole()))
        painter.end()

    


    def set_frame(self,frame):
        if self.mode == "one-select":
            self.last_selected_frame = frame
            self.first_selected_frame = frame
        elif frame>self.last_selected_frame:
            self.last_selected_frame = frame
        elif frame<self.first_selected_frame:
            self.first_selected_frame = frame
        elif self.last_selected_frame-frame < frame - self.first_selected_frame:
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
        self.seqs_copy = []
        for i in sequences:
            self.seqs_copy.append(i.copy())


        self.sequences.clear()
        

        for sq in self.seqs_copy:
            tab = sq.copy()
            bf2 = sq.sort_values("frame",ascending=True)
            i = 0

            while i+1<bf2['frame'].shape[0]:
                frame1 = bf2['frame'].iloc[i]
                frame2 = bf2['frame'].iloc[i+1]
                min_x1,min_x2,max_x1,max_x2 = bf2['x'].iloc[i],bf2['x'].iloc[i+1],bf2['h'].iloc[i],bf2['h'].iloc[i+1]
                min_y1,min_y2,max_y1,max_y2 = bf2['y'].iloc[i],bf2['y'].iloc[i+1],bf2['w'].iloc[i],bf2['w'].iloc[i+1]
                for frame in range(frame1+1,frame2):
                    tab = pd.concat([tab,pd.DataFrame({"frame":[frame],"track_id":[0], "x":[(min_x2-min_x1)*(frame-frame1)/(frame2-frame1) + min_x1], "y":[(min_y2-min_y1)*(frame-frame1)/(frame2-frame1) + min_y1],
                                                        "h":[(max_x2-max_x1)*(frame-frame1)/(frame2-frame1) + max_x1], "w":[(max_y2-max_y1)*(frame-frame1)/(frame2-frame1) + max_y1],"label":[bf2['label'].iloc[i]]})],ignore_index=True)
                i+=1

            self.sequences.append(tab.sort_values(by="frame",ascending=True))


       
        
    
    def update_seq(self,seq_i):       
        sq = self.seqs_copy[seq_i]
        tab = sq.copy()
        for tr in sq['track_id'].unique():
            i = 0
            while i+1<sq['frame'].shape[0]:
                frame1 = sq['frame'].iloc[i]
                frame2 = sq['frame'].iloc[i+1]
                min_x1,min_x2,max_x1,max_x2 = sq['x'].iloc[i],sq['x'].iloc[i+1],sq['h'].iloc[i],sq['h'].iloc[i+1]
                min_y1,min_y2,max_y1,max_y2 = sq['y'].iloc[i],sq['y'].iloc[i+1],sq['w'].iloc[i],sq['w'].iloc[i+1]
                for frame in range(frame1+1,frame2):
                    tab.loc[len(tab.index)] = [frame,tr, (min_x2-min_x1)*(frame-frame1)/(frame2-frame1) + min_x1, (min_y2-min_y1)*(frame-frame1)/(frame2-frame1) + min_y1, (max_x2-max_x1)*(frame-frame1)/(frame2-frame1) + max_x1, (max_y2-max_y1)*(frame-frame1)/(frame2-frame1) + max_y1,sq['label'].iloc[i]]
        self.sequences.pop(seq_i)
        self.sequences.append(tab)    
        self.repaint()

    def sizeHint(self) -> QSize:
        return QSize(1000,10*self.frame_box_size)
    
    
    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            point = e.pos()
            if point.y() > 10 and point.y()<10 + self.frame_box_size*len(self.seqs_copy):
                point.x()//self.frame_box_size
                self.selected_bbox = (point.y()-10)//self.frame_box_size   
                self.selectedBboxUpdate.emit(self.selected_bbox)            
                self.repaint()
    
    def selectBBox(self, bbox_id):
        self.selected_bbox = bbox_id
        self.selectedBboxUpdate.emit(self.selected_bbox)
        self.repaint()

    def draw_class(self,cls):
        if cls >= len(self.labels_color):
            return
        frames = self.seqs_copy[self.selected_bbox]["frame"]
        self.seqs_copy[self.selected_bbox].loc[np.bitwise_and(frames >= self.first_selected_frame, frames <= self.last_selected_frame),"label"] = cls
        self.sequences[self.selected_bbox].loc[np.bitwise_and(frames >= self.first_selected_frame, frames <= self.last_selected_frame),"label"] = cls
        self.classUpdate.emit(cls,self.first_selected_frame,self.last_selected_frame)
        self.repaint()
        
    
    def add_new_keypoint(self):
        if self.mode != "one-select" and np.any(sq["frame"]==self.last_selected_frame):
            return
        
        sq = self.seqs_copy.pop(self.selected_bbox)
        

        if not sq.shape[0] == 0 and sq["frame"].iloc[0]<self.last_selected_frame<sq["frame"].iloc[sq.shape[0]-1]:
            sq = pd.concat([sq,self.sequences[self.sequences["frame"] == self.last_selected_frame]],ignore_index=True)
        else: 
            sq_orig = self.sequences.pop(self.selected_bbox) 
            if self.last_selected_frame < sq["frame"].iloc[0]:
                buff = sq[0:1].copy()
                buff.loc[:,"frame"] = self.last_selected_frame
                buff2 = pd.concat([buff]*(sq["frame"].iloc[0]-self.last_selected_frame),ignore_index=True)

                buff2.loc[:,"frame"] = np.arange(self.last_selected_frame,sq["frame"].iloc[0],dtype=np.int64)

                buff2 = pd.concat([buff2,sq_orig],ignore_index=True).sort_values("frame",ascending=True)   

                sq = pd.concat([buff,sq],ignore_index=True)
               
                
            else:
                buff = sq[sq.shape[0]-1:sq.shape[0]].copy()
                buff.loc[:,"frame"] = self.last_selected_frame
                buff2 = pd.concat([buff]*(self.last_selected_frame-sq["frame"].iloc[sq.shape[0]-1]),ignore_index=True)
                
                buff2.loc[:,"frame"] = np.arange(sq["frame"].iloc[sq.shape[0]-1]+1,self.last_selected_frame+1)

                buff2 = pd.concat([sq_orig,buff2],ignore_index=True).sort_values("frame",ascending=True) 

                sq = pd.concat([sq,buff],ignore_index=True)                
                  

            self.sequences.insert(self.selected_bbox,buff2)
        
        sq = sq.sort_values("frame",ascending=True)
        self.seqs_copy.insert(self.selected_bbox,sq)
     
        self.repaint()