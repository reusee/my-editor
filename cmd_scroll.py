class CmdScroll:
  def scrollCurrentLineToTop(self):
    current_line_number = self.send('sci_linefromposition', self.getPos())
    top_line_number = self.send('sci_getfirstvisibleline')
    self.send('sci_linescroll', 0, current_line_number - top_line_number)

  def scrollCurrentLineToBottom(self):
    current_line_number = self.send('sci_linefromposition', self.getPos())
    bottom_line_number = self.send('sci_getfirstvisibleline') + self.send('sci_linesonscreen') - 1
    self.send('sci_linescroll', 0, current_line_number - bottom_line_number)
