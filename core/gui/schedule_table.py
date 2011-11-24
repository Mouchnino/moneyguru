# Created By: Virgil Dupras
# Created On: 2009-08-11
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import datetime

from hscommon.trans import trget, tr
from ..model.amount import convert_amount
from .column import Column
from .table import GUITable, Row, rowattr

trcol = trget('columns')

class ScheduleTable(GUITable):
    SAVENAME = 'ScheduleTable'
    COLUMNS = [
        Column('start_date', display=trcol('Start Date')),
        Column('stop_date', display=trcol('Stop Date')),
        Column('repeat_type', display=trcol('Repeat Type')),
        Column('interval', display=trcol('Interval')),
        Column('checkno', display=trcol('Description'), visible=False, optional=True),
        Column('description', display=trcol('Payee'), optional=True),
        Column('payee', display=trcol('Check #'), visible=False, optional=True),
        Column('from', display=trcol('From')),
        Column('to', display=trcol('To')),
        Column('amount', display=trcol('Amount')),
    ]
    
    def __init__(self, schedule_view):
        GUITable.__init__(self, document=schedule_view.document)
        self.mainwindow = schedule_view.mainwindow
    
    #--- Override
    def _update_selection(self):
        self.mainwindow.selected_schedules = self.selected_schedules
    
    def _fill(self):
        for schedule in self.document.schedules:
            self.append(ScheduleTableRow(self, schedule))
    
    #--- Public
    def delete(self):
        self.document.delete_schedules(self.selected_schedules)
    
    def edit(self):
        self.mainwindow.edit_item()
    
    #--- Properties
    @property
    def selected_schedules(self):
        return [row.schedule for row in self.selected_rows]
    
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
        self._interval = str(schedule.repeat_every)
        self._description = txn.description
        self._payee = txn.payee
        self._checkno = txn.checkno
        splits = txn.splits
        froms, tos = txn.splitted_splits()
        self._from_count = len(froms)
        self._to_count = len(tos)
        UNASSIGNED = tr('Unassigned') if len(froms) > 1 else ''
        self._from = ', '.join(s.account.name if s.account is not None else UNASSIGNED for s in froms)
        UNASSIGNED = tr('Unassigned') if len(tos) > 1 else ''
        self._to = ', '.join(s.account.name if s.account is not None else UNASSIGNED for s in tos)
        try:
            self._amount = sum(s.amount for s in tos)
        except ValueError: # currency coercing problem
            currency = self.document.default_currency
            self._amount = sum(convert_amount(s.amount, currency, s.transaction.date) for s in tos)
        self._amount_fmt = self.document.format_amount(self._amount)
    
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
