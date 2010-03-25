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
        ('notesEdit', 'notes'),
    ]
    
    def __init__(self, mainwindow):
        Panel.__init__(self, mainwindow)
        self.mainwindow = mainwindow
        self._setupUi()
        self.model = TransactionPanelModel(view=self, mainwindow=mainwindow.model)
        self.splitTable = SplitTable(transactionPanel=self, view=self.splitTableView)
        self.splitTable.model.connect()
        
        self.mctButton.clicked.connect(self.model.mct_balance)
        self.addSplitButton.clicked.connect(self.splitTable.model.add)
        self.removeSplitButton.clicked.connect(self.splitTable.model.delete)
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _loadFields(self):
        Panel._loadFields(self)
        self.tabWidget.setCurrentIndex(0)
    
    #--- model --> view
    def refresh_for_multi_currency(self):
        self.mctButton.setEnabled(self.model.is_multi_currency)
    
