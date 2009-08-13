# Created By: Virgil Dupras
# Created On: 2009-08-11
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
from .table import GUITable, Row, rowattr
from .transaction_table import TransactionTableRow

class ScheduleTable(DocumentGUIObject, GUITable, TransactionCompletionMixIn):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        GUITable.__init__(self)
        self._columns = [] # empty columns == unrestricted autofill
    
    #--- Override
    def connect(self):
        DocumentGUIObject.connect(self)
        self.refresh()
        self.view.refresh()
    
    #--- Public
    def refresh(self):
        del self[:]
        for schedule in self.document.scheduled:
            self.append(ScheduleTableRow(self, schedule))
    
    #--- Event handlers
    def edition_must_stop(self):
        self.view.stop_editing()
        self.save_edits()
    
    def file_loaded(self):
        self.refresh()
        self.view.refresh()
    
    def redone(self):
        self.refresh()
        self.view.refresh()
    
    def undone(self):
        self.refresh()
        self.view.refresh()
    

AUTOFILL_ATTRS = frozenset(['description', 'payee', 'from', 'to', 'amount'])

class ScheduleTableRow(Row):
    def __init__(self, table, schedule):
        Row.__init__(self, table)
        self.document = table.document
        self.schedule = schedule
        self.transaction = schedule.ref
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
    
    def load(self):
        schedule = self.schedule
        txn = schedule.ref
        self._start_date = txn.date
        self._start_date_fmt = None
        self._stop_date = schedule.stop_date
        self._stop_date_fmt = None
        self._repeat_type = schedule.repeat_type
        self._interval = unicode(schedule.repeat_every)
        self._description = txn.description
        self._payee = txn.payee
        self._checkno = txn.checkno
        splits = txn.splits
        froms, tos = txn.splitted_splits()
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
    
    def save(self):
        kw = {'date': self._start_date, 'description': self._description, 'payee': self._payee,
              'checkno': self._checkno}
        if self._from_count == 1:
            kw['from_'] = self._from
        if self._to_count == 1:
            kw['to'] = self._to
        if self._from_count == self._to_count == 1:
            kw['amount'] = self._amount
        kw['repeat_type'] = self._repeat_type
        kw['repeat_every'] = int(self._interval)
        kw['stop_date'] = self._stop_date
        self.document.change_schedule(self.schedule, **kw)
    
    # The "get" part of those properies below are called *very* often, hence, the format caching
    
    @property
    def start_date(self):
        if self._start_date_fmt is None:
            self._start_date_fmt = self.table.document.app.format_date(self._start_date)
        return self._start_date_fmt
    
    @start_date.setter
    def start_date(self, value):
        parsed = self.table.document.app.parse_date(value)
        if parsed == self._start_date:
            return
        self._edit()
        self._start_date = parsed
        self._start_date_fmt = None
    
    @property
    def can_edit_start_date(self):
        return True
    
    @property
    def stop_date(self):
        if self._stop_date_fmt is None:
            if self._stop_date is None:
                self._stop_date_fmt = '--'
            else:
                self._stop_date_fmt = self.table.document.app.format_date(self._stop_date)
        return self._stop_date_fmt
    
    @stop_date.setter
    def stop_date(self, value):
        try:
            parsed = self.table.document.app.parse_date(value)
        except ValueError:
            # If the value is an invalid date, just don't set anything
            return
        if parsed == self._stop_date:
            return
        self._edit()
        self._stop_date = parsed
        self._stop_date_fmt = None
    
    @property
    def can_edit_stop_date(self):
        return True
    
    repeat_type = rowattr('_repeat_type')
    @property
    def can_edit_repeat_type(self):
        return True
    
    interval = rowattr('_interval')
    @property
    def can_edit_interval(self):
        return True
    
    description = rowattr('_description', 'description')
    @property
    def can_edit_description(self):
        return True
    
    payee = rowattr('_payee', 'payee')
    @property
    def can_edit_payee(self):
        return True
        
    checkno = rowattr('_checkno')
    @property
    def can_edit_checkno(self):
        return True
    
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
    
