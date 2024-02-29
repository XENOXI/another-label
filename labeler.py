from PyQt6.QtWidgets import QApplication, QWidget
import sys

from mainwindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
