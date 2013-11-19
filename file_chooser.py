from PyQt4.QtCore import *
from PyQt4.QtGui import *

class FileChooser(QWidget):
  def __init__(self, parent):
    super(QWidget, self).__init__(parent)

  def choose(self):
    return 'editor.py'
