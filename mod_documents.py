from PyQt4.Qsci import *
from PyQt4.QtCore import *
import os
import ctypes

class Documents(QObject):
  def __init__(self, editor):
    super(Documents, self).__init__()
    self.editor = editor
    editor.openRequested.connect(self.open)
    self.documents = {}
    self.path = None

  def open(self, path):
    if not path: return
    if self.path == path: return
    if self.path:
      self.documents[self.path].pos = self.editor.getPos()
    if path in self.documents:
      self.editor.send('sci_setdocpointer', 0, self.documents[path].pointer)
      self.editor.send('sci_setcurrentpos', self.documents[path].pos)
      self.editor.send('sci_setsel', -1, self.editor.getPos())
      self.path = path
    else:
      f = open(path, 'r')
      doc = self.editor.send('sci_createdocument')
      self.editor.send('sci_setdocpointer', 0, doc)
      self.editor.send('sci_settext', ctypes.create_string_buffer(f.read().encode('utf8')))
      self.documents[path] = Document(doc)
      self.path = path
      self.setupLexer(path)

  def setupLexer(self, path):
    if path.endswith('.py'): # lexer
      lexer = QsciLexerPython()
      lexer.setDefaultFont(self.editor.font)
      self.editor.setLexer(lexer)
      self.editor.send("sci_stylesetfont", 1, b'Terminus')

class Document:
  def __init__(self, pointer):
    self.pointer = pointer
    self.pos = 0
