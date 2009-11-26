# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-26
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QTableView

class TableView(QTableView):
    #--- QTableView override
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self.spacePressed.emit()
        else:
            QTableView.keyPressEvent(self, event)
    
    #--- Signals
    spacePressed = pyqtSignal()
