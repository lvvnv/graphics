import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QAction

import pgm
import ppm
from image import Image
from painter import Painter


class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu")
        self.resize(400, 200)
        self.centralWidget = QLabel()
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)
        self._createMenuBar()

    def open_pgm(self):
        pgm_ex = Image(self)
        pgm_ex.draw_pgm_sample()

    def open_pgm_painted(self):
        pgm_ex = Image(self)
        pgm_ex.draw_pgm_sample(pgm.image_paint_path)

    def open_ppm(self):
        pgm_ex = Image(self)
        pgm_ex.draw_ppm_sample()

    def open_ppm_painted(self):
        ppm_ex = Image(self)
        ppm_ex.draw_ppm_sample(ppm.image_paint_path)

    def open_painter(self):
        painter = Painter(self)
        painter.show()

    def _createMenuBar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&Open')

        p5_action = QAction('&P5', self)
        p5_action.triggered.connect(self.open_pgm)
        file_menu.addAction(p5_action)

        p6_action = QAction('&P6', self)
        p6_action.triggered.connect(self.open_ppm)
        file_menu.addAction(p6_action)

        p5_action_painted = QAction('&P5 - painted', self)
        p5_action_painted.triggered.connect(self.open_pgm_painted)
        file_menu.addAction(p5_action_painted)

        p6_action_painted = QAction('&P6 - painted', self)
        p6_action_painted.triggered.connect(self.open_ppm_painted)
        file_menu.addAction(p6_action_painted)

        painter = menu_bar.addAction('&Paint')
        painter.triggered.connect(self.open_painter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
