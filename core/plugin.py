# Created On: 2012/02/02
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.gui.column import Column
from hscommon.currency import Currency, CurrencyNotSupportedException

from .gui.base import BaseView
from .gui.table import GUITable, Row
from .const import PaneType

class Plugin:
    NAME = ''
    IS_VIEW = False

class ViewPlugin:
    IS_VIEW = True
    
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.document = mainwindow.document
    
class ReadOnlyTableRow(Row):
    def set_field(self, name, value, sort_value=None):
        setattr(self, name, value)
        if sort_value is not None:
            setattr(self, '_'+name, sort_value)
        
    
class ReadOnlyTable(GUITable):
    def __init__(self, plugin):
        self.plugin = plugin
        self.COLUMNS = plugin.COLUMNS
        GUITable.__init__(self, plugin.document)
    
    def _fill(self):
        self.plugin.fill_table()
    

class ReadOnlyTableView(BaseView):
    VIEW_TYPE = PaneType.ReadOnlyTablePlugin
    
    def __init__(self, plugin):
        BaseView.__init__(self, plugin.mainwindow)
        self.plugin = plugin
        self.table = ReadOnlyTable(plugin)
        self.bind_messages(self.INVALIDATING_MESSAGES, self._revalidate)
    
    def _revalidate(self):
        self.table.refresh_and_show_selection()
    

class ReadOnlyTablePlugin(ViewPlugin):
    COLUMNS = []
    
    def __init__(self, mainwindow):
        ViewPlugin.__init__(self, mainwindow)
        self.view = ReadOnlyTableView(self)
        self.table = self.view.table
    
    def add_row(self):
        row = ReadOnlyTableRow(self.table)
        self.table.append(row)
        return row
    
    def fill_table(self):
        raise NotImplementedError()
    
class CurrencyProviderPlugin(Plugin):
    def __init__(self):
        Plugin.__init__(self)
        self.supported_currency_codes = set()
        for code, name, exponent, fallback_rate in self.register_currencies():
            Currency.register(code, name, exponent, latest_rate=fallback_rate)
            self.supported_currency_codes.add(code)
    
    def wrapped_get_currency_rates(self, currency_code, start_date, end_date):
        # Do not override
        if currency_code not in self.supported_currency_codes:
            raise CurrencyNotSupportedException()
        try:
            simple_result = self.get_currency_rate_today(currency_code)
            if simple_result is not None:
                return [(date.today(), simple_result)]
            else:
                return []
        except NotImplementedError:
            try:
                return self.get_currency_rates(currency_code, start_date, end_date)
            except NotImplementedError:
                raise CurrencyNotSupportedException()
    
    def register_currencies(self):
        """Override this and return a list of new currencies to support.
        
        The expected return value is a list of tuples (code, name, exponent, fallback_rate).
        
        exponent is the number of decimal numbers that should be displayed when formatting amounts
        in this currency.
        
        fallback_rate is the rate to use in case we can't fetch a rate. You can use the rate that is
        in effect when you write the plugin. Of course, it will become wildly innaccurate over time,
        but it's still better than a rate of 1.
        """
        raise NotImplementedError()
    
    def get_currency_rate_today(self, currency_code):
        """Override this if you have a 'simple' provider.
        
        If your provider doesn't give rates for any other date than today, overriding this method
        instead of get_currency_rate() is the simplest choice.
        
        `currency_code` is a string representing the code of the currency to fetch, 'USD' for
        example.
        
        Return a float representing the value of 1 unit of your currency in CAD.
        
        If you can't get a rate, return None.
        
        This method is called asynchronously, so it won't block moneyGuru if it takes time to
        resolve.
        """
    
    def get_currency_rates(self, currency_code, start_date, end_date):
        """Override this if your provider gives rates for past dates.
        
        If your provider gives rates for past dates, it's better (although a bit more complicated)
        to override this method so that moneyGuru can have more accurate rates.
        
        You must return a list of tuples (date, rate) with all rates you can fetch between
        start_date and end_date. You don't need to have one item for every single date in the range
        (for example, most of the time we don't have values during week-ends), moneyGuru correctly
        handles holes in those values. Simply return whatever you can get.
        
        If you can't get a rate, return an empty list.
        
        This method is called asynchronously, so it won't block moneyGuru if it takes time to
        resolve.
        """
        raise NotImplementedError()
    
