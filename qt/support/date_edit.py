# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QTimer, QEvent
from PyQt4.QtGui import QLineEdit

from core.gui.date_widget import DateWidget

class DateEdit(QLineEdit):
    KEY2METHOD = {
        Qt.Key_Left: 'left',
        Qt.Key_Right: 'right',
        Qt.Key_Up: 'increase',
        Qt.Key_Down: 'decrease',
        Qt.Key_Backspace: 'backspace',
        Qt.Key_Delete: 'backspace',
    }
    ACCEPTED_KEYS = set([Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Return, Qt.Key_Enter])
    DATE_FORMAT = 'dd/MM/yyyy'
    
    def __init__(self, parent):
        QLineEdit.__init__(self, parent)
        self.widget = DateWidget(self.DATE_FORMAT)
    
    def _refresh(self):
        self.setText(self.widget.text)
        selStart, selEnd = self.widget.selection
        self.setSelection(selStart, selEnd-selStart+1)
    
    #--- QLineEdit overrides
    def keyPressEvent(self, event):
        key = event.key()
        if key in self.KEY2METHOD:
            getattr(self.widget, self.KEY2METHOD[key])()
            self._refresh()
        elif key in self.ACCEPTED_KEYS:
            # We want keypresses like Escape to go through.
            QLineEdit.keyPressEvent(self, event)
        else:
            text = unicode(event.text())
            if text in "0123456789/-.":
                self.widget.type(text)
                self._refresh()
    
    def focusInEvent(self, event):
        QLineEdit.focusInEvent(self, event)
        self.widget.text = unicode(self.text())
        # A timer is used here because a mouse event following the focusInEvent messes up the
        # selection (so the refresh *has* to happen after the mouse event).
        QTimer.singleShot(0, self._refresh)
    
    def focusOutEvent(self, event):
        self.prepareDataForCommit()
        QLineEdit.focusOutEvent(self, event)
    
    #--- Public
    def prepareDataForCommit(self):
        self.widget.exit()
        self._refresh()
    
