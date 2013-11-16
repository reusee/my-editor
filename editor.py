from PyQt4.Qsci import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
import time
import os
from ctypes import *

from status import *
from completer import *

EDIT, COMMAND = range(2)
NONE, STREAM, RECT = range(3)

class Editor(QsciScintilla):

  enterEditMode = pyqtSignal()
  leaveEditMode = pyqtSignal()
  notify = pyqtSignal(int, int, object, int, int, int, int, int, int, int)
  resizeSignal = pyqtSignal(QResizeEvent)
  cancelCommand = pyqtSignal()
  commandPrefix = pyqtSignal(str)
  commandRunned = pyqtSignal()
  commandInvalid = pyqtSignal()

  def __init__(self):
    super(QsciScintilla, self).__init__()

    self.commands = self.standardCommands()
    self.commands.clearKeys()
    self.mode = COMMAND
    self.base = self.pool()
    self.selectMode = NONE
    self.lexer = None

    self.setUtf8(True)
    self.font = QFont("Terminus", 13)
    self.setFont(self.font)
    self.setCaretWidth(3)
    self.setCaretForegroundColor(QColor("green"))
    self.send("sci_setcaretperiod", -1)
    self.setMarginWidth(0, 30)
    self.setMarginLineNumbers(0, True)
    self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
    self.setCaretLineVisible(True)
    self.setCaretLineBackgroundColor(QColor("#FFE4E4"))
    self.send("sci_sethscrollbar", 0)
    self.send('sci_setmousedowncaptures', 0)

    # indent and tabs
    self.setTabWidth(2)
    self.setIndentationWidth(0)
    self.setIndentationsUseTabs(False)
    self.setIndentationGuides(True)
    self.setAutoIndent(True)
    self.setBackspaceUnindents(True)

    # child widgets
    self.status = Status(self)
    self.completer = Completer(self)

    self.locateFunc = lambda _: None
    self.n = 0

    self.commandModeKeys = {
        'q': (
          lambda _: self.modeSelectRectangle(),
          lambda _: self.modeSelectNone(),
          lambda _: self.modeSelectNone(),
          ),
        'e': (
          self.lexe('Home'),
          self.lexe('HomeExtend'),
          self.lexe('HomeRectExtend'),
          ),
        'r': (
          self.lexe('LineEnd'), 
          self.lexe('LineEndExtend'), 
          self.lexe('LineEndRectExtend'),
          ),
        'y': (
          {
            'y': self.lexe('LineCopy'),
            'p': self.lexe('LineDuplicate'),
            'x': self.lexe('LineTranspose'),
            },
          self.lexe('SelectionCopy', self.modeSelectNone),
          self.lexe('SelectionCopy', self.modeSelectNone),
          ),
        'u': self.lexe('Undo'),
        'U': (
          self.lexe('PageUp'),
          self.lexe('PageUpExtend'),
          self.lexe('PageUpRectExtend'),
          ),
        'i': lambda _: self.modeEdit(),
        'o': self.lexe(self.beginUndoAction, 'LineEnd', 'Newline', self.modeEdit, self.endUndoAction),
        'O': self.lexe(self.beginUndoAction, 'Home', 'Newline', 'LineUp', self.modeEdit, self.endUndoAction),
        'p': self.lexe('Paste'),
        '[': (
          self.lexe('ParaUp'),
          self.lexe('ParaUpExtend'),
          self.lexe('ParaUpExtend'),
          ),
        ']': (
          self.lexe('ParaDown'),
          self.lexe('ParaDownExtend'),
          self.lexe('ParaDownExtend'),
          ),

        's': lambda _: self.cmdLocateTuple,
        'S': lambda _: self.cmdLocateTupleBackward,
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
          'g': (
            self.lexe('DocumentStart'),
            self.lexe('DocumentStartExtend'),
            self.lexe('DocumentStartExtend'),
            ),
          'a': self.lexe('SelectAll'),
          },
        'G': (
            self.lexe('DocumentEnd'),
            self.lexe('DocumentEndExtend'),
            self.lexe('DocumentEndExtend'),
            ),
        'h': (
            self.lexe('CharLeft'),
            self.lexe('CharLeftExtend'),
            self.lexe('CharLeftRectExtend'),
            ),
        'j': (
            self.lexe('LineDown'),
            self.lexe('LineDownExtend'),
            self.lexe('LineDownRectExtend'),
            ),
        'J': (
            self.lexe('LineScrollUp'),
            self.lexe('MoveSelectedLinesDown'),
            self.lexe('MoveSelectedLinesDown'),
            ),
        'k': (
            self.lexe('LineUp'),
            self.lexe('LineUpExtend'),
            self.lexe('LineUpRectExtend'),
            ),
        'K': (
            self.lexe('LineScrollDown'),
            self.lexe('MoveSelectedLinesUp'),
            self.lexe('MoveSelectedLinesUp'),
            ),
        'l': (
            self.lexe('CharRight'),
            self.lexe('CharRightExtend'),
            self.lexe('CharRightRectExtend'),
            ),
        ';': lambda _: self.locateFunc(None),

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
        'v': lambda _: self.modeSelectStream(),
        'V': lambda _: self.modeSelectLine(),
        'M': (
            self.lexe('PageDown'),
            self.lexe('PageDownExtend'),
            self.lexe('PageDownRectExtend'),
            ),

        ',': {
            'q': lambda _: sys.exit(),
          },
        }

    self.editModeKeys = {
        'k': {
          'd': lambda _: self.modeCommand(),
          },

        Qt.Key_Escape: lambda _: self.modeCommand(),
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
        Qt.Key_Tab: self.lexe('Tab'),
        }

    self.delayEvents = []
    self.keyResetTimer = QTimer()
    self.keyResetTimer.timeout.connect(self.keyResetTimeout)

    self.modeCommand()

    self.setupNCommands()

    self.base.SCN_MODIFIED.connect(lambda *args: self.notify.emit(*args))

  def resizeEvent(self, ev):
    self.resizeSignal.emit(ev)
    ev.accept()

  # keypress handler

  def keyPressEvent(self, ev):
    if self.mode == EDIT:
      self.handleEditKey(ev)
    elif self.mode == COMMAND:
      self.handleCommandKey(ev)

  def keyResetTimeout(self):
    for e in self.delayEvents:
      super(QsciScintilla, self).keyPressEvent(e[0])
    self.resetKeys(self.editModeKeys)

  def resetKeys(self, keys):
    self.delayEvents.clear()
    self.currentKeys = keys

  def handleEditKey(self, ev):
    key = ev.text() if ev.key() >= 0x20 and ev.key() <= 0x7e else ev.key()
    handle = self.currentKeys.get(key, None)
    if isinstance(handle, tuple):
      if self.selectMode == NONE:
        handle = handle[0]
      elif self.selectMode == STREAM:
        handle = handle[1]
      elif self.selectMmode == RECT:
        handle = handle[2]
    if callable(handle): # trigger a command
      self.keyResetTimer.stop()
      self.resetKeys(self.editModeKeys)
      handle(ev)
    elif isinstance(handle, dict): # is command prefix
      self.currentKeys = handle
      self.delayEvents.append((QKeyEvent(ev), now()))
      self.keyResetTimer.start(200)
    else:
      self.keyResetTimer.stop()
      for e in self.delayEvents: # pop all delay events
        super(QsciScintilla, self).keyPressEvent(e[0])
      self.resetKeys(self.editModeKeys)
      super(QsciScintilla, self).keyPressEvent(ev)

  def handleCommandKey(self, ev):
    if ev.key() == Qt.Key_Shift:
      return super(QsciScintilla, self).keyPressEvent(ev)
    elif ev.key() == Qt.Key_Escape:
      self.resetKeys(self.commandModeKeys)
      self.cancelCommand.emit()
      return
    handle = None
    if isinstance(self.currentKeys, dict):
      key = ev.text() if ev.key() >= 0x20 and ev.key() <= 0x7e else ev.key()
      handle = self.currentKeys.get(key, None)
      if isinstance(handle, tuple):
        if self.selectMode == NONE:
          handle = handle[0]
        elif self.selectMode == STREAM:
          handle = handle[1]
        elif self.selectMode == RECT:
          handle = handle[2]
    elif callable(self.currentKeys):
      handle = self.currentKeys
    if callable(handle): # trigger a command
      self.resetKeys(self.commandModeKeys)
      ret = handle(ev)
      if callable(ret): # more handle
        self.currentKeys = ret
        self.commandPrefix.emit(ev.text())
      else: # final command
        if ret != 'setN': # not prefix setting command
          for n in range(0, self.n - 1): # do command n times
            handle(ev)
          self.n = 0
          self.commandRunned.emit()
        else: # show number prefix
          self.commandPrefix.emit(ev.text())
    elif isinstance(handle, dict): # is command prefix
      self.currentKeys = handle
      self.delayEvents.append((QKeyEvent(ev), now()))
      self.commandPrefix.emit(ev.text())
    else:
      if isinstance(handle, str):
        print('maybe wrong key binding', handle)
      self.resetKeys(self.commandModeKeys)
      self.commandInvalid.emit()

  # utils

  def exe(self, *cmds):
    for cmd in cmds:
      self.commands.find(getattr(QsciCommand, cmd)).execute()

  def lexe(self, *cmds):
    def f(ev):
      for cmd in cmds:
        if isinstance(cmd, str):
          self.exe(cmd)
        else:
          cmd()
    return f

  def send(self, *args):
    return self.SendScintilla(*[
      getattr(self.base, arg.upper()) if isinstance(arg, str) 
      else arg 
      for arg in args])

  def load(self, path):
    f = QFile(os.path.expanduser(path))
    if f.open(QFile.ReadOnly):
      self.read(f)
    else:
      self.error("cannot open %s" % path)
      return

    if path.endswith('.py'): # lexer
      self.lexer = QsciLexerPython()
      self.lexer.setDefaultFont(self.font)
      self.setLexer(self.lexer)
      self.send("sci_stylesetfont", 1, b'Terminus')

  def error(self, msg): #TODO
    print(msg)

  def getPos(self):
    return self.send('sci_getcurrentpos')

  def caretXY(self):
    currentPosition = self.getPos()
    return (self.send('sci_pointxfromposition', 0, currentPosition),
        self.send('sci_pointyfromposition', 0, currentPosition))

  def lineHeight(self):
    return self.send('sci_textheight')

  # modes

  def modeEdit(self):
    self.mode = EDIT
    self.currentKeys = self.editModeKeys
    self.send("sci_setcaretstyle", "caretstyle_line")
    self.enterEditMode.emit()

  def modeCommand(self):
    self.mode = COMMAND
    self.currentKeys = self.commandModeKeys
    self.send("sci_setcaretstyle", "caretstyle_block")
    self.leaveEditMode.emit()

  def modeSelectStream(self):
    self.selectMode = STREAM
    self.send("sci_setcaretstyle", "caretstyle_line")
    self.send("sci_setselectionmode", "sc_sel_stream")

  def modeSelectNone(self):
    self.selectMode = NONE
    self.send("sci_setcaretstyle", "caretstyle_block")
    self.send('sci_cancel')

  def modeSelectRectangle(self):
    self.selectMode = RECT
    self.send("sci_setcaretstyle", "caretstyle_line")
    self.send("sci_setselectionmode", "sc_sel_rectangle")

  def modeSelectLine(self):
    self.selectMode = STREAM
    self.send("sci_setcaretstyle", "caretstyle_line")
    self.send("sci_setselectionmode", "sc_sel_lines")

  # factories

  def makeCharLocators(self, backward = False):
    handler = {}
    def makeLocator(c):
      c = create_string_buffer(bytes(c, "utf8"))
      if backward:
        def f(_):
          oldpos = self.getPos()
          self.send('sci_searchanchor')
          ret = self.send('sci_searchprev', self.base.SCFIND_MATCHCASE, c)
          if ret == -1: # not found
            self.send('sci_setcurrentpos', oldpos)
          else:
            self.exe('CharLeft')
            self.send('sci_scrollcaret')
            self.locateFunc = f
        return f
      else:
        def f(_):
          oldpos = self.getPos()
          self.exe('CharRight')
          self.send('sci_searchanchor')
          ret = self.send('sci_searchnext', self.base.SCFIND_MATCHCASE, c)
          if ret == -1:
            self.send('sci_setcurrentpos', oldpos)
          else:
            self.exe('CharLeft')
            self.send('sci_scrollcaret')
            self.locateFunc = f
        return f
    for i in range(0x20, 0x7F):
      handler[chr(i)] = makeLocator(chr(i))
    return handler

  def setupNCommands(self):
    def make(i):
      def f(ev):
        self.n = self.n * 10 + i
        return 'setN'
      return f
    for i in range(0, 10):
      self.commandModeKeys[str(i)] = make(i)

  # commands

  def cmdLocateTuple(self, ev):
    c = ev.text()
    def next(ev):
      buf = create_string_buffer(bytes(c + ev.text(), "utf8"))
      def f(_):
        oldpos = self.getPos()
        self.exe('CharRight')
        self.send('sci_searchanchor')
        ret = self.send('sci_searchnext', 0, buf)
        if ret == -1:
          self.send('sci_setcurrentpos', oldpos)
        else:
          self.exe('CharLeft')
          self.send('sci_scrollcaret')
          self.locateFunc = f
      f(None)
    return next

  def cmdLocateTupleBackward(self, ev):
    c = ev.text()
    def next(ev):
      buf = create_string_buffer(bytes(c + ev.text(), "utf8"))
      def f(_):
        oldpos = self.getPos()
        self.exe('CharLeft')
        self.send('sci_searchanchor')
        ret = self.send('sci_searchprev', 0, buf)
        if ret == -1:
          self.send('sci_setcurrentpos', oldpos)
        else:
          self.exe('CharLeft')
          self.send('sci_scrollcaret')
          self.locateFunc = f
      f(None)
    return next

  def isWordChar(c):
    return c.isalpha() or c.isdigit() or c == '-'

def now():
  return int(round(time.time() * 1000))
