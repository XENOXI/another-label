from PyQt6.QtCore import Qt, QRect, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPaintEvent, QImage, QPainter, QResizeEvent
from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6 import QtGui
import cv2
import numpy as np
import pandas as pd
from pandas import Series
import psutil

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
    
    def containsCoords(self, coords):
        lt = self.lt_corner()
        rb = self.rb_corner()
        return lt[0] <= coords[0] <= rb[0] and lt[1] <= coords[1] <= rb[1]
    
class ImageWidget(QWidget):
    selectedFrameChanged = pyqtSignal(int)
    selectedBBoxIdChanged = pyqtSignal(int)
    sequencesChanged = pyqtSignal(int)
    timelineRepaint = pyqtSignal()
    tableUpdate = pyqtSignal()
    def __init__(self) -> None:
        super().__init__()
        
        self.selectedBBoxId = 0
        self.selectedCorner = None
        self.sequences = []
        self.shape = None
        self.resizedShape = None
        self.frame = None
        self.cap = None
        self.lastMousePos = None
        self.startBBoxPos = None
        self.widthOffset = 0
        self.heightOffset = 0

        self.aspectRatio = 360/640
        freeRam = psutil.virtual_memory()[0]/8 #FREE RAM IN BYTES
        self.maxDataSize = freeRam//4
        self.ramBuffer = None
        self.maxImgCnt = 0
        self.bufferStartFrame = 0
        self.chunkToLoad = self.maxImgCnt//10

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def setSequences(self, sequences):
        self.sequences = sequences        

    def setVideo(self, filepath):
        self.cap = cv2.VideoCapture(filepath)
        width  = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
        height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
        self.shape = (height, width)
        self.aspectRatio = height/width
        self.frame = 0
        
        self.maxImgCnt = int(self.maxDataSize/(3*width*height))
        
        self.ramBuffer = np.empty((self.maxImgCnt,int(height),int(width),3),dtype=np.uint8)
        for i in range(self.maxImgCnt):
            _,self.ramBuffer[i] = self.cap.read()
    
    def updateBuffer(self):
        if self.frame >= self.bufferStartFrame and self.frame < self.maxImgCnt + self.bufferStartFrame:
            return
        
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.frame-self.maxImgCnt//2) # SET FRAME TO CENTER
        self.bufferStartFrame = self.frame-self.maxImgCnt//2
        
        for i in range(self.maxImgCnt):
            _,self.ramBuffer[i] = self.cap.read()

        

        

    def setFrame(self, frame):
        self.frame = frame
        self.repaint()
    
    def getCoordsFromMouseEvent(self, e: QMouseEvent):
        height, width = self.shape
        x = int((e.pos().x() - self.widthOffset) / self.resizedShape[0] * width)
        y = int((e.pos().y() - self.heightOffset) / self.resizedShape[1] * height)
        return (x, y)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if self.shape is None:
            return
        coords = self.getCoordsFromMouseEvent(e)
        if e.button() == Qt.MouseButton.LeftButton:
            self.lastMousePos = coords
            if self.selectedBBoxId is not None:
                self.setCursor(Qt.CursorShape.SizeAllCursor)
            else:
                self.startBBoxPos = coords
        if e.button() == Qt.MouseButton.RightButton:
            for track_id, seq in enumerate(self.sequences):
                df = seq[seq['frame'] == self.frame]
                if len(df) == 0:
                    if seq["frame"].iloc[0]>self.frame or self.frame>seq["frame"].iloc[seq.shape[0]-1]:
                        continue
                    i = np.argwhere(seq["frame"]<self.frame)[-1,0]
                    frame_before = seq.iloc[i]
                    frame_after = seq.iloc[i+1]
                    div = (self.frame-int(frame_before["frame"]))/(int(frame_after["frame"]-frame_before["frame"]))
                    r = (frame_after-frame_before)*div + frame_before
                else:
                    r = df.iloc[0]
                bbox = BBox(r)

                if bbox.containsCoords(coords):
                    self.selectedBBoxId = track_id
                    self.selectedBBoxIdChanged.emit(self.selectedBBoxId)
                    self.repaint()
                    return
                
            self.selectedBBoxId = None
            self.repaint()
            

    def mouseReleaseEvent(self, e: QMouseEvent | None) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.selectedCorner = None
        if e.button() == Qt.MouseButton.LeftButton:
            self.lastMousePos = None

            if self.startBBoxPos:
                self.tableUpdate.emit()

                coords = self.getCoordsFromMouseEvent(e)
                x = (self.startBBoxPos[0] + coords[0])//2
                y = (self.startBBoxPos[1] + coords[1])//2
                w = abs(self.startBBoxPos[0] - coords[0])
                h = abs(self.startBBoxPos[1] - coords[1])               

    
                
                datas = pd.DataFrame({"frame":[self.frame],"track_id":[0], "x":[x], "y":[y],
                                    "h":[h], "w":[w],"label":[0]})
                self.sequences.append(datas)
                self.selectedBBoxIdChanged.emit(len(self.sequences)-1)
                self.sequencesChanged.emit(len(self.sequences))
                self.timelineRepaint.emit()

                self.startBBoxPos = None
                
    
    def mouseMoveEvent(self, e: QMouseEvent | None) -> None:
        if self.selectedBBoxId is not None and self.lastMousePos is not None:
            lastX, lastY = self.lastMousePos
            x, y = self.getCoordsFromMouseEvent(e)

            selectedBBoxIdData = self.sequences[self.selectedBBoxId]
            datas = selectedBBoxIdData[selectedBBoxIdData['frame'] == self.frame]
            if len(datas) == 0:    
                if selectedBBoxIdData["frame"].iloc[0]>self.frame or self.frame>selectedBBoxIdData["frame"].iloc[selectedBBoxIdData.shape[0]-1]:
                    return
                self.tableUpdate.emit()
                i = np.argwhere(selectedBBoxIdData["frame"]<self.frame)[-1,0]
                frame_before = selectedBBoxIdData.iloc[i]
                frame_after = selectedBBoxIdData.iloc[i+1]


                min_x1,min_x2,max_x1,max_x2 =  selectedBBoxIdData['x'].iloc[i],selectedBBoxIdData['x'].iloc[i+1],selectedBBoxIdData['h'].iloc[i],selectedBBoxIdData['h'].iloc[i+1]
                min_y1,min_y2,max_y1,max_y2 = selectedBBoxIdData['y'].iloc[i],selectedBBoxIdData['y'].iloc[i+1],selectedBBoxIdData['w'].iloc[i],selectedBBoxIdData['w'].iloc[i+1]
                
                div = (self.frame-int(frame_before["frame"]))/(int(frame_after["frame"]-frame_before["frame"]))

                datas = pd.DataFrame({"frame":[self.frame],"track_id":[0], "x":[(min_x2-min_x1)*div + min_x1], "y":[(min_y2-min_y1)*div + min_y1],
                                    "h":[(max_x2-max_x1)*div + max_x1], "w":[(max_y2-max_y1)*div + max_y1],"label":[selectedBBoxIdData['label'].iloc[i]]})
                self.sequences[self.selectedBBoxId] = pd.concat([selectedBBoxIdData,datas],ignore_index=True).sort_values("frame",ascending=True)
                self.timelineRepaint.emit()
                
            
            data = datas.iloc[0]

            bbox = BBox(data)

            last = np.array(self.lastMousePos)

            
            if np.linalg.norm(np.array(bbox.rt_corner()) - last) <= 20 or self.selectedCorner == 0:
                self.selectedCorner = 0
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'w'] += x - lastX
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'h'] -= y - lastY
                self.repaint()
            elif np.linalg.norm(np.array(bbox.lt_corner()) - last) <= 20 or self.selectedCorner == 1:
                self.selectedCorner = 1
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'w'] -= x - lastX
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'h'] -= y - lastY
                self.repaint()
            elif np.linalg.norm(np.array(bbox.rb_corner()) - last) <= 20 or self.selectedCorner == 2:
                self.selectedCorner = 2
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'w'] += x - lastX
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'h'] += y - lastY
                self.repaint()
            elif np.linalg.norm(np.array(bbox.lb_corner()) - last) <= 20 or self.selectedCorner == 3:
                self.selectedCorner = 3
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'w'] -= x - lastX
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'h'] += y - lastY
                self.repaint()
            elif(bbox.containsCoords(self.lastMousePos)):
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'x'] += x - lastX
                selectedBBoxIdData.loc[selectedBBoxIdData['frame'] == self.frame,'y'] += y - lastY
                self.repaint()
            self.lastMousePos = (x, y)
        if self.startBBoxPos:
            self.lastMousePos = self.getCoordsFromMouseEvent(e)
            self.repaint()

            
    
    def paintEvent(self, a0: QPaintEvent | None) -> None:
        painter = QPainter(self)
        
        if not self.cap:
            brush = QtGui.QBrush()
            brush.setColor(QtGui.QColor('black'))
            brush.setStyle(Qt.BrushStyle.SolidPattern)
            rect = QRect(0, 0, painter.device().width(), painter.device().height())
            painter.fillRect(rect, brush)
            return
        
        self.updateBuffer()
        image = self.ramBuffer[self.frame-self.bufferStartFrame]
        
        
        for track_id, seq in enumerate(self.sequences):
            df = seq[seq['frame'] == self.frame]
            if len(df) == 0:
                if seq.shape[0]==0 or seq["frame"].iloc[0]>self.frame or self.frame>seq["frame"].iloc[seq.shape[0]-1]:
                    continue
                i = np.argwhere((seq["frame"]<self.frame).to_numpy())[-1,0]
                frame_before = seq.iloc[i]
                frame_after = seq.iloc[i+1]
                div = (self.frame-int(frame_before["frame"]))/(int(frame_after["frame"]-frame_before["frame"]))
                r = (frame_after-frame_before)*div + frame_before
            else:
                r = df.iloc[0]
            
            color = (0, 255, 0)
            if r['label'] == 1:
                color = (255, 0, 0)
            if track_id == self.selectedBBoxId:
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

        if self.startBBoxPos:
            # print(self.startBBoxPos, self.lastMousePos)
            image = cv2.rectangle(image, self.startBBoxPos, self.lastMousePos, (255, 255, 255), 2)
        
        if self.aspectRatio > self.height()/self.width():
            newWidth = int(self.height()/self.aspectRatio)
            self.resizedShape = (newWidth, self.height())
            self.heightOffset = 0
            self.widthOffset = (self.width() - newWidth)//2
        else:
            newHeight = int(self.aspectRatio*self.width())
            self.resizedShape = (self.width(), newHeight)
            self.heightOffset = (self.height() - newHeight)//2
            self.widthOffset = 0

        image = cv2.resize(image, self.resizedShape)
        height, width, _ = image.shape
        bytesPerLine = width*3
        size = QSize(width, height)
        qImg = QImage(image.data, width, height, bytesPerLine, QImage.Format.Format_BGR888)
        painter.drawImage(QRect(QPoint(self.widthOffset, self.heightOffset), size), qImg)

    def sizeHint(self) -> QSize:
        return QSize(640, 360)
    
    def selectBBox(self, bbox_id):
        self.selectedBBoxId = bbox_id
        self.repaint()

    
