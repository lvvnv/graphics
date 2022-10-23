from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMainWindow, QAction, QFileDialog
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen

import modules.pgm as pgm
import modules.ppm as ppm
import numpy as np
from modules.painter import Painter
from modules.config_module import ConfigParser


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "Photoshop"
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 400
        self.label = QLabel()

        self.initUI()
        # self.setWindowTitle("Menu")
        # self.resize(400, 200)
        # self.centralWidget = QLabel()
        # self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # self.setCentralWidget(self.centralWidget)

        self.configModule = ConfigParser("./config.cfg")
        self.configModule.read_config()

        self.current_image = None

        self._createMenuBar()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setCentralWidget(self.label)

    def open_painter(self):
        painter = Painter(self)
        painter.show()

    def print_image(self, _type):
        file = open(self.current_image, "rb")
        im = None
        if _type == "pgm":
            im, self.width, self.height = pgm.read_pgm(file)
        elif _type == "ppm":
            im, self.width, self.height = ppm.read_ppm(file)
        canvas = QPixmap(self.width, self.height)
        self.label.setPixmap(canvas)
        painter = QPainter(self.label.pixmap())
        pen = QPen()
        raster_map = np.array(im)
        for y in range(len(raster_map)):
            row = raster_map[y]
            for x in range(len(row)):
                if _type == "pgm":
                    bit = row[x]
                    pen.setColor(QColor(bit, bit, bit))
                elif _type == "ppm":
                    b, g, r = [row[x][-i] for i in range(3)]
                    pen.setColor(QColor(r, g, b))
                painter.setPen(pen)
                painter.drawPoint(x, y)
        painter.end()
        self.resize(self.width, self.height)
        self.update()

    def open_file(self):
        filepath = QFileDialog.getOpenFileName(self, 'Open file', './images')[0]
        filetype = filepath.split('.')[-1]
        if filetype not in self.configModule.config["accepted_files"]:
            print("wrong type of image file")
            return
        self.current_image = filepath
        self.print_image(filetype)

    def _createMenuBar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')

        open_file_action = QAction('&Open', self)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        painter = menu_bar.addAction('&Paint')
        painter.triggered.connect(self.open_painter)
