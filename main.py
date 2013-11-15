from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys

from editor import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.editor = Editor()
        self.setCentralWidget(self.editor)

        self.editor.load(sys.argv[1])

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
