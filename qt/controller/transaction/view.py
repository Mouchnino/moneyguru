# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.transaction_view import TransactionView as TransactionViewModel
from core.trans import tr

from ..base_view import BaseView
from .filter_bar import TransactionFilterBar
from .table import TransactionTable
from ui.transaction_view_ui import Ui_TransactionView

class TransactionView(BaseView, Ui_TransactionView):
    PRINT_TITLE_FORMAT = tr("Transactions from {startDate} to {endDate}")
    
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self.doc = mainwindow.doc
        self._setupUi()
        self.model = TransactionViewModel(view=self, mainwindow=mainwindow.model)
        self.ttable = TransactionTable(self, view=self.tableView)
        self.tfbar = TransactionFilterBar(self, view=self.filterBar)
        children = [self.ttable.model, self.tfbar.model]
        self.model.set_children(children)
        self._setupColumns() # Can only be done after the model has been connected
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.ttable.setColumnsWidth()
        self.ttable.setColumnsOrder()
    
    #--- QWidget override
    def setFocus(self):
        self.ttable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.ttable)
    
    def updateOptionalWidgetsVisibility(self):
        self.ttable.setHiddenColumns(self.doc.app.prefs.transactionHiddenColumns)
    
