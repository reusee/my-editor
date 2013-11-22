from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class ErrorHandler:
  def __init__(self, editor):
    editor.errored.connect(self.show)
    self.editor = editor
    self.errorLabel = QLabel(editor)
    self.errorLabel.setStyleSheet('''
    QLabel {
      background-color: yellow;
    }
    ''')
    self.errorLabel.setWordWrap(True)
    self.fontMetrics = QFontMetrics(self.errorLabel.font())
    self.errorLabel.hide()
    self.timer = None

  def show(self, msg):
    parentSize = self.editor.size()
    rect = self.fontMetrics.boundingRect(msg)
    self.errorLabel.resize(rect.size())
    self.errorLabel.setText(msg)
    x = parentSize.width() / 2 - rect.width() / 2
    y = parentSize.height() / 2 - rect.height() / 2
    self.errorLabel.move(x, y)
    self.errorLabel.show()
    if self.timer: self.timer.stop()
    self.timer = QTimer.singleShot(3000, lambda: self.errorLabel.hide())
