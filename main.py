#!/usr/bin/env python
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
from layout import *

from editor import *

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.editor = Editor()
        self.editor2 = self.editor.clone()

        self.centralWidget.setLayout(
                H(self.editor, self.editor2),
                )

def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
