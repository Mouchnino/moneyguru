# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-02
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QDialog

from core.gui.account_reassign_panel import AccountReassignPanel as AccountReassignPanelModel

from .panel import Panel
from ui.account_reassign_panel_ui import Ui_AccountReassignPanel

#XXX the Hack part is there for the same reasons as with the CustomDateRangePanel
class AccountReassignPanel(Panel, Ui_AccountReassignPanel):
    FIELDS = [
        ('accountComboBox', 'account_index'),
    ]
    
    def __init__(self, parent, doc):
        Panel.__init__(self, parent)
        self.setupUi(self)
        self.doc = doc
        self.model = AccountReassignPanelModel(view=self, document=doc.model)
    
    def _loadFields(self):
        self._changeComboBoxItems(self.accountComboBox, self.model.available_accounts)
        Panel._loadFields(self)
    
    #--- Hack
    def accept(self):
        self._saveFields()
        self.model.ok()
        QDialog.accept(self)
    
    def load(self):
        self.model.load()
        self._loadFields()
        self._connectSignals()
        self.show()
    
