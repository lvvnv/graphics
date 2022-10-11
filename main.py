import sys

from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow

import pgm
import ppm


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Test image'
        self.left = 0
        self.top = 0
        self.width = 640
        self.height = 426
        self.label = QLabel()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        canvas = QPixmap(self.width, self.height)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)

    def draw_pgm_sample(self):
        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()

        raster_map = pgm.crete_raster_sample_map()
        for y in range(len(raster_map)):
            row = raster_map[y]
            for x in range(len(row)):
                bit = row[x]
                pen.setColor(QColor(bit, bit, bit))
                painter.setPen(pen)
                painter.drawPoint(x, y)

        painter.end()
        self.show()

    def draw_ppm_sample(self):
        painter = QtGui.QPainter(self.label.pixmap())
        pen = QtGui.QPen()

        raster_map = ppm.crete_raster_sample_map()
        for y in range(len(raster_map)):
            row = raster_map[y]
            for x in range(len(row)):
                b, g, r = [row[x][-i] for i in range(3)]
                pen.setColor(QColor(r, g, b))
                painter.setPen(pen)
                painter.drawPoint(x, y)

        painter.end()
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    pgm_ex = App()
    pgm_ex.draw_pgm_sample()

    ppm_ex = App()
    ppm_ex.draw_ppm_sample()

    sys.exit(app.exec_())
