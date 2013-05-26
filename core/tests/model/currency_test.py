# Created By: Virgil Dupras
# Created On: 2008-05-22
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date, timedelta
import xmlrpc.client
import time

from pytest import raises
from hscommon.currency import Currency, USD, CAD
from hscommon.testutil import jointhreads, eq_

from ...model.amount import convert_amount
from ...model.currency import RatesDB, default_currency_rate_provider
from ...model.amount import Amount

def slow_down(func):
    def wrapper(*args, **kwargs):
        time.sleep(0.05)
        return func(*args, **kwargs)
    
    return wrapper

def set_ratedb_for_tests(async=False, slow_down_provider=False, provider=None):
    log = []
    
    # Returns a RatesDB that isn't async and that uses a fake provider
    def fake_provider(currency, start_date, end_date):
        log.append((start_date, end_date, currency))
        number_of_days = (end_date - start_date).days + 1
        return [(start_date + timedelta(i), 1.42 + (.01 * i)) for i in range(number_of_days)]
    
    db = RatesDB(':memory:', async=async)
    if provider is None:
        provider = fake_provider
    if slow_down_provider:
        provider = slow_down(provider)
    db.register_rate_provider(provider)
    Currency.set_rates_db(db)
    return db, log

def test_unknown_currency():
    # Only known currencies are accepted.
    with raises(ValueError):
        Currency('FOO')

def test_async_and_repeat():
    # If you make an ensure_rates() call and then the same call right after (before the first one
    # is finished, the server will not be hit twice.
    db, log = set_ratedb_for_tests(async=True, slow_down_provider=True)
    db.ensure_rates(date(2008, 5, 20), ['USD'])
    db.ensure_rates(date(2008, 5, 20), ['USD'])
    jointhreads()
    eq_(len(log), 1)

def test_seek_rate():
    # Trying to get rate around the existing date gives the rate in question.
    set_ratedb_for_tests()
    USD.set_CAD_value(0.98, date(2008, 5, 20))
    amount = Amount(42, USD)
    expected = Amount(42 * .98, CAD)
    eq_(convert_amount(amount, CAD, date(2008, 5, 21)), expected)
    eq_(convert_amount(amount, CAD, date(2008, 5, 19)), expected)

#---
def test_ask_for_rates_in_the_past():
    # If a rate is asked for a date lower than the lowest fetched date, fetch that range.
    db, log = set_ratedb_for_tests()
    db.ensure_rates(date(2008, 5, 20), ['USD']) # fetch some rates
    db.ensure_rates(date(2008, 5, 19), ['USD']) # this one should also fetch rates
    eq_(len(log), 2)
    eq_(log[1], (date(2008, 5, 19), date(2008, 5, 19), 'USD'))

def test_ask_for_rates_in_the_future():
    # If a rate is asked for a date equal or higher than the lowest fetched date, fetch cached_end - today.
    db, log = set_ratedb_for_tests()
    db.set_CAD_value(date(2008, 5, 20), 'USD', 1.42)
    db.ensure_rates(date(2008, 5, 20), ['USD']) # this one should fetch 2008-5-21 up to today
    expected = [(date(2008, 5, 21), date.today(), 'USD')]
    eq_(log, expected)

#--- Test for the default XMLRPC provider
class FakeServer:
    ERROR_TO_RAISE = Exception
    
    def __init__(self, *args, **kwargs):
        pass
    
    def get_CAD_values(self, start, end, currency):
        raise self.ERROR_TO_RAISE()

def test_no_internet(monkeypatch):
    # No crash occur if the computer don't have access to internet.
    from socket import gaierror
    monkeypatch.setattr(xmlrpc.client, 'ServerProxy', FakeServer)
    FakeServer.ERROR_TO_RAISE = gaierror
    try:
        default_currency_rate_provider('USD', date(2008, 5, 20), date(2008, 5, 20))
    except gaierror:
        assert False

def test_connection_timeout(monkeypatch):
    # No crash occur the connection times out.
    from socket import error
    def mock_get_CAD_values(self, start, end, currency):
        raise error()
    monkeypatch.setattr(xmlrpc.client, 'ServerProxy', FakeServer)
    FakeServer.ERROR_TO_RAISE = error
    try:
        default_currency_rate_provider('USD', date(2008, 5, 20), date(2008, 5, 20))
    except error:
        assert False

def test_xmlrpc_error(monkeypatch):
    # No crash occur when there's an error on the xmlrpc level.
    def mock_get_CAD_values(self, start, end, currency):
        raise xmlrpc.client.Error()
    monkeypatch.setattr(xmlrpc.client, 'ServerProxy', FakeServer)
    FakeServer.ERROR_TO_RAISE = xmlrpc.client.Error
    try:
        default_currency_rate_provider('USD', date(2008, 5, 20), date(2008, 5, 20))
    except xmlrpc.client.Error:
        assert False

