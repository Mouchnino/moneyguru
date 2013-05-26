# Created By: Virgil Dupras
# Created On: 2008-04-22
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging
import socket
import xmlrpc.client
from datetime import date, datetime

from hscommon.currency import Currency, RatesDB, BUILTIN_CURRENCY_CODES, CurrencyNotSupportedException

CURRENCY_SERVER = 'http://currency.hardcoded.net/'

def xmlrpcdate2normaldate(d):
    t = d.timetuple()
    return date(t.tm_year, t.tm_mon, t.tm_mday)

def default_currency_rate_provider(currency, start_date, end_date):
    if currency not in BUILTIN_CURRENCY_CODES:
        raise CurrencyNotSupportedException()
    server = xmlrpc.client.ServerProxy(CURRENCY_SERVER)
    try:
        # dates passed to xmlrpclib *have* to be xmlrpclib.DateTime instances since 2.6
        start = xmlrpc.client.DateTime(datetime(start_date.year, start_date.month, start_date.day))
        end = xmlrpc.client.DateTime(datetime(end_date.year, end_date.month, end_date.day))
        values = server.get_CAD_values(start, end, currency)
        # Now, the dates we have in our list are xmlrpc dates. We have to convert them to real dates
        return [(xmlrpcdate2normaldate(d), r) for d, r in values]
    except (socket.gaierror, socket.error, xmlrpc.client.Error) as e:
        logging.warning("Communication problem with currency.hardcoded.net: %s", e)
        return None # We can't connect
    except Exception as e:
        logging.warning("Unknown error while doing currency rates fetching: %s", e)
        return None

def initialize_db(path):
    """Initialize the app wide currency db if not already initialized."""
    ratesdb = RatesDB(str(path))
    ratesdb.register_rate_provider(default_currency_rate_provider)
    Currency.set_rates_db(ratesdb)
