from PyQt6.QtCore import Qt, pyqtSignal,QKeyCombination
from PyQt6.QtWidgets import QMainWindow, QSlider, QMenu, QSizePolicy, QFileDialog, QProgressDialog,QSplitter, QScrollArea
from PyQt6.QtGui import QAction, QKeyEvent,QPixmap,QKeySequence,QWheelEvent
import cv2
from ultralytics import YOLO
import pandas as pd
# from numba import njit

from imagewidget import ImageWidget
from timeline import TimelineWidget

# @njit(nopython=False)
def detectLabels(videoPath):
    model = YOLO("yolov8m-pose.pt")
    video = cv2.VideoCapture(videoPath)
    framesCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Frames count: {framesCount}")
    progress = QProgressDialog("Tracking", "Cancel", 0, framesCount)
    progress.setWindowModality(Qt.WindowModality.WindowModal)

    labelsDict = {"frame": [], "track_id": [], "x": [], "y": [], "h": [], "w": [], "label": []}
    for t in range(17):
        labelsDict['x'+str(t)] = []
        labelsDict['y'+str(t)] = []

    for i in range(framesCount):
        progress.setValue(i)
        if progress.wasCanceled():
            break
        ret, frame = video.read()
        if not ret:
            progress.cancel()
            break
        
        res = model.track(frame, persist=True)

        if res[0].boxes.id is not None:  # Add this check
            cls = res[0].boxes.cls.int().cpu().tolist()
            boxes = res[0].boxes.xywh.cpu()
            track_ids = res[0].boxes.id.int().cpu().tolist()
            keypoints = res[0].keypoints.xy.cpu().tolist()
        else:
            cls = []
            boxes = []
            track_ids = []

        for box, track_id, cl, keys in zip(boxes, track_ids, cls, keypoints):
            if cl != 0:
                continue

            x, y, w, h = box

            labelsDict['frame'].append(i)
            labelsDict['track_id'].append(track_id)
            labelsDict['x'].append(x.item())
            labelsDict['y'].append(y.item())
            labelsDict['w'].append(w.item())
            labelsDict['h'].append(h.item())
            labelsDict['label'].append(0)
            for t in range(17):
                labelsDict['x'+str(t)].append(int(keys[t][0]))
                labelsDict['y'+str(t)].append(int(keys[t][1]))
    else:
        progress.setValue(framesCount)
    
    video.release()
    return (framesCount, labelsDict)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Labeler")
        self.grabKeyboard()
        menuBar = self.menuBar()
        fileMenu = QMenu("File", self)
        menuBar.addMenu(fileMenu)

        openVideo = QAction("Open video and calculate labels", self)
        importLabels = QAction("Open video and import labels", self)
        exportLabels = QAction("Export labels to csv", self)

        openVideo.triggered.connect(self.openVideoCB)
        importLabels.triggered.connect(self.importLabelsCb)
        exportLabels.triggered.connect(self.exportLabelsCb)

        fileMenu.addActions([openVideo, importLabels, exportLabels])

        self.imageWidget = ImageWidget()
        self.timelineWidget = TimelineWidget()
        self.timelineWidget.frameSelected.connect(self.imageWidget.setFrame)
        self.timelineWidget.keypointsDisplay.selectedBboxUpdate.connect(self.imageWidget.selectBBox)
        self.imageWidget.selectedBBoxIdChanged.connect(self.timelineWidget.keypointsDisplay.selectBBox)
        self.timelineWidget.keypointsDisplay.classUpdate.connect(self.imageWidget.changeClass)

        mainSplitter = QSplitter(Qt.Orientation.Vertical, self)
        mainSplitter.setStretchFactor(0, 1)
        mainSplitter.setStretchFactor(1, 0)
        print(mainSplitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        mainSplitter.addWidget(self.imageWidget)
        mainSplitter.addWidget(self.timelineWidget)

        self.setCentralWidget(mainSplitter)

        self.sequences = []

    def openVideoCB(self):
        videoPath = QFileDialog.getOpenFileName(self, "Open video")
        if videoPath[0] == "":
            return
        
        framesCount, labelsDict = detectLabels(videoPath[0])
        
        labels = pd.DataFrame(labelsDict)
        for i in labels["track_id"].unique():
            self.sequences.append(labels[labels["track_id"]==i].copy().sort_values(by="frame",ascending=True))
        self.imageWidget.setSequences(self.sequences)
        self.timelineWidget.setSequences(self.sequences)
        self.imageWidget.setVideo(videoPath[0])
        self.timelineWidget.setFramesCount(framesCount)
        
        print("done")

    def importLabelsCb(self):
        videoPath = QFileDialog.getOpenFileName(self, "Open video", filter="*.mp4")
        labelsPath = QFileDialog.getOpenFileName(self, "Import labels", filter="*.csv")

        if videoPath[0] == '' or labelsPath[0] == '':
            return
        
        video = cv2.VideoCapture(videoPath[0])
        framesCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Frames count: {framesCount}")
        video.release()

        df = pd.read_csv(labelsPath[0])
        for i in df["track_id"].unique():
            self.sequences.append(df[df["track_id"]==i].copy().sort_values(by="frame",ascending=True))
        self.imageWidget.setVideo(videoPath[0])
        self.imageWidget.setSequences(self.sequences)
        self.timelineWidget.setSequences(self.sequences)
        self.timelineWidget.setFramesCount(framesCount)

    def exportLabelsCb(self):
        labels_path = QFileDialog.getSaveFileName(self, "Save csv", None, "*.csv")[0]
        if labels_path == '':
            return
        pd.concat(self.sequences, ignore_index=True).to_csv(labels_path, index=False)
    
    def wheelEvent(self, event:QWheelEvent):
        
        numDegrees = event.angleDelta().x() // 8

        self.timelineWidget.timeline.setValue(self.timelineWidget.timeline.value()-numDegrees)

        event.accept()

        
    def keyPressEvent(self, e: QKeyEvent | None) -> None:
        key,modifier = e.key(),e.modifiers()
    
        if modifier == Qt.KeyboardModifier.ShiftModifier or key==Qt.Key.Key_Shift:
            self.timelineWidget.keypointsDisplay.mode = "multiselect"
        else:
            self.timelineWidget.keypointsDisplay.mode = "one-select"
        
        match key:
            case Qt.Key.Key_Right:
                self.timelineWidget.timeline.setValue(1+self.timelineWidget.timeline.value())
            case Qt.Key.Key_Left:
                self.timelineWidget.timeline.setValue(self.timelineWidget.timeline.value()-1)
            case Qt.Key.Key_Down:
                if self.timelineWidget.keypointsDisplay.selected_bbox + 1 < len(self.timelineWidget.keypointsDisplay.sequences):
                    self.timelineWidget.keypointsDisplay.selectBBox(self.timelineWidget.keypointsDisplay.selected_bbox+1)
            case Qt.Key.Key_Up:
                if self.timelineWidget.keypointsDisplay.selected_bbox > 0:
                    self.timelineWidget.keypointsDisplay.selectBBox(self.timelineWidget.keypointsDisplay.selected_bbox-1)
            case Qt.Key.Key_1:
                self.timelineWidget.keypointsDisplay.draw_class(0)
            case Qt.Key.Key_2:
                self.timelineWidget.keypointsDisplay.draw_class(1)
            case Qt.Key.Key_3:
                self.timelineWidget.keypointsDisplay.draw_class(2)
            case Qt.Key.Key_4:
                self.timelineWidget.keypointsDisplay.draw_class(3)
            case Qt.Key.Key_5:
                self.timelineWidget.keypointsDisplay.draw_class(4)
            case Qt.Key.Key_6:
                self.timelineWidget.keypointsDisplay.draw_class(5)
            case Qt.Key.Key_7:
                self.timelineWidget.keypointsDisplay.draw_class(6)
            case Qt.Key.Key_8:
                self.timelineWidget.keypointsDisplay.draw_class(7)
            case Qt.Key.Key_9:
                self.timelineWidget.keypointsDisplay.draw_class(8)
            case Qt.Key.Key_A:
                self.timelineWidget.keypointsDisplay.add_new_keypoint()
            # case Qt.Key.Key_0:
            #     self.timelineWidget.keypointsDisplay.draw_class(0) 
        

        
        
        

        
    

        
