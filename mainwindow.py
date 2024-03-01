from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QSlider, QMenu, QVBoxLayout, QFileDialog, QProgressDialog,QSplitter, QScrollArea
from PyQt6.QtGui import QAction,QPixmap
import cv2
from ultralytics import YOLO
import pandas as pd

from imagewidget import ImageWidget
from timeline import TimelineWidget

def detectLabels(videoPath):
    model = YOLO("yolov8m.pt")
    video = cv2.VideoCapture(videoPath)
    framesCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Frames count: {framesCount}")
    progress = QProgressDialog("Tracking", "Cancel", 0, framesCount)
    progress.setWindowModality(Qt.WindowModality.WindowModal)

    labelsDict = {"frame": [], "track_id": [], "x": [], "y": [], "h": [], "w": [], "label": []}

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
        else:
            cls = []
            boxes = []
            track_ids = []

        for cl, box, track_id in zip(cls, boxes, track_ids):
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
    else:
        progress.setValue(framesCount)
    
    video.release()
    return (framesCount, labelsDict)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Labeler")

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

        cw = QWidget(self)

        main_layout = QVBoxLayout()

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(self.imageWidget)
        main_splitter.addWidget(self.timelineWidget)

        main_layout.addWidget(main_splitter)

        cw.setLayout(main_layout)
        self.setCentralWidget(cw)

        self.labels = None

    def openVideoCB(self):
        videoPath = QFileDialog.getOpenFileName(self, "Open video")
        if videoPath[0] == "":
            return
        
        framesCount, labelsDict = detectLabels(videoPath[0])
        
        self.labels = pd.DataFrame(labelsDict)
        self.imageWidget.setLabels(self.labels)
        self.timelineWidget.setLabels(self.labels)
        self.imageWidget.setVideo(videoPath[0])
        self.timelineWidget.setFramesCount(framesCount)
        
        print("done")

    def importLabelsCb(self):
        videoPath = QFileDialog.getOpenFileName(self, "Open video")
        labelsPath = QFileDialog.getOpenFileName(self, "Import labels")

        if videoPath[0] == '' or labelsPath[0] == '':
            return
        
        video = cv2.VideoCapture(videoPath[0])
        framesCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Frames count: {framesCount}")
        video.release()

        df = pd.read_csv(labelsPath[0])
        self.imageWidget.setVideo(videoPath[0])
        self.imageWidget.setLabels(df)
        self.timelineWidget.setLabels(df)
        self.timelineWidget.setFramesCount(framesCount)

    def exportLabelsCb(self):
        labels_path = QFileDialog.getSaveFileName(self, "Save csv", None, "*.csv")[0]
        if labels_path == '':
            return
        self.labels.to_csv(labels_path, index=False)
        
