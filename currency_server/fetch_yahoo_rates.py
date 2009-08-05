#!/usr/bin/env python
# This script fetches today's rates from Yahoo Finance for some currencies that are not at BOC
# I have not yet figured how to fetch more than one currency from a single request.
# Created By: Virgil Dupras
# Created On: 2008-11-08
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import time
from datetime import date
from urllib import urlencode, urlopen

from currency_server.db import RatesDB

CURRENCIES_TO_FETCH = ['BHD', 'EGP']

# Open the db
db = RatesDB()

def fetch_currency(currency):
    # the result of this request is a single CSV line like this:
    # "CADBHD=X",0.3173,"11/7/2008","5:11pm",N/A,N/A,N/A,N/A,N/A 
    response = urlopen('http://download.finance.yahoo.com/d/quotes.csv?s=%sCAD=X&f=sl1d1t1c1ohgv&e=.csv' % currency)
    content = response.read()
    rate = float(content.split(',')[1])
    db.set_CAD_value(date.today(), currency, rate)

for currency in CURRENCIES_TO_FETCH:
    fetch_currency(currency)
    time.sleep(5)

