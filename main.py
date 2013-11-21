#!/usr/bin/env python
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

from editor import *

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.centralWidget.setLayout(self.layout)

        self.editor = Editor()
        self.layout.addWidget(self.editor)
        self.editor.parentLayout = self.layout
        self.editor.active = True

        self.editors = []
        self.register(self.editor)

    def register(self, editor):
        self.editors.append(editor)
        editor.nextEditorRequested.connect(self.nextEditor)
        editor.prevEditorRequested.connect(self.prevEditor)
        editor.cloned.connect(self.register)

    def nextEditor(self, e):
        e.active = False
        index = self.editors.index(e)
        index += 1
        if index == len(self.editors):
            index = 0
        self.editors[index].active = True
        self.editors[index].setFocus()

    def prevEditor(self, e):
        e.active = False
        index = self.editors.index(e)
        index -= 1
        if index < 0:
            index = len(self.editors) - 1
        self.editors[index].active = True
        self.editors[index].setFocus()

def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
