from PyQt4.QtCore import *
from PyQt4.QtGui import *
import re

MAX_WORD_LENGTH = 256

class Completer(QWidget):
  buf = bytearray(MAX_WORD_LENGTH)
  prefixPattern = re.compile(r'[a-zA-Z0-9_][a-zA-Z0-9-_]*\Z')
  wordPattern = re.compile(r'[a-zA-Z0-9_][a-zA-Z0-9-_]*')

  def __init__(self, parent):
    super(QWidget, self).__init__(parent)
    self.editor = parent

    self.model = QStringListModel()
    self.view = View(parent)
    self.view.setModel(self.model)

    self.words = set()
    self.currentRange = None
    self.completing = False

    self.editor.editModeEntered.connect(self.editModeEntered)
    self.editor.editModeLeaved.connect(self.editModeLeaved)
    self.editor.modified.connect(self.textChanged)

  def editModeEntered(self):
    self.newRange(self.editor.getPos())

  def editModeLeaved(self):
    self.collectCurrentRange()
    self.view.hide()
    self.currentRange = None

  def textChanged(self, position, modType, text, length, linesAdded, _line, _foldLevelNow, _foldLevelPrev, _token, _annotationLinesAdded):
    if self.completing: return
    if text: text = text.decode('utf8')
    if self.editor.mode == self.editor.EDIT:
      if modType & self.editor.base.SC_MOD_INSERTTEXT: # insert by edit
        if self.isWordChar(text): # a word char
          assert len(text) == 1 # typing
          assert not self.currentRange is None
          if self.currentRange.index != -1: # a dirty range
            self.newRange(position + 1)
          else: # good range
            self.currentRange.feed(text, position)
        else: # not a word char
          if not self.currentRange is None: # end of a word
            self.collectCurrentRange()
            self.newRange(position + len(text))
      elif modType & self.editor.base.SC_MOD_DELETETEXT: # delete by edit
        self.newRange(self.editor.getPos())
    elif self.editor.mode == self.editor.COMMAND:
      if modType & self.editor.base.SC_MOD_INSERTTEXT: # insert by command
        self.words.update( # update word dict
            set(self.wordPattern.findall(text)))

  def collectCurrentRange(self):
    if not self.currentRange is None:
      word = ''.join(self.currentRange.chars)
      if word == '': return
      self.words.add(word)

  def rangeChanged(self):
    if self.editor.mode == self.editor.EDIT:
      if self.currentRange:
        words = self.currentRange.showing
        if len(words) > 0:
          self.model.setStringList(words)
          self.view.resize(300, self.view.lineHeight * (2 + len(words)))
          self.view.setCurrentIndex(self.model.index(self.currentRange.index))
          self.view.show()
          x, y = self.editor.getPosXY(self.currentRange.startPos)
          self.view.move(x, y + self.editor.getLineHeight())
          return
    self.view.hide()

  def isWordChar(self, c):
    return c.isalpha() or c.isdigit() or c in {'-', '_'}

  def newRange(self, pos):
    start = pos - MAX_WORD_LENGTH
    if start < 0: start = 0
    self.editor.send('sci_gettextrange', start, pos, self.buf)
    left = self.buf[:pos - start].decode('utf8')
    prefix = self.prefixPattern.findall(left)
    r = Range(self.editor, self.words, pos, pos)
    if len(prefix) > 0:
      prefix = prefix[0]
      start = pos - len(prefix)
      r.startPos = start
      r.endPos = start
      for i, c in enumerate(prefix):
        r.feed(c, start + i)
    r.changed.connect(self.rangeChanged)
    self.currentRange = r
    self.rangeChanged()

  def nextCandidate(self):
    if len(self.currentRange.showing) == 0:
      return False
    self.completing = True
    if self.currentRange.index == -1:
      self.currentRange.showing.append( # add current chars to showing
          ''.join(self.currentRange.chars))
    self.currentRange.index += 1
    if self.currentRange.index == len(self.currentRange.showing):
      self.currentRange.index = 0
    replace = self.currentRange.showing[self.currentRange.index]
    replace = replace.encode('utf8')
    self.editor.send('sci_settargetstart', self.currentRange.startPos)
    self.editor.send('sci_settargetend', self.currentRange.endPos)
    self.editor.send('sci_replacetarget', len(replace), replace)
    for i in range(len(replace)): self.editor.send('sci_charright')
    self.currentRange.endPos = self.currentRange.startPos + len(replace)
    self.rangeChanged()
    self.completing = False
    return True

class Range(QObject):
  changed = pyqtSignal()

  def __init__(self, editor, words, startPos, endPos):
    super(QObject, self).__init__()
    self.words = words
    self.editor = editor

    self.startPos = startPos # start position of document
    self.endPos = endPos # end position of document
    self.chars = [] # user entered chars
    self.candidates = set() # word candidates
    self.showing = [] # showing candidates
    self.index = -1 # selected candidate index

  def dump(self):
    print('Range:', '%d-%d' % (self.startPos, self.endPos), ''.join(self.chars))
    for c in self.showing:
      print('\t', c)

  def feed(self, c, pos):
    assert pos == self.endPos
    self.endPos += 1
    self.chars.append(c)
    lowerC = c.lower()
    prefix = ''.join(self.chars)
    if len(self.chars) == 1: # first char of a word
      self.candidates = {word
          for word in self.words
          if word[0].lower() == lowerC and word != prefix
          }
    else:
      self.candidates.difference_update({word
        for word in self.candidates
        if not self.fuzzyMatch(prefix.lower(), word.lower()) or (word == prefix)
        })
    self.showing = sorted(self.candidates, key = lambda w: (
      not w.startswith(prefix),
      len(w),
      ))
    self.index = -1
    self.changed.emit()

  def fuzzyMatch(self, key, s):
    if key == s: return False
    keyI = 0
    sI = 0
    while keyI < len(key) and sI < len(s):
      if s[sI] == key[keyI]:
        sI += 1
        keyI += 1
      else:
        sI += 1
    return keyI == len(key)

class View(QListView):
  def __init__(self, parent):
    super(QListView, self).__init__(parent)
    self.setAttribute(Qt.WA_TransparentForMouseEvents)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setSelectionBehavior(self.SelectRows)
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.hide()
    self.setStyleSheet('''
    QListView {
      border: 0;
      border-radius: 20px;
      background-color: rgba(32, 32, 32, 70%);
      color: #FFF;
      font-weight: bold;
      padding: 10px;
    }
    QListView::item:selected {
      background-color: rgba(0, 0, 0, 0%);
      color: #0F0;
      font-weight: bold;
    }
    ''')
    self.setFont(QFont('Terminus', 13))
    metric = QFontMetrics(self.font())
    rect = metric.boundingRect('foo')
    self.lineHeight = rect.height()
