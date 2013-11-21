class CmdNewline:
  def newlineBelow(self):
    self.exe(
        self.beginUndoAction,
        'LineEnd',
        'Newline',
        self.modeEdit,
        self.endUndoAction,
        )

  def newlineAbove(self):
    self.exe(
        self.beginUndoAction,
        'LineEnd',
        'Newline',
        'LineTranspose',
        'LineUp',
        self.modeEdit,
        self.endUndoAction,
        )