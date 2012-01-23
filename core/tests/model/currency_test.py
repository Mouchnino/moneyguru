# Created By: Virgil Dupras
# Created On: 2008-05-22
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date, timedelta, datetime
import xmlrpc.client
import time

from pytest import raises
from hscommon.currency import Currency, USD, CAD
from hscommon.testutil import jointhreads, eq_

from ...model.amount import convert_amount
from ...model.currency import RatesDB
from ...model.amount import Amount
from ..conftest import get_original_rates_db_ensure_rates

#--- ServerProxy mock
# We have to mock xmlrpc.client.ServerProxy for every single test because if we don't, a xmlrpc call will
# be made for every single time we load a file. You must also mock it in test units of all modules 
# that import moneyguru.currency.

class FakeServer:
    log = []
    def __init__(self, url, use_datetime=False):
        pass
    
    @classmethod
    def hooklog(cls, log):
        cls.log = log
    
    def get_CAD_values(self, start, end, currency): # start and end are xmlrpc.client.DateTime instances
        assert isinstance(start, xmlrpc.client.DateTime)
        assert isinstance(end, xmlrpc.client.DateTime)
        t = start.timetuple()
        start = date(t.tm_year, t.tm_mon, t.tm_mday)
        t = end.timetuple()
        end = date(t.tm_year, t.tm_mon, t.tm_mday)
        FakeServer.log.append((start, end, currency))
        number_of_days = (end - start).days + 1
        start = datetime(start.year, start.month, start.day)
        return [(xmlrpc.client.DateTime(start + timedelta(i)), 1.42 + (.01 * i)) for i in range(number_of_days)]


def slow_down(func):
    def wrapper(*args, **kwargs):
        time.sleep(0.05)
        return func(*args, **kwargs)
    
    return wrapper


def test_unknown_currency():
    # Only known currencies are accepted.
    with raises(ValueError):
        Currency('FOO')

def test_async_and_repeat(monkeypatch):
    # If you make an ensure_rates() call and then the same call right after (before the first one
    # is finished, the server will not be hit twice.
    monkeypatch.setattr(RatesDB, 'ensure_rates', get_original_rates_db_ensure_rates()) # See tests.currency_test
    monkeypatch.setattr(xmlrpc.client, 'ServerProxy', FakeServer)
    db = RatesDB(':memory:', True)
    monkeypatch.setattr(FakeServer, 'get_CAD_values', slow_down(FakeServer.get_CAD_values))
    log = []
    FakeServer.hooklog(log)
    db.ensure_rates(date(2008, 5, 20), ['USD'])
    db.ensure_rates(date(2008, 5, 20), ['USD'])
    jointhreads()
    eq_(len(log), 1)

def test_seek_rate(monkeypatch):
    # Trying to get rate around the existing date gives the rate in question.
    monkeypatch.setattr(RatesDB, 'ensure_rates', get_original_rates_db_ensure_rates()) # See tests.currency_test
    monkeypatch.setattr(xmlrpc.client, 'ServerProxy', FakeServer)
    Currency.set_rates_db(RatesDB(':memory:', False))
    USD.set_CAD_value(0.98, date(2008, 5, 20))
    amount = Amount(42, USD)
    expected = Amount(42 * .98, CAD)
    eq_(convert_amount(amount, CAD, date(2008, 5, 21)), expected)
    eq_(convert_amount(amount, CAD, date(2008, 5, 19)), expected)

#---
def setup_async_db(monkeypatch):
    monkeypatch.setattr(RatesDB, 'ensure_rates', get_original_rates_db_ensure_rates()) # See tests.currency_test
    monkeypatch.setattr(xmlrpc.client, 'ServerProxy', FakeServer)
    return RatesDB(':memory:', False)

def test_ask_for_rates_in_the_past(monkeypatch):
    # If a rate is asked for a date lower than the lowest fetched date, fetch that range.
    db = setup_async_db(monkeypatch)
    db.ensure_rates(date(2008, 5, 20), ['USD']) # fetch some rates
    log = []
    FakeServer.hooklog(log)
    db.ensure_rates(date(2008, 5, 19), ['USD']) # this one should also fetch rates
    expected = [(date(2008, 5, 19), date(2008, 5, 19), 'USD')]
    eq_(log, expected)

def test_ask_for_rates_in_the_future(monkeypatch):
    # If a rate is asked for a date equal or higher than the lowest fetched date, fetch cached_end - today.
    db = setup_async_db(monkeypatch)
    db.set_CAD_value(date(2008, 5, 20), 'USD', 1.42)
    log = []
    FakeServer.hooklog(log)
    db.ensure_rates(date(2008, 5, 20), ['USD']) # this one should fetch 2008-5-21 up to today
    expected = [(date(2008, 5, 21), date.today(), 'USD')]
    eq_(log, expected)

def test_no_internet(monkeypatch):
    # No crash occur if the computer don't have access to internet.
    db = setup_async_db(monkeypatch)
    from socket import gaierror
    def mock_get_CAD_values(self, start, end, currency):
        raise gaierror()
    monkeypatch.setattr(FakeServer, 'get_CAD_values', mock_get_CAD_values)
    try:
        db.ensure_rates(date(2008, 5, 20), ['USD'])
    except gaierror:
        assert False

def test_connection_timeout(monkeypatch):
    # No crash occur the connection times out.
    db = setup_async_db(monkeypatch)
    from socket import error
    def mock_get_CAD_values(self, start, end, currency):
        raise error()
    monkeypatch.setattr(FakeServer, 'get_CAD_values', mock_get_CAD_values)
    try:
        db.ensure_rates(date(2008, 5, 20), ['USD'])
    except error:
        assert False

def test_xmlrpc_error(monkeypatch):
    # No crash occur when there's an error on the xmlrpc level.
    db = setup_async_db(monkeypatch)
    def mock_get_CAD_values(self, start, end, currency):
        raise xmlrpc.client.Error()
    monkeypatch.setattr(FakeServer, 'get_CAD_values', mock_get_CAD_values)
    try:
        db.ensure_rates(date(2008, 5, 20), ['USD'])
    except xmlrpc.client.Error:
        assert False

