# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QDialog

from core.gui.transaction_panel import TransactionPanel as TransactionPanelModel

from .panel import Panel
from .split_table import SplitTable
from ui.transaction_panel_ui import Ui_TransactionPanel

class TransactionPanel(Panel, Ui_TransactionPanel):
    FIELDS = [
        ('dateEdit', 'date'),
        ('descriptionEdit', 'description'),
        ('payeeEdit', 'payee'),
        ('checkNoEdit', 'checkno'),
        ('amountEdit', 'amount'),
    ]
    
    def __init__(self, parent, doc):
        Panel.__init__(self, parent)
        self._setupUi()
        self.doc = doc
        self.model = TransactionPanelModel(view=self, document=doc.model)
        self.splitTable = SplitTable(transactionPanel=self, view=self.splitTableView)
        self.splitTable.model.connect()
        
        self.mctButton.clicked.connect(self.model.mct_balance)
        self.addSplitButton.clicked.connect(self.splitTable.model.add)
        self.removeSplitButton.clicked.connect(self.splitTable.model.delete)
    
    def _setupUi(self):
        self.setupUi(self)
    
    #--- model --> view
    def refresh_mct_button(self):
        self.mctButton.setEnabled(self.model.can_do_mct_balance)
    
