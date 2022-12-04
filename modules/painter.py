from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAction

from modules.pgm import create_pgm
from modules.ppm import create_ppm


# Рисовалка
class Painter(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(640, 480)
        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.last_x, self.last_y = None, None
        self._createMenuBar()
        self.color = QtGui.QColor('yellow')

    def mousePressEvent(self, e):
        switcher = {
            1: 'yellow',
            2: 'green',
            4: 'red',
            8: 'white',
            16: 'blue'
        }
        self.color = QtGui.QColor(switcher.get(e.button()))

    def mouseMoveEvent(self, e):
        if self.last_x is None:
            self.last_x = e.x()
            self.last_y = e.y()
            return

        painter = QtGui.QPainter(self.label.pixmap())
        p = painter.pen()
        p.setColor(self.color)
        painter.setPen(p)
        painter.drawLine(self.last_x, self.last_y, e.x(), e.y())
        painter.end()
        self.update()
        self.last_x = e.x()
        self.last_y = e.y()

    def mouseReleaseEvent(self, e):
        self.last_x = None
        self.last_y = None

    def _createMenuBar(self):
        menu_bar = self.menuBar()
        save_menu = menu_bar.addMenu('&Save')

        p5_action = QAction('&P5', self)
        p5_action.triggered.connect(self.save_p5)
        save_menu.addAction(p5_action)

        p6_action = QAction('&P6', self)
        p6_action.triggered.connect(self.save_p6)
        save_menu.addAction(p6_action)

    def save_p5(self):
        image_pixmap = self.label.pixmap().toImage()
        width, height = image_pixmap.rect().width(), image_pixmap.rect().height()
        p5_map = []
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b, a = QColor(image_pixmap.pixel(x, y)).getRgb()
                row.append(rgb_to_gray(r, g, b))
            p5_map.append(row)
        create_pgm(p5_map)

    def save_p6(self):
        image_pixmap = self.label.pixmap().toImage()
        width, height = image_pixmap.rect().width(), image_pixmap.rect().height()
        p6_map = []
        for y in range(height):
            row = []
            for x in range(width):
                color = [c for c in QColor(image_pixmap.pixel(x, y)).getRgb()][:3]
                row.append([color[2], color[0], color[1]])
            p6_map.append(row)
        create_ppm(p6_map)


def rgb_to_gray(r, g, b):
    return 0.2989 * r + 0.5870 * g + 0.1140 * b
