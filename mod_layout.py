from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Layout:
  editors = []

  def __init__(self, editor):
    self.editor = editor
    self.layout = None

  def register(self, editor):
    self.editors.append(editor)
    editor.cloned.connect(self.register)

  def setup(self, layout):
    layout.addWidget(self.editor)
    self.layout = layout
    self.register(self.editor)

  # split

  def siblingSplit(self):
    editor = self.editor.clone()
    index = self.layout.indexOf(self.editor)
    self.layout.insertWidget(index + 1, editor)
    editor.layout.layout = self.layout
    editor.setFocus()

  def split(self, layoutClass):
    editor = self.editor.clone()
    layout = layoutClass()
    index = self.layout.indexOf(self.editor)
    self.layout.removeWidget(self.editor)
    layout.addWidget(self.editor)
    layout.addWidget(editor)
    self.layout.insertLayout(index, layout)
    editor.layout.layout = layout
    self.layout = layout
    editor.setFocus()

  # switch

  def next(self):
    index = self.editors.index(self.editor)
    index += 1
    if index == len(self.editors):
        index = 0
    self.switch(index)

  def prev(self):
    index = self.editors.index(self.editor)
    index -= 1
    if index < 0:
        index = len(self.editors) - 1
    self.switch(index)

  def switch(self, index):
    self.editor.active = False
    self.editors[index].active = True
    self.editors[index].setFocus()

  def mapRect(self, editor):
    rect = editor.rect()
    return QRect(editor.mapToGlobal(rect.topLeft()), editor.mapToGlobal(rect.bottomRight()))

  def iterAndSwitch(self, p):
    for i, editor in enumerate(self.editors):
      if self.mapRect(editor).contains(p):
        self.switch(i)
        return True

  def north(self):
    p = self.mapRect(self.editor).topLeft() + QPoint(0, -10)
    if not self.iterAndSwitch(p):
      self.south()

  def south(self):
    p = self.mapRect(self.editor).bottomLeft() + QPoint(0, 10)
    if not self.iterAndSwitch(p):
      self.north()

  def west(self):
    p = self.mapRect(self.editor).topLeft() + QPoint(-10, 0)
    if not self.iterAndSwitch(p):
      self.east()

  def east(self):
    p = self.mapRect(self.editor).topRight() + QPoint(10, 0)
    if not self.iterAndSwitch(p):
      self.west()

  # close

  def close(self):
    if len(self.editors) == 1: return # do not close the only one editor
    self.layout.removeWidget(self.editor)
    self.editors.remove(self.editor)
    self.editor.hide()
    self.switch(0)
