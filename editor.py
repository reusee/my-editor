from PyQt4.Qsci import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
import os

from editor_base import *

# commands
from cmd_locate import *

# components
from status import *
from completer import *
from file_chooser import *

# lexer
# extra components
# key bindings
class Editor(EditorBase,
    CmdLocate,
    ):

  def __init__(self):
    super(Editor, self).__init__()

    self.lexer = None
    self.n = 0

    self.errored.connect(lambda msg: print(msg)) # TODO

    # components
    self.completer = Completer(self)
    self.status = Status(self)
    self.file_chooser = FileChooser(self)

    # key bindings
    self.commandModeKeys = {
        'q': (self.lexe(self.modeSelectRectangle), self.lexe(self.modeSelectNone), self.lexe(self.modeSelectNone)),
        'e': (self.lexe('Home'), self.lexe('HomeExtend'), self.lexe('HomeRectExtend')),
        'r': (self.lexe('LineEnd'), self.lexe('LineEndExtend'), self.lexe('LineEndRectExtend')),
        'y': (
          {'y': self.lexe('LineCopy'), 'p': self.lexe('LineDuplicate'), 'x': self.lexe('LineTranspose')},
          self.lexe('SelectionCopy', self.modeSelectNone),
          self.lexe('SelectionCopy', self.modeSelectNone),
          ),
        'u': self.lexe('Undo'),
        'U': (self.lexe('PageUp'), self.lexe('PageUpExtend'), self.lexe('PageUpRectExtend')),
        'i': self.lexe(self.modeEdit),
        'I': self.lexe('Home', self.modeEdit),
        'o': self.lexe(self.beginUndoAction, 'LineEnd', 'Newline', self.modeEdit, self.endUndoAction),
        'O': self.lexe(self.beginUndoAction, 'Home', 'Newline', 'LineUp', self.modeEdit, self.endUndoAction),
        'p': self.lexe('Paste'),
        '[': (self.lexe('ParaUp'), self.lexe('ParaUpExtend'), self.lexe('ParaUpExtend')),
        ']': (self.lexe('ParaDown'), self.lexe('ParaDownExtend'), self.lexe('ParaDownExtend')),

        'a': self.lexe('CharRight', self.modeEdit),
        'A': self.lexe('LineEnd', self.modeEdit),
        's': lambda _: self.locateByTwoChars,
        'S': lambda _: self.locateBackwardByTwoChars,
        'd': (
          {
            'e': self.lexe('DeleteLineLeft'),
            'r': self.lexe('DeleteLineRight'),
            'd': self.lexe('LineCut'),
            'h': self.lexe('DeleteWordLeft'),
            'l': self.lexe('DeleteWordRightEnd'),
            },
          self.lexe('SelectionCut', self.modeSelectNone),
          self.lexe('SelectionCut', self.modeSelectNone),
          ),
        'f': self.makeCharLocators(),
        'F': self.makeCharLocators(backward = True),
        'g': {
          'g': (self.lexe('DocumentStart'), self.lexe('DocumentStartExtend'), self.lexe('DocumentStartExtend')),
          'a': self.lexe('SelectAll'),
          },
        'G': (self.lexe('DocumentEnd'), self.lexe('DocumentEndExtend'), self.lexe('DocumentEndExtend')),
        'h': (self.lexe('CharLeft'), self.lexe('CharLeftExtend'), self.lexe('CharLeftRectExtend')),
        'j': (self.lexe('LineDown'), self.lexe('LineDownExtend'), self.lexe('LineDownRectExtend')),
        'J': (self.lexe('LineScrollUp'), self.lexe('MoveSelectedLinesDown'), self.lexe('MoveSelectedLinesDown')),
        'k': (self.lexe('LineUp'), self.lexe('LineUpExtend'), self.lexe('LineUpRectExtend')),
        'K': (self.lexe('LineScrollDown'), self.lexe('MoveSelectedLinesUp'), self.lexe('MoveSelectedLinesUp')),
        'l': (self.lexe('CharRight'), self.lexe('CharRightExtend'), self.lexe('CharRightRectExtend')),
        ';': lambda _: self.lastLocateFunc(None),

        'z': self.lexe('VerticalCentreCaret'),
        'x': self.lexe('Delete'),
        'X': self.lexe('DeleteBackNotLine'),
        'c': {
            'c': self.lexe(self.beginUndoAction, 'LineCut', 'Home', 'Newline', 'LineUp', self.modeEdit, self.endUndoAction),
            'e': self.lexe('DeleteLineLeft', self.modeEdit),
            'r': self.lexe('DeleteLineRight', self.modeEdit),
            'h': self.lexe('DeleteWordLeft', self.modeEdit),
            'l': self.lexe('DeleteWordRightEnd', self.modeEdit),
            },
        'C': self.lexe('DeleteLineRight', self.modeEdit),
        'v': self.lexe(self.modeSelectStream),
        'M': (self.lexe('PageDown'), self.lexe('PageDownExtend'), self.lexe('PageDownRectExtend')),

        ',': {
            'q': self.lexe(sys.exit),
            't': lambda _: self.open(self.file_chooser.choose()),
          },
        }
    self.setupNCommands()

    self.editModeKeys = {
        'k': {
          'd': self.lexe(self.modeCommand),
          'k': self.lexe(self.completer.nextCandidate),
          },
        ';': {
          ';': self.lexe('Tab'),
          },

        Qt.Key_Escape: self.lexe(self.modeCommand),
        Qt.Key_Return: self.lexe('Newline'),
        Qt.Key_Backspace: self.lexe('DeleteBackNotLine'),
        Qt.Key_Delete: self.lexe('Delete'),
        Qt.Key_Home: self.lexe('DocumentStart'),
        Qt.Key_End: self.lexe('DocumentEnd'),
        Qt.Key_PageUp: self.lexe('PageUp'),
        Qt.Key_PageDown: self.lexe('PageDown'),
        Qt.Key_Left: self.lexe('CharLeft'),
        Qt.Key_Right: self.lexe('CharRight'),
        Qt.Key_Up: self.lexe('LineUp'),
        Qt.Key_Down: self.lexe('LineDown'),
        Qt.Key_Tab: lambda _: self.exe('Tab') if not self.completer.nextCandidate() else None,
        }

    self.modeCommand() # default mode

  # utils

  def open(self, path):
    if not path: return
    f = QFile(os.path.expanduser(path))
    if f.open(QFile.ReadOnly):
      self.read(f)
    else:
      self.error("cannot open %s" % path)
      return
    self.setupLexer(path)

  def setupLexer(self, path):
    if path.endswith('.py'): # lexer
      self.lexer = QsciLexerPython()
      self.lexer.setDefaultFont(self.font)
      self.setLexer(self.lexer)
      self.send("sci_stylesetfont", 1, b'Terminus')

  # commands

  def setupNCommands(self):
    def make(i):
      def f(ev):
        self.n = self.n * 10 + i
        return 'setN'
      return f
    for i in range(0, 10):
      self.commandModeKeys[str(i)] = make(i)
