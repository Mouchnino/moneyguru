# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-09-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..model.account import sort_accounts
from ..model.amount import convert_amount
from ..model.date import ONE_DAY
from .entry_table import EntryTableRow, TotalRow, PreviousBalanceRow
from .table import Row
from .transaction_table_base import TransactionTableBase

class GeneralLedgerTable(TransactionTableBase):
    #--- Override
    def _fill(self):
        accounts = self.document.accounts
        sort_accounts(accounts)
        for account in accounts:
            rows = self._get_account_rows(account)
            if not rows:
                continue
            self.append(AccountRow(self, account))
            for row in rows:
                self.append(row)
    
    #--- Private
    def _get_account_rows(self, account):
        result = []
        date_range = self.document.date_range
        if account.is_balance_sheet_account():
            prev_entry = account.entries.last_entry(date_range.start-ONE_DAY)
            if prev_entry is not None:
                balance = prev_entry.balance
                rbalance = prev_entry.reconciled_balance
                result.append(PreviousBalanceRow(self, date_range.start, balance, rbalance, account))
        total_debit = 0
        total_credit = 0
        entries = self.mainwindow.visible_entries_for_account(account)
        for entry in entries:
            row = GeneralLedgerRow(self, entry, account)
            result.append(row)
            convert = lambda a: convert_amount(a, account.currency, entry.date)
            total_debit += convert(row._debit)
            total_credit += convert(row._credit)
        if result:
            total_row = TotalRow(self, account, date_range.end, total_debit, total_credit)
            result.append(total_row)
        return result
    
    #--- Public
    def is_account_row(self, row_index):
        return isinstance(self[row_index], AccountRow)
    
    def is_bold_row(self, row_index):
        return isinstance(self[row_index], (TotalRow, PreviousBalanceRow))
    
    #--- Properties
    @property
    def selected_entries(self):
        return [row.entry for row in self.selected_rows if hasattr(row, 'entry')]
    
    @property
    def selected_transactions(self):
        return [entry.transaction for entry in self.selected_entries]
    
    #--- Event Handlers
    def edition_must_stop(self):
        pass # the view doesn't have a stop_editing method
    
    def date_range_changed(self):
        self.refresh()
        self._update_selection()
        self.view.refresh()
        self.view.show_selected_row()
    

class AccountRow(Row):
    def __init__(self, table, account):
        Row.__init__(self, table)
        self.account_name = account.name
    

class GeneralLedgerRow(EntryTableRow):
    @property
    def balance(self):
        if self.account.is_balance_sheet_account():
            return EntryTableRow.balance.fget(self)
        else:
            return ''
    
