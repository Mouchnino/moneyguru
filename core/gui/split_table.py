# Created By: Virgil Dupras
# Created On: 2008-07-05
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..model.amount import parse_amount
from .base import TransactionPanelGUIObject
from .table import GUITable, Row, RowWithDebitAndCreditMixIn

class SplitTable(GUITable, TransactionPanelGUIObject):
    def __init__(self, transaction_panel):
        self.mainwindow = transaction_panel.mainwindow # CompletableEdit on Qt requires a mainwindow member
        self.document = transaction_panel.document
        GUITable.__init__(self)
        TransactionPanelGUIObject.__init__(self, self.view, transaction_panel)
    
    #--- Override
    def _do_add(self):
        split = self.panel.new_split()
        row = SplitTableRow(self, split)
        return row, len(self)
    
    def _do_delete(self):
        self.panel.delete_split(self.selected_row.split)
        self.refresh()
    
    def _is_edited_new(self):
        split = self.edited.split
        return split not in split.transaction.splits
    
    def _fill(self):
        transaction = self.panel.transaction
        splits = transaction.splits
        for split in splits:
            self.append(SplitTableRow(self, split))
    
    def _update_selection(self):
        self.panel.select_splits([row.split for row in self.selected_rows])
    
    #--- Public
    def move_split(self, from_index, to_index):
        row = self[from_index]
        row.split.move_to_index(to_index)
        self.refresh(refresh_view=False)
        self.select([to_index])
        self.view.refresh()
    
    #--- Event Handlers
    def panel_loaded(self):
        self.refresh(refresh_view=False)
        self.select([0])
        self.view.refresh()
    
    split_changed = GUITable._item_changed

class SplitTableRow(Row, RowWithDebitAndCreditMixIn):
    def __init__(self, table, split):
        Row.__init__(self, table)
        self.split = split
        self.load()
    
    def _parse_amount(self, value):
        if self.split.transaction.amount:
            currency = self.split.transaction.amount.currency
        else:
            currency = self.table.document.app.default_currency
        return self.table.document.app.parse_amount(value, default_currency=currency)
    
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
    
