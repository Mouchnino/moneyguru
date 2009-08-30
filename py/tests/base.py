# coding: utf-8 
# Created By: Virgil Dupras
# Created On: 2009-06-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op
import xmlrpclib
from collections import defaultdict
from datetime import date, datetime
from operator import attrgetter

from nose.tools import nottest, istest, eq_

from hsutil.path import Path
from hsutil.testcase import TestCase

from ..app import Application
from ..const import UNRECONCILIATION_CONTINUE
from ..document import Document
from ..exception import FileFormatError
from ..gui.account_panel import AccountPanel
from ..gui.account_pie_chart import AssetsPieChart, LiabilitiesPieChart, IncomePieChart, ExpensesPieChart
from ..gui.account_reassign_panel import AccountReassignPanel
from ..gui.balance_graph import BalanceGraph
from ..gui.balance_sheet import BalanceSheet
from ..gui.bar_graph import BarGraph
from ..gui.budget_panel import BudgetPanel
from ..gui.budget_table import BudgetTable
from ..gui.csv_options import CSVOptions
from ..gui.custom_date_range_panel import CustomDateRangePanel
from ..gui.entry_table import EntryTable
from ..gui.filter_bar import FilterBar, EntryFilterBar
from ..gui.income_statement import IncomeStatement
from ..gui.import_table import ImportTable
from ..gui.import_window import ImportWindow
from ..gui.main_window import MainWindow
from ..gui.mass_edition_panel import MassEditionPanel
from ..gui.net_worth_graph import NetWorthGraph
from ..gui.profit_graph import ProfitGraph
from ..gui.schedule_panel import SchedulePanel
from ..gui.schedule_table import ScheduleTable
from ..gui.search_field import SearchField
from ..gui.split_table import SplitTable
from ..gui.transaction_panel import TransactionPanel
from ..gui.transaction_table import TransactionTable
from ..loader import base
from ..model.account import ASSET, LIABILITY, INCOME, EXPENSE
from ..model.currency import RatesDB
from ..model.date import MonthRange
from ..model import currency as currency_module
from .. import document as document_module

class CallLogger(object):
    """This is a dummy object that logs all calls made to it.
    
    It will be used to simulate the GUI layer."""
    def __init__(self):
        self.calls = defaultdict(int)

    def __getattr__(self, func_name):
        def func(*args, **kw):
            self.calls[func_name] += 1
        return func

def log(method):
    def wrapper(self, *args, **kw):
        result = method(self, *args, **kw)
        self.calls[method.func_name] += 1
        return result
    
    return wrapper

class ApplicationGUI(CallLogger):
    def __init__(self):
        CallLogger.__init__(self)
        self.defaults = {}
    
    def get_default(self, key): # We don't want to log this one. It disturbs other test and is pointless to log
        return self.defaults.get(key)
    
    @log
    def set_default(self, key, value):
        self.defaults[key] = value
    

class DocumentGUI(CallLogger):
    def __init__(self):
        CallLogger.__init__(self)
        self.confirm_unreconciliation_result = UNRECONCILIATION_CONTINUE
        self.query_for_schedule_scope_result = False
    
    @log
    def confirm_unreconciliation(self, affected_split_count):
        # We usually only care about the last call
        self.last_affected_split_count = affected_split_count
        return self.confirm_unreconciliation_result
    
    @log
    def query_for_schedule_scope(self):
        return self.query_for_schedule_scope_result
    

class MainWindowGUI(CallLogger):
    """A mock window gui that connects/disconnects its children guis as the real interface does"""
    def __init__(self, etable, ttable, sctable, btable, bsheet, istatement, balgraph, bargraph, nwgraph, pgraph, 
                 efbar, tfbar, apie, lpie, ipie, epie, cdrpanel, arpanel):
        CallLogger.__init__(self)
        self.etable = etable
        self.ttable = ttable
        self.sctable = sctable
        self.btable = btable
        self.bsheet = bsheet
        self.istatement = istatement
        self.balgraph = balgraph
        self.bargraph = bargraph
        self._last_shown = balgraph # we need to remember it, the GUI side remembers
        # In the real GUI, it is not MainWindow's responsibility to connect/disconnect those, but
        # for the sake of the test suite simplicity, we do it here.
        self.efbar = efbar
        self.tfbar = tfbar
        self.apie = apie
        self.lpie = lpie
        self.ipie = ipie
        self.epie = epie
        self.nwgraph = nwgraph
        self.pgraph = pgraph
        self.cdrpanel = cdrpanel
        self.arpanel = arpanel
        self.views = [etable, ttable, sctable, btable, bsheet, istatement, efbar, tfbar, apie, lpie,
            ipie, epie, nwgraph, pgraph, balgraph, bargraph]
    
    def connect_views(self, views):
        for candidate in self.views:
            if candidate not in views:
                candidate.disconnect()
            else:
                candidate.connect()
    
    @log
    def show_account_reassign_panel(self):
        self.arpanel.load()
    
    @log
    def show_balance_sheet(self):
        self.connect_views([self.bsheet, self.apie, self.lpie, self.nwgraph])
    
    @log
    def show_bar_graph(self):
        self.balgraph.disconnect()
        self.bargraph.connect()
        self._last_shown = self.bargraph
    
    @log
    def show_custom_date_range_panel(self):
        self.cdrpanel.load()
    
    @log
    def show_entry_table(self):
        self.connect_views([self.etable, self.efbar, self._last_shown])
    
    @log
    def show_income_statement(self):
        self.connect_views([self.istatement, self.ipie, self.epie, self.pgraph])
    
    @log
    def show_line_graph(self):
        self.bargraph.disconnect()
        self.balgraph.connect()
        self._last_shown = self.balgraph
    
    @log
    def show_schedule_table(self):
        self.connect_views([self.sctable])
    
    @log
    def show_budget_table(self):
        self.connect_views([self.btable])
    
    @log
    def show_transaction_table(self):
        self.connect_views([self.ttable, self.tfbar])
    

class DictLoader(base.Loader):
    """Used for fake_import"""
    def __init__(self, default_currency, account_name, transactions):
        base.Loader.__init__(self, default_currency)
        self.account_name = account_name
        self.transaction_dicts = transactions
    
    def _parse(self, infile):
        pass
    
    def _load(self):
        self.account_info.name = self.account_name
        for txn in self.transaction_dicts:
            self.start_transaction()
            for attr, value in txn.items():
                if attr == 'date':
                    value = datetime.strptime(value, '%d/%m/%Y').date()
                setattr(self.transaction_info, attr, value)

@istest # nose is sometimes confused. This is to make sure that no test is ignored.
class TestCase(TestCase):
    cls_tested_module = document_module # for mocks
    
    def assert_gui_calls_equal(self, guicalls, expected):
        for callname, callcount in expected.items():
            if callcount == 0: # This means we just want to make sure that `callname` hasn't been called
                assert callname not in guicalls,\
                    "'%s' was not supposed to be called, but was called %d times" % (callname, guicalls[callname])
                del expected[callname]
        eq_(guicalls, expected)
    
    @classmethod
    def datadirpath(cls):
        return Path(__file__)[:-1] + 'testdata'
    
    def superSetUp(self):
        # During tests, we don't want the rates db to hit the currency server
        self.mock(RatesDB, 'ensure_rates', lambda *a, **kw: None)
        currency_module.initialize_db(':memory:')
        def raise_if_called(*args, **kwargs):
            raise Exception('This is not supposed to be used in a test case')
        self.mock(xmlrpclib, 'ServerProxy', raise_if_called)
    
    def check_gui_calls(self, gui, **expected):
        """Checks that the expected calls have been made to 'gui', then clears the log."""
        self.assert_gui_calls_equal(gui.calls, expected)
        gui.calls.clear()
    
    def check_gui_calls_partial(self, gui, **expected):
        """Check that **expected has been called, but ignore other calls"""
        calls = dict((k, v) for k, v in gui.calls.items() if k in expected)
        self.assert_gui_calls_equal(calls, expected)
        gui.calls.clear()
    
    def clear_gui_calls(self):
        for attr in dir(self):
            if attr.endswith('_gui'):
                gui = getattr(self, attr)
                gui.calls.clear()

    def create_instances(self):
        """Creates a Document instance along with all gui layers attached to it.
        
        If you want to create an Application or a Document instance with non-blank args, create it 
        first then call create_instance.
        """
        if not hasattr(self, 'app'):
            self.app_gui = ApplicationGUI()
            self.app = Application(self.app_gui)
        if not hasattr(self, 'document'):
            self.document_gui = DocumentGUI()
            self.document = Document(self.document_gui, self.app)
        self.apanel_gui = CallLogger()
        self.apanel = AccountPanel(self.apanel_gui, self.document)
        self.arpanel_gui = CallLogger()
        self.arpanel = AccountReassignPanel(self.arpanel_gui, self.document)
        self.etable_gui = CallLogger()
        self.etable = EntryTable(self.etable_gui, self.document)
        self.ttable_gui = CallLogger()
        self.ttable = TransactionTable(self.ttable_gui, self.document)
        self.sctable_gui = CallLogger()
        self.sctable = ScheduleTable(self.sctable_gui, self.document)
        self.btable_gui = CallLogger()
        self.btable = BudgetTable(self.btable_gui, self.document)
        self.scpanel_gui = CallLogger()
        self.scpanel = SchedulePanel(self.scpanel_gui, self.document)
        self.tpanel_gui = CallLogger()
        self.tpanel = TransactionPanel(self.tpanel_gui, self.document)
        self.mepanel_gui = CallLogger()
        self.mepanel = MassEditionPanel(self.mepanel_gui, self.document)
        self.bpanel_gui = CallLogger()
        self.bpanel = BudgetPanel(self.bpanel_gui, self.document)
        self.stable_gui = CallLogger()
        self.stable = SplitTable(self.stable_gui, self.tpanel)
        self.scsplittable_gui = CallLogger()
        self.scsplittable = SplitTable(self.scsplittable_gui, self.scpanel)
        self.balgraph_gui = CallLogger()
        self.balgraph = BalanceGraph(self.balgraph_gui, self.document)
        self.bargraph_gui = CallLogger()
        self.bargraph = BarGraph(self.bargraph_gui, self.document)
        self.nwgraph_gui = CallLogger()
        self.nwgraph = NetWorthGraph(self.nwgraph_gui, self.document)
        self.pgraph_gui = CallLogger()
        self.pgraph = ProfitGraph(self.pgraph_gui, self.document)
        self.bsheet_gui = CallLogger()
        self.bsheet = BalanceSheet(self.bsheet_gui, self.document)
        self.apie_gui = CallLogger()
        self.apie = AssetsPieChart(self.apie_gui, self.document)
        self.lpie_gui = CallLogger()
        self.lpie = LiabilitiesPieChart(self.lpie_gui, self.document)
        self.ipie_gui = CallLogger()
        self.ipie = IncomePieChart(self.ipie_gui, self.document)
        self.epie_gui = CallLogger()
        self.epie = ExpensesPieChart(self.epie_gui, self.document)
        self.istatement_gui = CallLogger()
        self.istatement = IncomeStatement(self.istatement_gui, self.document)
        self.sfield_gui = CallLogger()
        self.sfield = SearchField(self.sfield_gui, self.document)
        # There are 2 filter bars: one for etable, one for ttable
        self.efbar_gui = CallLogger()
        self.efbar = EntryFilterBar(self.efbar_gui, self.document)
        self.tfbar_gui = CallLogger()
        self.tfbar = FilterBar(self.tfbar_gui, self.document)
        self.csvopt_gui = CallLogger()
        self.csvopt = CSVOptions(self.csvopt_gui, self.document)
        self.iwin_gui = CallLogger()
        self.iwin = ImportWindow(self.iwin_gui, self.document)
        self.itable_gui = CallLogger()
        self.itable = ImportTable(self.itable_gui, self.iwin)
        self.cdrpanel_gui = CallLogger()
        self.cdrpanel = CustomDateRangePanel(self.cdrpanel_gui, self.document)
        self.mainwindow_gui = MainWindowGUI(self.etable, self.ttable, self.sctable, self.btable, 
            self.bsheet, self.istatement, self.balgraph, self.bargraph, self.nwgraph, self.pgraph, 
            self.efbar, self.tfbar, self.apie, self.lpie, self.ipie, self.epie, self.cdrpanel, 
            self.arpanel)
        children = [self.bsheet, self.istatement, self.ttable, self.etable, self.sctable,
            self.btable, self.apanel, self.tpanel, self.mepanel, self.scpanel, self.bpanel]
        self.mainwindow = MainWindow(self.mainwindow_gui, self.document, children)
        self.document.connect()
        self.mainwindow.connect()
        self.stable.connect()
        self.sfield.connect()
        self.iwin.connect()
        self.itable.connect()
        self.csvopt.connect()
        self.cdrpanel.connect()
        # For the sake of simplicity, the scpanel is permanently connected, but in the real cocoa
        # code, the sctable is responsible for connecting it.
        self.scpanel.connect()
    
    def add_account(self, name=None, currency=None, account_type=ASSET, group_name=None, select=True):
        # I wanted to use the panel here, it messes with the undo tests, we'll have to fix this eventually
        group = self.document.groups.find(group_name, account_type) if group_name else None
        account = self.document.new_account(account_type, group)
        if name is not None:
            self.document.change_account(account, name=name)
        if currency is not None:
            self.document.change_account(account, currency=currency)
        self.document.select_account(account)
        if select:
            self.document.show_selected_account()
    
    def add_accounts(self, *names):
        # add a serie of simple accounts, *names being names for each account
        for name in names:
            self.add_account(name)
    
    def add_budget(self, account_name, target_name, str_amount, start_date=None, repeat_type_index=2):
        # if no target, set target_name to None
        self.mainwindow.select_budget_table()
        self.mainwindow.new_item()
        if start_date is None:
            start_date = self.app.format_date(date(date.today().year, date.today().month, 1))
        self.bpanel.start_date = start_date
        self.bpanel.repeat_type_index = repeat_type_index
        account_index = self.bpanel.account_options.index(account_name)
        self.bpanel.account_index = account_index
        target_index = self.bpanel.target_options.index(target_name) if target_name else 0
        self.bpanel.target_index = target_index
        self.bpanel.amount = str_amount
        self.bpanel.save()
    
    def add_entry(self, date=None, description=None, payee=None, transfer=None, increase=None, decrease=None, checkno=None):
        # This whole "if not None" thing allows to simulate a user tabbing over fields leaving the default value.
        self.etable.add()
        row = self.etable.edited
        if date is not None:
            row.date = date
        if description is not None:
            row.description = description
        if payee is not None:
            row.payee = payee
        if transfer is not None:
            row.transfer = transfer
        if increase is not None:
            row.increase = increase
        if decrease is not None:
            row.decrease = decrease
        if checkno is not None:
            row.checkno = checkno
        self.etable.save_edits()

    def add_group(self, name=None, account_type=ASSET):
        group = self.document.new_group(account_type)
        if name is not None:
            self.document.change_group(group, name=name)
    
    def add_txn(self, date=None, description=None, payee=None, from_=None, to=None, amount=None,
                checkno=None):
        self.mainwindow.select_transaction_table()
        self.ttable.add()
        row = self.ttable.edited
        if date is not None:
            row.date = date
        if description is not None:
            row.description = description
        if payee is not None:
            row.payee = payee
        if from_ is not None:
            row.from_ = from_
        if to is not None:
            row.to = to
        if amount is not None:
            row.amount = amount
        if checkno is not None:
            row.checkno = checkno
        self.ttable.save_edits()
    
    def account_names(self): # doesn't include Imbalance
        account_sort = {ASSET:0, LIABILITY: 1, INCOME: 2, EXPENSE: 3}
        accounts = list(self.document.accounts)
        accounts.sort(key=lambda a: (account_sort[a.type], a))
        return [a.name for a in accounts]
    
    def balances(self):
        return [self.etable[i].balance for i in range(len(self.etable))]
    
    def bar_graph_data(self):
        result = []
        for x1, x2, y1, y2 in self.bargraph.data:
            # We have to account for the padding...
            padding = (x2 - x1) / 3
            x1 = int(round(x1 - padding))
            x2 = int(round(x2 + padding))
            convert = lambda i: date.fromordinal(i).strftime('%d/%m/%Y')
            result.append((convert(x1), convert(x2), '%2.2f' % y1, '%2.2f' % y2))
        return result
    
    def close_and_load(self):
        self.document.close()
        self.app = Application(self.app_gui)
        self.document = Document(self.document_gui, self.app)
        self.create_instances()
    
    def entry_descriptions(self):
        return [self.etable[i].description for i in range(len(self.etable))]
    
    def fake_import(self, account_name, transactions):
        # When you want to test the post-parsing import process, rather than going through the hoops,
        # use this methods. 'transactions' is a list of dicts, the dicts being attribute values.
        # dates are strings in '%d/%m/%Y'.
        self.document.loader = DictLoader(self.app.default_currency, account_name, transactions)
        self.document.loader.load()
        self.document.notify('file_loaded_for_import')
    
    def graph_data(self):
        return [(date.fromordinal(x).strftime('%d/%m/%Y'), '%2.2f' % y) for (x, y) in self.balgraph.data]
    
    def nw_graph_data(self):
        return [(date.fromordinal(x).strftime('%d/%m/%Y'), '%2.2f' % y) for (x, y) in self.nwgraph.data]
    
    def save_file(self):
        filename = op.join(self.tmpdir(), 'foo.xml')
        self.document.save_to_xml(filename) # reset the dirty flag
    
    def save_and_load(self, newapp=True):
        # saves the current document and returns a document loaded with that saved file
        filepath = op.join(self.tmpdir(), 'foo.xml')
        self.document.save_to_xml(filepath)
        self.document.close()
        if newapp:
            newapp = Application(CallLogger(), default_currency=self.app.default_currency)
        else:
            newapp = self.app
        newdoc = Document(DocumentGUI(), newapp)
        newdoc.new_account(ASSET, None) # shouldn't be there after the load
        newdoc.load_from_xml(filepath)
        self.document._cook() # Make sure the balances have been converted using the latest fetched rates
        return newdoc
    
    def transaction_descriptions(self):
        return [row.description for row in self.ttable]
    

@nottest
class TestAppCompareMixin(object):
    # qif_mode: don't compare reconciliation status and, don't compare memos
    def _compareapps(self, first, second, qif_mode=False):
        def compare_txns(txn1, txn2):
            try:
                self.assertEqual(txn1.date, txn2.date)
                self.assertEqual(txn1.description, txn2.description)
                self.assertEqual(txn1.payee, txn2.payee)
                self.assertEqual(txn1.checkno, txn2.checkno)
                self.assertEqual(len(txn1.splits), len(txn2.splits))
            except AssertionError:
                raise
            splits1 = txn1.splits
            splits2 = txn2.splits
            splits1.sort(key=lambda s: getattr(s.account, 'name', ''))
            splits2.sort(key=lambda s: getattr(s.account, 'name', ''))
            for split1, split2 in zip(splits1, splits2):
                try:
                    account1 = split1.account.name if split1.account else ''
                    account2 = split2.account.name if split2.account else ''
                    self.assertEqual(account1, account2)
                    if qif_mode:
                        if split1.amount and split2.amount:
                            self.assertEqual(split1.amount.value, split2.amount.value)
                        else:
                            self.assertEqual(split1.amount, split2.amount)
                    else:
                        self.assertEqual(split1.memo, split2.memo)
                        self.assertEqual(split1.amount, split2.amount)
                    self.assertEqual(split1.reconciled, split2.reconciled)
                except AssertionError:
                    raise
        
        self.assertEqual(len(first.groups), len(second.groups))
        group_pairs = zip(sorted(first.groups, key=attrgetter('name')),
            sorted(second.groups, key=attrgetter('name')))
        for group1, group2 in group_pairs:
            try:
                self.assertEqual(group1.name, group2.name)
                self.assertEqual(group1.type, group2.type)
            except AssertionError:
                raise
        self.assertEqual(len(first.accounts), len(second.accounts))
        account_pairs = zip(sorted(first.accounts, key=attrgetter('name')),
            sorted(second.accounts, key=attrgetter('name')))
        for account1, account2 in account_pairs:
            try:
                self.assertEqual(account1.name, account2.name)
                self.assertEqual(account1.type, account2.type)
                if not qif_mode:
                    self.assertEqual(account1.currency, account2.currency)
                self.assertEqual(len(account1.entries), len(account2.entries))
            except AssertionError:
                raise
        self.assertEqual(len(first.transactions), len(second.transactions))
        for txn1, txn2 in zip(first.transactions, second.transactions):
            compare_txns(txn1, txn2)
        self.assertEqual(len(first.schedules), len(second.schedules))
        for rec1, rec2 in zip(first.schedules, second.schedules):
            self.assertEqual(rec1.repeat_type, rec2.repeat_type)
            self.assertEqual(rec1.repeat_every, rec2.repeat_every)
            compare_txns(rec1.ref, rec2.ref)
            self.assertEqual(rec1.stop_date, rec2.stop_date)
            self.assertEqual(len(rec1.date2exception), len(rec2.date2exception))
            for date in rec1.date2exception:
                exc1 = rec1.date2exception[date]
                exc2 = rec2.date2exception[date]
                if exc1 is None:
                    self.assertTrue(exc2 is None)
                else:
                    compare_txns(exc1, exc2)
            self.assertEqual(len(rec1.date2globalchange), len(rec2.date2globalchange))
            for date in rec1.date2globalchange:
                txn1 = rec1.date2globalchange[date]
                txn2 = rec2.date2globalchange[date]
                compare_txns(txn1, txn2)
    

class TestSaveLoadMixin(TestAppCompareMixin):
    def test_save_load(self):
        newdoc = self.save_and_load()
        newdoc.date_range = self.document.date_range
        newdoc._cook()
        self._compareapps(self.document, newdoc)
    

class TestQIFExportImportMixin(TestAppCompareMixin):
    def test_qif_export_import(self):
        filepath = op.join(self.tmpdir(), 'foo.qif')
        self.document.save_to_qif(filepath)
        newapp = Application(CallLogger(), default_currency=self.app.default_currency)
        newdoc = Document(DocumentGUI(), newapp)
        iwin = ImportWindow(self.iwin_gui, newdoc)
        iwin.connect()
        try:
            newdoc.parse_file_for_import(filepath)
            while iwin.panes:
                iwin.import_selected_pane()
        except FileFormatError:
            pass
        self._compareapps(self.document, newdoc, qif_mode=True)
    

class CommonSetup(object):
    def setup_monthly_range(self):
        self.document.date_range = MonthRange(date.today())
    
    def setup_one_entry(self):
        self.add_account('first')
        self.add_entry('11/07/2008', 'description', 'payee', transfer='second', decrease='42', checkno='24')
    
    def setup_one_entry_in_previous_range(self):
        # One entry with a date before the start of the current range. The only entry in the entry list
        # is a previous balance
        self.add_account()
        self.add_entry('1/1/2008')
        self.document.date_range = MonthRange(date(2008, 2, 1))
    
    def setup_scheduled_transaction(self, start_date=date(2008, 9, 13), description='foobar', 
            account=None, debit=None, repeat_type_index=0, repeat_every=1, stop_date=None):
        # 0 = daily, 1 = weekly, etc..
        # This setup also wraps a monthly range around the newly created schedule
        self.document.date_range = MonthRange(start_date)
        self.mainwindow.select_schedule_table()
        self.scpanel.new()
        self.scpanel.start_date = start_date.strftime('%d/%m/%Y')
        self.scpanel.description = description
        self.scpanel.repeat_type_index = repeat_type_index
        self.scpanel.repeat_every = repeat_every
        self.scpanel.stop_date = stop_date
        if account:
            self.scsplittable.add()
            self.scsplittable.edited.account = account
            if debit:
                self.scsplittable.edited.debit = debit
            self.scsplittable.save_edits()
        self.scpanel.save()
        self.mainwindow.select_transaction_table()
    
    def setup_three_accounts(self):
        #Three accounts, empty
        self.add_accounts('one', 'two', 'three') # three is the selected account (in second position)
    
    def setup_three_accounts_one_entry(self):
        # Two accounts of asset type, and one account of income type.
        self.add_accounts('one', 'two')
        self.add_entry(transfer='three', increase='42')
    
    def setup_account_with_budget(self, is_expense=True, account_name='Some Expense', target_name=None):
        # 4 days left to the month, 100$ monthly budget
        self.mock_today(2008, 1, 27)
        self.document.select_today_date_range()
        account_type = EXPENSE if is_expense else INCOME
        self.add_account(account_name, account_type=account_type)
        self.add_budget(account_name, target_name, '100')
        self.mainwindow.select_income_statement()
    
