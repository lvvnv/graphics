from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMainWindow, QAction, QFileDialog
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen

import modules.pgm as pgm
import modules.ppm as ppm
import numpy as np
from modules.painter import Painter
from modules.config_module import ConfigParser
from modules.color_spaces.hsv import Hsv
from modules.color_spaces.hsl import Hsl
from modules.color_spaces.rgb import Rgb
from modules.color_spaces.cmy import Cmy
from modules.color_spaces.ycbcr601 import YCbCr601
from modules.color_spaces.ycbcr709 import YCbCr709
from modules.color_spaces.ycocg import YCoCg


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
        self.scoped_colorspaces = []
        self.current_colorspace = 0
        self.defined_colorspace = None

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
        self.setFixedSize(self.layout().sizeHint())
        self.update()

    def open_file(self):
        filepath = QFileDialog.getOpenFileName(self, 'Open file', './images')[0]
        filetype = filepath.split('.')[-1]
        if filetype not in self.configModule.config["accepted_files"]:
            print("wrong type of image file")
            return
        self.current_image = filepath
        self.print_image(filetype)

    def switch_to_cmy(self):
        self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 0
        self.defined_colorspace = Cmy()

    def switch_to_hsl(self):
        self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 1
        self.defined_colorspace = Hsl()

    def switch_to_hsv(self):
        self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 2
        self.defined_colorspace = Hsv()

    def switch_to_rgb(self):
        self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 3
        self.defined_colorspace = Rgb()

    def switch_to_ycbcr601(self):
        self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 4
        self.defined_colorspace = YCbCr601()

    def switch_to_ycbcr709(self):
        self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 5
        self.defined_colorspace = YCbCr709()

    def switch_to_ycocg(self):
        self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 6
        self.defined_colorspace = YCoCg()

    def _createMenuBar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')

        open_file_action = QAction('&Open', self)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        painter = menu_bar.addAction('&Paint')
        painter.triggered.connect(self.open_painter)

        """
        Colorspace block
        
        Checkbox menu
        Only one can picked at a time
        call self.defined_colorspace when printing
        """
        colorspaces = menu_bar.addMenu('&Colorspaces')

        cmy_colorspace = QAction('&CMY', self)
        cmy_colorspace.triggered.connect(self.switch_to_cmy)
        cmy_colorspace.setCheckable(True)
        colorspaces.addAction(cmy_colorspace)

        hsl_colorspace = QAction('&HSL', self)
        hsl_colorspace.triggered.connect(self.switch_to_hsl)
        hsl_colorspace.setCheckable(True)
        colorspaces.addAction(hsl_colorspace)

        hsv_colorspace = QAction('&HSV', self)
        hsv_colorspace.triggered.connect(self.switch_to_hsv)
        hsv_colorspace.setCheckable(True)
        colorspaces.addAction(hsv_colorspace)

        rgb_colorspace = QAction('&RGB', self)
        rgb_colorspace.triggered.connect(self.switch_to_rgb)
        rgb_colorspace.setCheckable(True)
        rgb_colorspace.setChecked(True)
        colorspaces.addAction(rgb_colorspace)
        self.current_colorspace = 3

        ycbcr601_colorspace = QAction('&YCbCr601', self)
        ycbcr601_colorspace.triggered.connect(self.switch_to_ycbcr601)
        ycbcr601_colorspace.setCheckable(True)
        colorspaces.addAction(ycbcr601_colorspace)

        ycbcr709_colorspace = QAction('&YCbCr709', self)
        ycbcr709_colorspace.triggered.connect(self.switch_to_ycbcr709)
        ycbcr709_colorspace.setCheckable(True)
        colorspaces.addAction(ycbcr709_colorspace)

        ycocg_colorspace = QAction('&YCoCg', self)
        ycocg_colorspace.triggered.connect(self.switch_to_ycocg)
        ycocg_colorspace.setCheckable(True)
        colorspaces.addAction(ycocg_colorspace)

        self.scoped_colorspaces += \
            [
                cmy_colorspace,
                hsl_colorspace,
                hsv_colorspace,
                rgb_colorspace,
                ycbcr601_colorspace,
                ycbcr709_colorspace,
                ycocg_colorspace
            ]
