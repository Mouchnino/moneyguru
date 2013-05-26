# This plugin subclasses CurrencyProviderPlugin to provide additional currencies, whose rates are
# provided by Yahoo.

from core.plugin import CurrencyProviderPlugin

# We use Python's built-in urlopen to hit Yahoo's server and fetch the rates
from urllib.request import urlopen

# To create a currency provider plugin, one must subclass CurrencyProviderPlugin. You can see more
# details about how to subclass it in plugins.py. It's accessible online at:
# https://bitbucket.org/hsoft/moneyguru/src/tip/core/plugin.py
class YahooProviderPlugin(CurrencyProviderPlugin):
    NAME = 'Yahoo currency rates fetcher'
    
    # First, we must tell moneyGuru what currencies we support. We have to return a list of tuples
    # containing the code, the name, the decimal precision and a fallback rate for each currencies
    # we want to support.
    def register_currencies(self):
        return [
            ('XAU', 'Gold (ounce)', 2, 1430.39),
            ('XAG', 'Silver (ounce)', 2, 23.13),
        ]
    
    # Then, we must implement the rate fetching method. It has to return a float rate that is the
    # value, today of 1 "currency_code" in CAD (Canadian Dollars).
    # This method is called asynchronously, it will not block moneyGuru if it takes a long time to
    # resolve.
    def get_currency_rate_today(self, currency_code):
        # the result of this request is a single CSV line like this:
        # "CADBHD=X",0.3173,"11/7/2008","5:11pm",N/A,N/A,N/A,N/A,N/A 
        try:
            url = 'http://download.finance.yahoo.com/d/quotes.csv?s=%sCAD=X&f=sl1d1t1c1ohgv&e=.csv' % currency_code
            with urlopen(url, timeout=10) as response:
                content = response.read().decode('latin-1')
            return float(content.split(',')[1])
        except Exception:
            return None
    
