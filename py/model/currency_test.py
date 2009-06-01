# Unit Name: moneyguru.model.currency_test
# Created By: Virgil Dupras
# Created On: 2008-05-22
# $Id$
# Copyright 2008 Hardcoded Software (http://www.hardcoded.net)

from datetime import date, timedelta, datetime
import xmlrpclib
import time

from hsutil.testcase import TestCase
from hsutil.currency import Currency, USD, CAD

from .amount import convert_amount
from .currency import RatesDB
from .amount import Amount

#--- ServerProxy mock
# We have to mock xmlrpclib.ServerProxy for every single test because if we don't, a xmlrpc call will
# be made for every single time we load a file. You must also mock it in test units of all modules 
# that import moneyguru.currency.

class FakeServer(object):
    log = []
    def __init__(self, url, use_datetime=False):
        pass
    
    @classmethod
    def hooklog(cls, log):
        cls.log = log
    
    def get_CAD_values(self, start, end, currency): # start and end are xmlrpclib.DateTime instances
        assert isinstance(start, xmlrpclib.DateTime)
        assert isinstance(end, xmlrpclib.DateTime)
        t = start.timetuple()
        start = date(t.tm_year, t.tm_mon, t.tm_mday)
        t = end.timetuple()
        end = date(t.tm_year, t.tm_mon, t.tm_mday)
        FakeServer.log.append((start, end, currency))
        number_of_days = (end - start).days + 1
        start = datetime(start.year, start.month, start.day)
        return [(xmlrpclib.DateTime(start + timedelta(i)), 1.42 + (.01 * i)) for i in range(number_of_days)]


def slow_down(func):
    def wrapper(*args, **kwargs):
        time.sleep(0.05)
        return func(*args, **kwargs)
    
    return wrapper


class CurrencyTest(TestCase):
    def test_unknown_currency(self):
        """Only known currencies are accepted"""
        self.assertRaises(ValueError, Currency, 'FOO')


class AsyncRatesDB(TestCase):
    def setUp(self):
        self.mock(xmlrpclib, 'ServerProxy', FakeServer)
        self.db = RatesDB(':memory:', True)
    
    def test_async_and_repeat(self):
        """If you make an ensure_rates() call and then the same call right after (before the first one
        is finished, the server will not be hit twice.
        """
        self.mock(FakeServer, 'get_CAD_values', slow_down(FakeServer.get_CAD_values))
        log = []
        FakeServer.hooklog(log)
        self.db.ensure_rates(date(2008, 5, 20), ['USD'])
        self.db.ensure_rates(date(2008, 5, 20), ['USD'])
        self.jointhreads()
        self.assertEqual(len(log), 1)
    

class NotAsyncRatesDB(TestCase):
    def setUp(self):
        self.mock(xmlrpclib, 'ServerProxy', FakeServer)
        self.db = RatesDB(':memory:', False)
    
    def test_ask_for_rates_in_the_past(self):
        """If a rate is asked for a date lower than the lowest fetched date, fetch that range"""
        self.db.ensure_rates(date(2008, 5, 20), ['USD']) # fetch some rates
        log = []
        FakeServer.hooklog(log)
        self.db.ensure_rates(date(2008, 5, 19), ['USD']) # this one should also fetch rates
        expected = [(date(2008, 5, 19), date(2008, 5, 19), 'USD')]
        self.assertEqual(log, expected)
    
    def test_ask_for_rates_in_the_future(self):
        """If a rate is asked for a date equal or higher than the lowest fetched date, fetch cached_end - today"""
        self.db.set_CAD_value(date(2008, 5, 20), 'USD', 1.42)
        log = []
        FakeServer.hooklog(log)
        self.db.ensure_rates(date(2008, 5, 20), ['USD']) # this one should fetch 2008-5-21 up to today
        expected = [(date(2008, 5, 21), date.today(), 'USD')]
        self.assertEqual(log, expected)
    
    def test_no_internet(self):
        """No crash occur if the computer don't have access to internet"""
        from socket import gaierror
        def mock_get_CAD_values(self, start, end, currency):
            raise gaierror()
        self.mock(FakeServer, 'get_CAD_values', mock_get_CAD_values)
        try:
            self.db.ensure_rates(date(2008, 5, 20), ['USD'])
        except gaierror:
            self.fail()
    
    def test_connection_timeout(self):
        """No crash occur the connection times out"""
        from socket import error
        def mock_get_CAD_values(self, start, end, currency):
            raise error()
        self.mock(FakeServer, 'get_CAD_values', mock_get_CAD_values)
        try:
            self.db.ensure_rates(date(2008, 5, 20), ['USD'])
        except error:
            self.fail()
    
    def test_xmlrpc_error(self):
        """No crash occur when there's an error on the xmlrpc level"""
        def mock_get_CAD_values(self, start, end, currency):
            raise xmlrpclib.Error()
        self.mock(FakeServer, 'get_CAD_values', mock_get_CAD_values)
        try:
            self.db.ensure_rates(date(2008, 5, 20), ['USD'])
        except xmlrpclib.Error:
            self.fail()
    

class NotAsyncRatesDBWithRates(TestCase):
    def setUp(self):
        self.mock(xmlrpclib, 'ServerProxy', FakeServer)
        Currency.set_rates_db(RatesDB(':memory:', False))
        USD.set_CAD_value(0.98, date(2008, 5, 20))
    
    def test_seek_rate(self):
        """Trying to get rate around the existing date gives the rate in question"""
        amount = Amount(42, USD)
        expected = Amount(42 * .98, CAD)
        self.assertEqual(convert_amount(amount, CAD, date(2008, 5, 21)), expected)
        self.assertEqual(convert_amount(amount, CAD, date(2008, 5, 19)), expected)
    
