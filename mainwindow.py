from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QSlider, QMenu, QVBoxLayout, QFileDialog, QProgressDialog,QLabel
from PyQt6.QtGui import QAction,QPixmap
import cv2
from ultralytics import YOLO
import pandas as pd

from imagewidget import ImageWidget
from persontimeline import PersonTimeline


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Labeler")

        menu_bar = self.menuBar()
        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)

        open_video = QAction("Open video and calculate labels", self)
        import_labels = QAction("Open video and import labels", self)
        export_labels = QAction("Export labels to csv", self)

        open_video.triggered.connect(self.open_video_cb)
        import_labels.triggered.connect(self.import_labels_cb)
        export_labels.triggered.connect(self.export_labels_cb)

        file_menu.addActions([open_video, import_labels, export_labels])

        self.image_widget = ImageWidget()
        self.time_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.personTimeline = PersonTimeline()


        self.time_slider.valueChanged.connect(self.image_widget.set_frame)
        self.time_slider.valueChanged.connect(self.personTimeline.set_frame)
        self.image_widget.frame_selected.connect(self.test_cb)

        cw = QWidget(self)

        main_layout = QVBoxLayout()

        main_layout.addWidget(self.image_widget)
        main_layout.addWidget(self.time_slider)
        main_layout.addWidget(self.personTimeline)

        cw.setLayout(main_layout)
        
        self.setCentralWidget(cw)

        self.labels = None

    def open_video_cb(self):
        video_path = QFileDialog.getOpenFileName(self, "open video")
        model = YOLO("yolov8m.pt")
        video = cv2.VideoCapture(video_path[0])
        frames_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Frames count: {frames_count}")
        self.time_slider.setMaximum(frames_count-1)
        progress = QProgressDialog("Tracking", "Cancel", 0, frames_count)
        progress.setWindowModality(Qt.WindowModality.WindowModal)

        labels_dict = {"frame": [], "track_id": [], "x": [], "y": [], "h": [], "w": [], "label": []}

        for i in range(frames_count):
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

                labels_dict['frame'].append(i)
                labels_dict['track_id'].append(track_id)
                labels_dict['x'].append(x.item())
                labels_dict['y'].append(y.item())
                labels_dict['w'].append(w.item())
                labels_dict['h'].append(h.item())
                labels_dict['label'].append(0)
        else:
            progress.setValue(frames_count)
        
        video.release()
        self.labels = pd.DataFrame(labels_dict)
        self.image_widget.set_labels(self.labels)
        self.personTimeline.set_labels(self.labels)
        self.image_widget.set_video(video_path[0])
        self.personTimeline.set_frame_cnt(frames_count)
        
        print("done")

    def import_labels_cb(self):
        video_path = QFileDialog.getOpenFileName(self, "Open video")
        labels_path = QFileDialog.getOpenFileName(self, "Import labels")
        
        video = cv2.VideoCapture(video_path[0])
        frames_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Frames count: {frames_count}")
        self.time_slider.setMaximum(frames_count-1)
        video.release()

        df = pd.read_csv(labels_path[0])
        self.image_widget.set_video(video_path[0])
        self.image_widget.set_labels(df)
        self.personTimeline.set_labels(self.labels)
        self.personTimeline.set_frame_cnt(frames_count)

    def export_labels_cb(self):
        labels_path = QFileDialog.getSaveFileName(self, "Save csv", None, "*.csv")[0]
        if labels_path == '':
            return
        self.labels.to_csv(labels_path, index=False)

    def test_cb(self, id):
        print(id)
        
