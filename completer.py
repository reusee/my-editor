from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Completer(QWidget):
  def __init__(self, parent):
    super(QWidget, self).__init__(parent)
    self.incoming = []
    self.words = set()
    self.candidates = set()
    self.editor = parent

    self.model = QStringListModel()
    self.view = QListView(parent)
    self.view.setModel(self.model)
    self.view.setAttribute(Qt.WA_TransparentForMouseEvents)
    self.view.hide()

    self.editor.modified.connect(self.textChanged)
    self.editor.editModeEntered.connect(self.editModeEntered)
    self.editor.editModeLeaved.connect(self.editModeLeaved)

  def textChanged(self, position, modType, text, length, linesAdded, line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded):
    if modType & self.editor.base.SC_MOD_INSERTTEXT:
      print('insert', 'pos:', position, 'len:', length, 'lines:', linesAdded, 'text:', text)
    elif modType & self.editor.base.SC_MOD_DELETETEXT:
      print('delete', 'pos:', position, 'len:', length, 'lines:', linesAdded, 'text:', text)

  def editModeEntered(self):
    print('enterEditMode')

  def editModeLeaved(self):
    print('editModeLeaved')

  def feed(self, c):
    if c.isalpha() or c.isdigit(): # inside a word
      self.incoming.append(c)
      if len(self.incoming) == 1: # first char
        self.candidates.update({word
          for word in self.words
          if word[0].lower() == c.lower()})
      else: 
        self.candidates.difference_update({word
          for word in self.candidates
          if c.lower() not in word[len(self.incoming) - 1 : ].lower()
          })
    else: # found a word
      word = ''.join(self.incoming)
      if word:
        self.words.add(word)
      self.incoming.clear()
      self.candidates.clear()
    candidates = sorted(self.candidates, key = lambda w: len(w))[:10]
    if len(candidates) > 0:
      self.model.setStringList(candidates)
      x, y = self.editor.caretXY()
      self.view.move(x, y + self.editor.lineHeight())
      self.view.show()
    else:
      self.view.hide()
