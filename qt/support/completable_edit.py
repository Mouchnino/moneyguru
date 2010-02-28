# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-22
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLineEdit

from core.gui.completable_edit import CompletableEdit as CompletableEditModel

# The QCompleter works by having access to a list of possible matches, but we already have that
# logic implemented on the model side. It turns out subclassing the QCompleter to adapt it to our
# case would have been more complex than subclassing a QLineEdit.

# Moreover, QCompleter's behavior on up/down arrow is inadequate in InlineCompletion mode (doesn't
# cycle through possible completions)

# For a CompletableEdit to work, its model/attrname attributes *have* to be set. model has to be
# something that has complete(value, attrname), current_completion(), next_completion() and 
# prev_completion().

class CompletableEdit(QLineEdit):
    ATTRNAME = '' # must be set
    
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.model = CompletableEditModel()
        self.model.attrname = self.ATTRNAME
    
    def _refresh(self):
        self.setText(self.model.text + self.model.completion)
        self.setSelection(len(self.model.text), len(self.model.completion))
    
    def _prefix(self):
        # Returns the text before the selection
        if self.selectionStart() == -1:
            return unicode(self.text())
        else:
            return unicode(self.text()[:self.selectionStart()])
    
    #--- QLineEdit overrides
    def focusInEvent(self, event):
        QLineEdit.focusInEvent(self, event)
        self.model.text = ''
    
    def focusOutEvent(self, event):
        # On focus out, we want to see if the text we have is exactly the same as the completion,
        # case-insensitive-wise. If yes, we use the case of the completion rather than our own.
        # THIS DOESN'T WORK IN ITEM VIEW EDITION. When item views use this class as an editor,
        # the value of the editor is pushed down to the model *before* the focus out event. The
        # logic for completion replacement in these cases is in controller.table._setData.
        if self.selectedText() and self.selectedText() == self.model.completion:
            self.model.commit()
            self._refresh()
        QLineEdit.focusOutEvent(self, event)
    
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Up:
            if self.model.text:
                self.model.up()
                self._refresh()
        elif key == Qt.Key_Down:
            if self.model.text:
                self.model.down()
                self._refresh()
        else:
            oldPrefix = self._prefix()
            QLineEdit.keyPressEvent(self, event)
            prefix = self._prefix()
            if len(oldPrefix) < len(prefix):
                self.model.text = prefix
                self._refresh()
    

class DescriptionEdit(CompletableEdit):
    ATTRNAME = 'description'

class PayeeEdit(CompletableEdit):
    ATTRNAME = 'payee'

class AccountEdit(CompletableEdit):
    ATTRNAME = 'account'
