from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CmdLayout:
  def __init__(self):
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
