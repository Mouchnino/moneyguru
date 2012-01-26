# Created By: Virgil Dupras
# Created On: 2009-11-22
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLineEdit

# The QCompleter works by having access to a list of possible matches, but we already have that
# logic implemented on the model side. It turns out subclassing the QCompleter to adapt it to our
# case would have been more complex than subclassing a QLineEdit.

# Moreover, QCompleter's behavior on up/down arrow is inadequate in InlineCompletion mode (doesn't
# cycle through possible completions)

class CompletableEdit(QLineEdit):
    ATTRNAME = '' # must be set
    
    def __init__(self, model, parent):
        QLineEdit.__init__(self, parent)
        self.model = model
        self.model.view = self
    
    def _prefix(self):
        # Returns the text before the selection
        if self.selectionStart() == -1:
            return str(self.text())
        else:
            return str(self.text())[:self.selectionStart()]
    
    #--- QLineEdit overrides
    def focusInEvent(self, event):
        QLineEdit.focusInEvent(self, event)
        self.model.view = self
        self.model.attrname = self.ATTRNAME
        self.model.text = ''
    
    def focusOutEvent(self, event):
        self.prepareDataForCommit()
        QLineEdit.focusOutEvent(self, event)
    
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Up:
            self.model.up()
        elif key == Qt.Key_Down:
            self.model.down()
        else:
            oldPrefix = self._prefix()
            QLineEdit.keyPressEvent(self, event)
            prefix = self._prefix()
            if len(oldPrefix) < len(prefix):
                self.model.text = prefix
    
    #--- Public
    def prepareDataForCommit(self):
        # On focus out, we want to see if the text we have is exactly the same as the completion,
        # case-insensitive-wise. If yes, we use the case of the completion rather than our own.
        if self.selectedText() and self.selectedText() == self.model.completion:
            self.model.commit()
    
    #--- model --> view
    def refresh(self):
        self.setText(self.model.text + self.model.completion)
        self.setSelection(len(self.model.text), len(self.model.completion))
    

class DescriptionEdit(CompletableEdit):
    ATTRNAME = 'description'

class PayeeEdit(CompletableEdit):
    ATTRNAME = 'payee'

class AccountEdit(CompletableEdit):
    ATTRNAME = 'account'
