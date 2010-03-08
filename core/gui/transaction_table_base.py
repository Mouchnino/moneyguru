# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base import DocumentGUIObject
from .table import GUITable

class TransactionTableBase(GUITable, DocumentGUIObject):
    """Common superclass for TransactionTable and EntryTable, which share a lot of logic.
    """
    def __init__(self, view, mainwindow):
        DocumentGUIObject.__init__(self, view, mainwindow.document)
        GUITable.__init__(self)
        self.mainwindow = mainwindow
        self._columns = [] # empty columns == unrestricted autofill
    
    #--- Override
    def _is_edited_new(self):
        return self.edited.transaction not in self.document.transactions
    
    def _update_selection(self):
        self.document.explicitly_select_transactions(self.selected_transactions)
    
    def add(self):
        GUITable.add(self)
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.refresh()
        self.document.select_transactions(self.selected_transactions)
        self.view.refresh()
        self.view.show_selected_row()
    
    #--- Public
    def can_move(self, row_indexes, position):
        if self._sort_descriptor is not None and self._sort_descriptor != ('date', False):
            return False
        if not GUITable.can_move(self, row_indexes, position):
            return False
        if not all(self[index].can_edit() for index in row_indexes):
            return False
        transactions = [self[index].transaction for index in row_indexes]
        before = self[position - 1] if position > 0 else None
        after = self[position] if position < len(self) else None
        # before and after are rows, get the txn if it exists
        before = before.transaction if hasattr(before, 'transaction') else None
        after = after.transaction if hasattr(after, 'transaction') else None
        return self.document.can_move_transactions(transactions, before, after)
    
    def change_columns(self, columns):
        """Call this when the order or the visibility of the columns change"""
        
        columns = [c if c != 'from_' else 'from' for c in columns]
        self._columns = columns
    
    def duplicate_selected(self):
        self.document.duplicate_transactions(self.selected_transactions)
    
    def move(self, row_indexes, to_index):
        try:
            to_row = self[to_index]
            to_transaction = getattr(to_row, 'transaction', None)
        except IndexError:
            to_transaction = None
        # we can use any from_index, let's use the first
        transactions = [self[index].transaction for index in row_indexes]
        self.document.move_transactions(transactions, to_transaction)
    
    def move_down(self):
        """Moves the selected entry down one slot if possible"""
        if len(self.selected_indexes) != 1:
            return
        position = self.selected_indexes[-1] + 2
        if self.can_move(self.selected_indexes, position):
            self.move(self.selected_indexes, position)
    
    def move_up(self):
        """Moves the selected entry up one slot if possible"""
        if len(self.selected_indexes) != 1:
            return
        position = self.selected_indexes[0] - 1
        if self.can_move(self.selected_indexes, position):
            self.move(self.selected_indexes, position)
    
    def select_transactions(self, transactions):
        selected_indexes = []
        for index, row in enumerate(self):
            if hasattr(row, 'transaction') and row.transaction in transactions:
                selected_indexes.append(index)
        self.selected_indexes = selected_indexes
    
    #--- Event Handlers
    filter_applied = GUITable._filter_applied
    transaction_changed = GUITable._item_changed
    transaction_deleted = GUITable._item_deleted
