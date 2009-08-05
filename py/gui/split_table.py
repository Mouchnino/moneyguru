# Created By: Virgil Dupras
# Created On: 2008-07-05
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base import TransactionPanelGUIObject
from .complete import TransactionCompletionMixIn
from .table import GUITable, RowWithDebitAndCredit

class SplitTable(TransactionPanelGUIObject, GUITable, TransactionCompletionMixIn):
    def __init__(self, view, transaction_panel):
        TransactionPanelGUIObject.__init__(self, view, transaction_panel)
        GUITable.__init__(self)
        self.document = transaction_panel.document # TransactionCompletionMixIn requires a document member
    
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
    
    def _update_selection(self):
        self.document.select_splits([row.split for row in self.selected_rows])
    
    #--- Public
    def refresh(self):
        transaction = self.panel.transaction
        splits = transaction.splits
        selected_indexes = self.selected_indexes
        del self[:]
        for split in splits:
            self.append(SplitTableRow(self, split))
        self.selected_indexes = selected_indexes
    
    #--- Event Handlers
    def edition_must_stop(self):
        self.view.stop_editing()
        self.save_edits()
    
    def panel_loaded(self):
        self.refresh()
        self.select([0])
        self.view.refresh()
    
    def split_changed(self):
        self.refresh()
        self.view.refresh()
    

class SplitTableRow(RowWithDebitAndCredit):
    def __init__(self, table, split):
        RowWithDebitAndCredit.__init__(self, table)
        self.split = split
        self.load()
    
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
            self._credit = self.table.document.app.parse_amount(value)
        except ValueError:
            pass
    
    @property
    def debit(self):
        return self.table.document.app.format_amount(self._debit, blank_zero=True)
    
    @debit.setter
    def debit(self, value):
        try:
            self._debit = self.table.document.app.parse_amount(value)
        except ValueError:
            pass
    
