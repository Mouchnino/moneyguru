# Created By: Virgil Dupras
# Created On: 2008-09-13
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import copy
import datetime
from calendar import monthrange
from itertools import chain

from hscommon.util import nonone
from hscommon.trans import tr

from .date import (inc_day, inc_week, inc_month, inc_year, inc_weekday_in_month,
    inc_last_weekday_in_month, strftime)
from .transaction import Transaction

class RepeatType:
    Daily = 'daily'
    Weekly = 'weekly'
    Monthly = 'monthly'
    Yearly = 'yearly'
    Weekday = 'weekday'
    WeekdayLast = 'weekday_last'

RTYPE2INCFUNC = {
    RepeatType.Daily: inc_day,
    RepeatType.Weekly: inc_week,
    RepeatType.Monthly: inc_month,
    RepeatType.Yearly: inc_year,
    RepeatType.Weekday: inc_weekday_in_month,
    RepeatType.WeekdayLast: inc_last_weekday_in_month,
}

ONE_DAY = datetime.timedelta(1)

class DateCounter:
    def __init__(self, base_date, repeat_type, repeat_every, end):
        self.base_date = base_date
        self.end = end
        self.inccount = 0
        self.incfunc = RTYPE2INCFUNC[repeat_type]
        self.incsize = repeat_every
        self.current_date = None
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current_date is None: # first date of the iteration is base_date
            self.current_date = self.base_date
            return self.current_date
        new_date = None
        while new_date is None:
            self.inccount += self.incsize
            new_date = self.incfunc(self.base_date, self.inccount)
        if new_date <= self.current_date or new_date > self.end:
            raise StopIteration()
        self.current_date = new_date
        return new_date
    

class Spawn(Transaction):
    def __init__(self, recurrence, ref, recurrence_date, date=None):
        date = date or recurrence_date
        Transaction.__init__(self, date, ref.description, ref.payee, ref.checkno)
        self.recurrence_date = recurrence_date
        self.ref = ref
        self.recurrence = recurrence
        self.set_splits(ref.splits)
        for split in self.splits:
            split.reconciliation_date = None
        self.balance()
    

class Recurrence:
    def __init__(self, ref, repeat_type, repeat_every):
        if repeat_type not in RTYPE2INCFUNC:
            # invalid repeat type, default to monthly
            repeat_type = RepeatType.Monthly
        self.ref = ref
        self._repeat_type = repeat_type
        self._repeat_every = repeat_every
        self.stop_date = None
        self.date2exception = {}
        self.date2globalchange = {}
        self.date2instances = {}
        self.rtype2desc = {
            RepeatType.Daily: tr('Daily'),
            RepeatType.Weekly: tr('Weekly'),
            RepeatType.Monthly: tr('Monthly'),
            RepeatType.Yearly: tr('Yearly'),
            RepeatType.Weekday: '', # dynamic
            RepeatType.WeekdayLast: '', # dynamic
        }
        self._update_rtype_descs()
    
    def __repr__(self):
        return '<Recurrence %s %d>' % (self.repeat_type, self.repeat_every)
    
    #--- Private
    def _all_exceptions(self):
        exceptions = chain(self.date2exception.values(), self.date2globalchange.values())
        return (e for e in exceptions if e is not None)
    
    def _create_spawn(self, ref, date):
        return Spawn(self, ref, date)
    
    def _update_ref(self):
        # Go through our recurrence dates and see if we should either move our start date due to
        # deleted spawns or to update or ref transaction due to a global change that end up being
        # on our first recurrence date.
        date_counter = DateCounter(self.start_date, self.repeat_type, self.repeat_every, datetime.date.max)
        for d in date_counter:
            if d in self.date2exception and self.date2exception[d] is None:
                continue
            if d in self.date2globalchange:
                self.ref = self.date2globalchange[d].replicate()
            else:
                self.ref.date = d
            break
        self.date2exception = {d: ex for d, ex in self.date2exception.items() if d > self.start_date}
        self.date2globalchange = {d: ex for d, ex in self.date2globalchange.items() if d > self.start_date}
        self.reset_spawn_cache()
        self._update_rtype_descs()
    
    def _update_rtype_descs(self):
        date = self.start_date
        weekday_name = strftime('%A', date)
        week_no = (date.day - 1) // 7
        position = [tr('first'), tr('second'), tr('third'), tr('fourth'), tr('fifth')][week_no]
        self.rtype2desc[RepeatType.Weekday] = tr('Every %s %s of the month') % (position, weekday_name)
        _, days_in_month = monthrange(date.year, date.month)
        if days_in_month - date.day < 7:
            self.rtype2desc[RepeatType.WeekdayLast] = tr('Every last %s of the month') % weekday_name
        else:
            self.rtype2desc[RepeatType.WeekdayLast] = ''
    
    #--- Public
    def add_exception(self, spawn):
        self.date2exception[spawn.recurrence_date] = spawn
    
    def affected_accounts(self):
        result = self.ref.affected_accounts()
        for exception in self._all_exceptions():
            result |= exception.affected_accounts()
        return result
    
    def change_globally(self, spawn):
        for date in list(self.date2globalchange.keys()):
            if date >= spawn.recurrence_date:
                del self.date2globalchange[date]
        for date, exception in list(self.date2exception.items()):
            # we don't want to remove local deletions
            if exception is not None and date >= spawn.recurrence_date:
                del self.date2exception[date]
        self.date2globalchange[spawn.recurrence_date] = spawn
        self.date2exception[spawn.recurrence_date] = spawn
        self._update_ref()
    
    def delete(self, spawn):
        self.delete_at(spawn.recurrence_date)
    
    def delete_at(self, date):
        self.date2exception[date] = None
        self._update_ref()
    
    def get_spawns(self, end):
        # END DATE ADJUSTMENT
        # if a changed date end up being smaller than the "spawn date", it's possible that a spawn
        # that should have been spawned for the date range is not spawned. Therefore, we always
        # spawn at least until the date of the last exception. For global changes, it's even more
        # complicated. If the global date delta is negative enough, we can end up with a spawn that
        # doesn't go far enough, so we must adjust our max date by this delta.
        if self.date2exception:
            end = max(end, max(self.date2exception.keys()))
        if self.date2globalchange:
            min_date_delta = min(ref.date-date for date, ref in self.date2globalchange.items())
            if min_date_delta < datetime.timedelta(days=0):
                end += -min_date_delta
        end = min(end, nonone(self.stop_date, datetime.date.max))
        
        date_counter = DateCounter(self.start_date, self.repeat_type, self.repeat_every, end)
        result = []
        global_date_delta = datetime.timedelta(days=0)
        current_ref = self.ref
        for current_date in date_counter:
            if current_date in self.date2globalchange:
                current_ref = self.date2globalchange[current_date]
                global_date_delta = current_ref.date - current_date
            if current_date in self.date2exception:
                exception = self.date2exception[current_date]
                if exception is not None:
                    result.append(exception)
            else:
                if current_date not in self.date2instances:
                    spawn = self._create_spawn(current_ref, current_date)
                    if global_date_delta:
                        # Only muck with spawn.date if we have a delta. otherwise we're breaking
                        # budgets.
                        spawn.date = current_date + global_date_delta
                    self.date2instances[current_date] = spawn
                result.append(self.date2instances[current_date])
        return result
    
    def reassign_account(self, account, reassign_to=None):
        self.ref.reassign_account(account, reassign_to)
        for exception in self._all_exceptions():
            exception.reassign_account(account, reassign_to)
        self.reset_spawn_cache()
    
    def replicate(self):
        result = copy.copy(self)
        result.date2exception = copy.copy(self.date2exception)
        result.date2globalchange = copy.copy(self.date2globalchange)
        result.date2instances = {}
        result.ref = self.ref.replicate()
        return result
    
    def reset_exceptions(self):
        self.date2exception = {}
        self.date2globalchange = {}
    
    def reset_spawn_cache(self):
        self.date2instances = {}
    
    def stop_at(self, spawn):
        self.stop_date = spawn.recurrence_date
    
    def stop_before(self, spawn):
        self.stop_date = spawn.recurrence_date - ONE_DAY
    
    #--- Properties
    @property
    def is_alive(self):
        """Returns whether get_spawns() can ever return anything given the start and stop date"""
        if self.stop_date is None:
            return True
        return bool(self.get_spawns(self.stop_date))
    
    @property
    def repeat_every(self):
        return self._repeat_every
    
    @repeat_every.setter
    def repeat_every(self, value):
        if value == self._repeat_every:
            return
        self._repeat_every = value
        self.reset_exceptions()
    
    @property
    def repeat_type(self):
        return self._repeat_type
    
    @repeat_type.setter
    def repeat_type(self, value):
        if value == self._repeat_type:
            return
        self._repeat_type = value
        self.reset_exceptions()
    
    @property
    def repeat_type_desc(self):
        return self.rtype2desc[self._repeat_type]
    
    @property
    def start_date(self):
        return self.ref.date
    
    @start_date.setter
    def start_date(self, value):
        if value == self.ref.date:
            return
        self.ref.date = value
        self.reset_exceptions()
        self._update_rtype_descs()
    
