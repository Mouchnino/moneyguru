# Unit Name: moneyguru.gui.balance_sheet
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from __future__ import division
from datetime import timedelta, date

from ..model.account import ASSET, LIABILITY
from ..model.amount import convert_amount
from ..model.date import DateRange, ONE_DAY
from .report import Report, Node, get_delta_perc

class BalanceSheet(Report):
    #--- Override
    def _compute_account_node(self, node):
        account = node.account
        date_range = self.document.date_range
        start_date = date_range.start
        end_date = date_range.end
        currency = self.app.default_currency
        start_amount = account.normal_balance(start_date - timedelta(1))
        start_amount_native = account.normal_balance(start_date - timedelta(1), currency=currency)
        end_amount = account.normal_balance(end_date)
        end_amount_native = account.normal_balance(end_date, currency=currency)
        budgeted_amount = self.document.budgeted_amount_for_target(account, date_range)
        budgeted_amount_native = convert_amount(budgeted_amount, currency, date_range.end)
        prev_date_range = DateRange(date.min, date_range.start - ONE_DAY)
        prev_budgeted_amount = self.document.budgeted_amount_for_target(account, prev_date_range)
        prev_budgeted_amount_native = convert_amount(prev_budgeted_amount, currency, date_range.start)
        # budgeted_amount is not normalized. We *subtract* here because what we want to do is to
        # reflect the "other side" of the budget. Therefore, if 100$ is budgeted for an income,
        # budgeted_amount will be -100. We must subtract -100 from end_amount to get the projected
        # amount
        start_amount_final = start_amount - prev_budgeted_amount
        start_amount_native_final = start_amount_native - prev_budgeted_amount_native
        end_amount_final = end_amount - prev_budgeted_amount - budgeted_amount
        end_amount_native_final = end_amount_native - budgeted_amount_native - prev_budgeted_amount_native
        delta = end_amount_final - start_amount

        # Amounts for totals are converted in the document's currency
        node.start_amount = start_amount_native_final
        node.end_amount = end_amount_native_final

        # Amounts for display are kept in the account's currency
        node.start = self.app.format_amount(start_amount_final)
        node.end = self.app.format_amount(end_amount_final)
        node.delta = self.app.format_amount(delta)
        node.delta_perc = get_delta_perc(delta, start_amount_final)
    
    def _make_node(self, name):
        node = Report._make_node(self, name)
        node.start = ''
        node.end = ''
        node.delta = ''
        node.delta_perc = ''
        node.start_amount = 0
        node.end_amount = 0
        return node
    
    def _refresh(self):
        self.clear()
        self.assets = self.make_type_node('ASSETS', ASSET)
        self.liabilities = self.make_type_node('LIABILITIES', LIABILITY)
        self.net_worth = Node(self, 'NET WORTH')
        net_worth_start = self.assets.start_amount - self.liabilities.start_amount
        net_worth_end = self.assets.end_amount - self.liabilities.end_amount
        net_worth_delta = net_worth_end - net_worth_start
        self.net_worth.start = self.app.format_amount(net_worth_start)
        self.net_worth.end = self.app.format_amount(net_worth_end)
        self.net_worth.delta = self.app.format_amount(net_worth_delta)
        self.net_worth.delta_perc = get_delta_perc(net_worth_delta, net_worth_start)
        self.net_worth.is_total = True
        self.append(self.assets)
        self.append(self.liabilities)
        self.append(self.net_worth)
    
    #--- Public
    def make_total_node(self, parent, name):
        node = Report.make_total_node(self, name)
        currency = self.app.default_currency
        parent.start_amount = sum(child.start_amount for child in parent)
        parent.end_amount = sum(child.end_amount for child in parent)
        delta_amount = parent.end_amount - parent.start_amount
        node.start = parent.start = self.app.format_amount(parent.start_amount)
        node.end = parent.end = self.app.format_amount(parent.end_amount)
        node.delta = parent.delta = self.app.format_amount(delta_amount)
        node.delta_perc = parent.delta_perc = get_delta_perc(delta_amount, parent.start_amount)
        return node
    
