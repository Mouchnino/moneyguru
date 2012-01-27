# Created By: Virgil Dupras
# Created On: 2010-01-06
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import datetime

from .base import ViewChild, MESSAGES_DOCUMENT_CHANGED
from .table import GUITable
from .completable_edit import CompletableEdit

class TransactionTableBase(GUITable, ViewChild):
    """Common superclass for TransactionTable and EntryTable, which share a lot of logic.
    """
    INVALIDATING_MESSAGES = MESSAGES_DOCUMENT_CHANGED | {'filter_applied', 'date_range_changed'}
    
    def __init__(self, parent_view):
        ViewChild.__init__(self, parent_view)
        GUITable.__init__(self, document=parent_view.document)
        self.completable_edit = CompletableEdit(parent_view.mainwindow)
    
    #--- Override
    def _is_edited_new(self):
        return self.edited.transaction not in self.document.transactions
    
    def _restore_selection(self, previous_selection):
        # We do the default selection restore, but if we end up selecting the Total row and there's
        # a row above it, we select it.
        GUITable._restore_selection(self, previous_selection)
        if self.selected_indexes == [len(self)-1] and len(self) > 1:
            self.selected_indexes = [len(self) - 2]
    
    def _update_selection(self):
        self.mainwindow.explicitly_selected_transactions = self.selected_transactions
    
    def add(self):
        GUITable.add(self)
    
    def _revalidate(self):
        self.refresh()
    
    def show(self):
        ViewChild.show(self)
        self._restore_from_explicit_selection()
        self.mainwindow.selected_transactions = self.selected_transactions
        self.view.show_selected_row()
    
    #--- Private
    def _restore_from_explicit_selection(self):
        if self.mainwindow.explicitly_selected_transactions:
            self.select_transactions(self.mainwindow.explicitly_selected_transactions)
            if not self.selected_indexes:
                self._select_nearest_date(self.mainwindow.explicitly_selected_transactions[0].date)
            self.view.update_selection()
    
    def _select_nearest_date(self, target_date):
        # This method assumes that self is sorted by date
        last_delta = datetime.timedelta.max
        for index, row in enumerate(self):
            delta = abs(row._date - target_date)
            if delta > last_delta:
                # The last iteration was the correct one
                self.selected_index = index - 1
                break
            last_delta = delta
        else:
            self.selected_index = len(self) - 1
    
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
