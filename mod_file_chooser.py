from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os

class FileChooser(QDialog):
  def __init__(self, parent):
    super().__init__(parent)

    self.path = ''
    self.head = ''

    self.layout = QVBoxLayout()
    self.setLayout(self.layout)
    self.layout.setAlignment(Qt.AlignTop)

    self.edit = QLineEdit(self)
    self.layout.addWidget(self.edit)
    self.edit.returnPressed.connect(self.editPressed)
    self.edit.textChanged.connect(self.updateList)

    self.model = QStringListModel()
    self.view = QListView()
    self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
    self.view.setModel(self.model)
    self.layout.addWidget(self.view)
    self.view.installEventFilter(self)

  def exec_(self):
    self.edit.clear()
    self.edit.setFocus()
    self.updateList('')
    super().exec_()

  def editPressed(self):
    if self.model.rowCount() == 0: return
    self.path = self.model.data(self.view.currentIndex(), Qt.DisplayRole)
    path = os.path.join(self.head, self.path)
    if os.path.isfile(path):
      self.accept()
    else: # open directory
      path += os.path.sep
      self.edit.setText(path)
      self.updateList(path)

  def reject(self):
    self.path = None
    super().reject()

  def choose(self):
    self.exec_()
    if not self.head: self.head = ''
    if not self.path: self.path = ''
    return os.path.join(self.head, self.path)

  def updateList(self, text):
    head, tail = os.path.split(os.path.expanduser(text))
    if head == '':
      head = os.path.abspath('.')
    self.head = head
    try:
      self.model.setStringList(sorted([f
          for f in os.listdir(head)
          if self.fuzzyMatch(tail, f)]))
      self.view.setStyleSheet('QLineEdit { color: black; }')
    except FileNotFoundError:
      self.model.setStringList([])
      self.view.setStyleSheet('QLineEdit { color: red; }')
    self.view.setCurrentIndex(self.model.index(0, 0))

  def fuzzyMatch(self, key, s):
    keyI = 0
    sI = 0
    while keyI < len(key) and sI < len(s):
      if s[sI].lower() == key[keyI].lower():
        sI += 1
        keyI += 1
      else:
        sI += 1
    return keyI == len(key)

  def eventFilter(self, watched, event):
    if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
      path = self.model.data(self.view.currentIndex(), Qt.DisplayRole)
      path = os.path.join(self.head, path)
      if os.path.isfile(path):
        self.path = path
        self.accept()
      else:
        path += os.path.sep
        self.edit.setText(path)
        self.updateList(path)
      return True
    return False
