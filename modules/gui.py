import numpy as np
from PyQt5.QtGui import QPixmap, QColor, QPainter, QPen
from PyQt5.QtWidgets import QLabel, QMainWindow, QAction, QFileDialog, QColorDialog, QInputDialog

import modules.pgm as pgm
import modules.ppm as ppm
from modules import jpeg_decoder as jpeg
from modules import png
from modules.color_spaces.cmy import Cmy
from modules.color_spaces.hsl import Hsl
from modules.color_spaces.hsv import Hsv
from modules.color_spaces.rgb import Rgb
from modules.color_spaces.ycbcr601 import YCbCr601
from modules.color_spaces.ycbcr709 import YCbCr709
from modules.color_spaces.ycocg import YCoCg
from modules.config_module import ConfigParser
from modules.dithering import Dithering
from modules.filter import Filter
from modules.histogram import Histogram
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
        self.colorspace_checkbox = []
        self.colorspace_num = 3
        self.colorspace = Rgb

        self.line_point_1 = None
        self.line_point_2 = None
        self.gamma = None
        self.histogram = None

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
                self.int_to_float(line_drawer.draw(self.float_to_int(), self.line_point_1, self.line_point_2))
                self.draw_raster_map(self._type)

    def float_to_int(self):
        return np.round(self.raster_map * 255)

    def int_to_float(self, raster_map):
        self.raster_map = raster_map / 255

    def close_image(self):
        self.current_image = None
        self.raster_map = None
        self._type = None
        self.label.clear()
        self.initUI()
        self.update()

    def draw_raster_map(self, _type):
        if self.raster_map is None:
            return
        raster_map = self.raster_map
        if _type == "ppm":
            raster_map = self.colorspace.to_rgb_pixmap(raster_map)

        if self.label.pixmap() is None:
            canvas = QPixmap(self.width, self.height)
            self.label.setPixmap(canvas)
        painter = QPainter(self.label.pixmap())
        pen = QPen()
        for y in range(len(raster_map)):
            row = raster_map[y]
            for x in range(len(row)):
                if _type == "pgm":
                    bit = np.round(self.from_gamma(row[x]) * 255)
                    pen.setColor(QColor(bit, bit, bit))
                elif _type == "ppm":
                    b, g, r = [row[x][-i] for i in range(3)]
                    r = np.round((self.to_srgb(self.from_gamma(r))) * 255)
                    g = np.round((self.to_srgb(self.from_gamma(g))) * 255)
                    b = np.round((self.to_srgb(self.from_gamma(b))) * 255)
                    pen.setColor(QColor(r, g, b))
                painter.setPen(pen)
                painter.drawPoint(x, y)
        painter.end()
        self.resize(self.width, self.height)
        # self.setFixedSize(self.layout().sizeHint())
        self.update()

    def open_file(self):
        filepath = QFileDialog.getOpenFileName(self, 'Open file', './images')[0]
        filetype = filepath.split('.')[-1]
        if filetype not in self.configModule.config["accepted_files"]:
            print("wrong type of image file")
            return
        self._type = filetype
        self.current_image = filepath
        file = open(self.current_image, "rb")
        im = None
        if self._type == "pgm":
            im, self.width, self.height = pgm.read_pgm(file)
            self.gamma = 0
        elif self._type == "ppm":
            im, self.width, self.height = ppm.read_ppm(file)
            self.gamma = 0
        elif self._type == "png":
            im, self.width, self.height, self.gamma = png.read_png(file)
            self._type = "ppm" if len(im.shape) == 3 else "pgm"
        elif self._type == "jpg" or self._type == "jpeg":
            decoder = jpeg.JpegDecoder(file)
            im = decoder.result_image
            self.height = len(im)
            self.width = len(im[0])
            self._type = "ppm"
            self.gamma = 0
        canvas = QPixmap(self.width, self.height)
        self.label.setPixmap(canvas)
        self.int_to_float(np.array(im))
        self.draw_raster_map(self._type)

    def save_file(self):
        if self._type is None or self.raster_map is None:
            return
        filepath = QFileDialog.getSaveFileName(self, 'Save file', './images', '.' + self._type)[0]
        if filepath == '':
            return
        if self._type == "pgm":
            pgm.create_pgm(self.float_to_int(), filepath + '.pgm')
        elif self._type == "ppm":
            ppm.create_ppm(self.float_to_int(), filepath + '.ppm')

    def save_png(self):
        if self._type is None or self.raster_map is None:
            return
        filepath = QFileDialog.getSaveFileName(self, 'Save file', './images', '.png')[0]
        png.create_png(self.float_to_int(), self.gamma, filepath + '.png')


    def from_gamma(self, pixel):
        if self.gamma != 0:
            return np.abs(pixel) ** (1 / self.gamma)
        return self.from_srgb(pixel)

    def from_srgb(self, pixel):
        if pixel <= 0.0031308:
            return pixel * 12.92

        return 1.055 * (pixel ** (1 / 2.4)) - 0.055

    def to_gamma(self, pixel, new_gamma):
        if new_gamma != 0:
            return np.abs(pixel) ** new_gamma
        return self.to_srgb(pixel)

    def to_srgb(self, pixel):
        if pixel <= 0.04045:
            return pixel / 12.92

        return ((pixel + 0.055) / 1.055) ** 2.4

    def gamma_assign(self):
        if self._type is not None:
            new_gamma, pressed = QInputDialog.getDouble(self, "Value", "Value", self.gamma, 0, 5)
            if pressed:
                self.gamma = new_gamma
                self.draw_raster_map(self._type)

    def gamma_convert(self):
        if self._type is not None and self.colorspace == Rgb:
            new_gamma, pressed = QInputDialog.getDouble(self, "Value", "Value", self.gamma, 0, 5)
            if pressed:
                self.convert_gamma(new_gamma)
                self.gamma = new_gamma
                self.draw_raster_map(self._type)

    def convert_gamma(self, new_gamma):
        if self._type == "ppm":
            for i in range(len(self.raster_map)):
                for j in range(len(self.raster_map[0])):
                    b, g, r = [self.raster_map[i][j][-k] for k in range(3)]
                    r = self.from_gamma(r)
                    r = self.to_gamma(r, new_gamma)
                    g = self.from_gamma(g)
                    g = self.to_gamma(g, new_gamma)
                    b = self.from_gamma(b)
                    b = self.to_gamma(b, new_gamma)
                    self.raster_map[i][j] = [b, r, g]
        elif self._type == "pgm":
            for i in range(len(self.raster_map)):
                for j in range(len(self.raster_map[0])):
                    self.raster_map[i][j] = self.from_gamma(self.raster_map[i][j])
                    self.raster_map[i][j] = self.to_gamma(self.raster_map[i][j], new_gamma)

    def view_channel(self):
        if self._type == "ppm":
            channel, pressed = QInputDialog.getInt(self, "Channel", "Channel", 1, 1, 3)
            if pressed:
                new_raster_map = [[self.raster_map[i][j][channel - 1]
                                   for j in range(len(self.raster_map[0]))]
                                  for i in range(len(self.raster_map))]
                self.raster_map = new_raster_map
                self._type = "pgm"
                self.draw_raster_map(self._type)

    def pgm_gradient(self):
        self._type = "pgm"
        self.raster_map = Dithering.pgm_gradient(self.height, self.width)
        self.gamma = 1
        self.draw_raster_map(self._type)

    def ppm_gradient(self):
        self._type = "ppm"
        channel, pressed = QInputDialog.getInt(self, "Channel", "Channel", 1, 1, 3)
        if pressed:
            self.raster_map = Dithering.ppm_gradient(self.height, self.width, channel)
            self.gamma = 1
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

    def switching(self, new_colorspace):
        if self.raster_map is not None and self._type == "ppm":
            self.raster_map = self.colorspace.to_rgb_pixmap(self.raster_map)
            self.colorspace = new_colorspace
            self.raster_map = self.colorspace.from_rgb_pixmap(self.raster_map)
        else:
            self.colorspace = new_colorspace

    def switch_to_cmy(self):
        if self.colorspace is not None:
            self.colorspace_checkbox[self.colorspace_num].setChecked(False)
        self.colorspace_num = 0
        self.switching(Cmy)
        self.draw_raster_map(self._type)

    def switch_to_hsl(self):
        if self.colorspace is not None:
            self.colorspace_checkbox[self.colorspace_num].setChecked(False)
        self.colorspace_num = 1
        self.switching(Hsl)
        self.draw_raster_map(self._type)

    def switch_to_hsv(self):
        if self.colorspace is not None:
            self.colorspace_checkbox[self.colorspace_num].setChecked(False)
        self.colorspace_num = 2
        self.switching(Hsv)
        self.draw_raster_map(self._type)

    def switch_to_rgb(self):
        if self.colorspace is not None:
            self.colorspace_checkbox[self.colorspace_num].setChecked(False)
        self.colorspace_num = 3
        self.switching(Rgb)
        self.draw_raster_map(self._type)

    def switch_to_ycbcr601(self):
        if self.colorspace is not None:
            self.colorspace_checkbox[self.colorspace_num].setChecked(False)
        self.colorspace_num = 4
        self.switching(YCbCr601)
        self.draw_raster_map(self._type)

    def switch_to_ycbcr709(self):
        if self.colorspace is not None:
            self.colorspace_checkbox[self.colorspace_num].setChecked(False)
        self.colorspace_num = 5
        self.switching(YCbCr709)
        self.draw_raster_map(self._type)

    def switch_to_ycocg(self):
        if self.colorspace is not None:
            self.colorspace_checkbox[self.colorspace_num].setChecked(False)
        self.colorspace_num = 6
        self.switching(YCoCg)
        self.draw_raster_map(self._type)

    def one_channel_histogram(self):
        if self._type == "ppm":
            channel, pressed = QInputDialog.getInt(self, "Channel", "Channel", 1, 1, 3)
            if pressed:
                self.histogram = Histogram(self.float_to_int()[:, :, channel - 1].flatten())
                self.histogram.one_channel(channel)
        elif self._type == "pgm":
            self.histogram = Histogram(self.float_to_int().flatten())
            self.histogram.pgm()

    def three_channels_histogram(self):
        if self._type == "ppm":
            self.histogram = Histogram(self.float_to_int())
            self.histogram.three_channels()

    def correction(self):
        if self._type is not None:
            fraction, pressed = QInputDialog.getDouble(self, "Ignore rate", "Ignore rate", 0.2, 0, 0.49, 2)
            if pressed:
                min_value, max_value = Histogram.find_borders(self.raster_map, fraction)
                self.raster_map = Histogram.correction(self.raster_map, min_value, max_value)
                self.draw_raster_map(self._type)

    def filter_threshold(self):
        threshold, pressed = QInputDialog.getInt(self, "Threshold value", "Threshold value", 128, 0, 255)
        if pressed:
            self.raster_map = Filter.threshold(self.raster_map, self._type, threshold)
            self.draw_raster_map(self._type)

    def filter_otsu(self):
        self.raster_map = Filter.otsu(self.raster_map, self._type)
        self.draw_raster_map(self._type)

    def filter_median(self):
        radius, pressed = QInputDialog.getInt(self, "Radius value", "Radius value", 5, 0, 10)
        if pressed:
            self.raster_map = Filter.median(self.raster_map, self._type, radius)
            self.draw_raster_map(self._type)

    def filter_gaussian(self):
        sigma, pressed = QInputDialog.getInt(self, "Sigma value", "Sigma value", 2, 1, 5)
        if pressed:
            self.raster_map = Filter.gaussian_filter(self.raster_map, self._type, sigma)
            self.draw_raster_map(self._type)

    def filter_box_blur(self):
        radius, pressed = QInputDialog.getInt(self, "Radius value", "Radius value", 5, 0, 10)
        if pressed:
            self.raster_map = Filter.box_blur_filter(self.raster_map, self._type, radius)
            self.draw_raster_map(self._type)

    def filter_sobel(self):
        self.raster_map = Filter.sobel_filter(self.raster_map, self._type)
        self.draw_raster_map(self._type)

    def filter_cas(self):
        sharpness, pressed = QInputDialog.getDouble(self, "Sharpness value", "Sharpness value", 0.5, 0, 1)
        if pressed:
            self.raster_map = Filter.cas_filter(self.raster_map, self._type, sharpness)
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

        save_png_action = QAction('&Save as PNG', self)
        save_png_action.triggered.connect(self.save_png)
        file_menu.addAction(save_png_action)

        close_file_action = QAction('&Close', self)
        close_file_action.triggered.connect(self.close_image)
        file_menu.addAction(close_file_action)

        painter = menu_bar.addAction('&Paint')
        painter.triggered.connect(self.open_painter)

        gamma_menu = menu_bar.addMenu('&Gamma')

        gamma_assign_action = QAction('&Assign', self)
        gamma_assign_action.triggered.connect(self.gamma_assign)
        gamma_menu.addAction(gamma_assign_action)

        gamma_convert_action = QAction('&Convert', self)
        gamma_convert_action.triggered.connect(self.gamma_convert)
        gamma_menu.addAction(gamma_convert_action)

        view_menu = menu_bar.addMenu('&View')

        channel_view = QAction('&Channel', self)
        channel_view.triggered.connect(self.view_channel)
        view_menu.addAction(channel_view)

        generate_pgm = QAction('&PGM gradient', self)
        generate_pgm.triggered.connect(self.pgm_gradient)
        view_menu.addAction(generate_pgm)

        generate_ppm = QAction('&PPM gradient', self)
        generate_ppm.triggered.connect(self.ppm_gradient)
        view_menu.addAction(generate_ppm)

        drawer = menu_bar.addMenu('&Draw')
        line_drawer = QAction('&Line', self)
        line_drawer.triggered.connect(self.draw_line)
        drawer.addAction(line_drawer)

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

        colorspace = menu_bar.addMenu('&Colorspace')

        cmy_colorspace = QAction('&CMY', self)
        cmy_colorspace.triggered.connect(self.switch_to_cmy)
        cmy_colorspace.setCheckable(True)
        colorspace.addAction(cmy_colorspace)

        hsl_colorspace = QAction('&HSL', self)
        hsl_colorspace.triggered.connect(self.switch_to_hsl)
        hsl_colorspace.setCheckable(True)
        colorspace.addAction(hsl_colorspace)

        hsv_colorspace = QAction('&HSV', self)
        hsv_colorspace.triggered.connect(self.switch_to_hsv)
        hsv_colorspace.setCheckable(True)
        colorspace.addAction(hsv_colorspace)

        rgb_colorspace = QAction('&RGB', self)
        rgb_colorspace.triggered.connect(self.switch_to_rgb)
        rgb_colorspace.setCheckable(True)
        rgb_colorspace.setChecked(True)
        colorspace.addAction(rgb_colorspace)

        ycbcr601_colorspace = QAction('&YCbCr601', self)
        ycbcr601_colorspace.triggered.connect(self.switch_to_ycbcr601)
        ycbcr601_colorspace.setCheckable(True)
        colorspace.addAction(ycbcr601_colorspace)

        ycbcr709_colorspace = QAction('&YCbCr709', self)
        ycbcr709_colorspace.triggered.connect(self.switch_to_ycbcr709)
        ycbcr709_colorspace.setCheckable(True)
        colorspace.addAction(ycbcr709_colorspace)

        ycocg_colorspace = QAction('&YCoCg', self)
        ycocg_colorspace.triggered.connect(self.switch_to_ycocg)
        ycocg_colorspace.setCheckable(True)
        colorspace.addAction(ycocg_colorspace)

        self.colorspace_checkbox += \
            [
                cmy_colorspace,
                hsl_colorspace,
                hsv_colorspace,
                rgb_colorspace,
                ycbcr601_colorspace,
                ycbcr709_colorspace,
                ycocg_colorspace
            ]

        histogram_menu = menu_bar.addMenu('&Histogram')

        show_histogram = QAction('&Show one channel', self)
        show_histogram.triggered.connect(self.one_channel_histogram)
        histogram_menu.addAction(show_histogram)

        show_histogram = QAction('&Show three channels', self)
        show_histogram.triggered.connect(self.three_channels_histogram)
        histogram_menu.addAction(show_histogram)

        contrast_correction = QAction('&Contrast correction', self)
        contrast_correction.triggered.connect(self.correction)
        histogram_menu.addAction(contrast_correction)

        filter_menu = menu_bar.addMenu('&Filter')

        filter_threshold_action = QAction('&Threshold', self)
        filter_threshold_action.triggered.connect(self.filter_threshold)
        filter_menu.addAction(filter_threshold_action)

        filter_otsu_action = QAction('&Otsu', self)
        filter_otsu_action.triggered.connect(self.filter_otsu)
        filter_menu.addAction(filter_otsu_action)

        filter_median_action = QAction('&Median', self)
        filter_median_action.triggered.connect(self.filter_median)
        filter_menu.addAction(filter_median_action)

        filter_gaussian_action = QAction('&Gaussian', self)
        filter_gaussian_action.triggered.connect(self.filter_gaussian)
        filter_menu.addAction(filter_gaussian_action)

        filter_box_blur_action = QAction('&Box blur', self)
        filter_box_blur_action.triggered.connect(self.filter_box_blur)
        filter_menu.addAction(filter_box_blur_action)

        filter_sobel_action = QAction('&Sobel', self)
        filter_sobel_action.triggered.connect(self.filter_sobel)
        filter_menu.addAction(filter_sobel_action)

        filter_cas_action = QAction('&CAS', self)
        filter_cas_action.triggered.connect(self.filter_cas)
        filter_menu.addAction(filter_cas_action)

    def mousePressEvent(self, e):
        x, y = e.x(), e.y()
        if e.button() == 1:
            self.line_point_1 = (x, y)
        elif e.button() == 2:
            self.line_point_2 = (x, y)
