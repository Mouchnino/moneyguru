# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt

from core.gui.budget_table import BudgetTable as BudgetTableModel
from ..column import Column
from ..table import Table

class BudgetTable(Table):
    COLUMNS = [
        Column('start_date', 'Start Date', 90),
        Column('stop_date', 'Stop Date', 90),
        Column('repeat_type', 'Repeat Type', 80),
        Column('interval', 'Interval', 50),
        Column('account', 'Account', 144),
        Column('target', 'Target', 144),
        Column('amount', 'Amount', 100, alignment=Qt.AlignRight),
    ]
    
    def __init__(self, doc, view):
        model = BudgetTableModel(view=self, document=doc.model)
        Table.__init__(self, model, view)
        self.view.deletePressed.connect(self.model.delete)
        self.view.doubleClicked.connect(self.model.edit)
    
