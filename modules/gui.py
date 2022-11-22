import numpy as np
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen
from PyQt5.QtWidgets import QLabel, QMainWindow, QAction, QFileDialog, QColorDialog, QInputDialog

import modules.pgm as pgm
import modules.ppm as ppm
from modules.color_spaces.cmy import Cmy
from modules.color_spaces.hsl import Hsl
from modules.color_spaces.hsv import Hsv
from modules.color_spaces.rgb import Rgb
from modules.color_spaces.ycbcr601 import YCbCr601
from modules.color_spaces.ycbcr709 import YCbCr709
from modules.color_spaces.ycocg import YCoCg
from modules.config_module import ConfigParser
from modules.dithering import Dithering
from modules.line_drawer import LineDrawer
from modules.painter import Painter


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "Photoshop"
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 400
        self.raster_map = None
        self.label = QLabel()

        self.initUI()

        self.configModule = ConfigParser("./config.cfg")
        self.configModule.read_config()

        self._type = None
        self.current_image = None
        self.scoped_colorspaces = []
        self.current_colorspace = None
        self.defined_colorspace = None

        self.line_point_1 = None
        self.line_point_2 = None

        self._createMenuBar()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setCentralWidget(self.label)

    def open_painter(self):
        painter = Painter(self)
        painter.show()

    def draw_line(self):
        r, g, b, a = QColorDialog.getColor().getRgb()
        transparency, pressed = QInputDialog.getInt(self, "Transparency", "Transparency", 0, 0, 100)
        if pressed:
            width, pressed = QInputDialog.getInt(self, "Width", "Width", 4, 1, 10)
            if pressed:
                line_drawer = LineDrawer(b, g, r, self._type, transparency, width)
                self.raster_map = line_drawer.draw(self.raster_map, self.line_point_1, self.line_point_2)
                self.draw_raster_map(self._type)

    def print_image(self, _type):
        file = open(self.current_image, "rb")
        im = None
        if _type == "pgm":
            im, self.width, self.height = pgm.read_pgm(file)
        elif _type == "ppm":
            im, self.width, self.height = ppm.read_ppm(file)
        canvas = QPixmap(self.width, self.height)
        self.label.setPixmap(canvas)
        self.raster_map = np.array(im)
        self.draw_raster_map(_type)

    def close_image(self):
        self.current_image = None
        self.raster_map = None
        self._type = None
        self.label.clear()
        self.initUI()
        self.update()

    def draw_raster_map(self, _type):
        raster_map = self.raster_map
        if raster_map is None:
            return
        if self.label.pixmap() is None:
            canvas = QPixmap(self.width, self.height)
            self.label.setPixmap(canvas)
        painter = QPainter(self.label.pixmap())
        pen = QPen()
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
        self._type = filetype
        self.current_image = filepath
        self.print_image(filetype)

    def save_file(self):
        if self._type is None or self.raster_map is None:
            return
        filepath = QFileDialog.getSaveFileName(self, 'Save file', './images', '.' + self._type)[0]
        if self._type == "pgm":
            pgm.create_pgm(self.raster_map, filepath)
        elif self._type == "ppm":
            ppm.create_ppm(self.raster_map, filepath)


    def pgm_gradient(self):
        self._type = "pgm"
        self.raster_map = Dithering.pgm_gradient(self.height, self.width)
        self.draw_raster_map(self._type)

    def ppm_gradient(self):
        self._type = "ppm"
        self.raster_map = Dithering.ppm_gradient(self.height, self.width)
        self.draw_raster_map(self._type)

    def ordered_dithering(self):
        if self._type == "pgm":
            width, pressed = QInputDialog.getInt(self, "Bitrate", "Bitrate", 1, 1, 8)
            if pressed:
                dither = Dithering(self.raster_map, width)
                self.raster_map = dither.ordered_pgm()
                self.draw_raster_map(self._type)
        elif self._type == "ppm":
            width, pressed = QInputDialog.getInt(self, "Bitrate", "Bitrate", 1, 1, 8)
            if pressed:
                dither = Dithering(self.raster_map, width)
                self.raster_map = dither.ordered_ppm()
                self.draw_raster_map(self._type)

    def random_dithering(self):
        if self._type == "pgm":
            width, pressed = QInputDialog.getInt(self, "Bitrate", "Bitrate", 1, 1, 8)
            if pressed:
                dither = Dithering(self.raster_map, width)
                self.raster_map = dither.random_pgm()
                self.draw_raster_map(self._type)
        elif self._type == "ppm":
            width, pressed = QInputDialog.getInt(self, "Bitrate", "Bitrate", 1, 1, 8)
            if pressed:
                dither = Dithering(self.raster_map, width)
                self.raster_map = dither.random_ppm()
                self.draw_raster_map(self._type)

    def fs_dithering(self):
        if self._type == "pgm":
            width, pressed = QInputDialog.getInt(self, "Bitrate", "Bitrate", 1, 1, 8)
            if pressed:
                dither = Dithering(self.raster_map, width)
                self.raster_map = dither.floyd_steinberg_pgm()
                self.draw_raster_map(self._type)
        elif self._type == "ppm":
            width, pressed = QInputDialog.getInt(self, "Bitrate", "Bitrate", 1, 1, 8)
            if pressed:
                dither = Dithering(self.raster_map, width)
                self.raster_map = dither.floyd_steinberg_ppm()
                self.draw_raster_map(self._type)

    def atkinson_dithering(self):
        if self._type == "pgm":
            width, pressed = QInputDialog.getInt(self, "Bitrate", "Bitrate", 1, 1, 8)
            if pressed:
                dither = Dithering(self.raster_map, width)
                self.raster_map = dither.atkinson_pgm()
                self.draw_raster_map(self._type)
        if self._type == "ppm":
            width, pressed = QInputDialog.getInt(self, "Bitrate", "Bitrate", 1, 1, 8)
            if pressed:
                dither = Dithering(self.raster_map, width)
                self.raster_map = dither.atkinson_ppm()
                self.draw_raster_map(self._type)

    def switching(self):
        """
        формально, нужно тут нужно получать
        растер мапу для картинки или обновлять
        текущую
        Полученная raster_map должна быть в том colorspace,
        который сейчас выбран (то есть, self.defined_colorspace)

        :return: raster_map или void, если менять raster_map прямо здесь
        """
        pass

    def switch_to_cmy(self):
        if self.defined_colorspace is not None:
            self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 0
        self.defined_colorspace = Cmy
        self.switching()
        self.draw_raster_map(self._type)

    def switch_to_hsl(self):
        if self.defined_colorspace is not None:
            self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 1
        self.defined_colorspace = Hsl
        self.switching()
        self.draw_raster_map(self._type)

    def switch_to_hsv(self):
        if self.defined_colorspace is not None:
            self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 2
        self.defined_colorspace = Hsv
        self.switching()
        self.draw_raster_map(self._type)

    def switch_to_rgb(self):
        if self.defined_colorspace is not None:
            self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 3
        self.defined_colorspace = Rgb
        self.switching()
        self.draw_raster_map(self._type)

    def switch_to_ycbcr601(self):
        if self.defined_colorspace is not None:
            self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 4
        self.defined_colorspace = YCbCr601
        self.switching()
        self.draw_raster_map(self._type)

    def switch_to_ycbcr709(self):
        if self.defined_colorspace is not None:
            self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 5
        self.defined_colorspace = YCbCr709
        self.switching()
        self.draw_raster_map(self._type)

    def switch_to_ycocg(self):
        if self.defined_colorspace is not None:
            self.scoped_colorspaces[self.current_colorspace].setChecked(False)
        self.current_colorspace = 6
        self.defined_colorspace = YCoCg
        self.switching()
        self.draw_raster_map(self._type)

    def _createMenuBar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')

        open_file_action = QAction('&Open', self)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction('&Save', self)
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)

        close_file_action = QAction('&Close', self)
        close_file_action.triggered.connect(self.close_image)
        file_menu.addAction(close_file_action)

        painter = menu_bar.addAction('&Paint')
        painter.triggered.connect(self.open_painter)

        generate_menu = menu_bar.addMenu('&Generate')

        generate_pgm = QAction('&PGM', self)
        generate_pgm.triggered.connect(self.pgm_gradient)
        generate_menu.addAction(generate_pgm)

        generate_ppm = QAction('&PPM', self)
        generate_ppm.triggered.connect(self.ppm_gradient)
        generate_menu.addAction(generate_ppm)

        dithering_menu = menu_bar.addMenu('&Dithering')

        dithering_ordered = QAction('&Ordered', self)
        dithering_ordered.triggered.connect(self.ordered_dithering)
        dithering_menu.addAction(dithering_ordered)

        dithering_random = QAction('&Random', self)
        dithering_random.triggered.connect(self.random_dithering)
        dithering_menu.addAction(dithering_random)

        dithering_fs = QAction('&Floyd-Steinberg', self)
        dithering_fs.triggered.connect(self.fs_dithering)
        dithering_menu.addAction(dithering_fs)

        dithering_atkinson = QAction('&Atkinson', self)
        dithering_atkinson.triggered.connect(self.atkinson_dithering)
        dithering_menu.addAction(dithering_atkinson)

        """
        Colorspace block
        
        Radiobutton
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
        self.switch_to_rgb()

        drawer = menu_bar.addMenu('&Draw')
        line_drawer = QAction('&Line', self)
        line_drawer.triggered.connect(self.draw_line)
        drawer.addAction(line_drawer)

    def mousePressEvent(self, e):
        x, y = e.x(), e.y()
        if e.button() == 1:
            self.line_point_1 = (x, y)
        elif e.button() == 2:
            self.line_point_2 = (x, y)
