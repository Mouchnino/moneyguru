# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.gui.budget_view import BudgetView as BudgetViewModel

from ..base_view import BaseView
from .table import BudgetTable
from ui.budget_view_ui import Ui_BudgetView

class BudgetView(BaseView, Ui_BudgetView):
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self.doc = mainwindow.doc
        self._setupUi()
        self.model = BudgetViewModel(view=self, mainwindow=mainwindow.model)
        self.btable = BudgetTable(self, view=self.tableView)
        children = [self.btable.model]
        self.model.set_children(children)
        self._setupColumns() # Can only be done after the model has been connected
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.btable.restore_columns()
    
    #--- QWidget override
    def setFocus(self):
        self.btable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.btable)
    
