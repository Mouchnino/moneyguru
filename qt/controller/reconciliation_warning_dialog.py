# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-10
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from moneyguru.const import (UNRECONCILIATION_ABORT, UNRECONCILIATION_CONTINUE, 
    UNRECONCILIATION_CONTINUE_DONT_UNRECONCILE)

from ui.reconciliation_warning_dialog_ui import Ui_ReconciliationWarningDialog

class ReconciliationWarningDialog(QDialog, Ui_ReconciliationWarningDialog):
    def __init__(self, count, parent=None):
        # The flags we pass are that so we don't get the "What's this" button in the title bar
        QDialog.__init__(self, None, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.setupUi(self)
        self.promptLabel.setText(unicode(self.promptLabel.text()).replace('<count>', unicode(count)))
    
    def askForResolution(self):
        self.exec_()
        choiceIndex = self.choiceComboBox.currentIndex()
        return [
            UNRECONCILIATION_ABORT,
            UNRECONCILIATION_CONTINUE,
            UNRECONCILIATION_CONTINUE_DONT_UNRECONCILE,
        ][choiceIndex]
