# Created By: Eric Mc Sween
# Created On: 2008-07-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import datetime
from operator import attrgetter

from ..document import FILTER_UNASSIGNED, FILTER_INCOME, FILTER_EXPENSE, FILTER_TRANSFER
from ..model.account import INCOME, EXPENSE
from ..model.amount import parse_amount, convert_amount
from ..model.recurrence import Spawn
from .base import DocumentGUIObject
from .complete import TransactionCompletionMixIn
from .table import GUITable, RowWithDebitAndCredit, RowWithDate, rowattr

class EntryTable(DocumentGUIObject, GUITable, TransactionCompletionMixIn):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        GUITable.__init__(self)
        self.account = None
        self._columns = [] # empty columns == unrestricted autofill
        self._total_increase = 0
        self._total_decrease = 0
    
    #--- Override
    def _do_add(self):
        entry = self.document.new_entry()
        for index, row in enumerate(self):
            if not isinstance(row, EntryTableRow):
                continue
            if row._date > entry.date:
                insert_index = index
                break
        else:
            insert_index = len(self)
        row = EntryTableRow(self, entry, entry.account)
        self.insert(insert_index, row)
        self.select([insert_index])
        self.document.select_transactions([entry.transaction])
        return row
    
    def _do_delete(self):
        entries = self.selected_entries()
        if entries:
            self.document.delete_entries(entries)
    
    def _is_edited_new(self):
        return self.edited.entry.transaction not in self.document.transactions
    
    def _update_selection(self):
        self.document.explicitly_select_transactions(self.selected_transactions())
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.refresh()
        self.view.refresh()
        self.view.show_selected_row()
        self.document.select_transactions(self.selected_transactions())
    
    #--- Public
    def add(self):
        if self.account is None:
            return
        GUITable.add(self)
    
    def can_edit_column(self, column):
        if column in ('date', 'description', 'payee', 'checkno', 'increase', 'decrease'):
            return self.selected_row.can_edit()
        elif column == 'transfer':
            return self.selected_row.can_edit_transfer()
        else:
            return False

    def can_move(self, row_indexes, position):
        if not GUITable.can_move(self, row_indexes, position):
            return False
        if not all(self[index].can_edit() for index in row_indexes):
            return False
        transactions = [self[index].entry.transaction for index in row_indexes]
        before = self[position - 1] if position > 0 else None
        after = self[position] if position < len(self) else None
        # before and after are rows, get the txn if it exists
        before = before.entry.transaction if hasattr(before, 'entry') else None
        after = after.entry.transaction if hasattr(after, 'entry') else None
        return self.document.can_move_transactions(transactions, before, after)
    
    def change_columns(self, columns):
        """Call this when the order or the visibility of the columns change"""
        self._columns = columns
    
    def move(self, row_indexes, to_index):
        try:
            to_row = self[to_index]
            if not hasattr(to_row, 'entry'): # adjustment
                to_row = self[to_index + 1]
            to_entry = to_row.entry
        except IndexError:
            to_entry = None
        # we can use any from_index, let's use the first
        entries = [self[index].entry for index in row_indexes]
        self.document.move_entries(entries, to_entry)
    
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
    
    def refresh(self):
        self.cancel_edits()
        selected_indexes = self.selected_indexes
        del self[:]
        account = self.document.selected_account
        if account is None:
            return
        date_range = self.document.date_range
        self.account = account
        if account.is_balance_sheet_account():
            prev_entry = self.document.previous_entry
            if prev_entry is not None:
                balance = prev_entry.balance
                rbalance = prev_entry.reconciled_balance
                self.append(PreviousBalanceRow(self, date_range.start, balance, rbalance, account))
        self._total_increase = 0
        self._total_decrease = 0
        for entry in self.document.visible_entries:
            row = EntryTableRow(self, entry, account)
            self.append(row)
            convert = lambda a: convert_amount(a, account.currency, entry.date)
            self._total_increase += convert(row._increase)
            self._total_decrease += convert(row._decrease)
        if self.document.explicitly_selected_transactions:
            self.select_transactions(self.document.explicitly_selected_transactions)
            if not self.selected_indexes:
                self.select_nearest_date(self.document.explicitly_selected_transactions[0].date)
        else:
            if not selected_indexes:
                selected_indexes = [len(self) - 1]
            self.select(selected_indexes)
    
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
    
    def selected_entries(self):
        return [row.entry for row in self.selected_rows if hasattr(row, 'entry')]
    
    def select_transactions(self, transactions):
        selected_indexes = []
        for index, row in enumerate(self):
            entry = getattr(row, 'entry', None)
            if hasattr(entry, 'transaction') and entry.transaction in transactions:
                selected_indexes.append(index)
        self.selected_indexes = selected_indexes
    
    def selected_transactions(self):
        return [entry.transaction for entry in self.selected_entries()]
    
    def should_show_balance_column(self):
        return bool(self.document.selected_account) and self.document.selected_account.is_balance_sheet_account()
    
    def toggle_reconciled(self):
        """Toggle the reconcile flag of selected entries"""
        entries = [row.entry for row in self.selected_rows if row.can_reconcile()]
        self.document.toggle_entries_reconciled(entries)
    
    #--- Properties
    @property
    def totals(self):
        shown = len(self.document.visible_entries)
        total = self.document.visible_unfiltered_entry_count
        increase = self.app.format_amount(self._total_increase)
        decrease = self.app.format_amount(self._total_decrease)
        msg = u"Showing {shown} out of {total}. Total increase: {increase} Total decrease: {decrease}"
        return msg.format(shown=shown, total=total, increase=increase, decrease=decrease)
    
    #--- Event Handlers
    def date_range_changed(self):
        date_range = self.document.date_range
        self.refresh()
        self.select_transactions(self.document.selected_transactions)
        if not self.selected_indexes:
            self.select_nearest_date(date_range.start + self._delta_before_change)
        self.view.refresh()
        self.view.show_selected_row()
        self.document.select_transactions(self.selected_transactions())
    
    def date_range_will_change(self):
        date_range = self.document.date_range
        transactions = self.selected_transactions()
        date = transactions[0].date if transactions else date_range.end
        delta = date - date_range.start
        self._delta_before_change = delta
    
    def edition_must_stop(self):
        self.view.stop_editing()
        self.save_edits()
    
    def entry_changed(self):
        self.refresh()
        self.view.refresh()
        self.view.show_selected_row()
    
    def entry_deleted(self):
        self.refresh()
        self.document.select_transactions(self.selected_transactions())
        self.view.refresh()
    
    def entries_imported(self):
        self.refresh()
        self.document.select_transactions(self.selected_transactions())
        self.view.refresh()
    
    def file_loaded(self):
        self.refresh()
        self.document.select_transactions(self.selected_transactions())
        self.view.refresh()
    
    def filter_applied(self):
        self.refresh()
        self.view.refresh()
    
    def reconciliation_changed(self):
        self.refresh()
        self.view.refresh()
    
    def redone(self):
        self.refresh()
        self.view.refresh()
        
    def undone(self):
        self.refresh()
        self.view.refresh()
    

class BaseEntryTableRow(RowWithDebitAndCredit):
    def __init__(self, table):
        super(BaseEntryTableRow, self).__init__(table)
        self._date = datetime.date.today()
        self._description = ''
        self._payee = ''
        self._checkno = ''
        self._amount = 0
        self._transfer = ''
        self._balance = 0
        self._reconciled_balance = 0
        self._reconciled = False
        self._reconciliation_pending = False
        self._recurrent = False
    
    def _the_balance(self):
        if self.table.document._in_reconciliation_mode:
            balance = self._reconciled_balance
        else:
            balance = self._balance
        if balance and self.table.document.selected_account.is_credit_account():
            balance = -balance
        return balance
    
    def can_edit(self):
        return False
    
    def can_edit_transfer(self):
        return False
    
    def can_reconcile(self):
        return False
    
    def is_balance_negative(self):
        return self._the_balance() < 0
    
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
    def balance(self):
        account_currency = self.table.account.currency
        return self.table.document.app.format_amount(self._the_balance(), zero_currency=account_currency)
    
    @property
    def read_only(self):
        return not self.can_edit()

    @property
    def reconciled(self):
        return self._reconciled
    
    @property
    def reconciliation_pending(self):
        return self._reconciliation_pending
    
    @property
    def recurrent(self):
        return self._recurrent
    
    
AUTOFILL_ATTRS = frozenset(['description', 'payee', 'transfer', 'increase', 'decrease'])
AMOUNT_AUTOFILL_ATTRS = frozenset(['increase', 'decrease'])

class EntryTableRow(RowWithDate, BaseEntryTableRow):
    def __init__(self, table, entry, account):
        super(EntryTableRow, self).__init__(table)
        self.entry = entry
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
    
    def can_edit(self):
        return True

    def can_edit_transfer(self):
        return len(self.entry.splits) == 1
    
    def can_reconcile(self):
        inmode = self.table.document._in_reconciliation_mode
        canedit = self.can_edit()
        future = self._date > datetime.date.today()
        foreign = self._amount != 0 and self._amount.currency != self.account.currency
        balance_sheet = self.account.is_balance_sheet_account()
        return inmode and canedit and not future and not foreign and balance_sheet
    
    def load(self):
        entry = self.entry
        self._date = entry.date
        self._description = entry.description
        self._payee = entry.payee
        self._checkno = entry.checkno
        self._amount = entry.amount
        self._transfer = ', '.join(s.name for s in entry.transfer)
        self._balance = entry.balance_with_budget
        self._reconciled_balance = entry.reconciled_balance if entry.reconciled or entry.reconciliation_pending else None
        self._reconciled = entry.reconciled
        self._reconciliation_pending = entry.reconciliation_pending
        self._recurrent = isinstance(entry.transaction, Spawn)
    
    def save(self):
        change = self.table.document.change_entry
        change(self.entry, date=self._date, description=self._description, payee=self._payee, 
               checkno=self._checkno, transfer=self._transfer, amount=self._amount)
        self.load()
    
    def toggle_reconciled(self):
        assert self.table.document._in_reconciliation_mode
        self.table.selected_row = self
        self.table._update_selection()
        self.table.toggle_reconciled()
    
    description = rowattr('_description', 'description')
    payee = rowattr('_payee', 'payee')
    checkno = rowattr('_checkno')
    transfer = rowattr('_transfer', 'transfer')
    
    @BaseEntryTableRow.increase.setter
    def increase(self, value):
        try:
            increase = parse_amount(value, self.table.document.selected_account.currency)
        except ValueError:
            return
        if increase == self._increase:
            return
        self._increase = increase
    
    @BaseEntryTableRow.decrease.setter
    def decrease(self, value):
        try:
            decrease = parse_amount(value, self.table.document.selected_account.currency)
        except ValueError:
            return
        if decrease == self._decrease:
            return
        self._decrease = decrease
    

class PreviousBalanceRow(BaseEntryTableRow):
    def __init__(self, table, date, balance, reconciled_balance, account):
        super(PreviousBalanceRow, self).__init__(table)
        self.account = account
        self._date = date
        self._balance = balance
        self._reconciled_balance = reconciled_balance
        self._description = 'Previous Balance'
        self._reconciled = False
        self._reconciliation_pending = False
    
