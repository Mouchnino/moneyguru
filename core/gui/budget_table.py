# Created By: Virgil Dupras
# Created On: 2009-08-22
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import datetime

from .base import ViewChild
from .column import Column
from .table import GUITable, Row, rowattr

class BudgetTable(GUITable, ViewChild):
    SAVENAME = 'BudgetTable'
    COLUMNS = [
        Column('start_date'),
        Column('stop_date'),
        Column('repeat_type'),
        Column('interval'),
        Column('account'),
        Column('target'),
        Column('amount'),
    ]
    INVALIDATING_MESSAGES = set(['budget_changed', 'budget_deleted', 'account_deleted'])
    
    def __init__(self, view, budget_view):
        ViewChild.__init__(self, view, budget_view)
        GUITable.__init__(self)
    
    #--- Override
    def _update_selection(self):
        self.mainwindow.selected_budgets = self.selected_budgets
    
    def _fill(self):
        for budget in self.document.budgets:
            self.append(BudgetTableRow(self, budget))
    
    def _revalidate(self):
        self.refresh()
    
    #--- Public
    def delete(self):
        self.document.delete_budgets(self.selected_budgets)
    
    def edit(self):
        self.mainwindow.edit_item()
    
    #--- Properties
    @property
    def selected_budgets(self):
        return [row.budget for row in self.selected_rows]
    
    #--- Event handlers
    budget_changed = GUITable._item_changed
    budget_deleted = GUITable._item_deleted
    
    def edition_must_stop(self):
        pass # the view doesn't have a stop_editing method
    

class BudgetTableRow(Row):
    def __init__(self, table, budget):
        Row.__init__(self, table)
        self.document = table.document
        self.budget = budget
        self.load()
    
    #--- Public
    def load(self):
        budget = self.budget
        self._start_date = budget.start_date
        self._start_date_fmt = self.document.app.format_date(self._start_date)
        self._stop_date = budget.stop_date
        self._stop_date_fmt = self.document.app.format_date(self._stop_date) if self._stop_date is not None else ''
        self._repeat_type = budget.repeat_type_desc
        self._interval = str(budget.repeat_every)
        self._account = budget.account.name
        self._target = budget.target.name if budget.target else ''
        self._amount = budget.amount
        self._amount_fmt = self.document.app.format_amount(self._amount)
    
    def save(self):
        pass # read-only
    
    def sort_key_for_column(self, column_name):
        if column_name == 'stop_date' and self._stop_date is None:
            return datetime.date.min
        else:
            return Row.sort_key_for_column(self, column_name)
    
    #--- Properties
    start_date = rowattr('_start_date_fmt')
    stop_date = rowattr('_stop_date_fmt')
    repeat_type = rowattr('_repeat_type')
    interval = rowattr('_interval')
    account = rowattr('_account')
    target = rowattr('_target')
    amount = rowattr('_amount_fmt')
