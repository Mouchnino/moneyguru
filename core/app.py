# Created By: Virgil Dupras
# Created On: 2009-02-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import datetime
import threading
from collections import namedtuple

from hscommon.currency import USD
from hscommon.notify import Broadcaster
from hscommon.reg import RegistrableApplication
from hscommon import io
from hscommon.util import nonone

from .const import DATE_FORMAT_FOR_PREFERENCES
from .model import currency
from .model.amount import parse_amount, format_amount
from .model.date import parse_date, format_date

HAD_FIRST_LAUNCH_PREFERENCE = 'HadFirstLaunch'
FIRST_WEEKDAY_PREFERENCE = 'FirstWeekday'
AHEAD_MONTHS_PREFERENCE = 'AheadMonths'
YEAR_START_MONTH_PREFERENCE = 'YearStartMonth'
AUTOSAVE_INTERVAL_PREFERENCE = 'AutoSaveInterval'
AUTO_DECIMAL_PLACE_PREFERENCE = 'AutoDecimalPlace'
CUSTOM_RANGES_PREFERENCE = 'CustomRanges'

SavedCustomRange = namedtuple('SavedCustomRange', 'name start end')

class Application(Broadcaster, RegistrableApplication):
    APP_NAME = "moneyGuru"
    VERSION = '2.3.6'
    
    def __init__(self, view, date_format='dd/MM/yyyy', decimal_sep='.', grouping_sep='', 
        default_currency=USD, cache_path=None):
        Broadcaster.__init__(self)
        RegistrableApplication.__init__(self, appid=2)
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
        self.is_first_run = not self.get_default(HAD_FIRST_LAUNCH_PREFERENCE, False)
        if self.is_first_run:
            self.set_default(HAD_FIRST_LAUNCH_PREFERENCE, True)
        self._default_currency = default_currency
        self._date_format = date_format
        self._decimal_sep = decimal_sep
        self._grouping_sep = grouping_sep
        self._autosave_timer = None
        self._first_weekday = self.get_default(FIRST_WEEKDAY_PREFERENCE, 0)
        self._ahead_months = self.get_default(AHEAD_MONTHS_PREFERENCE, 2)
        self._year_start_month = self.get_default(YEAR_START_MONTH_PREFERENCE, 1)
        self._autosave_interval = self.get_default(AUTOSAVE_INTERVAL_PREFERENCE, 10)
        self._auto_decimal_place = self.get_default(AUTO_DECIMAL_PLACE_PREFERENCE, False)
        self.saved_custom_ranges = [None] * 3
        self._load_custom_ranges()
        self._update_autosave_timer()
    
    #--- Override
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
    
    def _load_custom_ranges(self):
        custom_ranges = self.get_default(CUSTOM_RANGES_PREFERENCE)
        if not custom_ranges:
            return
        for index, custom_range in enumerate(custom_ranges):
            if custom_range:
                name = custom_range[0]
                start = datetime.datetime.strptime(custom_range[1], DATE_FORMAT_FOR_PREFERENCES).date()
                end = datetime.datetime.strptime(custom_range[2], DATE_FORMAT_FOR_PREFERENCES).date()
                self.saved_custom_ranges[index] = SavedCustomRange(name, start, end)
            else:
                self.saved_custom_ranges[index] = None
    
    def _save_custom_ranges(self):
        custom_ranges = []
        for custom_range in self.saved_custom_ranges:
            if custom_range:
                start_str = custom_range.start.strftime(DATE_FORMAT_FOR_PREFERENCES)
                end_str = custom_range.end.strftime(DATE_FORMAT_FOR_PREFERENCES)
                custom_ranges.append([custom_range.name, start_str, end_str])
            else:
                # We can't insert None in arrays for preferences
                custom_ranges.append([])
        self.set_default(CUSTOM_RANGES_PREFERENCE, custom_ranges)
    
    #--- Public
    def format_amount(self, amount, **kw):
        return format_amount(amount, self._default_currency, decimal_sep=self._decimal_sep,
                             grouping_sep=self._grouping_sep, **kw)
    
    def format_date(self, date):
        return format_date(date, self._date_format)
    
    def parse_amount(self, amount, default_currency=None):
        if default_currency is None:
            default_currency = self._default_currency
        return parse_amount(amount, default_currency, auto_decimal_place=self._auto_decimal_place)
    
    def parse_date(self, date):
        return parse_date(date, self._date_format)
    
    def parse_search_query(self, query_string):
        # Returns a dict of query arguments
        query_string = query_string.lower()
        if query_string.startswith('account:'):
            accounts = query_string[len('account:'):].split(',')
            accounts = set([s.strip().lower() for s in accounts])
            return {'account': accounts}
        if query_string.startswith('group:'):
            groups = query_string[len('group:'):].split(',')
            groups = set([s.strip().lower() for s in groups])
            return {'group': groups}
        query = {'all': query_string}
        try:
            query['amount'] = abs(parse_amount(query_string, self._default_currency, with_expression=False))
        except ValueError:
            pass
        return query
    
    def save_custom_range(self, slot, name, start, end):
        self.saved_custom_ranges[slot] = SavedCustomRange(name, start, end)
        self._save_custom_ranges()
        self.notify('saved_custom_ranges_changed')
    
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
        if value == self._year_start_month:
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
    def default_currency(self):
        return self._default_currency
    
    @default_currency.setter
    def default_currency(self, value):
        if value == self._default_currency:
            return
        self._default_currency = value
        self.notify('default_currency_changed')
    
    @property
    def auto_decimal_place(self):
        return self._auto_decimal_place
    
    @auto_decimal_place.setter
    def auto_decimal_place(self, value):
        if value == self._auto_decimal_place:
            return
        self._auto_decimal_place = value
        self.set_default(AUTO_DECIMAL_PLACE_PREFERENCE, value)
    
