from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QLineEdit


class GammaInput(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.line_input = QLineEdit(self)
        self.line_input.setValidator(QDoubleValidator(0.01, 5.00, 2))

        self.line_input.editingFinished.connect(self.editing_finished)

        self.setGeometry(300, 100, 350, 250)
        self.setWindowTitle('QLineEdit')
        self.show()

    def gamma_value(self):
        if float(self.line_input.text()) > 1:
            return (float(self.line_input.text()) - 1) * 25
        return -(1 / (float(self.line_input.text())) - 1)

    def editing_finished(self):
        print(self.gamma_value())
        self.parent.gamma = self.gamma_value()
        if self.parent.current_image is not None:
            self.parent.draw_raster_map(self.parent._type)
