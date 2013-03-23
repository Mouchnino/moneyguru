# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import timedelta, date

from hscommon.trans import trget, tr
from hscommon.gui.column import Column
from ..model.account import AccountType
from ..model.amount import convert_amount
from ..model.date import DateRange
from .report import Report, get_delta_perc

trcol = trget('columns')

class BalanceSheet(Report):
    SAVENAME = 'BalanceSheet'
    COLUMNS = [
        Column('name', display=trcol("Account")),
        Column('account_number', display=trcol("Account #"), visible=False, optional=True),
        Column('end', display=trcol("End")),
        Column('start', display=trcol("Start"), optional=True),
        Column('delta', display=trcol("Change"), visible=False, optional=True),
        Column('delta_perc', display=trcol("Change %"), visible=False, optional=True),
        Column('budgeted', display=trcol("Budgeted"), optional=True),
    ]
    
    #--- Override
    def _compute_account_node(self, node):
        account = node.account
        date_range = self.document.date_range
        start_date = date_range.start
        end_date = date_range.end
        currency = self.document.default_currency
        start_amount = account.entries.normal_balance(start_date - timedelta(1))
        start_amount_native = account.entries.normal_balance(start_date - timedelta(1), currency=currency)
        end_amount = account.entries.normal_balance(end_date)
        end_amount_native = account.entries.normal_balance(end_date, currency=currency)
        budget_date_range = DateRange(date.today(), end_date)
        budgeted_amount = self.document.budgeted_amount_for_target(account, budget_date_range)
        budgeted_amount_native = convert_amount(budgeted_amount, currency, date_range.end)
        delta = end_amount - start_amount

        # Amounts for totals are converted in the document's currency
        node.start_amount = start_amount_native
        node.end_amount = end_amount_native
        node.budgeted_amount = budgeted_amount_native

        # Amounts for display are kept in the account's currency
        node.start = self.document.format_amount(start_amount)
        node.end = self.document.format_amount(end_amount)
        node.budgeted = self.document.format_amount(budgeted_amount)
        node.delta = self.document.format_amount(delta)
        node.delta_perc = get_delta_perc(delta, start_amount)
    
    def _make_node(self, name):
        node = Report._make_node(self, name)
        node.start = ''
        node.end = ''
        node.budgeted = ''
        node.delta = ''
        node.delta_perc = ''
        node.start_amount = 0
        node.end_amount = 0
        node.budgeted_amount = 0
        return node
    
    def _refresh(self):
        self.clear()
        self.assets = self.make_type_node(tr('ASSETS'), AccountType.Asset)
        self.liabilities = self.make_type_node(tr('LIABILITIES'), AccountType.Liability)
        self.net_worth = self._make_node(tr('NET WORTH'))
        net_worth_start = self.assets.start_amount - self.liabilities.start_amount
        net_worth_end = self.assets.end_amount - self.liabilities.end_amount
        budget_date_range = DateRange(date.today(), self.document.date_range.end)
        # The net worth's budget is not a simple subtraction, it must count the target-less budgets
        net_worth_budgeted = self.document.budgeted_amount_for_target(None, budget_date_range)
        net_worth_delta = net_worth_end - net_worth_start
        self.net_worth.start = self.document.format_amount(net_worth_start)
        self.net_worth.end = self.document.format_amount(net_worth_end)
        self.net_worth.budgeted = self.document.format_amount(net_worth_budgeted)
        self.net_worth.delta = self.document.format_amount(net_worth_delta)
        self.net_worth.delta_perc = get_delta_perc(net_worth_delta, net_worth_start)
        self.net_worth.is_total = True
        self.append(self.assets)
        self.append(self.liabilities)
        self.append(self.net_worth)
    
    #--- Public
    def make_total_node(self, parent, name):
        node = Report.make_total_node(self, name)
        currency = self.document.default_currency
        parent.start_amount = sum(child.start_amount for child in parent)
        parent.end_amount = sum(child.end_amount for child in parent)
        parent.budgeted_amount = sum(child.budgeted_amount for child in parent)
        delta_amount = parent.end_amount - parent.start_amount
        node.start = parent.start = self.document.format_amount(parent.start_amount)
        node.end = parent.end = self.document.format_amount(parent.end_amount)
        node.budgeted = parent.budgeted = self.document.format_amount(parent.budgeted_amount)
        node.delta = parent.delta = self.document.format_amount(delta_amount)
        node.delta_perc = parent.delta_perc = get_delta_perc(delta_amount, parent.start_amount)
        return node
    
