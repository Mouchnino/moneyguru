# Unit Name: moneyguru.gui.balance_graph
# Created By: Virgil Dupras
# Created On: 2008-07-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from __future__ import division
from datetime import date, timedelta

from ..model.date import DateRange
from .graph import Graph

class BalanceGraph(Graph):
    # BalanceGraph's data point is (float x, float y)
    #--- Virtual
    def _balance_for_date(self, date):
        if self._account is None:
            return 0
        entry = self._account.last_entry(date=date)
        return entry.normal_balance() if entry else 0
    
    def _budget_for_date(self, date):
        date_range = DateRange(date.min, date)
        return self.document.budgeted_amount_for_target(self._account, date_range)
    
    #--- Override
    # Computation Notes: When the balance in the graph changes, we have to create a flat line until
    # one day prior to the change. However, when budgets are involved, the line is *not* flattened.
    # To save some calculations (in a year range, those take a lot of time if they're made every day), 
    # rather than calculating the budget every day, they are only calculated when the balance without
    # budget changes. this is what the algorithm below reflects.
    def compute_data(self):
        self._account = self.document.selected_account
        date_range = self.document.date_range
        self._data = []
        last_balance = self._balance_for_date(date_range.start - timedelta(1))
        last_added_date = None
        if last_balance:
            budget = self._budget_for_date(date_range.start - timedelta(1))
            self._data.append((date_range.start.toordinal(), float(last_balance - budget)))
            last_added_date = date_range.start.toordinal() - 1
        for date in date_range:
            ordinal_date = date.toordinal()
            balance = self._balance_for_date(date)
            # For budgeting reasons, if date == date.today(), add a data point
            if (balance == last_balance) and (date != date.today()):
                continue
            if last_added_date and (last_added_date != ordinal_date - 1) and last_balance != balance:
                last_budget = self._budget_for_date(date - timedelta(days=1))
                self._data.append((ordinal_date, float(last_balance - last_budget)))
            budget = self._budget_for_date(date)
            self._data.append((ordinal_date + 1, float(balance - budget)))
            last_added_date = ordinal_date
            last_balance = balance
        if last_added_date and date_range.end.toordinal() > last_added_date:
            balance = self._balance_for_date(date_range.end)
            budget = self._budget_for_date(date_range.end)
            self._data.append((date_range.end.toordinal() + 1, float(balance - budget)))
    
    def yrange(self):
        if self._data:
            ymin = min(0, min(point[1] for point in self._data))
            ymax = max(0, ymin + 100, max(point[1] for point in self._data))
            return (ymin, ymax)
        else:
            return (0, 100)
    
    @property
    def title(self):
        return self.document.selected_account.name
    
    @property
    def currency(self):
        return self._account.currency
    
    @property
    def xtoday(self):
        """The X value representing today"""
        return date.today().toordinal() + 1
    
