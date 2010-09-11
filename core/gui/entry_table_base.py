# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-09-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import datetime
from operator import attrgetter

from ..model.amount import convert_amount
from ..model.date import ONE_DAY
from ..model.recurrence import Spawn
from ..trans import tr
from .table import Row, RowWithDebitAndCreditMixIn, RowWithDateMixIn, rowattr
from .transaction_table_base import TransactionTableBase

class BaseEntryTableRow(Row, RowWithDateMixIn, RowWithDebitAndCreditMixIn):
    def __init__(self, table, account):
        Row.__init__(self, table)
        RowWithDateMixIn.__init__(self)
        self.account = account
        self._date = datetime.date.today()
        self._position = 0
        self._description = ''
        self._payee = ''
        self._checkno = ''
        self._amount = 0
        self._transfer = ''
        self._balance = 0
        self._reconciled_balance = 0
        self._reconciled = False
        self._reconciliation_date = None
        self._recurrent = False
        self._is_budget = False
        self.is_bold = False
    
    def _the_balance(self):
        reconciliation_mode = getattr(self.table, 'reconciliation_mode', False)
        if reconciliation_mode:
            balance = self._reconciled_balance
        else:
            balance = self._balance
        if balance and self.account.is_credit_account():
            balance = -balance
        return balance
    
    #--- Public
    def can_edit(self):
        return False
    
    def can_reconcile(self):
        return False
    
    def is_balance_negative(self):
        return self._the_balance() < 0
    
    def sort_key_for_column(self, column_name):
        if column_name == 'date':
            return (self._date, self._position)
        elif column_name == 'reconciliation_date':
            rdate =  self._reconciliation_date
            if rdate is None:
                rdate = datetime.date.max
            return (rdate, self._date, self._position)
        elif column_name == 'status':
            # First reconciled, then plain ones, then schedules, then budgets
            if self.reconciled:
                return 0
            elif self.recurrent:
                return 2
            elif self.is_budget:
                return 3
            else:
                return 1
        else:
            return Row.sort_key_for_column(self, column_name)
    
    #--- Properties
    @property
    def description(self):
        return self._description
    
    @property
    def payee(self):
        return self._payee
    
    @property
    def checkno(self):
        return self._checkno
    
    @property
    def transfer(self):
        return self._transfer
    
    @property
    def increase(self):
        return self.table.document.app.format_amount(self._increase, blank_zero=True)
    
    @property
    def decrease(self):
        return self.table.document.app.format_amount(self._decrease, blank_zero=True)
    
    @property
    def debit(self):
        return self.table.document.app.format_amount(self._debit, blank_zero=True)
    
    @property
    def credit(self):
        return self.table.document.app.format_amount(self._credit, blank_zero=True)
    
    @property
    def balance(self):
        account_currency = self.account.currency
        return self.table.document.app.format_amount(self._the_balance(), zero_currency=account_currency)
    can_edit_balance = False
    
    @property
    def reconciled(self):
        return self._reconciled
    
    @property
    def reconciliation_date(self):
        if self._reconciliation_date is not None:
            return self.table.document.app.format_date(self._reconciliation_date)
        else:
            return ''
    
    @property
    def recurrent(self):
        return self._recurrent
    
    @property
    def is_budget(self):
        return self._is_budget
    
    
AUTOFILL_ATTRS = {'description', 'payee', 'transfer', 'increase', 'decrease'}
AMOUNT_AUTOFILL_ATTRS = {'increase', 'decrease'}

class EntryTableRow(BaseEntryTableRow):
    FIELDS = [
        ('_date', 'date'),
        ('_description', 'description'),
        ('_payee', 'payee'),
        ('_checkno', 'checkno'),
        ('_amount', 'amount'),
        ('_reconciliation_date', 'reconciliation_date'),
    ]
    def __init__(self, table, entry, account):
        BaseEntryTableRow.__init__(self, table, account)
        self.entry = entry
        # makes possible to move more code down to TransactionTableBase
        self.transaction = entry.transaction
        self.load()
    
    def _autofill_row(self, ref_row, dest_attrs):
        if len(ref_row.entry.transfer) > 1:
            dest_attrs.discard('_transfer')
        BaseEntryTableRow._autofill_row(self, ref_row, dest_attrs)
    
    def _get_autofill_attrs(self):
        return AUTOFILL_ATTRS
    
    def _get_autofill_dest_attrs(self, key_attr, all_attrs):
        dest_attrs = BaseEntryTableRow._get_autofill_dest_attrs(self, key_attr, AUTOFILL_ATTRS)
        if dest_attrs & AMOUNT_AUTOFILL_ATTRS:
            dest_attrs -= AMOUNT_AUTOFILL_ATTRS
            dest_attrs.add('amount')
        return dest_attrs
    
    def _get_autofill_rows(self):
        original = self.entry
        entries = sorted(self.account.entries, key=attrgetter('mtime'), reverse=True)
        for entry in entries:
            if entry is original:
                continue
            yield EntryTableRow(self.table, entry, self.account)
    
    def _set_amount_property(self, propname, stramount):
        try:
            currency = self.table.mainwindow.shown_account.currency
            parsed = self.table.document.app.parse_amount(stramount, default_currency=currency)
        except ValueError:
            return
        if parsed != getattr(self, propname):
            setattr(self, propname, parsed)
    
    def can_edit(self):
        return not self.is_budget
    
    def can_reconcile(self):
        inmode = self.table.reconciliation_mode
        canedit = self.can_edit()
        future = self._date > datetime.date.today()
        foreign = self._amount != 0 and self._amount.currency != self.account.currency
        balance_sheet = self.account.is_balance_sheet_account()
        return inmode and canedit and not future and not foreign and balance_sheet
    
    def load(self):
        entry = self.entry
        self._load_from_fields(entry, self.FIELDS)
        self._position = entry.transaction.position
        self._transfer = ', '.join(s.combined_display for s in entry.transfer)
        self._balance = entry.balance_with_budget
        self._reconciled_balance = entry.reconciled_balance if entry.reconciled else None
        self._reconciled = entry.reconciled
        self._recurrent = isinstance(entry.transaction, Spawn)
        self._is_budget = getattr(entry.transaction, 'is_budget', False)
    
    def save(self):
        entry = self.entry
        changed_fields = self._get_changed_fields(entry, self.FIELDS)
        if len(entry.transfer) <= 1:
            oldvalue = entry.transfer[0].combined_display if entry.transfer else ''
            if self._transfer != oldvalue:
                changed_fields['transfer'] = self._transfer
        self.table.document.change_entry(entry, **changed_fields)
        self.load()
    
    def toggle_reconciled(self):
        assert self.table.reconciliation_mode
        self.table.selected_row = self
        self.table._update_selection()
        self.table.toggle_reconciled()
    
    #--- Properties
    @BaseEntryTableRow.reconciliation_date.setter
    def reconciliation_date(self, value):
        try:
            parsed = self.table.document.app.parse_date(value)
        except ValueError:
            parsed = None
        if parsed == self._reconciliation_date:
            return
        self._edit()
        self._reconciliation_date = parsed
    
    description = rowattr('_description', 'description')
    payee = rowattr('_payee', 'payee')
    checkno = rowattr('_checkno')
    transfer = rowattr('_transfer', 'transfer')
    
    @BaseEntryTableRow.increase.setter
    def increase(self, value):
        self._set_amount_property('_increase', value)
    
    @BaseEntryTableRow.decrease.setter
    def decrease(self, value):
        self._set_amount_property('_decrease', value)
    
    @BaseEntryTableRow.debit.setter
    def debit(self, value):
        self._set_amount_property('_debit', value)
    
    @BaseEntryTableRow.credit.setter
    def credit(self, value):
        self._set_amount_property('_credit', value)
    
    @property
    def can_edit_transfer(self):
        return len(self.entry.splits) == 1
    can_edit_increase = can_edit_transfer
    can_edit_decrease = can_edit_transfer
    can_edit_debit = can_edit_transfer
    can_edit_credit = can_edit_transfer
    
    @property
    def can_edit_reconciliation_date(self):
        foreign = self._amount != 0 and self._amount.currency != self.account.currency
        return not foreign
    

class PreviousBalanceRow(BaseEntryTableRow):
    def __init__(self, table, date, balance, reconciled_balance, account):
        super(PreviousBalanceRow, self).__init__(table, account)
        self._date = date
        self._balance = balance
        self._reconciled_balance = reconciled_balance
        self._description = tr('Previous Balance')
        self._reconciled = False
        self.is_bold = True
    

class TotalRow(BaseEntryTableRow):
    def __init__(self, table, account, date, total_debit, total_credit):
        super(TotalRow, self).__init__(table, account)
        self._date = date
        self._description = tr('TOTAL')
        # don't touch _increase and _decrease, they trigger editing.
        self._debit_fmt = table.document.app.format_amount(total_debit, blank_zero=True)
        self._credit_fmt = table.document.app.format_amount(total_credit, blank_zero=True)
        delta = total_debit - total_credit
        if delta:
            if account.is_credit_account():
                delta *= -1
            positive = delta > 0
            delta_fmt = table.document.app.format_amount(abs(delta))
            delta_fmt = ('+' if positive else '-') + delta_fmt
            self._balance_fmt = delta_fmt
        else:
            self._balance_fmt = ''
        self.is_bold = True
    
    @property
    def increase(self):
        return self._credit_fmt if self.table.account.is_credit_account() else self._debit_fmt
    
    @property
    def decrease(self):
        return self._debit_fmt if self.table.account.is_credit_account() else self._credit_fmt
    
    @property
    def debit(self):
        return self._debit_fmt
    
    @property
    def credit(self):
        return self._credit_fmt
    
    @property
    def balance(self):
        return self._balance_fmt
    

class EntryTableBase(TransactionTableBase):
    ENTRY_ROWCLASS = EntryTableRow
    
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
            row = self.ENTRY_ROWCLASS(self, entry, account)
            result.append(row)
            convert = lambda a: convert_amount(a, account.currency, entry.date)
            total_debit += convert(row._debit)
            total_credit += convert(row._credit)
        if result:
            total_row = TotalRow(self, account, date_range.end, total_debit, total_credit)
            result.append(total_row)
        return result
    
    #--- Properties
    @property
    def selected_entries(self):
        return [row.entry for row in self.selected_rows if hasattr(row, 'entry')]
    
    @property
    def selected_transactions(self):
        return [entry.transaction for entry in self.selected_entries]
    