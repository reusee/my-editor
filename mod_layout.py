from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Layout:
  editors = []

  def __init__(self, editor):
    self.editor = editor
    self.layout = None

  def siblingSplit(self):
    editor = self.editor.clone()
    index = self.layout.indexOf(self.editor)
    self.layout.insertWidget(index + 1, editor)
    editor.layout.layout = self.layout

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

  def next(self):
    self.editor.active = False
    index = self.editors.index(self.editor)
    index += 1
    if index == len(self.editors):
        index = 0
    self.editors[index].active = True
    self.editors[index].setFocus()

  def prev(self):
    self.editor.active = False
    index = self.editors.index(self.editor)
    index -= 1
    if index < 0:
        index = len(self.editors) - 1
    self.editors[index].active = True
    self.editors[index].setFocus()

  def register(self, editor):
    self.editors.append(editor)
    editor.cloned.connect(self.register)

  def setup(self, layout):
    layout.addWidget(self.editor)
    self.layout = layout
    self.register(self.editor)
