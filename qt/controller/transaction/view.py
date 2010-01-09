# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.transaction_view import TransactionView as TransactionViewModel

from ..base_view import BaseView
from .filter_bar import TransactionFilterBar
from .table import TransactionTable
from ui.transaction_view_ui import Ui_TransactionView

class TransactionView(BaseView, Ui_TransactionView):
    PRINT_TITLE_FORMAT = "Transactions from {startDate} to {endDate}"
    
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.ttable = TransactionTable(doc=doc, view=self.tableView)
        self.tfbar = TransactionFilterBar(doc=doc, view=self.filterBar)
        self.children = [self.ttable, self.tfbar]
        core_children = [self.ttable.model, self.tfbar.model]
        self.model = TransactionViewModel(view=self, document=doc.model, children=core_children)
        self._setupColumns() # Can only be done after the model has been connected
        
        self.doc.app.willSavePrefs.connect(self._savePrefs)
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.ttable.setColumnsWidth(self.doc.app.prefs.transactionColumnWidths)
        self.ttable.setColumnsOrder(self.doc.app.prefs.transactionColumnOrder)
    
    def _savePrefs(self):
        h = self.tableView.horizontalHeader()
        widths = [h.sectionSize(index) for index in xrange(len(self.ttable.COLUMNS))]
        self.doc.app.prefs.transactionColumnWidths = widths
        order = [h.logicalIndex(index) for index in xrange(len(self.ttable.COLUMNS))]
        self.doc.app.prefs.transactionColumnOrder = order
    
    # Temporary
    def connect(self):
        self.model.connect()
        BaseView.connect(self)
    
    def disconnect(self):
        self.model.disconnect()
        BaseView.disconnect(self)
    
    #--- QWidget override
    def setFocus(self):
        self.ttable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.ttable)
    
    def updateOptionalWidgetsVisibility(self):
        self.ttable.setHiddenColumns(self.doc.app.prefs.transactionHiddenColumns)
    
    #--- model --> view
    def refresh_totals(self):
        self.totalsLabel.setText(self.model.totals)
    
