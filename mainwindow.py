from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QMenu, QSizePolicy, QFileDialog, QProgressDialog,QSplitter, QApplication
from PyQt6.QtGui import QAction, QKeyEvent,QShortcut,QKeySequence,QWheelEvent,QUndoStack,QUndoCommand
import cv2
from ultralytics import YOLO
import pandas as pd

from imagewidget import ImageWidget
from timeline import TimelineWidget

def detectLabels(videoPath):
    model = YOLO("yolov8m.pt")
    video = cv2.VideoCapture(videoPath)
    framesCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = video.get(cv2.CAP_PROP_FPS)
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
    return (framesCount, fps, labelsDict)


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
        self.timelineWidget.keypointsDisplay.selectedBboxUpdate.connect(self.imageWidget.selectBBox)
        self.imageWidget.selectedBBoxIdChanged.connect(self.timelineWidget.keypointsDisplay.selectBBox)
        self.imageWidget.sequencesChanged.connect(self.timelineWidget.labelList.set_bboxes_cnt)
        self.timelineWidget.keypointsDisplay.imageWidgetRepaint.connect(self.imageWidget.repaint)
        self.timelineWidget.keypointsDisplay.setFrame.connect(self.setFrame)
        self.timelineWidget.keypointsDisplay.tableUpdate.connect(self.make_undo_command)
        self.imageWidget.tableUpdate.connect(self.make_undo_command)
        self.imageWidget.timelineRepaint.connect(self.timelineWidget.keypointsDisplay.repaint)

        self.mUndoStack = QUndoStack(self)
        self.mUndoStack.setUndoLimit(10)

        self.undoShortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undoShortcut.activated.connect(self.mUndoStack.undo)

        self.redoShortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.redoShortcut.activated.connect(self.mUndoStack.redo)

        self.deleteShortcut = QShortcut(QKeySequence("Del"), self)
        self.deleteShortcut.activated.connect(self.timelineWidget.keypointsDisplay.delete_keypoint)

        self.deleteSequenceShortcut = QShortcut(QKeySequence("Backspace"), self)
        self.deleteSequenceShortcut.activated.connect(self.timelineWidget.keypointsDisplay.delete_sequance)

        self.newSequenceShortcut = QShortcut(QKeySequence("N"), self)
        self.newSequenceShortcut.activated.connect(self.timelineWidget.keypointsDisplay.add_sequance)

        self.newKeypointShortcut = QShortcut(QKeySequence('A'), self)
        self.newKeypointShortcut.activated.connect(self.timelineWidget.keypointsDisplay.add_new_keypoint)

        self.selectDownSequenceShortcut = QShortcut(QKeySequence("Down"), self)
        self.selectDownSequenceShortcut.activated.connect(self.selectDownSequence)

        self.selectUpSequenceShortcut = QShortcut(QKeySequence("Up"), self)
        self.selectUpSequenceShortcut.activated.connect(self.selectUpSequence)

        self.selectNextFrameShortcut = QShortcut(QKeySequence("Right"), self)
        self.selectNextFrameShiftedShortcut = QShortcut(QKeySequence("Shift+Right"), self)
        self.selectNextFrameShortcut.activated.connect(self.selectNextFrame)
        self.selectNextFrameShiftedShortcut.activated.connect(self.selectNextFrame)

        self.selectPrevFrameShortcut = QShortcut(QKeySequence("Left"), self)
        self.selectPrevFrameShiftedShortcut = QShortcut(QKeySequence("Shift+Left"), self)
        self.selectPrevFrameShortcut.activated.connect(self.selectPrevFrame)
        self.selectPrevFrameShiftedShortcut.activated.connect(self.selectPrevFrame)

        for i in range(9):
            digitShortcut = QShortcut(QKeySequence(f"{i+1}"), self)
            digitShortcut.activated.connect(lambda self = self,i=i: self.timelineWidget.keypointsDisplay.draw_class(i))


        mainSplitter = QSplitter(Qt.Orientation.Vertical, self)
        mainSplitter.setStretchFactor(0, 1)
        mainSplitter.setStretchFactor(1, 0)
        print(mainSplitter.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))
        mainSplitter.addWidget(self.imageWidget)
        mainSplitter.addWidget(self.timelineWidget)

        self.setCentralWidget(mainSplitter)

        self.sequences = []

    def selectDownSequence(self):
        if self.timelineWidget.keypointsDisplay.selected_bbox + 1 < len(self.timelineWidget.keypointsDisplay.sequences):
            self.timelineWidget.keypointsDisplay.selectBBox(self.timelineWidget.keypointsDisplay.selected_bbox+1)
    
    def selectUpSequence(self):
        if self.timelineWidget.keypointsDisplay.selected_bbox > 0:
            self.timelineWidget.keypointsDisplay.selectBBox(self.timelineWidget.keypointsDisplay.selected_bbox-1)
    
    def selectNextFrame(self):
        self.setFrame(self.timelineWidget.timeline.value()+1)
    
    def selectPrevFrame(self):
        self.setFrame(self.timelineWidget.timeline.value()-1)


    def openVideoCB(self):
        videoPath = QFileDialog.getOpenFileName(self, "Open video")
        if videoPath[0] == "":
            return
        
        framesCount, fps, labelsDict = detectLabels(videoPath[0])
        
        labels = pd.DataFrame(labelsDict)
        for i in labels["track_id"].unique():
            self.sequences.append(labels[labels["track_id"]==i].copy().sort_values(by="frame",ascending=True))
        self.imageWidget.setSequences(self.sequences)
        self.timelineWidget.setSequences(self.sequences)
        self.imageWidget.setVideo(videoPath[0])
        self.timelineWidget.setFramesProperties(framesCount, fps)
        
        print("done")

    def importLabelsCb(self):
        videoPath = QFileDialog.getOpenFileName(self, "Open video", filter="*.mp4")
        labelsPath = QFileDialog.getOpenFileName(self, "Import labels", filter="*.csv")

        if videoPath[0] == '' or labelsPath[0] == '':
            return
        
        video = cv2.VideoCapture(videoPath[0])
        framesCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        print(f"Frames count: {framesCount}")
        video.release()

        df = pd.read_csv(labelsPath[0])
        for i in df["track_id"].unique():
            self.sequences.append(df[df["track_id"]==i].copy().sort_values(by="frame",ascending=True))
        self.imageWidget.setVideo(videoPath[0])
        self.imageWidget.setSequences(self.sequences)
        self.timelineWidget.setSequences(self.sequences)
        self.timelineWidget.setFramesProperties(framesCount, fps)

    def exportLabelsCb(self):
        labels_path = QFileDialog.getSaveFileName(self, "Save csv", None, "*.csv")[0]
        if labels_path == '':
            return
        pd.concat(self.sequences, ignore_index=True).to_csv(labels_path, index=False)
    
    def wheelEvent(self, event:QWheelEvent):
        
        numDegrees = event.angleDelta().x() // 8

        self.timelineWidget.timeline.setValue(self.timelineWidget.timeline.value()-numDegrees)

        event.accept()

    def setFrame(self,frame:int):
        self.timelineWidget.timeline.setValue(frame)
    
    def make_undo_command(self):
        self.mUndoStack.push(UndoCommand(self))

    
    
        
class UndoCommand(QUndoCommand):
    def __init__(self, parent:MainWindow):
        super().__init__()
        self.parent = parent
        self.prev_seqs = []
        for sq in parent.sequences:
            self.prev_seqs.append(sq.copy())

        self.seqs = []
        for sq in parent.sequences:
            self.seqs.append(sq.copy())

    def undo(self):
        print("hello")
        self.seqs = []
        for sq in self.parent.sequences:
            self.seqs.append(sq.copy())

        self.parent.sequences.clear()
        for sq in self.prev_seqs:
            self.parent.sequences.append(sq.copy())

        self.parent.update()
        self.parent.timelineWidget.labelList.set_bboxes_cnt(len(self.prev_seqs))
        self.parent.imageWidget.repaint()
        self.parent.timelineWidget.keypointsDisplay.repaint()

    def redo(self):
        self.parent.sequences.clear()
        for sq in self.seqs:
            self.parent.sequences.append(sq.copy())

        self.parent.update()
        self.parent.timelineWidget.labelList.set_bboxes_cnt(len(self.seqs))
        self.parent.imageWidget.repaint()
        self.parent.timelineWidget.keypointsDisplay.repaint()
    
    
        
        
        

        
