# !/usr/bin/env python

import sys

from PyQt6 import QtCore, QtGui, QtWidgets, QtMultimedia, QtMultimediaWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor

class TestWidget(QtMultimediaWidgets.QVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setPen(QColor(Qt.GlobalColor.red))
        painter.drawRect(50, 50, 150, 150)


class VideoWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(VideoWindow, self).__init__(parent)
        self.setWindowTitle("PyQt Video Player Widget Example - pythonprogramminglanguage.com")

        self.mediaPlayer = QtMultimedia.QMediaPlayer()

        videoWidget = TestWidget()

        container = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(videoWidget)

        buttonn = QtWidgets.QPushButton("button", container)


        self.playButton = QtWidgets.QPushButton()
        self.playButton.setEnabled(False)
        # self.playButton.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QtWidgets.QLabel()
        self.errorLabel.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred,
                                      QtWidgets.QSizePolicy.Policy.Maximum)

        # Create new action
        openAction = QtGui.QAction(QtGui.QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # Create exit action
        exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        # fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QtWidgets.QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        controlLayout = QtWidgets.QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(container)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.playbackStateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        # self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Movie",
                                                  QtCore.QDir.homePath())

        if fileName:
            self.mediaPlayer.setSource(QtCore.QUrl.fromLocalFile(fileName))
            self.playButton.setEnabled(True)

    def play(self):
        if self.mediaPlayer.playbackState() == QtMultimedia.QMediaPlayer.PlaybackState.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if state == QtMultimedia.QMediaPlayer.PlaybackState.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    player = VideoWindow()
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec())