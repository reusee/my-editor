from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Status(QWidget):
  def __init__(self, parent):
    super(QWidget, self).__init__(parent)
    self.editor = parent
    self.raise_()
    self.setAttribute(Qt.WA_TransparentForMouseEvents)
    self.commandText = ""

  def paintEvent(self, ev):
    painter = QPainter(self)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.TextAntialiasing)
    painter.setPen(QPen(QColor("#F58220")))
    painter.setFont(QFont('Times', 64))
    painter.drawText(QPoint(self.width() / 2, self.height() / 2), self.commandText)

  def appendCommandText(self, t):
    self.commandText += t
    self.update()

  def clearCommandText(self):
    self.commandText = ""
    self.update()
