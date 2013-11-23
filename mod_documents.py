from PyQt5.Qsci import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import ctypes
import time

class Documents(QObject):
  def __init__(self, editor):
    super().__init__()
    self.editor = editor
    self.documents = []
    self.index = -1
    editor.cloned.connect(self.clone)

  def open(self, path):
    if not path: return
    self.saveDocumentState()
    index = -1
    for i in range(len(self.documents)):
      if self.documents[i].path == path:
        index = i
        break
    if index >= 0: # already opened
      self.switchByIndex(index)
    else: # open
      try:
        f = open(path, 'rb')
      except IsADirectoryError:
        return
      doc = self.editor.send('sci_createdocument')
      self.editor.send('sci_setdocpointer', 0, doc)
      self.editor.setUtf8(True)
      self.editor.send('sci_settext', f.read())
      self.documents.append(Document(path, doc))
      self.index = len(self.documents) - 1
    self.setupLexer(path)
    self.editor.setThemeRequested.emit()
    self.editor.setMarginsBackgroundColor(QColor("#222222"))
    self.editor.send('sci_emptyundobuffer')

  def setupLexer(self, path):
    if path.endswith('.py'): # lexer
      lexer = QsciLexerPython()
      self.editor.setLexer(lexer)
    else:
      self.editor.send('sci_stylesetback', self.editor.base.STYLE_DEFAULT, 0x000000)
      self.editor.send('sci_stylesetfore', self.editor.base.STYLE_DEFAULT, 0x000000)
      self.editor.send('sci_styleclearall')

  def saveDocumentState(self):
    if self.index >= 0:
      self.documents[self.index].pos = self.editor.getPos()
      self.documents[self.index].topLineNumber = self.editor.send('sci_getfirstvisibleline')

  def switchByIndex(self, index):
    self.saveDocumentState()
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

  def save(self):
    if self.index < 0: return
    if not self.editor.send('sci_getmodify'): return
    path = self.documents[self.index].path
    tmpPath = path + '.' + str(time.time())
    with open(tmpPath, 'wb+') as out:
      length = self.editor.send('sci_getlength')
      buf = bytearray(length + 1)
      self.editor.send('sci_gettext', length + 1, buf)
      out.write(buf[:length])
    os.rename(tmpPath, path)
    self.editor.send('sci_setsavepoint')

class Document:
  def __init__(self, path, pointer):
    self.path = path
    self.pointer = pointer
    self.pos = 0
    self.topLineNumber = 0
