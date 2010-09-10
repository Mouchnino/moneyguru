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
from .entry_table import EntryTableRow, TotalRow
from .table import Row
from .transaction_table_base import TransactionTableBase

class GeneralLedgerTable(TransactionTableBase):
    #--- Override
    def _fill(self):
        accounts = self.document.accounts
        sort_accounts(accounts)
        for account in accounts:
            self.append(AccountRow(self, account))
            rows = self._get_account_rows(account)
            for row in rows:
                self.append(row)
    
    #--- Private
    def _get_account_rows(self, account):
        date_range = self.document.date_range
        total_debit = 0
        total_credit = 0
        for entry in account.entries:
            row = EntryTableRow(self, entry, account)
            yield row
            convert = lambda a: convert_amount(a, account.currency, entry.date)
            total_debit += convert(row._debit)
            total_credit += convert(row._credit)
        total_row = TotalRow(self, account, date_range.end, total_debit, total_credit)
        yield total_row
    
    #--- Public
    def is_account_row(self, row_index):
        return isinstance(self[row_index], AccountRow)
    
    def is_bold_row(self, row_index):
        return isinstance(self[row_index], TotalRow)
    
    #--- Properties
    @property
    def selected_entries(self):
        return [row.entry for row in self.selected_rows if hasattr(row, 'entry')]
    
    @property
    def selected_transactions(self):
        return [entry.transaction for entry in self.selected_entries]
    

class AccountRow(Row):
    def __init__(self, table, account):
        Row.__init__(self, table)
        self.account_name = account.name
    
