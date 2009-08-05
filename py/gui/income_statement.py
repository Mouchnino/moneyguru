# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..model.account import INCOME, EXPENSE
from .report import Report, Node, get_delta_perc

class IncomeStatement(Report):
    #--- Override
    def _compute_account_node(self, node):
        account = node.account
        date_range = self.document.date_range
        currency = self.app.default_currency
        cash_flow = account.normal_cash_flow(date_range)
        cash_flow_native = account.normal_cash_flow(date_range, currency)
        last_cash_flow = account.normal_cash_flow(date_range.prev())
        last_cash_flow_native = account.normal_cash_flow(date_range.prev(), currency)
        budgeted = self.document.normal_budgeted_amount(account, date_range)
        budgeted_native = self.document.normal_budgeted_amount(account, date_range, currency)
        last_budgeted = self.document.normal_budgeted_amount(account, date_range.prev())
        last_budgeted_native = self.document.normal_budgeted_amount(account, date_range.prev(), currency)
        total_cash_flow = cash_flow + budgeted
        last_total_cash_flow = last_cash_flow + last_budgeted
        delta = total_cash_flow - last_total_cash_flow

        # Amounts for totals are converted in the document's currency
        node.cash_flow_amount = cash_flow_native + budgeted_native
        node.last_cash_flow_amount = last_cash_flow_native + last_budgeted_native

        # Amounts for display are kept in the account's currency
        node.cash_flow = self.app.format_amount(total_cash_flow)
        node.last_cash_flow = self.app.format_amount(last_total_cash_flow)
        node.delta = self.app.format_amount(delta)
        node.delta_perc = get_delta_perc(delta, last_total_cash_flow)
    
    def _make_node(self, name):
        node = Report._make_node(self, name)
        node.cash_flow = ''
        node.last_cash_flow = ''
        node.delta = ''
        node.delta_perc = ''
        node.cash_flow_amount = 0
        node.last_cash_flow_amount = 0
        return node
    
    def _refresh(self):
        self.clear()
        self.income = self.make_type_node('INCOME', INCOME)
        self.expenses = self.make_type_node('EXPENSES', EXPENSE)
        self.net_income = Node(self, 'NET INCOME')
        net_income = self.income.cash_flow_amount - self.expenses.cash_flow_amount
        last_net_income = self.income.last_cash_flow_amount - self.expenses.last_cash_flow_amount
        delta = net_income - last_net_income
        self.net_income.cash_flow = self.app.format_amount(net_income)
        self.net_income.last_cash_flow = self.app.format_amount(last_net_income)
        self.net_income.delta = self.app.format_amount(delta)
        self.net_income.delta_perc = get_delta_perc(delta, last_net_income)
        self.net_income.is_total = True
        self.append(self.income)
        self.append(self.expenses)
        self.append(self.net_income)
    
    #--- Public
    def make_total_node(self, parent, name):
        node = Report.make_total_node(self, name)
        parent.cash_flow_amount = sum(child.cash_flow_amount for child in parent)
        parent.last_cash_flow_amount = sum(child.last_cash_flow_amount for child in parent)
        delta = parent.cash_flow_amount - parent.last_cash_flow_amount
        node.cash_flow = parent.cash_flow = self.app.format_amount(parent.cash_flow_amount)
        node.last_cash_flow = parent.last_cash_flow = self.app.format_amount(parent.last_cash_flow_amount)
        node.delta = parent.delta = self.app.format_amount(delta)
        node.delta_perc = parent.delta_perc = get_delta_perc(delta, parent.last_cash_flow_amount)
        return node
    
