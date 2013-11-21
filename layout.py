from PyQt4.QtCore import *
from PyQt4.QtGui import *

H, V = range(2)

def parseLayout(desc):
  layoutClass = QHBoxLayout
  if desc[0] == V:
    layoutClass = QVBoxLayout
  layout = layoutClass()
  layout.setSpacing(0)
  layout.setContentsMargins(0, 0, 0, 0)
  for child in desc[1:]:
    if isinstance(child, list):
      layout.addLayout(parseLayout(child))
    else:
      layout.addWidget(child)
  return layout
