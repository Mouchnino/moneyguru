# Created By: Virgil Dupras
# Created On: 2009-08-11
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import datetime

from ..model.amount import convert_amount
from .base import DocumentGUIObject
from .table import GUITable, Row, rowattr

class ScheduleTable(GUITable, DocumentGUIObject):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        GUITable.__init__(self)
    
    #--- Override
    def _update_selection(self):
        self.document.select_schedules(self.selected_schedules)
    
    def _fill(self):
        for schedule in self.document.schedules:
            self.append(ScheduleTableRow(self, schedule))
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.refresh()
        self.view.refresh()
    
    #--- Public
    def delete(self):
        self.document.delete_schedules(self.selected_schedules)
    
    # This is a temporary workaround so that double-clicks and pressing return works in the sctable
    def edit(self):
        self.document.edit_selected()
    
    #--- Properties
    @property
    def selected_schedules(self):
        return [row.schedule for row in self.selected_rows]
    
    #--- Event handlers
    def edition_must_stop(self):
        pass # the view doesn't have a stop_editing method
    
    schedule_changed = GUITable._item_changed
    schedule_deleted = GUITable._item_deleted

class ScheduleTableRow(Row):
    def __init__(self, table, schedule):
        Row.__init__(self, table)
        self.document = table.document
        self.schedule = schedule
        self.transaction = schedule.ref
        self.load()
    
    #--- Public
    def load(self):
        schedule = self.schedule
        txn = schedule.ref
        self._start_date = txn.date
        self._start_date_fmt = self.table.document.app.format_date(self._start_date)
        self._stop_date = schedule.stop_date
        self._stop_date_fmt = self.table.document.app.format_date(self._stop_date) if self._stop_date is not None else ''
        self._repeat_type = schedule.repeat_type_desc
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
            self._amount = sum(convert_amount(s.amount, currency, s.transaction.date) for s in tos)
        self._amount_fmt = self.document.app.format_amount(self._amount)
    
    def save(self):
        pass # read-only
    
    def sort_key_for_column(self, column_name):
        if column_name == 'stop_date' and self._stop_date is None:
            return datetime.date.min
        else:
            return Row.sort_key_for_column(self, column_name)
    
    #--- Properties
    start_date = rowattr('_start_date_fmt')
    stop_date = rowattr('_stop_date_fmt')
    repeat_type = rowattr('_repeat_type')
    interval = rowattr('_interval')
    description = rowattr('_description')
    payee = rowattr('_payee')
    checkno = rowattr('_checkno')
    from_ = rowattr('_from')
    to = rowattr('_to')
    amount = rowattr('_amount_fmt')
