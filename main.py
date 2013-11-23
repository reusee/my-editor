#!/usr/bin/env python
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import sys
import traceback

from editor import *

class Main(QWidget):
    def __init__(self):
        super().__init__()

        # root layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(1)
        self.setLayout(self.layout)

        # first editor
        self.editorLayout = QVBoxLayout()
        self.layout.addLayout(self.editorLayout)
        self.editor = Editor()
        self.editor.layout.setup(self.editorLayout) #TODO 
        self.editor.active = True

        # exception handling
        sys.excepthook = self.excepthook
        self.exceptionBoard = ExceptionBoard()
        self.layout.addWidget(self.exceptionBoard)
        self.exceptionBoard.hide()

    def excepthook(self, type, value, tback):
        self.exceptionBoard.setText('\n'.join(traceback.format_exception(type, value, tback)))
        self.exceptionBoard.show()

class ExceptionBoard(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
