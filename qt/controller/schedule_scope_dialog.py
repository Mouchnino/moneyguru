# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-10
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from ui.schedule_scope_dialog_ui import Ui_ScheduleScopeDialog

class ScheduleScopeDialog(QDialog, Ui_ScheduleScopeDialog):
    def __init__(self, parent=None):
        # The flags we pass are that so we don't get the "What's this" button in the title bar
        QDialog.__init__(self, None, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.setupUi(self)
    
