class RelativeLineNumber:
  def __init__(self, editor, margin):
    editor.base.SCN_UPDATEUI.connect(self.update)
    self.editor = editor
    self.editor.setMarginType(margin, self.editor.TextMargin)
    self.margin = margin

  def update(self):
    current_line_number = self.editor.send('sci_linefromposition', self.editor.getPos())
    maxLength = 0
    for i in range(self.editor.send('sci_linesonscreen')):
      line_number = i + self.editor.send('sci_getfirstvisibleline')
      view = line_number - current_line_number
      if view == 0:
        view = current_line_number
      view = str(view)
      self.editor.setMarginText(line_number, view, self.editor.base.STYLE_LINENUMBER)
      if len(view) > maxLength:
        maxLength = len(view)
    width = 12 * maxLength
    if width < 30: width = 30
    self.editor.setMarginWidth(self.margin, width)
