import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Test image'
        self.left = 0
        self.top = 0
        self.width = 640
        self.height = 480
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create widget
        label = QLabel(self)
        pixmap = QPixmap('2107.jpeg')
        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
