from PyQt4.QtCore import *
from PyQt4.QtGui import *

class Completer(QWidget):
  def __init__(self, parent):
    super(QWidget, self).__init__(parent)
    self.incoming = []
    self.words = set()
    self.candidates = set()
    self.callback = None

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
    if self.callback:
      self.callback(sorted(self.candidates, key = lambda w: len(w)))

  def feedString(self, s): # todo
    for c in s:
      self.feed(c)

  def paintEvent(self, ev):
    print('ok')
    pass
