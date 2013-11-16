from PyQt4.Qsci import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def configureEditor(self):
    self.standardCommands().clearKeys() # clear default key bindings
    self.setUtf8(True) # use utf8
    self.setCaretWidth(3)
    self.setCaretForegroundColor(QColor("green"))
    self.send("sci_setcaretperiod", -1)
    self.setMarginWidth(0, 30)
    self.setMarginLineNumbers(0, True)
    self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
    self.setCaretLineVisible(True)
    self.setCaretLineBackgroundColor(QColor("#FFE4E4"))
    self.send("sci_sethscrollbar", 0)
    self.send('sci_setmousedowncaptures', 0)
    self.setTabWidth(2) # tabs
    self.setIndentationWidth(0)
    self.setIndentationsUseTabs(False)
    self.setIndentationGuides(True)
    self.setAutoIndent(True)
    self.setBackspaceUnindents(True)
