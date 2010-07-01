# Created By: Virgil Dupras
# Created On: 2009-08-16
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from hsutil.misc import first

from ..exception import OperationAborted
from ..model.recurrence import Recurrence, RepeatType
from ..model.transaction import Transaction
from ..trans import tr
from .transaction_panel import PanelWithTransaction

REPEAT_OPTIONS_ORDER = [RepeatType.Daily, RepeatType.Weekly, RepeatType.Monthly, RepeatType.Yearly,
    RepeatType.Weekday, RepeatType.WeekdayLast]

# i18n note: We don't call tr() here because these descriptions are pluralized. We call tr() on the
# final desc
REPEAT_EVERY_DESCS = {
    RepeatType.Daily: 'day',
    RepeatType.Weekly: 'week',
    RepeatType.Monthly: 'month',
    RepeatType.Yearly: 'year',
    RepeatType.Weekday: 'month',
    RepeatType.WeekdayLast: 'month',
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
        return tr(desc)
    
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
        schedule = first(self.mainwindow.selected_schedules)
        self._load_schedule(schedule)
    
    def _new(self):
        self._load_schedule(Recurrence(Transaction(date.today(), amount=0), RepeatType.Monthly, 1))
    
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
    
