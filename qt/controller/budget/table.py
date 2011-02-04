# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt

from qtlib.column import Column
from hscommon.trans import tr
from core.gui.budget_table import BudgetTable as BudgetTableModel
from ..table import Table

class BudgetTable(Table):
    COLUMNS = [
        Column('start_date', tr('Start Date'), 90),
        Column('stop_date', tr('Stop Date'), 90),
        Column('repeat_type', tr('Repeat Type'), 80),
        Column('interval', tr('Interval'), 50),
        Column('account', tr('Account'), 144),
        Column('target', tr('Target'), 144),
        Column('amount', tr('Amount'), 100, alignment=Qt.AlignRight),
    ]
    
    def __init__(self, budget_view, view):
        model = BudgetTableModel(view=self, budget_view=budget_view.model)
        Table.__init__(self, model, view)
        self.view.sortByColumn(0, Qt.AscendingOrder) # sorted by start_date by default
        self.view.deletePressed.connect(self.model.delete)
        self.view.doubleClicked.connect(self.model.edit)
        # we have to prevent Return from initiating editing.
        self.view.editSelected = lambda: None
    
