class RelativeLineNumber:
  def __init__(self, editor, margin):
    self.editor = editor
    self.editor.beated.connect(self.update)
    self.editor.setMarginType(margin, self.editor.TextMargin)
    self.margin = margin
    self.update()

  def update(self):
    if not self.editor.active:
        self.editor.setMarginWidth(self.margin, 0)
        return
    current_line_number = self.editor.send('sci_linefromposition', self.editor.getPos())
    maxLength = 0
    for i in range(self.editor.send('sci_linesonscreen') + 1):
      line_number = i + self.editor.send('sci_getfirstvisibleline')
      view = line_number - current_line_number
      if view == 0:
        view = current_line_number
        view = '{0: <4}'.format(view)
      else:
        view = '{0: 4}'.format(view)
      self.editor.setMarginText(line_number, view, self.editor.base.STYLE_DEFAULT)
      if len(view) > maxLength:
        maxLength = len(view)
    width = 12 * maxLength
    if width < 30: width = 30
    self.editor.setMarginWidth(self.margin, width)
