# Created By: Eric Mc Sween
# Created On: 2008-07-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import datetime
from operator import attrgetter

from ..model.amount import convert_amount
from ..model.entry import Entry
from ..model.recurrence import Spawn
from ..model.transaction import Transaction
from ..trans import tr
from .column import Column
from .table import RowWithDebitAndCredit, RowWithDate, rowattr
from .transaction_table_base import TransactionTableBase

class EntryTable(TransactionTableBase):
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
    INVALIDATING_MESSAGES = TransactionTableBase.INVALIDATING_MESSAGES | set(['shown_account_changed'])
    
    def __init__(self, view, account_view):
        TransactionTableBase.__init__(self, view, account_view)
        self.account = None
        self._reconciliation_mode = False
    
    #--- Override
    def _do_add(self):
        entry = self._new_entry()
        rows = self[:-1] # ignore total row
        for index, row in enumerate(rows):
            if not isinstance(row, EntryTableRow):
                continue
            if row._date > entry.date:
                insert_index = index
                break
        else:
            insert_index = len(rows)
        row = EntryTableRow(self, entry, entry.account)
        return row, insert_index
    
    def _do_delete(self):
        entries = self.selected_entries
        if entries:
            self.document.delete_entries(entries)
    
    def _fill(self):
        account = self.mainwindow.shown_account
        if account is None:
            return
        date_range = self.document.date_range
        self.account = account
        if account.is_balance_sheet_account():
            prev_entry = self._previous_entry
            if prev_entry is not None:
                balance = prev_entry.balance
                rbalance = prev_entry.reconciled_balance
                self.header = PreviousBalanceRow(self, date_range.start, balance, rbalance, account)
        total_debit = 0
        total_credit = 0
        for entry in self.parent_view.visible_entries:
            row = EntryTableRow(self, entry, account)
            self.append(row)
            convert = lambda a: convert_amount(a, account.currency, entry.date)
            total_debit += convert(row._debit)
            total_credit += convert(row._credit)
        self.footer = TotalRow(self, date_range.end, total_debit, total_credit)
        balance_visible = account.is_balance_sheet_account()
        self.columns.set_column_visible('balance', balance_visible)
    
    def _restore_selection(self, previous_selection):
        if self.mainwindow.explicitly_selected_transactions:
            self.select_transactions(self.mainwindow.explicitly_selected_transactions)
            if not self.selected_indexes:
                self.select_nearest_date(self.mainwindow.explicitly_selected_transactions[0].date)
        TransactionTableBase._restore_selection(self, previous_selection)
    
    #--- Private
    def _new_entry(self):
        account = self.mainwindow.shown_account
        transactions = self.mainwindow.selected_transactions
        date = transactions[0].date if transactions else datetime.date.today()
        balance = 0
        reconciled_balance = 0
        balance_with_budget = 0
        previous_entry = account.entries.last_entry(date=date)
        if previous_entry:
            balance = previous_entry.balance
            reconciled_balance = previous_entry.reconciled_balance
            balance_with_budget = previous_entry.balance_with_budget
        transaction = Transaction(date, account=self.mainwindow.shown_account, amount=0)
        split = transaction.splits[0]
        entry = Entry(split, 0, balance, reconciled_balance, balance_with_budget)
        return entry
    
    @property
    def _previous_entry(self): # the entry just before the date range
        account = self.mainwindow.shown_account
        if account is None:
            return None
        date_range = self.document.date_range
        prev_entries = [entry for entry in account.entries if entry.date < date_range.start]
        return prev_entries[-1] if prev_entries else None
    
    #--- Public
    def add(self):
        if self.account is None:
            return
        TransactionTableBase.add(self)
    
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
    
    @property
    def selected_entries(self):
        return [row.entry for row in self.selected_rows if hasattr(row, 'entry')]
    
    @property
    def selected_transactions(self):
        return [entry.transaction for entry in self.selected_entries]
    
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
        TransactionTableBase.transaction_changed(self)
        # It's possible that because of the change, the selected txn has been removed, so we have
        # to update document selection.
        self._update_selection()
    
    def transactions_imported(self):
        self.refresh_and_restore_selection()

class BaseEntryTableRow(RowWithDebitAndCredit):
    def __init__(self, table):
        super(BaseEntryTableRow, self).__init__(table)
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
        if self.table.reconciliation_mode:
            balance = self._reconciled_balance
        else:
            balance = self._balance
        if balance and self.table.mainwindow.shown_account.is_credit_account():
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
            return RowWithDebitAndCredit.sort_key_for_column(self, column_name)
    
    #--- Properties
    @property
    def date(self):
        return self.table.document.app.format_date(self._date)
    
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
        account_currency = self.table.account.currency
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
    
    
AUTOFILL_ATTRS = frozenset(['description', 'payee', 'transfer', 'increase', 'decrease'])
AMOUNT_AUTOFILL_ATTRS = frozenset(['increase', 'decrease'])

class EntryTableRow(RowWithDate, BaseEntryTableRow):
    def __init__(self, table, entry, account):
        super(EntryTableRow, self).__init__(table)
        self.entry = entry
        # makes possible to move more code down to TransactionTableBase
        self.transaction = entry.transaction
        self.account = account
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
        self._date = entry.date
        self._position = entry.transaction.position
        self._description = entry.description
        self._payee = entry.payee
        self._checkno = entry.checkno
        self._amount = entry.amount
        self._transfer = ', '.join(s.combined_display for s in entry.transfer)
        self._balance = entry.balance_with_budget
        self._reconciled_balance = entry.reconciled_balance if entry.reconciled else None
        self._reconciled = entry.reconciled
        self._reconciliation_date = entry.reconciliation_date
        self._recurrent = isinstance(entry.transaction, Spawn)
        self._is_budget = getattr(entry.transaction, 'is_budget', False)
    
    def save(self):
        change = self.table.document.change_entry
        change(self.entry, date=self._date, reconciliation_date=self._reconciliation_date, 
            description=self._description, payee=self._payee, checkno=self._checkno,
            transfer=self._transfer, amount=self._amount)
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

class PreviousBalanceRow(BaseEntryTableRow):
    def __init__(self, table, date, balance, reconciled_balance, account):
        super(PreviousBalanceRow, self).__init__(table)
        self.account = account
        self._date = date
        self._balance = balance
        self._reconciled_balance = reconciled_balance
        self._description = tr('Previous Balance')
        self._reconciled = False
        self.is_bold = True
    

class TotalRow(BaseEntryTableRow):
    def __init__(self, table, date, total_debit, total_credit):
        super(TotalRow, self).__init__(table)
        self._date = date
        self._description = tr('TOTAL')
        # don't touch _increase and _decrease, they trigger editing.
        self._debit_fmt = table.document.app.format_amount(total_debit, blank_zero=True)
        self._credit_fmt = table.document.app.format_amount(total_credit, blank_zero=True)
        delta = total_debit - total_credit
        if delta:
            if self.table.account.is_credit_account():
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
    

