# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QDialog

from moneyguru.gui.transaction_panel import TransactionPanel as TransactionPanelModel

from .panel import Panel
from .split_table import SplitTable
from ui.transaction_panel_ui import Ui_TransactionPanel

class TransactionPanel(Panel, Ui_TransactionPanel):
    def __init__(self, doc):
        Panel.__init__(self)
        self._setupUi()
        self.doc = doc
        self.model = TransactionPanelModel(view=self, document=doc.model)
        self.splitTable = SplitTable(transaction_panel=self, view=self.splitTableView)
        self.splitTable.model.connect()
    
    def _loadFields(self):
        self.dateEdit.setText(self.model.date)
        self.descriptionEdit.setText(self.model.description)
        self.payeeEdit.setText(self.model.payee)
        self.checkNoEdit.setText(self.model.checkno)
    
    def _saveFields(self):
        self.model.date = unicode(self.dateEdit.text())
        self.model.description = unicode(self.descriptionEdit.text())
        self.model.payee = unicode(self.payeeEdit.text())
        self.model.checkno = unicode(self.checkNoEdit.text())
    
    def _setupUi(self):
        self.setupUi(self)
    
    #--- model --> view
    def refresh_mct_button(self):
        pass
    
