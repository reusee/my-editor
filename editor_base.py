from PyQt4.Qsci import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ctypes import *
import time

from configure import *

# base editor facilities:
#   modes
#   commands
#   signals
#   configuration
class EditorBase(QsciScintilla):

  EDIT, COMMAND = range(2)
  NONE, STREAM, RECT = range(3)

  editModeEntered = pyqtSignal()
  editModeLeaved = pyqtSignal()

  resized = pyqtSignal(QResizeEvent)
  modified = pyqtSignal(int, int, object, int, int, int, int, int, int, int)
  errored = pyqtSignal(str)

  commandCanceled = pyqtSignal()
  commandPrefix = pyqtSignal(str)
  commandRunned = pyqtSignal()
  commandInvalid = pyqtSignal()

  def __init__(self):
    super(EditorBase, self).__init__()

    self.base = self.pool()
    self.lastLocateFunc = lambda _: None
    self.commands = self.standardCommands() 

    self.mode = self.COMMAND
    self.selectMode = self.NONE
    self.delayEvents = []
    self.keyResetTimer = QTimer()

    configureEditor(self)
    self.font = QFont("Terminus", 13) # font
    self.setFont(self.font)

    self.base.SCN_MODIFIED.connect(lambda *args: self.modified.emit(*args))
    self.keyResetTimer.timeout.connect(self.keyResetTimeout)

  def resizeEvent(self, ev):
    self.resized.emit(ev)
    ev.accept()

  # util functions

  def getPos(self):
    return self.send('sci_getcurrentpos')

  def getPosXY(self, pos):
    return (self.send('sci_pointxfromposition', 0, pos),
        self.send('sci_pointyfromposition', 0, pos))

  def getLineHeight(self):
    return self.send('sci_textheight')

  def exe(self, *cmds):
    for cmd in cmds:
      self.commands.find(getattr(QsciCommand, cmd)).execute()

  def lexe(self, *cmds):
    def f(ev):
      for cmd in cmds:
        if isinstance(cmd, str):
          self.exe(cmd)
        elif isinstance(cmd, tuple):
          cmd[0](*cmd[1:])
        else:
          cmd()
    return f

  def send(self, *args):
    return self.SendScintilla(*[
      getattr(self.base, arg.upper()) if isinstance(arg, str) 
      else arg 
      for arg in args])

  def error(self, msg):
    self.errored.emit(msg)

  def now(self):
    return int(round(time.time() * 1000))

  # keypress handler

  def keyPressEvent(self, ev):
    if self.mode == self.EDIT:
      self.handleEditKey(ev)
    elif self.mode == self.COMMAND:
      self.handleCommandKey(ev)

  def keyResetTimeout(self):
    for e in self.delayEvents:
      super(Editor, self).keyPressEvent(e[0])
    self.resetKeys(self.editModeKeys)

  def resetKeys(self, keys):
    self.delayEvents.clear()
    self.currentKeys = keys

  def handleEditKey(self, ev):
    key = ev.text() if ev.key() >= 0x20 and ev.key() <= 0x7e else ev.key()
    handle = self.currentKeys.get(key, None)
    if isinstance(handle, tuple):
      if self.selectMode == self.NONE:
        handle = handle[0]
      elif self.selectMode == self.STREAM:
        handle = handle[1]
      elif self.selectMmode == self.RECT:
        handle = handle[2]
    if callable(handle): # trigger a command
      self.keyResetTimer.stop()
      self.resetKeys(self.editModeKeys)
      handle(ev)
    elif isinstance(handle, dict): # is command prefix
      self.currentKeys = handle
      self.delayEvents.append((QKeyEvent(ev), self.now()))
      self.keyResetTimer.start(200)
    else:
      self.keyResetTimer.stop()
      for e in self.delayEvents: # pop all delay events
        super(QsciScintilla, self).keyPressEvent(e[0])
      self.resetKeys(self.editModeKeys)
      super(QsciScintilla, self).keyPressEvent(ev)

  def handleCommandKey(self, ev):
    if ev.key() == Qt.Key_Shift: # ignore shift key
      return super(QsciScintilla, self).keyPressEvent(ev)
    elif ev.key() == Qt.Key_Escape: # cancel command
      self.resetKeys(self.commandModeKeys)
      self.commandCanceled.emit()
      return
    handle = None
    if isinstance(self.currentKeys, dict): # dict handler
      key = ev.text() if ev.key() >= 0x20 and ev.key() <= 0x7e else ev.key()
      handle = self.currentKeys.get(key, None)
      if isinstance(handle, tuple): # tuple command
        if self.selectMode == self.NONE:
          handle = handle[0]
        elif self.selectMode == self.STREAM:
          handle = handle[1]
        elif self.selectMode == self.RECT:
          handle = handle[2]
    elif callable(self.currentKeys): # function handler
      handle = self.currentKeys
    if callable(handle): # trigger a command or call handler function
      self.resetKeys(self.commandModeKeys)
      ret = handle(ev)
      if callable(ret): # another function handler
        self.currentKeys = ret
        self.commandPrefix.emit(ev.text())
      else: # final command
        if ret != 'setN': # not prefix setting command
          for n in range(0, self.n - 1): # do command n times
            handle(ev)
          self.n = 0
          self.commandRunned.emit()
        else: # is number prefix
          self.commandPrefix.emit(ev.text())
    elif isinstance(handle, dict): # another dict handler
      self.currentKeys = handle
      self.delayEvents.append((QKeyEvent(ev), self.now()))
      self.commandPrefix.emit(ev.text())
    else: # no handler
      self.resetKeys(self.commandModeKeys)
      self.commandInvalid.emit()

  # modes

  def modeEdit(self):
    self.mode = self.EDIT
    self.currentKeys = self.editModeKeys
    self.send("sci_setcaretstyle", "caretstyle_line")
    self.editModeEntered.emit()

  def modeCommand(self):
    self.mode = self.COMMAND
    self.currentKeys = self.commandModeKeys
    self.send("sci_setcaretstyle", "caretstyle_block")
    self.editModeLeaved.emit()

  def modeSelectStream(self):
    self.selectMode = self.STREAM
    self.send("sci_setcaretstyle", "caretstyle_line")
    self.send("sci_setselectionmode", "sc_sel_stream")

  def modeSelectNone(self):
    self.selectMode = self.NONE
    self.send("sci_setcaretstyle", "caretstyle_block")
    self.send('sci_cancel')

  def modeSelectRectangle(self):
    self.selectMode = self.RECT
    self.send("sci_setcaretstyle", "caretstyle_line")
    self.send("sci_setselectionmode", "sc_sel_rectangle")

  # locate commands

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
            self.lastLocateFunc = f
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
            self.lastLocateFunc = f
        return f
    for i in range(0x20, 0x7F):
      handler[chr(i)] = makeLocator(chr(i))
    return handler

  def locateByTwoChars(self, ev):
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
          self.lastLocateFunc = f
      f(None)
    return next

  def locateBackwardByTwoChars(self, ev):
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
          self.lastLocateFunc = f
      f(None)
    return next
