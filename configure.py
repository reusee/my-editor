from PyQt5.Qsci import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

def configureEditor(self):
    self.standardCommands().clearKeys() # clear default key bindings
    self.setMarginWidth(1, 0) # hide non-folding symbols
    self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
    self.send('sci_setmousedowncaptures', 0)
    self.setUtf8(True)

    # tab and identation
    self.setTabWidth(2) # tabs
    self.setIndentationWidth(0)
    self.setIndentationsUseTabs(False)
    self.setIndentationGuides(True)
    self.setAutoIndent(True)
    self.setBackspaceUnindents(True)
    #self.send('sci_setviewws', self.base.SCWS_VISIBLEALWAYS)

    # scrollbar
    self.send("sci_sethscrollbar", 0)
    self.send("sci_setvscrollbar", 0)

    # caret
    self.setCaretWidth(3)
    self.setCaretForegroundColor(QColor("yellow"))
    self.send("sci_setcaretperiod", -1)
    self.setCaretLineVisible(True)
    self.setCaretLineBackgroundColor(QColor("#333333"))
    self.send('sci_setcaretlinevisiblealways', 1)
