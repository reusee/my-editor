from PyQt4.Qsci import *
from PyQt4.QtCore import *
import os
import ctypes

class Documents(QObject):
  def __init__(self, editor):
    super(Documents, self).__init__()
    self.editor = editor
    editor.openRequested.connect(self.open)
    self.documents = []
    self.index = -1

  def open(self, path):
    if not path: return
    if self.index >= 0:
      if self.documents[self.index].path == path: return
      self.documents[self.index].pos = self.editor.getPos()
    index = -1
    for i in range(len(self.documents)):
      if self.documents[i].path == path:
        index = i
        break
    if index >= 0: # already opened
      self.switchByIndex(index)
    else: # open
      f = open(path, 'r')
      doc = self.editor.send('sci_createdocument')
      self.editor.send('sci_setdocpointer', 0, doc)
      self.editor.send('sci_settext', ctypes.create_string_buffer(f.read().encode('utf8')))
      self.documents.append(Document(path, doc))
      self.index = len(self.documents) - 1
      self.setupLexer(path)

  def setupLexer(self, path):
    if path.endswith('.py'): # lexer
      lexer = QsciLexerPython()
      lexer.setDefaultFont(self.editor.font)
      self.editor.setLexer(lexer)
      self.editor.send("sci_stylesetfont", 1, b'Terminus')

  def switchByIndex(self, index):
    document = self.documents[index]
    self.editor.send('sci_setdocpointer', 0, document.pointer)
    self.editor.send('sci_setcurrentpos', document.pos)
    self.editor.send('sci_setsel', -1, self.editor.getPos())
    self.index = index

  def nextDocument(self):
    index = self.index + 1
    if index == len(self.documents):
      index = 0
    self.switchByIndex(index)

  def prevDocument(self):
    index = self.index - 1
    if index < 0:
      index = len(self.documents) - 1
    self.switchByIndex(index)

class Document:
  def __init__(self, path, pointer):
    self.path = path
    self.pointer = pointer
    self.pos = 0
