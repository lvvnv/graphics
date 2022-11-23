from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QSlider, QLabel


class GammaSlider(QtWidgets.QMainWindow):
    def __init__(self, value=0, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI(value)

    def initUI(self, value):

        hbox = QHBoxLayout()

        self.sld = QSlider(Qt.Orientation.Horizontal, self)
        self.sld.setRange(-49, 50)
        self.sld.setPageStep(1)
        self.sld.setValue(value)

        self.sld.valueChanged.connect(self.updateLabel)
        self.sld.sliderReleased.connect(self.slider_released)

        self.label = QLabel(str(value), self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter |
                                Qt.AlignmentFlag.AlignVCenter)
        self.label.setMinimumWidth(80)

        hbox.addWidget(self.sld)
        hbox.addSpacing(15)
        hbox.addWidget(self.label)

        self.setLayout(hbox)

        self.setGeometry(300, 100, 350, 250)
        self.setWindowTitle('QSlider')
        self.setCentralWidget(self.sld)
        self.show()

    def updateLabel(self, value):
        self.label.setText(str(value))

    def slider_released(self):
        self.parent.gamma = self.sld.value()
        if self.parent.current_image is not None:
            self.parent.draw_raster_map(self.parent._type)
