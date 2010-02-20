# Created By: Virgil Dupras
# Created On: 2008-07-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..model.amount import parse_amount
from .base import TransactionPanelGUIObject
from .complete import CompletionMixIn
from .table import GUITable, RowWithDebitAndCredit

class SplitTable(GUITable, TransactionPanelGUIObject, CompletionMixIn):
    def __init__(self, view, transaction_panel):
        TransactionPanelGUIObject.__init__(self, view, transaction_panel)
        GUITable.__init__(self)
        self.document = transaction_panel.document # CompletionMixIn requires a document member
    
    #--- Override
    def _do_add(self):
        split = self.panel.new_split()
        row = SplitTableRow(self, split)
        self.append(row)
        self.select([len(self) - 1])
        return row
    
    def _do_delete(self):
        self.panel.delete_split(self.selected_row.split)
        self.refresh()
        self.view.refresh()
    
    def _fill(self):
        transaction = self.panel.transaction
        splits = transaction.splits
        for split in splits:
            self.append(SplitTableRow(self, split))
    
    def _update_selection(self):
        self.document.select_splits([row.split for row in self.selected_rows])
    
    #--- Event Handlers
    def panel_loaded(self):
        self.refresh()
        self.select([0])
        self.view.refresh()
    
    split_changed = GUITable._item_changed

class SplitTableRow(RowWithDebitAndCredit):
    def __init__(self, table, split):
        RowWithDebitAndCredit.__init__(self, table)
        self.split = split
        self.load()
    
    def _parse_amount(self, value):
        if self.split.transaction.amount:
            currency = self.split.transaction.amount.currency
        else:
            currency = self.table.document.app.default_currency
        return parse_amount(value, currency)
    
    def load(self):
        self._account = self.split.account.name if self.split.account else ''
        self._memo = self.split.memo
        self._amount = self.split.amount
    
    def save(self):
        self.table.panel.change_split(self.split, self.account, self._amount, self._memo)
    
    @property
    def account(self):
        return self._account
    
    @account.setter
    def account(self, value):
        self._edit()
        self._account = value
    
    @property
    def memo(self):
        return self._memo
    
    @memo.setter
    def memo(self, value):
        self._edit()
        self._memo = value
    
    @property
    def credit(self):
        return self.table.document.app.format_amount(self._credit, blank_zero=True)
    
    @credit.setter
    def credit(self, value):
        try:
            self._credit = self._parse_amount(value)
        except ValueError:
            pass
    
    @property
    def debit(self):
        return self.table.document.app.format_amount(self._debit, blank_zero=True)
    
    @debit.setter
    def debit(self, value):
        try:
            self._debit = self._parse_amount(value)
        except ValueError:
            pass
    
