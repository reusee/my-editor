from PyQt4.QtCore import *
from PyQt4.QtGui import *

def H(*args, **kwargs):
  return layout(QHBoxLayout, *args, **kwargs)

def V(*args, **kwargs):
  return layout(QVBoxLayout, *args, **kwargs)

def layout(t, *args, **kwargs):
  layout = t()
  layout.setSpacing(kwargs.get('spacing', 0))
  layout.setContentsMargins(0, 0, 0, 0)
  for child in args:
    stretch = 0
    if isinstance(child, tuple):
      child, stretch = child
    if isinstance(child, QLayout):
      layout.addLayout(child, child.__dict__.get('_stretch', 0))
    elif isinstance(child, QWidget):
      layout.addWidget(child, stretch)
    elif isinstance(child, S):
      layout.addStretch(child.stretch)
    elif isinstance(child, int):
      layout.__dict__['_stretch'] = child
    else:
      not_addable
  return layout

class S:
  def __init__(self, stretch = 1):
    self.stretch = stretch
