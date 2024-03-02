from PyQt6.QtWidgets import QWidget, QSlider, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal

from keypointsdisplay import KeypointsDisplay
from labellist import LabelList


class TimelineWidget(QWidget):
    frameSelected = pyqtSignal(int)
    def __init__(self):
        super().__init__()

        self.timeline = QSlider(Qt.Orientation.Horizontal, self)
        self.playButton = QPushButton("Play/Stop", self)

        self.labelList = LabelList()
        keypointsDisplayScroll = QScrollArea(self)
        keypointsDisplayScroll.setWidgetResizable(True)
        keypointsDisplayScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        keypointsDisplaySplitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.keypointsDisplay = KeypointsDisplay()

        keypointsDisplaySplitter.addWidget(self.labelList)
        keypointsDisplaySplitter.addWidget(self.keypointsDisplay)
        keypointsDisplayScroll.setWidget(keypointsDisplaySplitter)
        
        mainLayout = QVBoxLayout(self)
        controlsLayout = QHBoxLayout(self)

        controlsLayout.addWidget(self.playButton)
        controlsLayout.addWidget(self.timeline)

        mainLayout.addLayout(controlsLayout)
        mainLayout.addWidget(keypointsDisplayScroll)

        self.setLayout(mainLayout)

        self.timeline.valueChanged.connect(self.sliderValueChanged)

    def setFramesCount(self, framesCount):
        self.timeline.setMaximum(framesCount-1)
        self.keypointsDisplay.set_frame_cnt(framesCount)

    def setLabels(self, labels):
        self.keypointsDisplay.set_labels(labels)

    def sliderValueChanged(self, frame):
        self.frameSelected.emit(frame)
        self.keypointsDisplay.set_frame(frame)

