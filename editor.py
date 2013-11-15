from PyQt4.Qsci import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import time
import os

EDIT, COMMAND = range(2)
NONE, STREAM, RECT = range(3)

class Editor(QsciScintilla):
  def __init__(self):
    super(QsciScintilla, self).__init__()

    self.commands = self.standardCommands()
    self.commands.clearKeys()
    self.mode = COMMAND
    self.base = self.pool()
    self.select_mode = NONE
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

    self.commandModeKeys = {
        'q': (
          self.modeSelectRectangle,
          self.modeSelectNone,
          self.modeSelectNone,
          ),
        'w': (
          self.lexe('Home'),
          self.lexe('HomeExtend'),
          self.lexe('HomeRectExtend'),
          ),
        'e': (
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
        'i': self.modeEdit,
        'o': self.lexe('LineEnd', 'Newline', self.modeEdit),
        'O': self.lexe('Home', 'Newline', 'LineUp', self.modeEdit),
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

        'd': (
          {
            'w': self.lexe('DeleteLineLeft'),
            'e': self.lexe('DeleteLineRight'),
            'd': self.lexe('LineCut'),
            'h': self.lexe('DeleteWordLeft'),
            'l': self.lexe('DeleteWordRightEnd'),
            },
          self.lexe('SelectionCut', self.modeSelectNone),
          self.lexe('SelectionCut', self.modeSelectNone),
          ),
        'f': lambda: print(self.send("sci_searchintarget", len("import"), b'import')),
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
            self.lexe('LineScrollDown'),
            self.lexe('MoveSelectedLinesDown'),
            self.lexe('MoveSelectedLinesDown'),
            ),
        'k': (
            self.lexe('LineUp'),
            self.lexe('LineUpExtend'),
            self.lexe('LineUpRectExtend'),
            ),
        'K': (
            self.lexe('LineScrollUp'),
            self.lexe('MoveSelectedLinesUp'),
            self.lexe('MoveSelectedLinesUp'),
            ),
        'l': (
            self.lexe('CharRight'),
            self.lexe('CharRightExtend'),
            self.lexe('CharRightRectExtend'),
            ),

        'z': self.lexe('VerticalCentreCaret'),
        'x': self.lexe('Delete'),
        'X': self.lexe('DeleteBackNotLine'),
        'v': self.modeSelectStream,
        'V': self.modeSelectLine,
        'M': (
            self.lexe('PageDown'),
            self.lexe('PageDownExtend'),
            self.lexe('PageDownRectExtend'),
            ),

        ',': {
          'q': sys.exit,
          },
        }

    self.editModeKeys = {
        'k': {
          'd': self.modeCommand,
          },

        Qt.Key_Escape: self.modeCommand,
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
        }

    self.delayEvents = []
    self.keyResetTimer = QTimer()
    self.keyResetTimer.timeout.connect(self.keyResetTimeout)

    self.modeCommand()

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
    self.delayEvents = []
    self.currentKeys = keys

  def handleEditKey(self, ev):
    key = ev.text() if ev.key() >= 0x20 and ev.key() <= 0x7e else ev.key()
    handle = self.currentKeys.get(key, None)
    if isinstance(handle, tuple):
      if self.select_mode == NONE:
        handle = handle[0]
      elif self.select_mode == STREAM:
        handle = handle[1]
      elif self.select_mode == RECT:
        handle = handle[2]
    if callable(handle): # trigger a command
      self.keyResetTimer.stop()
      self.resetKeys(self.editModeKeys)
      handle()
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
    key = ev.text() if ev.key() >= 0x20 and ev.key() <= 0x7e else ev.key()
    handle = self.currentKeys.get(key, None)
    if isinstance(handle, tuple):
      if self.select_mode == NONE:
        handle = handle[0]
      elif self.select_mode == STREAM:
        handle = handle[1]
      elif self.select_mode == RECT:
        handle = handle[2]
    if callable(handle): # trigger a command
      self.resetKeys(self.commandModeKeys)
      handle()
    elif isinstance(handle, dict): # is command prefix
      self.currentKeys = handle
      self.delayEvents.append((QKeyEvent(ev), now()))
    else:
      if isinstance(handle, str):
        print('maybe wrong key binding', handle)
      self.resetKeys(self.commandModeKeys)

  # utils

  def exe(self, *cmds):
    for cmd in cmds:
      self.commands.find(getattr(QsciCommand, cmd)).execute()

  def lexe(self, *cmds):
    def f():
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
    if path.endswith('.py'):
      self.lexer = QsciLexerPython()
      self.lexer.setDefaultFont(self.font)
      self.setLexer(self.lexer)
      self.send("sci_stylesetfont", 1, b'Terminus')

  def error(self, msg): #TODO
    print(msg)

  # modes

  def modeEdit(self):
    self.mode = EDIT
    self.currentKeys = self.editModeKeys
    self.send("sci_setcaretstyle", "caretstyle_line")

  def modeCommand(self):
    self.mode = COMMAND
    self.currentKeys = self.commandModeKeys
    self.send("sci_setcaretstyle", "caretstyle_block")

  def modeSelectStream(self):
    self.select_mode = STREAM
    self.send("sci_setselectionmode", "sc_sel_stream")

  def modeSelectNone(self):
    self.select_mode = NONE
    if self.select_mode == RECT:
      self.send("sci_setemptyselection")
    else:
      self.send("sci_setselectionmode", 0)

  def modeSelectRectangle(self):
    self.select_mode = RECT #TODO
    self.send("sci_setselectionmode", "sc_sel_rectangle")

  def modeSelectLine(self):
    self.select_mode = STREAM
    self.send("sci_setselectionmode", "sc_sel_lines")

def now():
  return int(round(time.time() * 1000))
