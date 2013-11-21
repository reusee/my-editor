from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class CmdLayout:
  def __init__(self):
    super().__init__()
    self.parentLayout = None

  def siblingSplit(self):
    editor = self.clone()
    self.parentLayout.addWidget(editor)
    self.parentLayout = self.parentLayout

  def split(self, layoutClass):
    editor = self.clone()
    layout = layoutClass()
    self.parentLayout.removeWidget(self)
    layout.addWidget(self)
    layout.addWidget(editor)
    self.parentLayout.addLayout(layout)
    editor.parentLayout = layout
    self.parentLayout = layout
