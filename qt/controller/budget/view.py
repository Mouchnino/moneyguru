# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..base_view import BaseView
from .table import BudgetTable
from ui.budget_view_ui import Ui_BudgetView

class BudgetView(BaseView, Ui_BudgetView):
    PRINT_TITLE_FORMAT = "Budgets from {startDate} to {endDate}"
    
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.btable = BudgetTable(doc=doc, view=self.tableView)
        self.children = [self.btable]
        self._setupColumns() # Can only be done after the model has been connected
        
        self.doc.app.willSavePrefs.connect(self._savePrefs)
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.btable.setColumnsWidth(self.doc.app.prefs.budgetColumnWidths)
        self.btable.setColumnsOrder(self.doc.app.prefs.budgetColumnOrder)
    
    def _savePrefs(self):
        h = self.tableView.horizontalHeader()
        widths = [h.sectionSize(index) for index in xrange(len(self.btable.COLUMNS))]
        self.doc.app.prefs.budgetColumnWidths = widths
        order = [h.logicalIndex(index) for index in xrange(len(self.btable.COLUMNS))]
        self.doc.app.prefs.budgetColumnOrder = order
    
    #--- QWidget override
    def setFocus(self):
        self.btable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.btable)
    
