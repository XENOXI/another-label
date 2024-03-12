from PyQt6.QtWidgets import QWidget, QSlider, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QSplitter, QSizePolicy, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

from keypointsdisplay import KeypointsDisplay
from labellist import LabelList


class TimelineWidget(QWidget):
    frameSelected = pyqtSignal(int)
    def __init__(self):
        super().__init__()

        self.timeline = QSlider(Qt.Orientation.Horizontal, self)
        self.timeline.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.playButton = QPushButton("Play/Stop", self)
        self.framesLabel = QLabel("0/0", self)

        self.framesCount = 0

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

        controlsLayout.addWidget(self.playButton)
        controlsLayout.addWidget(self.timeline)

        mainLayout.addLayout(controlsLayout)
        mainLayout.addWidget(self.framesLabel, 0, Qt.AlignmentFlag.AlignRight)
        mainLayout.addWidget(keypointsDisplayScroll)

        self.setLayout(mainLayout)

        self.timeline.valueChanged.connect(self.sliderValueChanged)
        self.keypointsDisplay.boxCountUpdated.connect(self.labelList.set_bboxes_cnt)
        self.keypointsDisplay.selectedBboxUpdate.connect(self.labelList.set_selected_bbox)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def setFramesCount(self, framesCount):
        self.timeline.setMaximum(framesCount-1)
        self.keypointsDisplay.set_frame_cnt(framesCount)
        self.framesCount = framesCount

    def setSequences(self, sequences):
        self.keypointsDisplay.set_sequences(sequences)
        

    def sliderValueChanged(self, frame):
        self.frameSelected.emit(frame)
        self.keypointsDisplay.set_frame(frame)
        self.framesLabel.setText(f"{frame+1}/{self.framesCount}")
    

