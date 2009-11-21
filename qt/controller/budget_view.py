# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base_view import BaseView
from .budget_table import BudgetTable
from ui.budget_view_ui import Ui_BudgetView

class BudgetView(BaseView, Ui_BudgetView):
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.btable = BudgetTable(doc=doc, view=self.tableView)
        self.children = [self.btable]
        self._setupColumns() # Can only be done after the model has been connected
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setHighlightSections(False)
    