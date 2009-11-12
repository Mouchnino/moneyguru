# Created By: Virgil Dupras
# Created On: 2008-07-11
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from operator import attrgetter

from ..model.amount import convert_amount
from ..model.recurrence import Spawn
from .base import DocumentGUIObject
from .complete import TransactionCompletionMixIn
from .table import GUITable, Row, RowWithDate, rowattr

class TransactionTable(GUITable, DocumentGUIObject, TransactionCompletionMixIn):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        GUITable.__init__(self)
        self._columns = [] # empty columns == unrestricted autofill
    
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
    
    def _is_edited_new(self):
        return self.edited.transaction not in self.document.transactions
    
    def _update_selection(self):
        self.document.explicitly_select_transactions(self.selected_transactions)
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.refresh()
        self.document.select_transactions(self.selected_transactions)
        self.view.refresh()
        self.view.show_selected_row()
    
    #--- Public
    def can_move(self, row_indexes, position):
        if not GUITable.can_move(self, row_indexes, position):
            return False
        transactions = [self[index].transaction for index in row_indexes]
        before = self[position - 1].transaction if position > 0 else None
        after = self[position].transaction if position < len(self) else None
        return self.document.can_move_transactions(transactions, before, after)
    
    def change_columns(self, columns):
        """Call this when the order or the visibility of the columns change"""
        self._columns = columns
    
    def move(self, row_indexes, to_index):
        try:
            to_row = self[to_index]
            to_transaction = to_row.transaction
        except IndexError:
            to_transaction = None
        # we can use any from_index, let's use the first
        transactions = [self[index].transaction for index in row_indexes]
        self.document.move_transactions(transactions, to_transaction)
    
    def move_down(self):
        if len(self.selected_indexes) != 1:
            return
        position = self.selected_indexes[0] + 2
        if self.can_move(self.selected_indexes, position):
            self.move(self.selected_indexes, position)

    def move_up(self):
        if len(self.selected_indexes) != 1:
            return
        position = self.selected_indexes[0] - 1
        if self.can_move(self.selected_indexes, position):
            self.move(self.selected_indexes, position)
    
    def select_transactions(self, transactions):
        self.selected_indexes = []
        for index, row in enumerate(self):
            if row.transaction in transactions:
                self.selected_indexes.append(index)
        if self and not self.selected_indexes:
            self.selected_indexes = [len(self) - 1]
    
    #--- Event handlers
    def date_range_changed(self):
        self.refresh()
        self._update_selection()
        self.view.refresh()
        self.view.show_selected_row()
    
    def filter_applied(self):
        self.refresh()
        self.view.refresh()
    
    transaction_changed = GUITable._item_changed
    transaction_deleted = GUITable._item_deleted
    
    def transactions_imported(self):
        self.refresh()
        self._update_selection()
        self.view.refresh()
    
    #--- Properties
    @property
    def selected_transactions(self):
        return [row.transaction for row in self.selected_rows]
    
    @property
    def totals(self):
        shown = len(self)
        total = self.document.visible_unfiltered_transaction_count
        msg = u"Showing {0} out of {1}."
        return msg.format(shown, total)
    

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
    
    def can_edit(self):
        return not self.is_budget
    
    def load(self):
        transaction = self.transaction
        self._date = self.transaction.date
        self._date_fmt = None
        self._description = self.transaction.description
        self._payee = self.transaction.payee
        self._checkno = self.transaction.checkno
        splits = transaction.splits
        froms, tos = self.transaction.splitted_splits()
        self._from_count = len(froms)
        self._to_count = len(tos)
        UNASSIGNED = 'Unassigned' if len(froms) > 1 else ''
        self._from = ', '.join(s.account.name if s.account is not None else UNASSIGNED for s in froms)
        UNASSIGNED = 'Unassigned' if len(tos) > 1 else ''
        self._to = ', '.join(s.account.name if s.account is not None else UNASSIGNED for s in tos)
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
    
