# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division
from datetime import date, timedelta

from ..model.date import DateRange, ONE_DAY
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
        self._account = self.document.shown_account
        date_range = self.document.date_range
        TODAY = date.today()
        date2value = {}
        last_balance = self._balance_for_date(date_range.start - ONE_DAY)
        if last_balance:
            date2value[date_range.start] = last_balance
        for date_point in date_range:
            balance = self._balance_for_date(date_point)
            if (balance != last_balance) or (date_point == TODAY) or (date_point == date_range.end):
                if date2value and last_balance != balance:
                    # create a "step"
                    date2value[date_point] = last_balance
                date2value[date_point + ONE_DAY] = balance
                last_balance = balance
        for date_point, value in date2value.items():
            if date_point <= TODAY:
                continue
            budget = self._budget_for_date(date_point - ONE_DAY)
            if budget:
                date2value[date_point] += budget
        if date_range.start not in date2value and date_range.start > TODAY:
            budget = self._budget_for_date(date_range.start - ONE_DAY)
            date2value[date_range.start] = budget
        self._data = []
        # if there's only zeroes, keep the data empty
        if any(date2value.values()):
            for date_point, value in sorted(date2value.items()):
                self._data.append((date_point.toordinal(), float(value)))
    
    def yrange(self):
        if self._data:
            ymin = min(0, min(point[1] for point in self._data))
            ymax = max(0, ymin + 100, max(point[1] for point in self._data))
            return (ymin, ymax)
        else:
            return (0, 100)
    
    @property
    def title(self):
        return self.document.shown_account.name
    
    @property
    def currency(self):
        return self._account.currency
    
    @property
    def xtoday(self):
        """The X value representing today"""
        return date.today().toordinal() + 1
    
    #--- Event Handlers
    account_must_be_shown = Graph._data_changed
