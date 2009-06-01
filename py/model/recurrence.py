# Unit Name: moneyguru.model.recurrence
# Created By: Virgil Dupras
# Created On: 2008-09-13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import copy
from datetime import date, timedelta

from hsutil.misc import nonone

from ..const import (REPEAT_NEVER, REPEAT_DAILY, REPEAT_WEEKLY, REPEAT_MONTHLY, REPEAT_YEARLY, 
    REPEAT_WEEKDAY, REPEAT_WEEKDAY_LAST)
from .date import (inc_day, inc_week, inc_month, inc_year, inc_weekday_in_month,
    inc_last_weekday_in_month)
from .transaction import Transaction

RTYPE2INCFUNC = {
    REPEAT_DAILY: inc_day,
    REPEAT_WEEKLY: inc_week,
    REPEAT_MONTHLY: inc_month,
    REPEAT_YEARLY: inc_year,
    REPEAT_WEEKDAY: inc_weekday_in_month,
    REPEAT_WEEKDAY_LAST: inc_last_weekday_in_month,
}

class Spawn(Transaction):
    def __init__(self, recurrence, ref, recurrence_date, date=None):
        date = date or recurrence_date
        Transaction.__init__(self, date, ref.description, ref.payee, ref.checkno)
        self.recurrence_date = recurrence_date
        self.ref = ref
        self.recurrence = recurrence
        self.set_splits(ref.splits)
        for split in self.splits:
            split.reconciled = False
    
class Recurrence(object):
    def __init__(self, ref, repeat_type, repeat_every, include_first=False):
        self.ref = ref
        self.repeat_type = repeat_type
        self.repeat_every = repeat_every
        self.stop_date = None
        self.date2exception = {}
        self.date2globalchange = {}
        self.date2instances = {}
        if not include_first:
            self.date2exception[ref.date] = None
    
    def __eq__(self, other): # eq only checks repeat_type and repeat_every, not ref
        if other is None:
            return False
        return self.repeat_type == other.repeat_type and self.repeat_every == other.repeat_every
    
    def __ne__(self, other):
        return not self == other
    
    def __repr__(self):
        return '<Recurrence %s %d>' % (self.repeat_type, self.repeat_every)
    
    def add_exception(self, spawn):
        self.date2exception[spawn.recurrence_date] = spawn
    
    def change_globally(self, spawn):
        for date in self.date2globalchange.keys():
            if date >= spawn.recurrence_date:
                del self.date2globalchange[date]
        for date, exception in self.date2exception.items():
            # we don't want to remove local deletions
            if exception is not None and date >= spawn.recurrence_date:
                del self.date2exception[date]
        self.date2globalchange[spawn.recurrence_date] = spawn
        self.date2exception[spawn.recurrence_date] = spawn
        self.date2instances = {}
    
    def delete(self, spawn):
        self.date2exception[spawn.recurrence_date] = None
    
    def get_spawns(self, end):
        # if a changed date end up being smaller than the "spawn date", it's possible that a spawn
        # that should have been spawned for the date range is not spawned. Therefore, we always
        # spawn at least until the date of the last exception or global change.
        changed_dates = self.date2exception.keys() + self.date2globalchange.keys()
        if changed_dates:
            end = max(end, max(changed_dates))
        end = min(end, nonone(self.stop_date, date.max))
        rtype = self.repeat_type
        incsize = self.repeat_every
        assert rtype is not REPEAT_NEVER
        if rtype in (REPEAT_WEEKDAY, REPEAT_WEEKDAY_LAST):
            incsize = 1
        result = []
        base_date = self.ref.date
        current_ref = self.ref
        current_date = base_date
        inccount = 0
        incfunc = RTYPE2INCFUNC[rtype]
        while True:
            if current_date in self.date2globalchange:
                current_ref = self.date2globalchange[current_date]
            if current_date in self.date2exception:
                exception = self.date2exception[current_date]
                if exception is not None:
                    result.append(exception)
            else:
                if current_date not in self.date2instances:
                    self.date2instances[current_date] = Spawn(self, current_ref, current_date)
                result.append(self.date2instances[current_date])
            new_date = None
            while new_date is None:
                inccount += incsize
                new_date = incfunc(base_date, inccount)
            if new_date <= current_date or new_date > end:
                break
            current_date = new_date
        return result
    
    def replicate(self):
        result = copy.copy(self)
        result.date2exception = copy.copy(self.date2exception)
        result.date2globalchange = copy.copy(self.date2globalchange)
        result.date2instances = {}
        return result
    
    def stop_at(self, spawn):
        self.stop_date = spawn.recurrence_date
    
    def stop_before(self, spawn):
        self.stop_date = spawn.recurrence_date - timedelta(1)
    
    @property
    def is_alive(self):
        """Returns whether get_spawns() can ever return anything given the start and stop date"""
        if self.stop_date is None:
            return True
        return bool(self.get_spawns(self.stop_date))
    
