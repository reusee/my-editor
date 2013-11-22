import sys

from editor_base import *

# commands
from cmd_locate import *
from cmd_newline import *
from cmd_scroll import *

# modules
from mod_status import *
from mod_completer import *
from mod_file_chooser import *
from mod_relative_line_number import *
from mod_documents import *
from mod_layout import *
from mod_error import *
from mod_theme import *

#   extra modules
#   key bindings
class Editor(EditorBase,
    # commands
    CmdLocate,
    CmdNewline,
    CmdScroll,
    ):

  openRequested = pyqtSignal(str)
  cloned = pyqtSignal(QObject)
  setThemeRequested = pyqtSignal()

  def __init__(self):
    super().__init__()

    self.n = 0
    self.active = False

    self.setStyleSheet('''
    Editor {
      border: 0;
    }
    ''')

    # modules
    self.completer = Completer(self)
    self.status = Status(self)
    self.file_chooser = FileChooser(self)
    self.relative_line_number = RelativeLineNumber(self, 3)
    self.documents = Documents(self)
    self.layout = Layout(self)
    self.errorHandler = ErrorHandler(self)
    self.theme = Theme(self)

    # key bindings
    self.commandModeKeys = {
        'q': (self.do(self.modeSelectRectangle), self.do(self.modeSelectNone), self.do(self.modeSelectNone)),
        'e': (self.do('Home'), self.do('HomeExtend'), self.do('HomeRectExtend')),
        'r': (self.do('LineEnd'), self.do('LineEndExtend'), self.do('LineEndRectExtend')),
        'y': (
          {'y': self.do('LineCopy'), 'p': self.do('LineDuplicate'), 'x': self.do('LineTranspose')},
          self.do('SelectionCopy', self.modeSelectNone),
          self.do('SelectionCopy', self.modeSelectNone),
          ),
        'u': self.do('Undo'),
        'U': (self.do('PageUp'), self.do('PageUpExtend'), self.do('PageUpRectExtend')),
        'i': self.do(self.modeEdit),
        'I': self.do('Home', self.modeEdit),
        'o': self.do(self.newlineBelow),
        'O': self.do(self.newlineAbove),
        'p': self.do('Paste'),
        '[': (self.do('ParaUp'), self.do('ParaUpExtend'), self.do('ParaUpExtend')),
        ']': (self.do('ParaDown'), self.do('ParaDownExtend'), self.do('ParaDownExtend')),

        'a': self.do('CharRight', self.modeEdit),
        'A': self.do('LineEnd', self.modeEdit),
        's': lambda _: self.locateByTwoChars,
        'S': lambda _: self.locateBackwardByTwoChars,
        'd': (
          {
            'e': self.do('DeleteLineLeft'),
            'r': self.do('DeleteLineRight'),
            'd': self.do('LineCut'),
            'h': self.do('DeleteWordLeft'),
            'l': self.do('DeleteWordRightEnd'),
            },
          self.do('SelectionCut', self.modeSelectNone),
          self.do('SelectionCut', self.modeSelectNone),
          ),
        'f': self.makeCharLocators(),
        'F': self.makeCharLocators(backward = True),
        'g': {
          'g': (self.do('DocumentStart'), self.do('DocumentStartExtend'), self.do('DocumentStartExtend')),
          'a': self.do('SelectAll'),
          },
        'G': (self.do('DocumentEnd'), self.do('DocumentEndExtend'), self.do('DocumentEndExtend')),
        'h': (self.do('CharLeft'), self.do('CharLeftExtend'), self.do('CharLeftRectExtend')),
        'H': self.do(self.documents.nextDocument),
        'j': (self.do('LineDown'), self.do('LineDownExtend'), self.do('LineDownRectExtend')),
        'J': (self.do('LineScrollUp'), self.do('MoveSelectedLinesDown'), self.do('MoveSelectedLinesDown')),
        'k': (self.do('LineUp'), self.do('LineUpExtend'), self.do('LineUpRectExtend')),
        'K': (self.do('LineScrollDown'), self.do('MoveSelectedLinesUp'), self.do('MoveSelectedLinesUp')),
        'l': (self.do('CharRight'), self.do('CharRightExtend'), self.do('CharRightRectExtend')),
        'L': self.do(self.documents.prevDocument),
        ';': lambda _: self.lastLocateFunc(None),

        'z': {
            'z': self.do('VerticalCentreCaret'),
            't': self.do(self.scrollCurrentLineToTop),
            'b': self.do(self.scrollCurrentLineToBottom),
            },
        'x': self.do('Delete'),
        'X': self.do('DeleteBackNotLine'),
        'c': {
            'c': self.do(self.beginUndoAction, 'LineCut', 'Home', 'Newline', 'LineUp', self.modeEdit, self.endUndoAction),
            'e': self.do('DeleteLineLeft', self.modeEdit),
            'r': self.do('DeleteLineRight', self.modeEdit),
            'h': self.do('DeleteWordLeft', self.modeEdit),
            'l': self.do('DeleteWordRightEnd', self.modeEdit),
            },
        'C': self.do('DeleteLineRight', self.modeEdit),
        'v': self.do(self.modeSelectStream),
        'M': (self.do('PageDown'), self.do('PageDownExtend'), self.do('PageDownRectExtend')),

        ',': {
            'q': self.do(sys.exit),
            't': lambda _: self.openRequested.emit(self.file_chooser.choose()),

            's': self.do(self.layout.siblingSplit),
            'h': self.do((self.layout.split, QHBoxLayout)),
            'j': self.do(self.layout.next),
            'k': self.do(self.layout.prev),

            'v': self.do((self.layout.split, QVBoxLayout)),
          },
        }
    self.setupNCommands()

    self.editModeKeys = {
        'k': {
          'd': self.do(self.modeCommand),
          'k': self.do(self.completer.nextCandidate),
          },
        ';': {
          ';': self.do('Tab'),
          },

        Qt.Key_Escape: self.do(self.modeCommand),
        Qt.Key_Return: self.do('Newline'),
        Qt.Key_Backspace: self.do('DeleteBackNotLine'),
        Qt.Key_Delete: self.do('Delete'),
        Qt.Key_Home: self.do('DocumentStart'),
        Qt.Key_End: self.do('DocumentEnd'),
        Qt.Key_PageUp: self.do('PageUp'),
        Qt.Key_PageDown: self.do('PageDown'),
        Qt.Key_Left: self.do('CharLeft'),
        Qt.Key_Right: self.do('CharRight'),
        Qt.Key_Up: self.do('LineUp'),
        Qt.Key_Down: self.do('LineDown'),
        Qt.Key_Tab: lambda _: self.exe('Tab') if not self.completer.nextCandidate() else None,
        }

    self.modeCommand() # default mode

  def do(self, *cmds):
    return lambda _: self.exe(*cmds)

  def setupNCommands(self):
    def make(i):
      def f(ev):
        self.n = self.n * 10 + i
        return 'setN'
      return f
    for i in range(0, 10):
      self.commandModeKeys[str(i)] = make(i)

  def clone(self):
    edit = Editor()
    self.cloned.emit(edit)
    return edit
