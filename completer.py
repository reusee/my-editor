from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re

MAX_WORD_LENGTH = 256

class Completer(QWidget):

  wordPattern = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9-]*')
  partialPattern = re.compile(r'[a-zA-Z0-9][a-zA-Z0-9-]*\Z')
  buf = bytearray(MAX_WORD_LENGTH)

  def __init__(self, parent):
    super(QWidget, self).__init__(parent)
    self.editor = parent

    self.model = QStringListModel()
    self.view = QListView(parent)
    self.view.setModel(self.model)
    self.view.setAttribute(Qt.WA_TransparentForMouseEvents)
    self.view.hide()

    self.words = set()
    self.partial = []
    self.partialStartPos = 0
    self.candidates = set()

    self.editor.modified.connect(self.textChanged)
    self.editor.editModeEntered.connect(self.editModeEntered)
    self.editor.editModeLeaved.connect(self.editModeLeaved)

  def textChanged(self, position, modType, text, length, linesAdded, _line, _foldLevelNow, _foldLevelPrev, _token, _annotationLinesAdded):
    if text: text = text.decode('utf8')
    if modType & self.editor.base.SC_MOD_INSERTTEXT and self.editor.mode == self.editor.COMMAND: # not by typing
      self.words.update(set(self.wordPattern.findall(text)))
    elif modType & self.editor.base.SC_MOD_INSERTTEXT and self.editor.mode == self.editor.EDIT: # typing in
      assert len(text) == 1
      if self.isWordChar(text): # is a word char
        self.feedPartialChar(text, self.editor.getPos() + 1)
      else:  # not a word char
        self.collectWord()
        self.reHint(self.editor.getPos() + 1)
    elif modType & self.editor.base.SC_MOD_DELETETEXT and self.editor.mode == self.editor.COMMAND: # delete command
      self.clearHint()
    elif modType & self.editor.base.SC_MOD_DELETETEXT and self.editor.mode == self.editor.EDIT: # delete edit
      self.reHint(self.editor.getPos())

    if self.editor.mode == self.editor.EDIT: # show candidates
      words = sorted(self.candidates, key = lambda w: len(w))[:10]
      if len(words) > 0:
        self.model.setStringList(words)
        self.view.show()
        x, y = self.editor.getCaretPos(self.partialStartPos)
        y += self.editor.getLineHeight()
        self.view.move(x, y)
      else:
        self.view.hide()

  def feedPartialChar(self, c, pos):
    lowerC = c.lower()
    self.partial.append(c)
    if len(self.partial) == 1: # first char
      self.candidates = {word
          for word in self.words
          if word[0].lower() == lowerC
          }
      self.partialStartPos = pos
    else:
      self.candidates.difference_update({word
        for word in self.candidates
        if not self.fuzzyMatch(''.join(self.partial), word.lower())
        })

  def clearHint(self):
    self.partial.clear()
    self.candidates.clear()
    self.view.hide()

  def reHint(self, caretPos):
    self.clearHint()
    startPos = caretPos - MAX_WORD_LENGTH
    if startPos < 0: startPos = 0
    self.editor.send('sci_gettextrange', startPos, caretPos, self.buf)
    left = self.buf.decode('utf8')[:caretPos - startPos]
    partial = self.partialPattern.findall(left)
    partialStartPos = caretPos - len(partial)
    if len(partial) > 0:
      for i, c in enumerate(partial[0]): 
        self.feedPartialChar(c, partialStartPos + i)

  def collectWord(self):
    word = ''.join(self.partial)
    if word: self.words.add(word)

  def editModeEntered(self):
    self.reHint(self.editor.getPos())

  def editModeLeaved(self):
    self.collectWord()
    self.clearHint()

  def isWordChar(self, c):
    return c.isalpha() or c.isdigit() or c == '-'

  def fuzzyMatch(self, key, s):
    keyI = 0
    sI = 0
    while keyI < len(key) and sI < len(s):
      if s[sI] == key[keyI]:
        sI += 1
        keyI += 1
      else:
        sI += 1
    return keyI == len(key)
