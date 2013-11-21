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
    editor.cloned.connect(self.clone)

  def open(self, path):
    if not path: return
    self.saveCurrent()
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

  def saveCurrent(self):
    if self.index >= 0:
      self.documents[self.index].pos = self.editor.getPos()
      self.documents[self.index].topLineNumber = self.editor.send('sci_getfirstvisibleline')

  def switchByIndex(self, index):
    self.saveCurrent()
    document = self.documents[index]
    self.editor.send('sci_setdocpointer', 0, document.pointer) # switch
    self.editor.send('sci_setcurrentpos', document.pos) # restore status
    self.editor.send('sci_setsel', -1, self.editor.getPos())
    self.editor.send('sci_linescroll', 0, document.topLineNumber - self.editor.send('sci_getfirstvisibleline'))
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

  def clone(self, editor):
    editor.documents.documents = self.documents

class Document:
  def __init__(self, path, pointer):
    self.path = path
    self.pointer = pointer
    self.pos = 0
    self.topLineNumber = 0
