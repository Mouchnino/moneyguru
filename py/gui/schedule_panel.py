# Created By: Virgil Dupras
# Created On: 2009-08-16
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from ..const import (REPEAT_DAILY, REPEAT_WEEKLY, REPEAT_MONTHLY, REPEAT_YEARLY, REPEAT_WEEKDAY, 
                     REPEAT_WEEKDAY_LAST)
from ..exception import OperationAborted
from ..model.recurrence import Recurrence
from ..model.transaction import Transaction
from .transaction_panel import PanelWithTransaction

REPEAT_OPTIONS_ORDER = [REPEAT_DAILY, REPEAT_WEEKLY, REPEAT_MONTHLY, REPEAT_YEARLY, REPEAT_WEEKDAY,
                        REPEAT_WEEKDAY_LAST]
REPEAT_EVERY_DESCS = {
    REPEAT_DAILY: 'day',
    REPEAT_WEEKLY: 'week',
    REPEAT_MONTHLY: 'month',
    REPEAT_YEARLY: 'year',
    REPEAT_WEEKDAY: 'month',
    REPEAT_WEEKDAY_LAST: 'month',
}

class PanelWithScheduleMixIn(object):
    @property
    def start_date(self):
        return self.app.format_date(self.schedule.start_date)
    
    @start_date.setter
    def start_date(self, value):
        date = self.app.parse_date(value)
        if date == self.schedule.start_date:
            return
        self.schedule.start_date = date
        self.view.refresh_repeat_options()
    
    @property
    def stop_date(self):
        if self.schedule.stop_date is None:
            return ''
        return self.app.format_date(self.schedule.stop_date)
    
    @stop_date.setter
    def stop_date(self, value):
        try:
            self.schedule.stop_date = self.app.parse_date(value)
        except (ValueError, TypeError):
            self.schedule.stop_date = None
    
    @property
    def repeat_every(self):
        return self.schedule.repeat_every
    
    @repeat_every.setter
    def repeat_every(self, value):
        value = max(1, value)
        self.schedule.repeat_every = value
        self.view.refresh_repeat_every()
    
    @property
    def repeat_every_desc(self):
        repeat_option = REPEAT_OPTIONS_ORDER[self._repeat_type_index]
        desc = REPEAT_EVERY_DESCS[repeat_option]
        if desc and self.schedule.repeat_every > 1:
            desc += 's'
        return desc
    
    @property
    def repeat_options(self):
        descs = [self.schedule.rtype2desc[rtype] for rtype in REPEAT_OPTIONS_ORDER]
        # remove empty descs
        descs = [desc for desc in descs if desc]
        return descs
    
    @property
    def repeat_type_index(self):
        return self._repeat_type_index
    
    @repeat_type_index.setter
    def repeat_type_index(self, value):
        if value == self._repeat_type_index:
            return
        self._repeat_type_index = value
        self.view.refresh_repeat_every()
    

class SchedulePanel(PanelWithTransaction, PanelWithScheduleMixIn):
    #--- Override
    def _load(self):
        self._load_schedule(self.document.selected_schedule)
    
    def _new(self):
        self._load_schedule(Recurrence(Transaction(date.today()), REPEAT_MONTHLY, 1))
    
    def _save(self):
        repeat_type = REPEAT_OPTIONS_ORDER[self.repeat_type_index]
        repeat_every = self.schedule.repeat_every
        stop_date = self.schedule.stop_date
        self.document.change_schedule(self.original, self.transaction, repeat_type=repeat_type,
                                      repeat_every=repeat_every, stop_date=stop_date)
    
    #--- Private
    def _load_schedule(self, schedule):
        if schedule is None:
            raise OperationAborted()
        self.original = schedule
        self.schedule = schedule.replicate()
        self.transaction = self.schedule.ref
        self._repeat_type_index = REPEAT_OPTIONS_ORDER.index(schedule.repeat_type)
        self.view.refresh_repeat_options()
        self.view.refresh_repeat_every()
        self.notify('panel_loaded')
    
