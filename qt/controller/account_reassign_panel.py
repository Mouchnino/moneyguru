# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QDialog

from core.gui.account_reassign_panel import AccountReassignPanel as AccountReassignPanelModel

from .panel import Panel
from ui.account_reassign_panel_ui import Ui_AccountReassignPanel

class AccountReassignPanel(Panel, Ui_AccountReassignPanel):
    FIELDS = [
        ('accountComboBox', 'account_index'),
    ]
    
    def __init__(self, parent, mainwindow):
        Panel.__init__(self, parent)
        self.setupUi(self)
        self.model = AccountReassignPanelModel(view=self, mainwindow=mainwindow.model)
    
    def _loadFields(self):
        self._changeComboBoxItems(self.accountComboBox, self.model.available_accounts)
        Panel._loadFields(self)
    
