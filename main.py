from PyQt5.QtWidgets import QApplication
from modules.gui import Window

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
