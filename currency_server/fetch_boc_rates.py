#!/usr/bin/env python
# This script fetches today's rates from the Bank of Canada website
# Created By: Eric Mc Sween
# Created On: 2008-05-19
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import sys
import re
from datetime import date
from urllib import urlencode, urlopen

from currency_server.db import RatesDB


# Open the db
db = RatesDB()

# Make the first query

db_min, db_max = db.date_range('USD')
start = db_max # We'll always refetch yesterday's data in case there was some missing.
end = date.today()
form_data = {
    # Hidden
    'cgi': 'famescript',
    'pageName': 'exchange-look.html',
    'famescript_formname': 'exchange-look.html',
    'famescript_html_template': 'fxlook-nojs.html',
    'ExchangeRates_frequency': 'business',
    'ExchangeRates_daterange': '',
    'ExchangeRates_replace_NC': 'Not available',
    'ExchangeRates_replace_ND': 'Not available',
    'ExchangeRates_replace_NA': 'Bank holiday',

    # Select options
    'show_xml': 'TRUE',

    # Select dates
    'ExchangeRates_dateclause': '=ExchangeRatesByDates',
    'ExchangeRatesByDates_frequency': 'daily',
    'ExchangeRatesByDates_daterange_start_Month': start.strftime('%b'),
    'ExchangeRatesByDates_daterange_start_Day': start.day,
    'ExchangeRatesByDates_daterange_start_Year': start.year,
    'ExchangeRatesByDates_daterange_end_Month': end.strftime('%b'),
    'ExchangeRatesByDates_daterange_end_Day': end.day,
    'ExchangeRatesByDates_daterange_end_Year': end.year,

    # Select currencies
    'ExchangeRates': [
        'IEXE0101',  # U.S. dollar (noon)
        'IEXE2702',  # Argentine peso (floating rate)
        'IEXE1601',  # Australian dollar
        'IEXE6001',  # Bahamian dollar
        'IEXE2801',  # Brazilian real
        'IEXE4501',  # CFA franc
        'IEXE4601',  # CFP franc
        'IEXE2901',  # Chilean peso
        'IEXE2201',  # Chinese renminbi (yuan)
        'IEXE3901',  # Colombian peso
        'IEXE6101',  # Croatian kuna
        'IEXE2301',  # Czech Republic koruna
        'IEXE0301',  # Danish krone
        'IEXE4001',  # East Caribbean dollar
        'EUROCAE01', # European Euro
        'IEXE4101',  # Fiji dollar
        'IEXE4702',  # Ghanaian cedi (new)
        'IEXE6501',  # Guatemalan quetzal
        'IEXE4301',  # Honduran lempira
        'IEXE1401',  # Hong Kong dollar
        'IEXE2501',  # Hungarian forint
        'IEXE4401',  # Icelandic krona
        'IEXE3001',  # Indian rupee
        'IEXE2601',  # Indonesian rupiah
        'IEXE5301',  # Israeli new shekel
        'IEXE6401',  # Jamaican dollar
        'IEXE0701',  # Japanese yen
        'IEXE3201',  # Malaysian ringgit
        'IEXE2001',  # Mexican peso
        'IEXE4801',  # Moroccan dirham
        'IEXE3801',  # Myanmar (Burma) kyat
        'IEXE4901',  # Neth. Antilles florin
        'IEXE1901',  # New Zealand dollar
        'IEXE0901',  # Norwegian krone
        'IEXE5001',  # Pakistan rupee
        'IEXE5101',  # Panamanian balboa
        'IEXE5201',  # Peruvian new sol
        'IEXE3301',  # Philippine peso
        'IEXE2401',  # Polish zloty
        'IEXE6505',  # Romanian new leu
        'IEXE2101',  # Russian rouble
        'IEXE6504',  # Serbian dinar
        'IEXE3701',  # Singapore dollar
        'IEXE6201',  # Slovak koruna
        'IEXE3401',  # South African rand
        'IEXE3101',  # South Korean won
        'IEXE5501',  # Sri Lanka rupee
        'IEXE1001',  # Swedish krona
        'IEXE1101',  # Swiss franc
        'IEXE3501',  # Taiwanese new dollar
        'IEXE3601',  # Thai baht
        #'IEXE5601',  # Trinidad & Tobago dollar
        'IEXE5701',  # Tunisian dinar
        #'IEXE5802',  # Turkish new lira
        'IEXE6506',  # U.A.E. dirham
        'IEXE1201',  # U.K. pound sterling
        'IEXE5902',  # Venezuelan bolivar fuerte
        'IEXE6503',  # Vietnamese dong
    ],
}
response = urlopen('http://www.bankofcanada.ca/cgi-bin/famecgi_fdps', urlencode(form_data, True))

# Find the XML file's URL

url_re = re.compile(r'/databank/client_output/.*\.xml')
for line in response:
    match = url_re.search(line)
    if match:
        xml_url = match.group()
        break
else:
    sys.exit("Error: couldn't find the XML file's URL in the response: %s" % response.read())

# Fetch the XML file

xml_file = urlopen('http://www.bankofcanada.ca' + xml_url)
db.import_bank_of_canada_rates(xml_file)
