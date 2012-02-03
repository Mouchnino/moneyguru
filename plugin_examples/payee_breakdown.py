# This plugin take all transactions in the current date range and adds all amount figures
# breaking totals by payee. This plugin assumes basic knowledge of the plugin structure. If you
# haven't already, take a look at account_list first.

# groupby takes a list and groups its elements according to a key (ours will be the payee attribute
# of each transaction)
from itertools import groupby
# attrgetter(name) is a convenience function that returns a function equivalent to
# lambda x: getattr(x, name). We use this to create sort and group keys on the payee attribute.
from operator import attrgetter

from core.plugin import ReadOnlyTablePlugin, Column
# Import convert_amount(), a utility function to convert amount from one currency to another.
from core.model.amount import convert_amount

class PayeeBreakdownPlugin(ReadOnlyTablePlugin):
    NAME = 'Payee Breakdown'
    
    COLUMNS = [
        Column('payee', "Payee"),
        Column('count', "# Transactions"),
        Column('amount', "Total Amount"),
    ]
    
    def fill_table(self):
        # The currently selected date range
        date_range = self.document.date_range
        # We fetch transactions from our document's "oven". We could fetch them directly from
        # document.transactions, but then we wouldn't have schedule spawns. The oven takes "raw"
        # transactions and schedules and "cooks" them into ready-to-display transactions and
        # schedule spawns. It's better to fetch transactions there.
        transactions = self.document.oven.transactions
        # We don't want all transactions, only those in the current date range, so we filter
        # them to only keep transactions with a date that fits in the range.
        transactions = [t for t in transactions if t.date in date_range]
        # Sort the transactions by payee so that we can group them.
        transactions.sort(key=attrgetter('payee'))
        # It's impossible to mix amount of different currencies together. However, it's possible
        # for us to have two transactions with the same payee but with a different currency.
        # Therefore, we'll do like we do in the rest of moneyGuru: we'll convert all foreign
        # currencies in our native currency. For this, we need to fetch our native currency.
        currency = self.document.default_currency
        # Group our sorted transactions by payee using itertools.groupby().
        for payee, subtransactions in groupby(transactions, key=attrgetter('payee')):
            # We ignore all transactions with an empty payee or a payee containing only whitespaces
            # (which is why we call strip()).
            if not payee.strip():
                continue
            # groupby() returns an iterator, but because we want to count the number of
            # transactions we have, we need to convert it to a list.
            subtransactions = list(subtransactions)
            total_amount = 0
            count = len(subtransactions)
            for txn in subtransactions:
                # Convert the transactions's amount to the native currency.
                native_amount = convert_amount(txn.amount, currency, txn.date)
                # Add that amount to the running total
                total_amount += native_amount
            row = self.add_row()
            row.set_field('payee', payee)
            # When we set field values, we set strings. However, our table can be sorted by any
            # column and when doing so, that column needs to know how to sort. By default, it uses
            # the display value (which works well in many cases), but sometimes it's wrong. For
            # example, if we sort counts as strings, '10' would be lower than '9' because the first
            # digit, '1' is lower than '9'. That is why we need to supply our row with a
            # 'sort_value' which is an integer instead of a string, which will allow the table to
            # correctly do its sorting.
            row.set_field('count', str(count), sort_value=count)
            # Amounts aren't strings and need to be formatted before being displayed. This
            # formatting depends on the users system settings. In document.app, we have a utility
            # function to do that.
            total_amount_fmt = self.document.app.format_amount(total_amount)
            row.set_field('amount', total_amount_fmt, sort_value=total_amount)
    
