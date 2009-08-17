# Created By: Virgil Dupras
# Created On: 2009-08-16
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from calendar import monthrange
from datetime import date

from hsutil.notify import Broadcaster
from hsutil.misc import first

from ..const import (REPEAT_DAILY, REPEAT_WEEKLY, REPEAT_MONTHLY, REPEAT_YEARLY, REPEAT_WEEKDAY, 
                     REPEAT_WEEKDAY_LAST)
from ..model.account import Account, INCOME, EXPENSE
from ..model.recurrence import Recurrence
from ..model.transaction import Split, Transaction
from .base import DocumentGUIObject
from .complete import TransactionCompletionMixIn

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

class SchedulePanel(DocumentGUIObject, Broadcaster, TransactionCompletionMixIn):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        Broadcaster.__init__(self)
    
    #--- Private
    def _load(self, schedule):
        self.schedule = schedule
        self.transaction = schedule.ref.replicate(link_splits=True)
        self._repeat_type_index = REPEAT_OPTIONS_ORDER.index(schedule.repeat_type)
        self._repeat_every = schedule.repeat_every
        self._stop_date = schedule.stop_date
        self.view.refresh_repeat_every()
        self.notify('panel_loaded')
        
    
    def can_load(self):
        return True
    
    def new(self):
        schedule = Recurrence(Transaction(date.today()), REPEAT_MONTHLY, 1, include_first=True)
        self._load(schedule)
    
    def load(self):
        self._load(self.document.selected_schedule)
    
    def save(self):
        repeat_type = REPEAT_OPTIONS_ORDER[self.repeat_type_index]
        self.document.change_schedule(self.schedule, self.transaction, repeat_type=repeat_type,
                                      repeat_every=self._repeat_every, stop_date=self._stop_date)
    
    def change_split(self, split, account_name, amount, memo):
        if account_name:
            account_type = split.account.type if split.account else EXPENSE if split.amount < 0 else INCOME
            split.account = Account(account_name, self.app.default_currency, account_type)
        else:
            split.account = None
        split.amount = amount
        split.memo = memo
        self.transaction.balance(split)
        self.notify('split_changed')
    
    def delete_split(self, split):
        self.transaction.splits.remove(split)
        self.transaction.balance()
     
    def new_split(self):
        transaction = self.transaction
        split = Split(transaction, None, 0)
        transaction.splits.append(split)
        return split
    
    @property
    def start_date(self):
        return self.app.format_date(self.transaction.date)
    
    @start_date.setter
    def start_date(self, value):
        date = self.app.parse_date(value)
        if date == self.transaction.date:
            return
        self.transaction.date = date
        self.view.refresh_repeat_options()
    
    @property
    def stop_date(self):
        if self._stop_date is None:
            return ''
        return self.app.format_date(self._stop_date)
    
    @stop_date.setter
    def stop_date(self, value):
        try:
            self._stop_date = self.app.parse_date(value)
        except ValueError:
            self._stop_date = None
    
    @property
    def description(self):
        return self.transaction.description
    
    @description.setter
    def description(self, value):
        self.transaction.description = value
    
    @property
    def payee(self):
        return self.transaction.payee
    
    @payee.setter
    def payee(self, value):
        self.transaction.payee = value
    
    @property
    def checkno(self):
        return self.transaction.checkno
    
    @checkno.setter
    def checkno(self, value):
        self.transaction.checkno = value
    
    @property
    def repeat_every(self):
        return self._repeat_every
    
    @repeat_every.setter
    def repeat_every(self, value):
        value = max(1, value)
        self._repeat_every = value
        self.view.refresh_repeat_every()
    
    @property
    def repeat_every_desc(self):
        repeat_option = REPEAT_OPTIONS_ORDER[self._repeat_type_index]
        desc = REPEAT_EVERY_DESCS[repeat_option]
        if desc and self._repeat_every > 1:
            desc += 's'
        return desc
    
    @property
    def repeat_options(self):
        result = ['Daily', 'Weekly', 'Monthly', 'Yearly']
        date = self.transaction.date
        weekday_name = date.strftime('%A')
        week_no = (date.day - 1) // 7
        position = ['first', 'second', 'third', 'fourth', 'fifth'][week_no]
        result.append('Every %s %s of the month' % (position, weekday_name))
        _, days_in_month = monthrange(date.year, date.month)
        if days_in_month - date.day < 7:
            result.append('Every last %s of the month' % weekday_name)
        return result
    
    @property
    def repeat_type_index(self):
        return self._repeat_type_index
    
    @repeat_type_index.setter
    def repeat_type_index(self, value):
        if value == self._repeat_type_index:
            return
        self._repeat_type_index = value
        self.view.refresh_repeat_every()
    

