# Created By: Virgil Dupras
# Created On: 2009-08-22
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..model.amount import convert_amount
from ..model.recurrence import Spawn
from .base import DocumentGUIObject
from .table import GUITable, Row, rowattr
from .transaction_table import TransactionTableRow

class BudgetTable(GUITable, DocumentGUIObject):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        GUITable.__init__(self)
    
    #--- Override
    def _update_selection(self):
        self.document.select_budgets(self.selected_budgets)
    
    def _fill(self):
        for budget in self.document.budgets:
            self.append(BudgetTableRow(self, budget))
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.refresh()
        self.view.refresh()
    
    #--- Public
    def delete(self):
        self.document.delete_budgets(self.selected_budgets)
    
    # This is a temporary workaround so that double-clicks and pressing return works in the btable
    def edit(self):
        self.document.edit_selected()
    
    #--- Properties
    @property
    def selected_budgets(self):
        return [row.budget for row in self.selected_rows]
    
    #--- Event handlers
    budget_changed = GUITable._item_changed
    budget_deleted = GUITable._item_deleted
    
    def edition_must_stop(self):
        pass # the view doesn't have a stop_editing method
    
    def file_loaded(self):
        self.refresh()
        self.view.refresh()
    

class BudgetTableRow(Row):
    def __init__(self, table, budget):
        Row.__init__(self, table)
        self.document = table.document
        self.budget = budget
        self.load()
    
    def load(self):
        budget = self.budget
        self._start_date = budget.start_date
        self._start_date_fmt = self.document.app.format_date(self._start_date)
        self._stop_date = budget.stop_date
        self._stop_date_fmt = self.document.app.format_date(self._start_date) if self._stop_date is not None else ''
        self._repeat_type = budget.repeat_type_desc
        self._interval = unicode(budget.repeat_every)
        self._account = budget.account.name
        self._target = budget.target.name if budget.target else ''
        self._amount = budget.amount
        self._amount_fmt = self.document.app.format_amount(self._amount)
    
    def save(self):
        pass # read-only
    
    start_date = rowattr('_start_date_fmt')
    stop_date = rowattr('_stop_date_fmt')
    repeat_type = rowattr('_repeat_type')
    interval = rowattr('_interval')
    account = rowattr('_account')
    target = rowattr('_target')
    amount = rowattr('_amount_fmt')
