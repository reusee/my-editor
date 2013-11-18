from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Terminal(QWidget):
  def __init__(self, parent):
    super(QWidget, self).__init__(parent)
    self.process = QProcess(self)
    self.process.start('urxvt',
        ['-embed', str(self.winId())])
    parent.resized.connect(self.resized)

  def resized(self):
    parentSize = self.parent().size()
    width = parentSize.width() / 2
    self.resize(width, parentSize.width())
    self.move(parentSize.width() - width, 0)
