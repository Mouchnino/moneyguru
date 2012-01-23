# Created By: Virgil Dupras
# Created On: 2009-08-16
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.util import first
from hscommon.gui.selectable_list import GUISelectableList
from hscommon.trans import tr

from ..exception import OperationAborted
from ..model.recurrence import Recurrence, RepeatType
from ..model.transaction import Transaction
from .transaction_panel import PanelWithTransaction

REPEAT_OPTIONS_ORDER = [RepeatType.Daily, RepeatType.Weekly, RepeatType.Monthly, RepeatType.Yearly,
    RepeatType.Weekday, RepeatType.WeekdayLast]

REPEAT_EVERY_DESCS = {
    RepeatType.Daily: tr('day'),
    RepeatType.Weekly: tr('week'),
    RepeatType.Monthly: tr('month'),
    RepeatType.Yearly: tr('year'),
    RepeatType.Weekday: tr('month'),
    RepeatType.WeekdayLast: tr('month'),
}

REPEAT_EVERY_DESCS_PLURAL = {
    RepeatType.Daily: tr('days'),
    RepeatType.Weekly: tr('weeks'),
    RepeatType.Monthly: tr('months'),
    RepeatType.Yearly: tr('years'),
    RepeatType.Weekday: tr('months'),
    RepeatType.WeekdayLast: tr('months'),
}

class RepeatTypeList(GUISelectableList):
    def __init__(self, panel):
        self.panel = panel
        GUISelectableList.__init__(self)
    
    def _update_selection(self):
        GUISelectableList._update_selection(self)
        repeat_type = REPEAT_OPTIONS_ORDER[self.selected_index]
        self.panel.repeat_type = repeat_type
    
    def refresh(self):
        descs = [self.panel.schedule.rtype2desc[rtype] for rtype in REPEAT_OPTIONS_ORDER]
        # remove empty descs
        descs = [desc for desc in descs if desc]
        self[:] = descs

class PanelWithScheduleMixIn:
    @property
    def start_date(self):
        return self.app.format_date(self.schedule.start_date)
    
    @start_date.setter
    def start_date(self, value):
        date = self.app.parse_date(value)
        if date == self.schedule.start_date:
            return
        self.schedule.start_date = date
        self.repeat_type_list.refresh()
    
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
        if self.schedule.repeat_every > 1:
            return REPEAT_EVERY_DESCS_PLURAL[self.schedule.repeat_type]
        else:
            return REPEAT_EVERY_DESCS[self.schedule.repeat_type]
    
    @property
    def repeat_type(self):
        return self.schedule.repeat_type
    
    @repeat_type.setter
    def repeat_type(self, value):
        if value == self.schedule.repeat_type:
            return
        self.schedule.repeat_type = value
        self.view.refresh_repeat_every()
    
    def create_repeat_type_list(self):
        self.repeat_type_list = RepeatTypeList(self)

class SchedulePanel(PanelWithTransaction, PanelWithScheduleMixIn):
    def __init__(self, mainwindow):
        PanelWithTransaction.__init__(self, mainwindow)
        self.create_repeat_type_list()
    
    #--- Override
    def _load(self):
        schedule = first(self.mainwindow.selected_schedules)
        self._load_schedule(schedule)
    
    def _new(self):
        self._load_schedule(Recurrence(Transaction(date.today(), amount=0), RepeatType.Monthly, 1))
    
    def _save(self):
        repeat_type = self.schedule.repeat_type
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
        self.repeat_type_list.refresh()
        self.repeat_type_list.select(REPEAT_OPTIONS_ORDER.index(schedule.repeat_type))
        self.view.refresh_repeat_every()
        self.split_table.refresh_initial()
    
