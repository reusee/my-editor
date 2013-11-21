from ctypes import *

class CmdLocate:
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

