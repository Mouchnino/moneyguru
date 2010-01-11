# Created By: Virgil Dupras
# Created On: 2008-07-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from operator import attrgetter

from ..model.amount import convert_amount
from ..model.recurrence import Spawn
from .table import Row, RowWithDate, rowattr
from .transaction_table_base import TransactionTableBase

class TransactionTable(TransactionTableBase):
    #--- Override
    def _do_add(self):
        transaction = self.document.new_transaction()
        for index, row in enumerate(self):
            if row._date > transaction.date:
                insert_index = index
                break
        else:
            insert_index = len(self)
        row = TransactionTableRow(self, transaction)
        self.insert(insert_index, row)
        self.select([insert_index])
        return row
    
    def _do_delete(self):
        transactions = self.selected_transactions
        if transactions:
            self.document.delete_transactions(transactions)
    
    def _fill(self):
        for transaction in self.document.visible_transactions:
            self.append(TransactionTableRow(self, transaction))
        if self.document.explicitly_selected_transactions:
            self.select_transactions(self.document.explicitly_selected_transactions)
    
    #--- Private
    def _show_account(self, use_to_column=False):
        # if `use_to_column` is True, use the To column, else, use the From column
        if not self.selected_transactions:
            return
        txn = self.selected_transactions[0]
        froms, tos = txn.splitted_splits()
        splits = tos if use_to_column else froms
        account_to_show = splits[0].account
        self.document.show_account(account_to_show)
    
    #--- Public
    def select_transactions(self, transactions):
        TransactionTableBase.select_transactions(self, transactions)
        if self and not self.selected_indexes:
            self.selected_indexes = [len(self) - 1]
    
    def show_from_account(self):
        self._show_account(use_to_column=False)
    
    def show_to_account(self):
        self._show_account(use_to_column=True)
    
    #--- Properties
    @property
    def selected_transactions(self):
        return [row.transaction for row in self.selected_rows]
    
    #--- Event handlers
    def date_range_changed(self):
        self.refresh()
        self._update_selection()
        self.view.refresh()
        self.view.show_selected_row()
    
    def transactions_imported(self):
        self.refresh()
        self._update_selection()
        self.view.refresh()
    

AUTOFILL_ATTRS = frozenset(['description', 'payee', 'from', 'to', 'amount'])

class TransactionTableRow(RowWithDate):
    def __init__(self, table, transaction):
        super(TransactionTableRow, self).__init__(table)
        self.document = table.document
        self.transaction = transaction
        self.load()
    
    def _autofill_row(self, ref_row, dest_attrs):
        self._amount_fmt = None
        if len(ref_row.transaction.splits) > 2:
            dest_attrs.discard('_from')
            dest_attrs.discard('_to')
        Row._autofill_row(self, ref_row, dest_attrs)
    
    def _get_autofill_attrs(self):
        return AUTOFILL_ATTRS
    
    def _get_autofill_rows(self):
        original = self.transaction
        transactions = sorted(self.document.transactions, key=attrgetter('mtime'), reverse=True)
        for transaction in transactions:
            if transaction is original:
                continue
            yield TransactionTableRow(self.table, transaction)
    
    #--- Public
    def can_edit(self):
        return not self.is_budget
    
    def load(self):
        transaction = self.transaction
        self._date = self.transaction.date
        self._date_fmt = None
        self._position = transaction.position
        self._description = self.transaction.description
        self._payee = self.transaction.payee
        self._checkno = self.transaction.checkno
        splits = transaction.splits
        froms, tos = self.transaction.splitted_splits()
        self._from_count = len(froms)
        self._to_count = len(tos)
        UNASSIGNED = 'Unassigned' if len(froms) > 1 else ''
        get_display = lambda s: s.account.combined_display if s.account is not None else UNASSIGNED
        self._from = ', '.join(map(get_display, froms))
        UNASSIGNED = 'Unassigned' if len(tos) > 1 else ''
        get_display = lambda s: s.account.combined_display if s.account is not None else UNASSIGNED
        self._to = ', '.join(map(get_display, tos))
        try:
            self._amount = sum(s.amount for s in tos)
        except ValueError: # currency coercing problem
            currency = self.document.app.default_currency
            self._amount = sum(convert_amount(s.amount, currency, transaction.date) for s in tos)
        self._amount_fmt = None
        self._recurrent = isinstance(transaction, Spawn)
        self._reconciled = any(split.reconciled for split in splits)
        self._is_budget = getattr(transaction, 'is_budget', False)
    
    def save(self):
        kw = {'date': self._date, 'description': self._description, 'payee': self._payee,
              'checkno': self._checkno}
        if self._from_count == 1:
            kw['from_'] = self._from
        if self._to_count == 1:
            kw['to'] = self._to
        if self._from_count == self._to_count == 1:
            kw['amount'] = self._amount
        self.document.change_transactions([self.transaction], **kw)
        self.load()
    
    def sort_key_for_column(self, column_name):
        if column_name == 'date':
            return (self._date, self._position)
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
            return RowWithDate.sort_key_for_column(self, column_name)
    
    #--- Properties
    # The "get" part of those properies below are called *very* often, hence, the format caching
    
    description = rowattr('_description', 'description')
    payee = rowattr('_payee', 'payee')
    checkno = rowattr('_checkno')
    from_ = rowattr('_from', 'from')
    @property
    def can_edit_from(self):
        return self._from_count == 1
    
    to = rowattr('_to', 'to')
    @property
    def can_edit_to(self):
        return self._to_count == 1
    
    @property
    def can_edit_amount(self):
        return self._from_count == self._to_count == 1
    
    @property
    def amount(self):
        if self._amount_fmt is None:
            self._amount_fmt = self.document.app.format_amount(self._amount)
        return self._amount_fmt
    
    @amount.setter
    def amount(self, value):
        self._edit()
        try:
            self._amount = self.document.app.parse_amount(value)
        except ValueError:
            return
        self._amount_fmt = None
    
    @property
    def reconciled(self):
        return self._reconciled
    
    @property
    def recurrent(self):
        return self._recurrent
    
    @property
    def is_budget(self):
        return self._is_budget
    
