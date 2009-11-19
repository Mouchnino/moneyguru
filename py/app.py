# Created By: Virgil Dupras
# Created On: 2009-02-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import logging
import threading

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
YEAR_START_MONTH_PREFERENCE = 'YearStartMonth'
AUTOSAVE_INTERVAL_PREFERENCE = 'AutoSaveInterval'
DONT_UNRECONCILE_PREFERENCE = 'DontUnreconcile'

class Application(Broadcaster, RegistrableApplication):
    VERSION = '1.6.8'
    DEMO_LIMIT_DESC = "In the demo version, documents with more than 100 transactions cannot be saved."
    
    def __init__(self, view, date_format='dd/MM/yyyy', decimal_sep='.', grouping_sep='', 
        default_currency=USD, cache_path=None):
        Broadcaster.__init__(self)
        RegistrableApplication.__init__(self, appid=6)
        self.view = view
        self.cache_path = cache_path
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
        self._autosave_timer = None
        self._first_weekday = self.get_default(FIRST_WEEKDAY_PREFERENCE, 0)
        self._ahead_months = self.get_default(AHEAD_MONTHS_PREFERENCE, 2)
        self._year_start_month = self.get_default(YEAR_START_MONTH_PREFERENCE, 1)
        self._autosave_interval = self.get_default(AUTOSAVE_INTERVAL_PREFERENCE, 10)
        self._update_autosave_timer()
        self._dont_unreconcile = self.get_default(DONT_UNRECONCILE_PREFERENCE, False)
    
    #--- Override
    #XXX Implement setup_as_registered in the Cocoa codebase!
    def _setup_as_registered(self):
        self.view.setup_as_registered()
    
    #--- Private
    def _autosave_all_documents(self):
        self.notify('must_autosave')
        self._update_autosave_timer()
    
    def _update_autosave_timer(self):
        if self._autosave_timer is not None:
            self._autosave_timer.cancel()
        if self._autosave_interval > 0 and self.cache_path: # no need to start a timer if we have nowhere to autosave to
            # By having the timer at the application level, we make sure that there will not be 2
            # documents trying to autosave at the same time, thus overwriting each other.
            self._autosave_timer = threading.Timer(self._autosave_interval * 60, self._autosave_all_documents)
            self._autosave_timer.start()
        else:
            self._autosave_timer = None
    
    #--- Public
    def format_amount(self, amount, **kw):
        return format_amount(amount, self.default_currency, decimal_sep=self._decimal_sep,
                             grouping_sep=self._grouping_sep, **kw)
    
    def format_date(self, date):
        return format_date(date, self._date_format)
    
    def parse_amount(self, amount):
        return parse_amount(amount, self.default_currency)
    
    def parse_date(self, date):
        return parse_date(date, self._date_format)
    
    def get_default(self, key, fallback_value=None):
        result = nonone(self.view.get_default(key), fallback_value)
        if fallback_value is not None and not isinstance(result, type(fallback_value)):
            # we don't want to end up with garbage values from the prefs
            try:
                result = type(fallback_value)(result)
            except Exception:
                result = fallback_value
        return result
    
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
    def year_start_month(self):
        return self._year_start_month
        
    @year_start_month.setter
    def year_start_month(self, value):
        assert 1 <= value <= 12
        if value == self._ahead_months:
            return
        self._year_start_month = value
        self.set_default(YEAR_START_MONTH_PREFERENCE, value)
        self.notify('year_start_month_changed')
    
    @property
    def autosave_interval(self):
        return self._autosave_interval
        
    @autosave_interval.setter
    def autosave_interval(self, value):
        if value == self._autosave_interval:
            return
        self._autosave_interval = value
        self.set_default(AUTOSAVE_INTERVAL_PREFERENCE, value)
        self._update_autosave_timer()
    
    @property
    def dont_unreconcile(self):
        return self._dont_unreconcile
        
    @dont_unreconcile.setter
    def dont_unreconcile(self, value):
        if value == self._dont_unreconcile:
            return
        self._dont_unreconcile = value
        self.set_default(DONT_UNRECONCILE_PREFERENCE, value)
    
