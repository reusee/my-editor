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
      back = ~send('sci_stylegetback', i) + 0x222222
      if back > 0xFFFFFF: back = 0xFFFFFF
      send('sci_stylesetback', i, back)
      send('sci_stylesetfore', i, ~send('sci_stylegetfore', i))
