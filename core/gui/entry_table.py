# Created By: Eric Mc Sween
# Created On: 2008-07-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import datetime

from .column import Column
from .entry_table_base import EntryTableBase, EntryTableRow, PreviousBalanceRow, TotalRow

class EntryTable(EntryTableBase):
    SAVENAME = 'EntryTable'
    COLUMNS = [
        Column('status'),
        Column('date'),
        Column('reconciliation_date', visible=False),
        Column('checkno', visible=False),
        Column('description'),
        Column('payee', visible=False),
        Column('transfer'),
        Column('increase'),
        Column('decrease'),
        Column('debit', visible=False),
        Column('credit', visible=False),
        Column('balance'),
    ]
    INVALIDATING_MESSAGES = EntryTableBase.INVALIDATING_MESSAGES | {'shown_account_changed'}
    
    def __init__(self, view, account_view):
        EntryTableBase.__init__(self, view, account_view)
        self.account = None
        self._reconciliation_mode = False
    
    #--- Override
    def _fill(self):
        account = self.mainwindow.shown_account
        if account is None:
            return
        self.account = account
        rows = self._get_account_rows(account)
        if not rows:
            # We still show a total row
            rows.append(TotalRow(self, account, self.document.date_range.end, 0, 0))
        if isinstance(rows[0], PreviousBalanceRow):
            self.header = rows[0]
            del rows[0]
        for row in rows[:-1]:
            self.append(row)
        self.footer = rows[-1]
        balance_visible = account.is_balance_sheet_account()
        self.columns.set_column_visible('balance', balance_visible)
        self._restore_from_explicit_selection()
    
    def _get_current_account(self):
        return self.mainwindow.shown_account
    
    def _restore_from_explicit_selection(self):
        if self.mainwindow.explicitly_selected_transactions:
            self.select_transactions(self.mainwindow.explicitly_selected_transactions)
            if not self.selected_indexes:
                self.select_nearest_date(self.mainwindow.explicitly_selected_transactions[0].date)
    
    #--- Public
    def select_nearest_date(self, target_date):
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
    
    def show_transfer_account(self):
        if not self.selected_entries:
            return
        entry = self.selected_entries[0]
        splits = entry.transaction.splits
        accounts = [split.account for split in splits if split.account is not None]
        if len(accounts) < 2:
            return # no transfer
        index = accounts.index(entry.account)
        if index < len(accounts) - 1:
            account_to_show = accounts[index+1]
        else:
            account_to_show = accounts[0]
        self.mainwindow.shown_account = account_to_show
    
    def toggle_reconciled(self):
        """Toggle the reconcile flag of selected entries"""
        entries = [row.entry for row in self.selected_rows if row.can_reconcile()]
        self.document.toggle_entries_reconciled(entries)
    
    #--- Properties
    @property
    def reconciliation_mode(self):
        return self._reconciliation_mode
    
    @reconciliation_mode.setter
    def reconciliation_mode(self, value):
        if value == self._reconciliation_mode:
            return
        self._reconciliation_mode = value
        self.refresh()
        self.view.refresh()
    
    #--- Event Handlers
    def date_range_changed(self):
        date_range = self.document.date_range
        self.refresh()
        self.select_transactions(self.mainwindow.selected_transactions)
        if not self.selected_indexes:
            self.select_nearest_date(date_range.start + self._delta_before_change)
        self.view.refresh()
        self.view.show_selected_row()
        self.mainwindow.selected_transactions = self.selected_transactions
    
    def date_range_will_change(self):
        date_range = self.document.date_range
        transactions = self.selected_transactions
        date = transactions[0].date if transactions else date_range.end
        delta = date - date_range.start
        self._delta_before_change = delta
    
    def shown_account_changed(self):
        self._invalidated = True
    
    def transaction_changed(self):
        EntryTableBase.transaction_changed(self)
        # It's possible that because of the change, the selected txn has been removed, so we have
        # to update document selection.
        self._update_selection()
    
    def transactions_imported(self):
        self.refresh()
        self.mainwindow.selected_transactions = self.selected_transactions
        self.view.refresh()
        self.view.show_selected_row()
    
