# Created By: Virgil Dupras
# Created On: 2008-04-22
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import logging
import socket
import threading
import xmlrpclib
from Queue import Queue, Empty
from datetime import timedelta, date, datetime

from hsutil.currency import Currency, RatesDB as RatesDBBase

CURRENCY_SERVER = 'http://currency.hardcoded.net/'

class RatesDB(RatesDBBase):
    def __init__(self, dbpath=':memory:', async=True):
        RatesDBBase.__init__(self, dbpath)
        self.async = async
        self._fetched_values = Queue()
        self._fetched_ranges = {} # a currency --> (start, end) map
        self._cache = {} # queries to the sqlite db are slow and frequent. this is an optimization
        sql = "select currency, date, rate from rates"
        cur = self._execute(sql)
        for currency, date, rate in cur:
            self._cache[(currency, date)] = rate
    
    def ensure_rates(self, start_date, currencies):
        """Ensures that the DB has all the rates it needs for 'currencies' between 'start_date' and today
        
        If there is any rate missing, a request will be made to the currency server. The requests
        are made asynchronously.
        """
        def do():
            server = xmlrpclib.ServerProxy(CURRENCY_SERVER)
            for currency, fetch_start, fetch_end in currencies_and_range:
                try:
                    # dates passed to xmlrpclib *have* to be xmlrpclib.DateTime instances since 2.6
                    start = xmlrpclib.DateTime(datetime(fetch_start.year, fetch_start.month, fetch_start.day))
                    end = xmlrpclib.DateTime(datetime(fetch_end.year, fetch_end.month, fetch_end.day))
                    values = server.get_CAD_values(start, end, currency)
                except (socket.gaierror, socket.error, xmlrpclib.Error), e:
                    logging.warning('Communication problem with currency.hardcoded.net: %s' % unicode(e))
                    return # We can't connect
                else:
                    self._fetched_values.put((values, currency))
        
        currencies_and_range = []
        for currency in currencies:
            if currency == 'CAD':
                continue
            try:
                cached_range = self._fetched_ranges[currency]
            except KeyError:
                cached_range = self.date_range(currency)
            range_start = start_date
            range_end = date.today()
            if cached_range is not None:
                cached_start, cached_end = cached_range
                if range_start >= cached_start:
                    # Make a forward fetch
                    range_start = cached_end + timedelta(days=1)
                else:
                    # Make a backward fetch
                    range_end = cached_start - timedelta(days=1)
            if range_start <= range_end:
                currencies_and_range.append((currency, range_start, range_end))
            self._fetched_ranges[currency] = (start_date, date.today())
        if self.async:
            threading.Thread(target=do).start()
        else:
            do()
    
    def _seek_value_in_CAD(self, str_date, currency_code):
        # We want to check self._fetched_values for rates to add.
        if not self._fetched_values.empty():
            self.save_fetched_rates()
        try:
            return self._cache[(currency_code, str_date)]
        except KeyError:
            result = RatesDBBase._seek_value_in_CAD(self, str_date, currency_code)
            self._cache[(currency_code, str_date)] = result
            return result
    
    def save_fetched_rates(self):
        while True:
            try:
                rates, currency = self._fetched_values.get_nowait()
                for rate_date, rate in rates: # rate_date is a xmlrpclib.DateTime instance
                    t = rate_date.timetuple()
                    rate_date = date(t.tm_year, t.tm_mon, t.tm_mday)
                    self.set_CAD_value(rate_date, currency, rate)
            except Empty:
                break
    
    def set_CAD_value(self, date, currency_code, value):
        RatesDBBase.set_CAD_value(self, date, currency_code, value)
        str_date = '%d%02d%02d' % (date.year, date.month, date.day)
        self._cache[(currency_code, str_date)] = value
    

def initialize_db(path):
    """Initialize the app wide currency db if not already initialized."""
    Currency.set_rates_db(RatesDB(unicode(path)))
