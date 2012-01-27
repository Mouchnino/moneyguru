# Created By: Eric Mc Sween
# Created On: 2008-07-06
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import datetime

from hscommon.trans import tr, trget
from hscommon.gui.column import Column, Columns
from .entry_table_base import EntryTableBase, PreviousBalanceRow, TotalRow

trcol = trget('columns')

class EntryTableColumns(Columns):
    def menu_items(self):
        items = Columns.menu_items(self)
        marked = self.column_is_visible('debit')
        items.append((tr("Debit/Credit"), marked))
        return items
    
    def toggle_menu_item(self, index):
        if index == len(self._optional_columns()):
            debit_visible = self.column_is_visible('debit')
            self.set_column_visible('debit', not debit_visible)
            self.set_column_visible('credit', not debit_visible)
            self.set_column_visible('increase', debit_visible)
            self.set_column_visible('decrease', debit_visible)
        else:
            Columns.toggle_menu_item(self, index)

class EntryTable(EntryTableBase):
    SAVENAME = 'EntryTable'
    COLUMNS = [
        Column('status', display=''),
        Column('date', display=trcol("Date")),
        Column('reconciliation_date', display=trcol("Reconciliation Date"), visible=False, optional=True),
        Column('checkno', display=trcol("Check #"), visible=False, optional=True),
        Column('description', display=trcol("Description"), optional=True),
        Column('payee', display=trcol("Payee"), visible=False, optional=True),
        Column('transfer', display=trcol("Transfer")),
        Column('increase', display=trcol("Increase")),
        Column('decrease', display=trcol("Decrease")),
        Column('debit', display=trcol("Debit"), visible=False),
        Column('credit', display=trcol("Credit"), visible=False),
        Column('balance', display=trcol("Balance")),
    ]
    
    def __init__(self, account_view):
        EntryTableBase.__init__(self, account_view)
        self.columns = EntryTableColumns(self, prefaccess=account_view.document, savename=self.SAVENAME)
        self.account = account_view.account
        self.completable_edit.account = self.account
        self._reconciliation_mode = False
    
    #--- Override
    def _fill(self):
        account = self.account
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
        return self.account
    
    def _get_totals_currency(self):
        return self._get_current_account().currency
    
    def _restore_from_explicit_selection(self):
        if self.mainwindow.explicitly_selected_transactions:
            self.select_transactions(self.mainwindow.explicitly_selected_transactions)
            if not self.selected_indexes:
                self.select_nearest_date(self.mainwindow.explicitly_selected_transactions[0].date)
            self.view.update_selection()
    
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
        self.mainwindow.open_account(account_to_show)
    
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
    
    #--- Event Handlers
    def date_range_changed(self):
        date_range = self.document.date_range
        self.refresh(refresh_view=False)
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
    
    def transaction_changed(self):
        EntryTableBase.transaction_changed(self)
        # It's possible that because of the change, the selected txn has been removed, so we have
        # to update document selection.
        self._update_selection()
    
    def transactions_imported(self):
        self.refresh(refresh_view=False)
        self.mainwindow.selected_transactions = self.selected_transactions
        self.view.refresh()
        self.view.show_selected_row()
    
