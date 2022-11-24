from PyQt5.QtWidgets import QInputDialog


class GammaInput:
    def __init__(self, parent=None):
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.line_input, pressed = QInputDialog.getDouble(self.parent, "Value", "Value", 2, 0.01, 5)
        if pressed:
            self.editing_finished()

    def gamma_value(self):
        if float(self.line_input) > 1:
            return (float(self.line_input) - 1) * 25
        return -(1 / (float(self.line_input)) - 1)

    def editing_finished(self):
        print(self.gamma_value())
        self.parent.gamma = self.gamma_value()
        if self.parent.current_image is not None:
            self.parent.draw_raster_map(self.parent._type)
