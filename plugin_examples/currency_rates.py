# This plugin makes a list of all currencies used in our document and lists their respective rate
# in our native currency. This plugin assumes basic knowledge of the plugin structure. If you
# haven't already, take a look at account_list first. payee_breakdown is a good preliminary
# reading too.

from datetime import date

# flatten(list) transforms [[1, 2], [3, 4]] into [1, 2, 3, 4]. We'll need this to have a list of all
# splits in our transactions.
from hscommon.util import flatten
from core.plugin import ReadOnlyTablePlugin, Column

class CurrencyRatesPlugin(ReadOnlyTablePlugin):
    NAME = 'Currency Rates'
    
    # The columns that will be present in our table. For each column we add here, we have to set
    # a field value in each row we'll add in fill_table().
    COLUMNS = [
        Column('name', "Currency"),
        Column('rate', "(will change dynamically)"),
    ]
    
    def __init__(self, mainwindow):
        ReadOnlyTablePlugin.__init__(self, mainwindow)
        native_currency = self.document.default_currency
        # A little hack to dynamically change our column title
        self.table.columns.column_by_name('rate').display = "Value in " + native_currency.code
    
    def fill_table(self):
        native_currency = self.document.default_currency
        # Create a list of all splits so that we can access all our amounts.
        allsplits = flatten(t.splits for t in self.document.transactions)
        # Create a set of all used currencies
        currencies = {s.amount.currency for s in allsplits}
        for currency in currencies:
            row = self.add_row()
            row.set_field('name', currency.name)
            # currencies have a value_in(other_currency, at_date) returning the exchange rathe
            # at the given date as a float value.
            exchange_rate = currency.value_in(native_currency, date.today())
            row.set_field('rate', '%0.4f' % exchange_rate, sort_value=exchange_rate)
    