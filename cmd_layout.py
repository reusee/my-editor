from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CmdLayout:
  def siblingSplit(self):
    editor = self.clone()
    self.parentLayout.addWidget(editor)
    setattr(editor, 'parentLayout', self.parentLayout)

  def split(self, layoutClass):
    editor = self.clone()
    layout = layoutClass()
    self.parentLayout.removeWidget(self)
    layout.addWidget(self)
    layout.addWidget(editor)
    self.parentLayout.addLayout(layout)
    setattr(editor, 'parentLayout', layout)
    setattr(self, 'parentLayout', layout)
