from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Status(QWidget):
  def __init__(self, parent):
    super().__init__(parent)
    self.editor = parent
    self.raise_()
    self.setAttribute(Qt.WA_TransparentForMouseEvents)
    self.commandText = ""

    parent.resized.connect(lambda ev: self.resize(ev.size()))
    parent.commandCanceled.connect(self.clearCommandText)
    parent.commandPrefix.connect(lambda t: self.appendCommandText(t))
    parent.commandRunned.connect(self.clearCommandText)
    parent.commandInvalid.connect(self.clearCommandText)

  def paintEvent(self, ev):
    painter = QPainter(self)
    painter.setPen(QPen(QColor("#F58220")))
    font = QFont('Times', 32)
    painter.setFont(font)
    rect = QFontMetrics(font).boundingRect(self.commandText)
    x, y = self.editor.getPosXY(self.editor.getPos())
    y += rect.height()
    if x + rect.width() > self.width():
      x -= rect.width()
    if y + rect.height() > self.height():
      y -= rect.height()
    painter.drawText(QPoint(x, y), self.commandText)

  def appendCommandText(self, t):
    self.commandText += t
    self.update()

  def clearCommandText(self):
    self.commandText = ""
    self.update()
