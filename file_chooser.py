from PyQt4.QtCore import *
from PyQt4.QtGui import *

class FileChooser(QDialog):
  def __init__(self, parent):
    super(FileChooser, self).__init__(parent)

    self.edit = QLineEdit(self)
    self.edit.returnPressed.connect(self.accept)
    self.foo = None

  def accept(self):
    self.foo = self.edit.text()
    super(FileChooser, self).accept()

  def reject(self):
    self.foo = None
    super(FileChooser, self).reject()

  def choose(self):
    self.exec_()
    return self.foo
