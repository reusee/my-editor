class Theme:
  def __init__(self, editor):
    editor.setThemeRequested.connect(self.setup)
    self.editor = editor
    self.setup()

  def setup(self):
    send = self.editor.send
    for i in range(256):
      send('sci_stylesetsize', i, 13)
      send('sci_stylesetfont', i, b'Terminus')
      send('sci_stylesetback', i, 0x222222 + 0xFFFFFF - send('sci_stylegetback', i))
      send('sci_stylesetfore', i, 0xFFFFFF - send('sci_stylegetfore', i))
