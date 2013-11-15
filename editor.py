from PyQt4.Qsci import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import time

EDIT, COMMAND = range(2)

class Editor(QsciScintilla):
  def __init__(self):
    super(QsciScintilla, self).__init__()
    self.setUtf8(True)
    self.commands = self.standardCommands()
    self.mode = COMMAND

    self.commandModeKeys = {
        'i': self.cmdInsert,
        'j': {
          'j': lambda: print("foo"),
          }
        }

    self.editModeKeys = {
        'k': {
          'd': self.cmdCommandMode,
          },
        }

    self.delayEvents = []
    self.keyResetTimer = QTimer()
    self.keyResetTimer.timeout.connect(self.keyResetTimeout)

    self.cmdCommandMode()

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
    handle = self.currentKeys.get(ev.text(), None)
    if callable(handle): # trigger a command
      self.keyResetTimer.stop()
      self.resetKeys(self.editModeKeys)
      handle()
    elif isinstance(handle, dict): # is command prefix
      self.currentKeys = handle
      self.delayEvents.append((QKeyEvent(ev), now()))
      self.keyResetTimer.start(200)
    else: # not a command, skip it
      self.keyResetTimer.stop()
      for e in self.delayEvents: # pop all delay events
        super(QsciScintilla, self).keyPressEvent(e[0])
      self.resetKeys(self.editModeKeys)
      super(QsciScintilla, self).keyPressEvent(ev)

  def handleCommandKey(self, ev):
    handle = self.currentKeys.get(ev.text(), None)
    if callable(handle): # trigger a command
      self.resetKeys(self.commandModeKeys)
      handle()
    elif isinstance(handle, dict): # is command prefix
      self.currentKeys = handle
      self.delayEvents.append((QKeyEvent(ev), now()))

  # utils

  def execute(self, *cmds):
    for cmd in cmds:
      self.commands.find(cmd).execute()

  # commands

  def cmdInsert(self):
    self.cmdEditMode()

  def cmdEditMode(self):
    self.mode = EDIT
    self.currentKeys = self.editModeKeys

  def cmdCommandMode(self):
    self.mode = COMMAND
    self.currentKeys = self.commandModeKeys

def now():
  return int(round(time.time() * 1000))
