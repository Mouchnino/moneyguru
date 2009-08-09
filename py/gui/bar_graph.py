# Created By: Virgil Dupras
# Created On: 2008-07-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division
from datetime import date, timedelta

from ..model.date import DateRange, MonthRange, YearToDateRange
from .graph import Graph

class BarGraph(Graph):
    # BarGraph's data point is (float x1, float x2, float past_value, float future_value).
    #--- Virtual
    def _currency(self):
        account = self.document.selected_account
        return account.currency
    
    def _get_cash_flow(self, date_range):
        self.document.oven.continue_cooking(date_range.end) # it's possible that the overflow is not cooked
        account = self.document.selected_account
        currency = self._currency()
        cash_flow = account.normal_cash_flow(date_range, currency=currency)
        budgeted = self.document.budgets.normal_amount_for_account(account, date_range, currency=currency)
        return cash_flow + budgeted
    
    #--- Override
    def compute_data(self):
        def monthly_period(start_date):
            return MonthRange(start_date)
        
        def weekly_period(start_date):
            first_weekday = self.app.first_weekday
            weekday = start_date.weekday()
            if weekday < first_weekday:
                weekday += 7
            diff = weekday - first_weekday
            period_start = start_date - timedelta(diff)
            period_end = period_start + timedelta(6)
            return DateRange(period_start, period_end)
        
        TODAY = date.today()
        date_range = self.document.date_range
        self._data = []
        self._min_date = date_range.start
        self._max_date = date_range.end
        period_getter = monthly_period if date_range.days >= 100 else weekly_period
        current_date = date_range.start
        while current_date <= date_range.end:
            period = period_getter(current_date)
            if isinstance(date_range, YearToDateRange): # we don't overflow in YTD
                period.end = min(period.end, self._max_date)
            self._min_date = min(period.start, self._min_date)
            self._max_date = max(period.end + timedelta(1), self._max_date)
            current_date = period.end + timedelta(1)
            if TODAY in period:
                past_amount = float(self._get_cash_flow(period.past))
                future_amount = float(self._get_cash_flow(period.future))
            else:
                amount = float(self._get_cash_flow(period))
                if TODAY > period.end: # all in the past
                    past_amount = amount
                    future_amount = 0
                else: # all in the future
                    future_amount = amount
                    past_amount = 0
            if past_amount + future_amount:
                left = period.start.toordinal()
                right = period.end.toordinal() + 1 # we want a 1 day period to have a width of 1
                padding = (right - left) / 5
                self._data.append((left + padding, right - padding, past_amount, future_amount))
    
    def compute_x_axis(self):
        Graph.compute_x_axis(self)
        self._xmin = self._min_date.toordinal()
        self._xmax = self._max_date.toordinal()
    
    def yrange(self):
        if self._data:
            ymin = min(0, min(min(h1, h2, h1+h2) for x1, x2, h1, h2 in self._data))
            ymax = max(0, ymin + 100, max(max(h1, h2, h1+h2) for x1, x2, h1, h2 in self._data))
            return (ymin, ymax)
        else:
            return (0, 100)
    
    @property
    def title(self):
        return self.document.selected_account.name
    
    @property
    def currency(self):
        return self._currency()
    
    #--- Event Handlers
    def first_weekday_changed(self):
        self.compute()
        self.view.refresh()
    

