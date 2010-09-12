# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-09-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..model.account import sort_accounts
from .table import Row
from .column import Column
from .entry_table_base import EntryTableBase, EntryTableRow, TotalRow, PreviousBalanceRow

class AccountRow(Row):
    def __init__(self, table, account):
        Row.__init__(self, table)
        self.account = account
        self.account_name = account.name
    

class GeneralLedgerRow(EntryTableRow):
    @property
    def balance(self):
        if self.account.is_balance_sheet_account():
            return EntryTableRow.balance.fget(self)
        else:
            return ''
    

class GeneralLedgerTable(EntryTableBase):
    SAVENAME = 'GeneralLedgerTable'
    COLUMNS = [
        Column('status'),
        Column('date'),
        Column('reconciliation_date', visible=False),
        Column('checkno', visible=False),
        Column('description'),
        Column('payee', visible=False),
        Column('transfer'),
        Column('debit'),
        Column('credit'),
        Column('balance'),
    ]
    ENTRY_ROWCLASS = GeneralLedgerRow
    
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
    
    def _get_current_account(self):
        row = self.selected_row
        return row.account if row is not None else None
    
    def _get_totals_currency(self):
        return self.app.default_currency
    
    #--- Public
    def is_account_row(self, row_index):
        return isinstance(self[row_index], AccountRow)
    
    def is_bold_row(self, row_index):
        return isinstance(self[row_index], (TotalRow, PreviousBalanceRow))
    
    #--- Event Handlers
    def date_range_changed(self):
        self.refresh()
        self._update_selection()
        self.view.refresh()
        self.view.show_selected_row()
    
