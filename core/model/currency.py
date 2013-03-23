# Created By: Virgil Dupras
# Created On: 2008-04-22
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import socket
import threading
import xmlrpc.client
from queue import Queue, Empty
from datetime import timedelta, date, datetime

from hscommon.currency import Currency, RatesDB as RatesDBBase

CURRENCY_SERVER = 'http://currency.hardcoded.net/'

class RatesDB(RatesDBBase):
    def __init__(self, dbpath=':memory:', async=True):
        RatesDBBase.__init__(self, dbpath)
        self.async = async
        self._fetched_values = Queue()
        self._fetched_ranges = {} # a currency --> (start, end) map
    
    def ensure_rates(self, start_date, currencies):
        """Ensures that the DB has all the rates it needs for 'currencies' between 'start_date' and today
        
        If there is any rate missing, a request will be made to the currency server. The requests
        are made asynchronously.
        """
        def do():
            server = xmlrpc.client.ServerProxy(CURRENCY_SERVER)
            for currency, fetch_start, fetch_end in currencies_and_range:
                try:
                    # dates passed to xmlrpclib *have* to be xmlrpclib.DateTime instances since 2.6
                    start = xmlrpc.client.DateTime(datetime(fetch_start.year, fetch_start.month, fetch_start.day))
                    end = xmlrpc.client.DateTime(datetime(fetch_end.year, fetch_end.month, fetch_end.day))
                    values = server.get_CAD_values(start, end, currency)
                except (socket.gaierror, socket.error, xmlrpc.client.Error) as e:
                    logging.warning("Communication problem with currency.hardcoded.net: %s", e)
                    return # We can't connect
                except Exception as e:
                    logging.warning("Unknown error while doing currency rates fetching: %s", e)
                    return                
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
    
    def get_rate(self, date, currency1_code, currency2_code):
        # We want to check self._fetched_values for rates to add.
        if not self._fetched_values.empty():
            self.save_fetched_rates()
        return RatesDBBase.get_rate(self, date, currency1_code, currency2_code)
    
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
    

def initialize_db(path):
    """Initialize the app wide currency db if not already initialized."""
    Currency.set_rates_db(RatesDB(str(path)))
