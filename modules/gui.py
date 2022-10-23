from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMainWindow, QAction, QFileDialog

import modules.pgm as pgm
import modules.ppm as ppm
from modules.image import Image
from modules.painter import Painter
from modules.config_module import ConfigParser

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menu")
        self.resize(400, 200)
        self.centralWidget = QLabel()
        self.centralWidget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setCentralWidget(self.centralWidget)

        self.configModule = ConfigParser("./config.cfg")
        self.configModule.read_config()

        self.current_image = None

        self._createMenuBar()

    def open_pgm(self, path):
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

    def open_file(self):
        filepath = QFileDialog.getOpenFileName(self, 'Open file', './images')[0]
        filetype = filepath.split('.')[-1]
        if filetype not in self.configModule.config["accepted_files"]:
            print("wrong type of image file")
            return
        self.current_image = filepath

        if filetype == 'pgm':
            pgm_ex = Image(self)
            pgm_ex.draw_pgm_sample(self.current_image)
        elif filetype == 'ppm':
            ppm_ex = Image(self)
            ppm_ex.draw_ppm_sample(self.current_image)



    def _createMenuBar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')

        open_file_action = QAction('&Open', self)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        # p5_action = QAction('&P5', self)
        # p5_action.triggered.connect(self.open_pgm)
        # file_menu.addAction(p5_action)
        #
        # p6_action = QAction('&P6', self)
        # p6_action.triggered.connect(self.open_ppm)
        # file_menu.addAction(p6_action)
        #
        # p5_action_painted = QAction('&P5 - painted', self)
        # p5_action_painted.triggered.connect(self.open_pgm_painted)
        # file_menu.addAction(p5_action_painted)
        #
        # p6_action_painted = QAction('&P6 - painted', self)
        # p6_action_painted.triggered.connect(self.open_ppm_painted)
        # file_menu.addAction(p6_action_painted)

        painter = menu_bar.addAction('&Paint')
        painter.triggered.connect(self.open_painter)
