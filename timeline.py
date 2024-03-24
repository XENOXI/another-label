from PyQt6.QtWidgets import QWidget, QSlider, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QSplitter, QSizePolicy, QLabel, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIntValidator

from keypointsdisplay import KeypointsDisplay
from labellist import LabelList


class TimelineWidget(QWidget):
    frameSelected = pyqtSignal(int)
    def __init__(self):
        super().__init__()

        self.timeline = QSlider(Qt.Orientation.Horizontal, self)
        self.timeline.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.timeLabel = QLabel("0:00:00", self)
        self.currentFrameEdit = QLineEdit("0")
        self.currentFrameEdit.setValidator(QIntValidator(0, 0))

        self.framesCount = 0
        self.fps = 0

        self.labelList = LabelList()
        keypointsDisplayScroll = QScrollArea(self)
        keypointsDisplayScroll.setWidgetResizable(True)
        keypointsDisplayScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        keypointsDisplaySplitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.keypointsDisplay = KeypointsDisplay()
        

        keypointsDisplaySplitter.addWidget(self.labelList)
        keypointsDisplaySplitter.addWidget(self.keypointsDisplay)
        keypointsDisplayScroll.setWidget(keypointsDisplaySplitter)

        keypointsDisplaySplitter.setStretchFactor(0, 0)
        keypointsDisplaySplitter.setStretchFactor(1, 1)

        mainLayout = QVBoxLayout(self)
        controlsLayout = QHBoxLayout(self)

        controlsLayout.addWidget(self.timeLabel)
        controlsLayout.addWidget(self.timeline)

        mainLayout.addLayout(controlsLayout)
        mainLayout.addWidget(self.currentFrameEdit, 0, Qt.AlignmentFlag.AlignRight)
        mainLayout.addWidget(keypointsDisplayScroll)

        self.setLayout(mainLayout)

        self.timeline.valueChanged.connect(self.sliderValueChanged)
        self.currentFrameEdit.textChanged.connect(self.currentFrameEditChanged)
        self.keypointsDisplay.boxCountUpdated.connect(self.labelList.set_frame_box_size)
        self.keypointsDisplay.selectedBboxUpdate.connect(self.labelList.set_selected_bbox)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def setFramesProperties(self, framesCount, fps):
        self.timeline.setMaximum(framesCount-1)
        self.keypointsDisplay.set_frame_cnt(framesCount)
        self.framesCount = framesCount
        self.currentFrameEdit.setValidator(QIntValidator(0, framesCount))
        self.fps = fps

    def setSequences(self, sequences):
        self.keypointsDisplay.set_sequences(sequences)
        

    def sliderValueChanged(self, frame):
        self.frameSelected.emit(frame)
        self.keypointsDisplay.set_frame(frame)

        self.currentFrameEdit.blockSignals(True)
        self.currentFrameEdit.setText(str(frame))
        self.currentFrameEdit.blockSignals(False)

        seconds = round(frame/self.fps)
        minutes = seconds//60
        hours = seconds//3600

        self.timeLabel.setText(f"{hours}:{minutes%60:02}:{seconds%60:02}")
    
    def currentFrameEditChanged(self, frame_str):
        self.timeline.setValue(int(frame_str))
    

