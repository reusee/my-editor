#!/usr/bin/env python
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys

from editor import *

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.editor = Editor()
        self.setCentralWidget(self.editor)

def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
