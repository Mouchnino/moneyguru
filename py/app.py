# Unit Name: moneyguru.app
# Created By: Virgil Dupras
# Created On: 2009-02-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import logging

from hsutil import io
from hsutil.currency import USD
from hsutil.notify import Broadcaster
from hsutil.reg import RegistrableApplication
from hsutil.misc import nonone

from .model import currency
from .model.amount import parse_amount, format_amount
from .model.date import parse_date, format_date

FIRST_WEEKDAY_PREFERENCE = 'FirstWeekday'
AHEAD_MONTHS_PREFERENCE = 'AheadMonths'
DONT_UNRECONCILE_PREFERENCE = 'DontUnreconcile'

class Application(Broadcaster, RegistrableApplication):
    def __init__(self, view, date_format='dd/MM/yyyy', decimal_sep='.', grouping_sep='', 
        default_currency=USD, cache_path=None):
        Broadcaster.__init__(self)
        RegistrableApplication.__init__(self, appid=6)
        self.view = view
        # cache_path is required, but for tests, we don't want to bother specifying it. When 
        # cache_path is kept as None, the path of the currency db will be ':memory:'
        if cache_path:
            if not io.exists(cache_path):
                io.makedirs(cache_path)
            db_path = cache_path + 'currency.db'
        else:
            db_path = ':memory:'
        currency.initialize_db(db_path)
        self.default_currency = default_currency
        self._date_format = date_format
        self._decimal_sep = decimal_sep
        self._grouping_sep = grouping_sep
        self._first_weekday = self.get_default(FIRST_WEEKDAY_PREFERENCE, 0)
        self._ahead_months = self.get_default(AHEAD_MONTHS_PREFERENCE, 2)
        self._dont_unreconcile = self.get_default(DONT_UNRECONCILE_PREFERENCE, False)
    
    def format_amount(self, amount, **kw):
        return format_amount(amount, self.default_currency, decimal_sep=self._decimal_sep,
                             grouping_sep=self._grouping_sep, **kw)
    
    def format_date(self, date):
        return format_date(date, self._date_format)
    
    def parse_amount(self, amount):
        return parse_amount(amount, self.default_currency)
    
    def parse_date(self, date):
        return parse_date(date, self._date_format)
    
    def get_default(self, key, value_if_missing=None):
        return nonone(self.view.get_default(key), value_if_missing)
    
    def set_default(self, key, value):
        self.view.set_default(key, value)
    
    #--- Preferences
    # 0=monday 6=sunday
    @property
    def first_weekday(self):
        return self._first_weekday
        
    @first_weekday.setter
    def first_weekday(self, value):
        if value == self._first_weekday:
            return
        self._first_weekday = value
        self.set_default(FIRST_WEEKDAY_PREFERENCE, value)
        self.notify('first_weekday_changed')
    
    @property
    def ahead_months(self):
        return self._ahead_months
        
    @ahead_months.setter
    def ahead_months(self, value):
        assert 0 <= value <= 11
        if value == self._ahead_months:
            return
        self._ahead_months = value
        self.set_default(AHEAD_MONTHS_PREFERENCE, value)
        self.notify('ahead_months_changed')
    
    @property
    def dont_unreconcile(self):
        return self._dont_unreconcile
        
    @dont_unreconcile.setter
    def dont_unreconcile(self, value):
        if value == self._dont_unreconcile:
            return
        self._dont_unreconcile = value
        self.set_default(DONT_UNRECONCILE_PREFERENCE, value)
    
