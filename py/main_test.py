# coding=utf-8
# Unit Name: moneyguru.main_test
# Created By: Eric Mc Sween
# Created On: 2008-01-02
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import os.path as op
import sys
import xmlrpclib
from collections import defaultdict
from datetime import date, datetime
from operator import attrgetter

from nose.tools import nottest, istest

from hsutil.currency import Currency, EUR
from hsutil.path import Path
from hsutil.testcase import TestCase

from .app import Application
from .const import UNRECONCILIATION_CONTINUE
from .document import Document
from .exception import FileFormatError
from .gui.account_panel import AccountPanel
from .gui.account_pie_chart import AssetsPieChart, LiabilitiesPieChart, IncomePieChart, ExpensesPieChart
from .gui.account_reassign_panel import AccountReassignPanel
from .gui.balance_graph import BalanceGraph
from .gui.balance_sheet import BalanceSheet
from .gui.bar_graph import BarGraph
from .gui.csv_options import CSVOptions
from .gui.custom_date_range_panel import CustomDateRangePanel
from .gui.entry_table import EntryTable
from .gui.filter_bar import FilterBar, EntryFilterBar
from .gui.income_statement import IncomeStatement
from .gui.import_table import ImportTable
from .gui.import_window import ImportWindow
from .gui.main_window import MainWindow
from .gui.mass_edition_panel import MassEditionPanel
from .gui.net_worth_graph import NetWorthGraph
from .gui.profit_graph import ProfitGraph
from .gui.search_field import SearchField
from .gui.split_table import SplitTable
from .gui.transaction_panel import TransactionPanel
from .gui.transaction_table import TransactionTable
from .loader import base
from .model.account import ASSET, LIABILITY, INCOME, EXPENSE
from .model.currency import RatesDB
from .model.currency_test import FakeServer
from .model.date import MonthRange, QuarterRange, YearRange, YearToDateRange
from .model import currency as currency_module
from . import document as document_module

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
    def __init__(self, etable, ttable, bsheet, istatement, balgraph, bargraph, nwgraph, pgraph, 
                 efbar, tfbar, apie, lpie, ipie, epie, cdrpanel, arpanel):
        CallLogger.__init__(self)
        self.etable = etable
        self.ttable = ttable
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
        self.views = [etable, ttable, bsheet, istatement, efbar, tfbar, apie, lpie, ipie, epie,
            nwgraph, pgraph, balgraph, bargraph]
    
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
        self.assertEqual(gui.calls, expected)
        gui.calls.clear()
    
    def check_gui_calls_partial(self, gui, **expected):
        """Check that **expected has been called, but ignore other calls"""
        calls = dict((k, v) for k, v in gui.calls.items() if k in expected)
        self.assertEqual(calls, expected)
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
        self.tpanel_gui = CallLogger()
        self.tpanel = TransactionPanel(self.tpanel_gui, self.document)
        self.mepanel_gui = CallLogger()
        self.mepanel = MassEditionPanel(self.mepanel_gui, self.document)
        self.stable_gui = CallLogger()
        self.stable = SplitTable(self.stable_gui, self.tpanel)
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
        self.mainwindow_gui = MainWindowGUI(self.etable, self.ttable, self.bsheet, self.istatement,
            self.balgraph, self.bargraph, self.nwgraph, self.pgraph, self.efbar, self.tfbar, 
            self.apie, self.lpie, self.ipie, self.epie, self.cdrpanel, self.arpanel)
        self.mainwindow = MainWindow(self.mainwindow_gui, self.document)
        self.document.connect()
        self.mainwindow.connect()
        self.stable.connect()
        self.sfield.connect()
        self.iwin.connect()
        self.itable.connect()
        self.csvopt.connect()
        self.cdrpanel.connect()
    
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
        self.document.select_transaction_table()
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
    
    def set_budget(self, str_amount, target_index=None):
        self.apanel.load()
        self.apanel.budget = str_amount
        if target_index is not None:
            self.apanel.budget_target_index = target_index
        self.apanel.save()
    
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
                self.assertEqual(account1.budget, account2.budget)
                if account1.budget_target is None:
                    self.assertTrue(account2.budget_target is None)
                else:
                    self.assertEqual(account1.budget_target.name, account2.budget_target.name)
                self.assertEqual(len(account1.entries), len(account2.entries))
            except AssertionError:
                raise
        self.assertEqual(len(first.transactions), len(second.transactions))
        for txn1, txn2 in zip(first.transactions, second.transactions):
            compare_txns(txn1, txn2)
        self.assertEqual(len(first._scheduled), len(second._scheduled))
        for rec1, rec2 in zip(first._scheduled, second._scheduled):
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
    
    def setup_three_accounts(self):
        #Three accounts, empty
        self.add_account('one')
        self.add_account('two')
        self.add_account('three') # This is the selected account (in second position)
    

#--- Transactions: 0

class NoSetup(TestCase):
    def test_can_use_another_amount_format(self):
        self.app = Application(CallLogger(), decimal_sep=',', grouping_sep=' ')
        self.create_instances()
        self.add_account()
        self.add_entry(increase='1234567890.99')
        self.assertEqual(self.etable[0].increase, '1 234 567 890,99')
    
    def test_can_use_another_date_format(self):
        self.app = Application(CallLogger(), date_format='MM-dd-yyyy')
        self.create_instances()
        self.add_account()
        self.add_entry(date='2-15-2008')
        self.assertEqual(self.etable[0].date, '02-15-2008')
    

class Pristine(TestCase, TestQIFExportImportMixin):
    # TestQIFExportImportMixin: Make sure nothing is wrong when the file is empty
    def setUp(self):
        self.create_instances()
        self.clear_gui_calls()
    
    def test_add_entry(self):
        """When we have no account selected, we want a 0 length entries that can't have anything 
        added.
        """
        self.etable.add()
        self.assertEqual(len(self.etable), 0)
    
    def test_close_document(self):
        # when the document is closed, the date range type and the first weekday are saved to 
        # preferences.
        self.document.select_year_range()
        self.app.first_weekday = 1
        self.app.ahead_months = 5
        self.app.dont_unreconcile = True
        self.document.close()
        newapp = Application(self.app_gui)
        newdoc = Document(self.document_gui, newapp)
        self.assertTrue(isinstance(newdoc.date_range, YearRange))
        self.assertEqual(newapp.first_weekday, 1)
        self.assertEqual(newapp.ahead_months, 5)
        self.assertTrue(newapp.dont_unreconcile)
    
    def test_date_range(self):
        """By default, the date range is a yearly range for today"""
        self.assertEqual(self.document.date_range, YearRange(date.today()))
    
    def test_delete_entries(self):
        """Don't crash when trying to remove an entry from an empty list"""
        self.etable.delete()
    
    def test_graph_yaxis(self):
        self.assertEqual(self.nwgraph.ymin, 0)
        self.assertEqual(self.nwgraph.ymax, 100)
        self.assertEqual(list(self.nwgraph.ytickmarks), range(0, 101, 20))
        self.assertEqual(list(self.nwgraph.ylabels), [dict(text=str(x), pos=x) for x in range(0, 101, 20)])
    
    def test_load_inexistant(self):
        """Raise IOError when filename doesn't exist"""
        filename = op.join(self.tmpdir(), 'does_not_exist.xml')
        self.assertRaises(IOError, self.document.load_from_xml, filename)
    
    def test_load_invalid(self):
        """Raises FileFormatError, which gives a message kind of like: <filename> is not a 
        moneyGuru file.
        """
        filename = self.filepath('randomfile')
        try:
            self.document.load_from_xml(filename)
        except FileFormatError, e:
            self.assert_(filename in str(e))
        else:
            self.fail()
    
    def test_load_empty(self):
        """When loading an empty file (we mock it here), make sure no exception occur"""
        self.mock(base.Loader, 'parse', lambda self, filename: None)
        self.mock(base.Loader, 'load', lambda self: None)
        self.document.load_from_xml('filename does not matter here')
    
    def test_load_while_on_ytd_range(self):
        # Previously, the document would try to call around() on the current date range, even if not
        # navigable, causing a crash.
        self.document.select_year_to_date_range()
        filename = self.filepath('moneyguru/payee_description.moneyguru')
        self.document.load_from_xml(filename) # no crash
    
    def test_modified_flag(self):
        """The modified flag is initially False"""
        self.assertFalse(self.document.is_dirty())
    
    def test_selected_entry_index(self):
        """entries.selected_index is None when there is no entry"""
        self.assertEqual(self.etable.selected_indexes, [])
    
    def test_set_ahead_months(self):
        # setting the ahead_months preference doesn't change the current date range type
        self.app.ahead_months = 5
        self.assertTrue(isinstance(self.document.date_range, YearRange))
    
class RangeOnOctober2007(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.clear_gui_calls()
    
    def test_close_and_load(self):
        # the date range start is remembered in preference
        self.close_and_load()
        self.assertEqual(self.document.date_range, MonthRange(date(2007, 10, 1)))
    
    def test_graph_xaxis(self):
        self.assertEqual(self.nwgraph.xmax - self.nwgraph.xmin, 31)
        self.assertEqual(self.nwgraph.xtickmarks, [self.nwgraph.xmin + x - 1 for x in [1, 32]])
        [label] = self.nwgraph.xlabels # there is only one
        self.assertEqual(label['text'], 'October')
        self.document.date_range = QuarterRange(self.document.date_range)
        self.assertEqual(self.nwgraph.xmax - self.nwgraph.xmin, 92)
        self.assertEqual(self.nwgraph.xtickmarks, [self.nwgraph.xmin + x for x in [0, 31, 61, 92]])
        self.assertEqual(
            self.nwgraph.xlabels, 
            [dict(text=text, pos=self.nwgraph.xmin + pos) 
             for (text, pos) in [('October', 15.5), ('November', 31 + 15), ('December', 61 + 15.5)]]
        )
        self.document.date_range = YearRange(self.document.date_range)
        self.assertEqual([d['text'] for d in self.nwgraph.xlabels], 
            ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    
    def test_modified_flag(self):
        """Changing the date range does not change the modified flag"""
        self.assertFalse(self.document.is_dirty())
    
    def test_quarter_range(self):
        """When there is no selected entry, the selected range is based on the current date range"""
        self.document.select_quarter_range()
        self.assertEqual(self.document.date_range, QuarterRange(date(2007, 10, 1)))
    
    def test_select_custom_date_range(self):
        self.document.select_custom_date_range()
        self.check_gui_calls(self.mainwindow_gui, show_custom_date_range_panel=1)
        self.cdrpanel.start_date = '09/12/2008'
        self.cdrpanel.end_date = '18/02/2009'
        self.cdrpanel.ok() # changes the date range
        self.assertEqual(self.document.date_range.start, date(2008, 12, 9))
        self.assertEqual(self.document.date_range.end, date(2009, 2, 18))
        self.assertEqual(self.document.date_range.display, '09/12/2008 - 18/02/2009')
        self.assertFalse(self.document.date_range.can_navigate)
    
    def test_select_custom_date_range_without_changing_the_dates(self):
        # When selecting a custom date range that has the same start/end as the previous one, it
        # still causes the change notification (so the DR display changes.
        self.document.select_custom_date_range()
        self.cdrpanel.ok()
        self.assertEqual(self.document.date_range.display, '01/10/2007 - 31/10/2007')
    
    def test_select_prev_date_range(self):
        """If no account is selected, the range is not limited"""
        try:
            self.document.select_prev_date_range()
        except Exception:
            self.fail()
        self.assertEqual(self.document.date_range, MonthRange(date(2007, 9, 1)))
    
    def test_select_today_date_range(self):
        # the document's date range wraps around today's date
        self.document.select_today_date_range()
        dr = self.document.date_range
        self.assertTrue(dr.start <= date.today() <= dr.end)
    
    def test_select_year_range(self):
        """Verify that the range changes"""
        self.document.select_year_range()
        self.assertEqual(self.document.date_range, YearRange(date(2007, 1, 1)))
        # We don't ask the GUI to perform any animation
        self.check_gui_calls(self.mainwindow_gui, refresh_date_range_selector=1)
    
    def test_select_year_to_date_range(self):
        # Year-to-date starts at the first day of this year and ends today.
        self.document.select_year_to_date_range()
        self.assertEqual(self.document.date_range.start, date(date.today().year, 1, 1))
        self.assertEqual(self.document.date_range.end, date.today())
        self.assertEqual(self.document.date_range.display, 'Year to date')
    

class RangeOnJuly2006(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2006, 7, 1))
    
    def test_graph_xaxis(self):
        self.assertEqual(self.nwgraph.xtickmarks, [self.nwgraph.xmin + x - 1 for x in [1, 32]])


class RangeOnYear2007(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
    
    def test_month_range(self):
        """When there is no selected entry, the selected range is based on the current date range"""
        self.document.select_month_range()
        self.assertEqual(self.document.date_range, MonthRange(date(2007, 1, 1)))
    

class RangeOnYearToDate(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2008, 11, 12)
        self.document.select_year_to_date_range()
    
    def test_close_and_load(self):
        # The date range preference is correctly restored
        self.close_and_load()
        self.assertEqual(self.document.date_range, YearToDateRange())
    
    def test_graph_xaxis(self):
        # The graph xaxis shows abbreviated month names
        expected = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
        self.assertEqual([d['text'] for d in self.nwgraph.xlabels], expected)
    
    def test_select_next_prev_today_range(self):
        # next/prev/today do nothing in YTD
        self.document.select_next_date_range()
        self.assertEqual(self.document.date_range.start, date(2008, 1, 1))
        self.document.select_prev_date_range()
        self.assertEqual(self.document.date_range.start, date(2008, 1, 1))
        self.document.select_today_date_range()
        self.assertEqual(self.document.date_range.start, date(2008, 1, 1))
    

class RangeOnRunningYear(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2009, 1, 25)
        self.document.select_running_year_range()
        self.clear_gui_calls()
    
    def test_11_ahead_months(self):
        self.app.ahead_months = 11
        self.assertEqual(self.document.date_range.start, date(2009, 1, 1))
        self.assertEqual(self.document.date_range.end, date(2009, 12, 31))
    
    def test_add_entry(self):
        # _adjust_date_range() on save_edits() caused a crash
        self.add_account()
        self.etable.add()
        self.etable.save_edits() # no crash
    
    def test_date_range(self):
        # Running year (with the default 2 ahead months) starts 10 months in the past and ends 2 
        # months in the future, rounding the months. (default ahead_months is 2)
        self.assertEqual(self.document.date_range.start, date(2008, 4, 1))
        self.assertEqual(self.document.date_range.end, date(2009, 3, 31))
        self.assertEqual(self.document.date_range.display, 'Running year')
    
    def test_prev_date_range(self):
        # prev_date_range() does nothing
        self.document.select_prev_date_range()
        self.assertEqual(self.document.date_range.start, date(2008, 4, 1))
    

class RangeOnRunningYearWithAheadMonths(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2009, 1, 25)
        self.app.ahead_months = 5
        self.document.select_running_year_range()
        self.clear_gui_calls()
    
    def test_date_range(self):
        # select_running_year_range() uses the ahead_months preference
        self.assertEqual(self.document.date_range.start, date(2008, 7, 1))
    

class CustomDateRange(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.select_custom_date_range()
        self.cdrpanel.start_date = '09/12/2008'
        self.cdrpanel.end_date = '18/02/2009'
        self.cdrpanel.ok() # changes the date range
    
    def test_close_and_load(self):
        # the custom date range's end date is kept in preferences.
        self.close_and_load()
        self.assertEqual(self.document.date_range.display, '09/12/2008 - 18/02/2009')
    

class OneEmptyAccountRangeOnOctober2007(TestCase):
    """One empty account, range on October 2007"""
    def setUp(self):
        self.create_instances()
        self.add_account('Checking', EUR)
        self.document.date_range = MonthRange(date(2007, 10, 1))
    
    def test_add_empty_entry_and_save(self):
        """An empty entry really gets saved"""
        self.etable.add()
        self.etable.save_edits()
        self.document.select_prev_date_range()
        self.document.select_next_date_range()
        self.assertEqual(len(self.etable), 1)
    
    def test_balance_recursion_limit(self):
        """Balance calculation don't cause recursion errors when there's a lot of them"""
        sys.setrecursionlimit(100)
        for i in range(100):
            self.add_entry('1/10/2007')
        try:
            self.etable[-1].balance
        except RuntimeError:
            self.fail()
        finally:
            sys.setrecursionlimit(1000)
    
    def test_modified_flag(self):
        """Adding an account is a modification"""
        self.assertTrue(self.document.is_dirty())
    
    def test_save(self):
        """Saving puts the modified flag back to false"""
        self.document.save_to_xml(op.join(self.tmpdir(), 'foo.xml'))
        self.assertFalse(self.document.is_dirty())
    
    def test_select_prev_date_range(self):
        """If the selected account has absolutely no entry, the date range is not limited"""
        self.document.select_prev_date_range()
        self.assertEqual(self.document.date_range, MonthRange(date(2007, 9, 1)))
    
    def test_should_show_balance_column(self):
        """When an asset account is selected, we show the balance column"""
        self.assertTrue(self.etable.should_show_balance_column())
    

class ThreeEmptyAccounts(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_three_accounts()
    
    def test_add_entry(self):
        """An entry is added in the selected account"""
        self.etable.add()
        self.assertEqual(len(self.etable), 1)
    
    def test_add_transfer_entry(self):
        """Add a balancing entry to the account of the entry's transfer"""
        self.add_entry(transfer='one', increase='42.00')
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 1)
    

class LiabilityAccount(TestCase):
    """One liability account, empty"""
    def setUp(self):
        self.create_instances()
        self.add_account(account_type=LIABILITY)
    
    def test_should_show_balance_column(self):
        """When a liability account is selected, we show the balance column"""
        self.assertTrue(self.etable.should_show_balance_column())
    

class IncomeAccount(TestCase):
    """One income account, empty"""
    def setUp(self):
        self.create_instances()
        self.add_account(account_type=INCOME)
    
    def test_should_show_balance_column(self):
        """When an income account is selected, we don't show the balance column"""
        self.assertFalse(self.etable.should_show_balance_column())
    

class ExpenseAccount(TestCase):
    """One expense account, empty"""
    def setUp(self):
        self.create_instances()
        self.add_account(account_type=EXPENSE)
    
    def test_should_show_balance_column(self):
        """When an expense account is selected, we don't show the balance column"""
        self.assertFalse(self.etable.should_show_balance_column())
    

class OneGroup(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_group()
    
    def test_should_show_balance_column(self):
        """When a group is selected, False is returned (not None)"""
        self.assertFalse(self.etable.should_show_balance_column())
        self.assertTrue(isinstance(self.etable.should_show_balance_column(), bool))
    

class AccountWithBudget(TestCase, TestSaveLoadMixin):
    def setUp(self):
        # Weeks of Jan: 31-6 7-13 14-20 21-27 28-3
        self.create_instances()
        self.add_account('asset')
        self.add_account('income', account_type=INCOME)
        self.apanel.load()
        self.apanel.budget = '400'
        self.apanel.save()
    

#--- Transactions: 1

class _ThreeAccountsAndOneEntry(TestCase):
    """Two accounts of asset type, and one account of income type."""
    def setUp(self):
        self.create_instances()
        self.add_account('one')
        self.add_account('two')
        self.add_entry(transfer='three', increase='42')
    

class ThreeAccountsAndOneEntry(_ThreeAccountsAndOneEntry):
    def test_bind_entry_to_income_expense_accounts(self):
        """Adding an entry with a transfer named after an existing income creates a bound entry in
        that account
        """
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.add_entry(transfer='three')
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(len(self.etable), 2)
    

class EntryInEditionMode(TestCase):
    """An empty account, but an entry is in edit mode in october 2007."""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.save_file()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.etable.add()
        row = self.etable.edited
        row.date = '1/10/2007'
        row.description = 'foobar'
        row.increase = '42.00'
    
    def test_add_entry(self):
        """Make sure that the currently edited entry is saved before another one is added"""
        self.etable.add()
        self.assertEqual(len(self.etable), 2)
        self.assertEqual(self.etable[0].date, '01/10/2007')
        self.assertEqual(self.etable[0].description, 'foobar')
        self.assertEqual(self.etable[0].increase, '42.00')
        
    def test_delete_entries(self):
        """Calling delete_entries() while in edition mode removes the edited entry and put the app
        out of edition mode.
        """
        self.etable.delete()
        self.assertEqual(len(self.etable), 0)
        self.etable.save_edits() # Shouldn't raise anything
    
    def test_increase_and_decrease(self):
        """Test the increase/decrease amount mechanism"""
        row = self.etable.selected_row
        self.assertEqual(row.increase, '42.00')
        self.assertEqual(row.decrease, '')
        row.decrease = '50'
        self.assertEqual(row.increase, '')
        self.assertEqual(row.decrease, '50.00')
        row.increase = '-12.42'
        self.assertEqual(row.increase, '')
        self.assertEqual(row.decrease, '12.42')
    
    def test_revert_entry(self):
        """Reverting a newly added entry deletes it"""
        self.etable.cancel_edits()
        self.assertEqual(len(self.etable), 0)
        self.assertFalse(self.document.is_dirty())
    
    def test_selected_entry_index(self):
        """entries.selected_index follows every entry that is added."""
        self.assertEqual(self.etable.selected_indexes[0], 0)
    
    def test_set_debit_to_zero_with_zero_credit(self):
        """Setting debit to zero when the credit is already zero sets the amount to zero"""
        row = self.etable.selected_row
        row.increase = ''
        self.assertEqual(self.etable[0].increase, '')
        
    def test_set_credit_to_zero_with_non_zero_debit(self):
        """Setting credit to zero when the debit being non-zero does nothing"""
        row = self.etable.selected_row
        row.decrease = ''
        self.assertEqual(self.etable[0].increase, '42.00')
    

class OneEntryYearRange2007(TestCase, TestSaveLoadMixin, TestQIFExportImportMixin):
    """One account, one entry, which is in the yearly date range (2007). The entry has a transfer
    and a debit value set.
    """
    # TestSaveLoadMixin: Make sure that the payee and checkno field is saved/loaded
    # TestQIFExportImportMixin: the same
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00', checkno='42')
        self.document.date_range = YearRange(date(2007, 1, 1))
    
    def _test_entry_attribute_get_set(self, column, value='some_value'):
        """Test that the get/set mechanism works correctly (sets the edition flag appropriately and 
        set the value underneath)"""
        row = self.etable.selected_row
        setattr(row, column, value) # Sets the flag
        self.etable.save_edits()
        # Make sure that the values really made it down in the model by using a spanking new gui
        etable = EntryTable(self.etable_gui, self.document)
        etable.connect()
        self.assertEqual(getattr(etable[0], column), value)
        self.save_file()
        row = self.etable.selected_row
        setattr(row, column, value) # Doesn't set the flag
        self.etable.save_edits() # Shouldn't do anything
        self.assertFalse(self.document.is_dirty())
    
    def test_change_transfer(self):
        """The 'Salary' account must be deleted when the bound entry is deleted"""
        row = self.etable.selected_row
        row.transfer = 'foobar'
        self.etable.save_edits()
        self.assertEqual(self.account_names(), ['Checking', 'foobar'])
    
    def test_create_income_account(self):
        """Adding an entry in the Salary transfer added a Salary income account with a bound entry
        in it
        """
        self.assertEqual(self.account_names(), ['Checking', 'Salary'])
        self.assertEqual(self.bsheet.assets.children_count, 3)
        self.assertEqual(self.bsheet.liabilities.children_count, 2)
        self.document.select_income_statement()
        self.assertEqual(self.istatement.income.children_count, 3)
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(len(self.etable), 1)
        self.assertEqual(self.etable[0].description, 'Deposit')
    
    def test_delete_entries(self):
        """Deleting an entry updates the graph and makes the Salary account go away"""
        self.etable.delete()
        self.assertEqual(list(self.balgraph.data), [])
        self.assertEqual(self.account_names(), ['Checking'])
    
    def test_delete_entries_with_Salary_selected(self):
        """Deleting the last entry of an income account does not remove that account"""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.etable.delete()
        self.assertEqual(self.account_names(), ['Checking', 'Salary'])
    
    def test_edit_then_revert(self):
        """Reverting an existing entry put the old values back"""
        row = self.etable.selected_row
        row.date = '11/10/2007'
        row.description = 'edited'
        row.transfer = 'edited'
        row.increase = '43'
        self.etable.cancel_edits()
        self.assertEqual(self.etable[0].date, '10/10/2007')
        self.assertEqual(self.etable[0].description, 'Deposit')
        self.assertEqual(self.etable[0].transfer, 'Salary')
        self.assertEqual(self.etable[0].increase, '42.00')
    
    def test_entry_checkno_get_set(self):
        self._test_entry_attribute_get_set('checkno')
    
    def test_entry_debit(self):
        """The entry is a debit"""
        self.assertEqual(self.etable[0].increase, '42.00')
    
    def test_entry_decrease_get_set(self):
        self._test_entry_attribute_get_set('decrease', '12.00')
    
    def test_entry_increase_get_set(self):
        self._test_entry_attribute_get_set('increase', '12.00')
    
    def test_entry_is_editable(self):
        """An Entry has everything but balance editable"""
        self.assertTrue(self.etable.can_edit_column('date'))
        self.assertTrue(self.etable.can_edit_column('description'))
        self.assertTrue(self.etable.can_edit_column('payee'))
        self.assertTrue(self.etable.can_edit_column('transfer'))
        self.assertTrue(self.etable.can_edit_column('increase'))
        self.assertTrue(self.etable.can_edit_column('decrease'))
        self.assertTrue(self.etable.can_edit_column('checkno'))
        self.assertFalse(self.etable.can_edit_column('balance')) # Only in reconciliation mode
        self.assertFalse(self.etable[0].can_reconcile()) # Only in reconciliation mode
    
    def test_entry_is_editable_of_opposite(self):
        """The other side of an Entry has the same edition rights as the Entry"""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertTrue(self.etable.can_edit_column('date'))
        self.assertTrue(self.etable.can_edit_column('description'))
        self.assertTrue(self.etable.can_edit_column('payee'))
        self.assertTrue(self.etable.can_edit_column('transfer'))
        self.assertTrue(self.etable.can_edit_column('increase'))
        self.assertTrue(self.etable.can_edit_column('decrease'))
        self.assertTrue(self.etable.can_edit_column('checkno'))
        self.assertFalse(self.etable.can_edit_column('balance')) # Only in reconciliation mode
        self.assertFalse(self.etable[0].can_reconcile()) # Only in reconciliation mode
    
    def test_entry_payee_get_set(self):
        self._test_entry_attribute_get_set('payee')
    
    def test_entry_transfer_get_set(self):
        self._test_entry_attribute_get_set('transfer')
    
    def test_graph(self):
        """The 'Checking' account has a line graph. The 'Salary' account has a bar graph."""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.bar_graph_data(), [('01/10/2007', '01/11/2007', '42.00', '0.00')])
        self.assertEqual(self.bargraph.title, 'Salary')
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.graph_data(), [('11/10/2007', '42.00'), ('01/01/2008', '42.00')])
    
    def test_new_entry_balance(self):
        """A newly added entry has a correct balance"""
        self.etable.add()
        self.assertEqual(self.etable[1].balance, '42.00')
    
    def test_new_entry_date(self):
        """A newly added entry has the same date as the selected entry"""
        self.etable.add()
        self.assertEqual(self.etable[1].date, '10/10/2007')

    def test_select_month_range(self):
        """Make sure that the month range selection will be the first valid (contains at least one 
        entry) range.
        """
        self.document.select_month_range()
        self.assertEqual(self.document.date_range, MonthRange(date(2007, 10, 1)))
    
    def test_select_quarter_range(self):
        """Make sure that the quarter range selection will be the first valid (contains at least one 
        entry) range.
        """
        self.document.select_quarter_range()
        self.assertEqual(self.document.date_range, QuarterRange(date(2007, 10, 1)))
    
    def test_set_date_in_range(self):
        """Setting the date in range doesn't cause useless notifications"""
        row = self.etable.selected_row
        row.dat = '11/10/2007'
        self.clear_gui_calls()
        self.etable.save_edits()
        self.check_gui_calls(self.mainwindow_gui)
    
    def test_set_date_out_of_range(self):
        """Setting the date out of range makes the app's date range change accordingly"""
        row = self.etable.selected_row
        row.date = '1/1/2008'
        self.clear_gui_calls()
        self.etable.save_edits()
        self.assertEqual(self.document.date_range, YearRange(date(2008, 1, 1)))
        self.check_gui_calls(self.mainwindow_gui, animate_date_range_forward=1, 
                             refresh_date_range_selector=1)
    

class EntryWithoutTransfer(TestCase):
    """An entry without a transfer account set"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry(description='foobar', decrease='130')
    
    def test_entry_transfer(self):
        """Instead of showing 'Imbalance', the transfer column shows nothing"""
        self.assertEqual(self.etable[0].transfer, '')
    

class EntryWithCredit(TestCase):
    """An entry with a credit"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry(decrease='42.00')
    
    def test_set_decrease_to_zero_with_zero_increase(self):
        """Setting decrease to zero when the increase is already zero sets the amount to zero"""
        row = self.etable.selected_row
        row.decrease = ''
        self.assertEqual(self.etable[0].decrease, '')
        
    def test_set_increase_to_zero_with_non_zero_decrease(self):
        """Setting increase to zero when the decrease being non-zero does nothing"""
        row = self.etable.selected_row
        row.increase = ''
        self.assertEqual(self.etable[0].decrease, '42.00')
    
    def test_amount(self):
        """The amount attribute is correct."""
        self.assertEqual(self.etable[0].decrease, '42.00')


class EntryInLiabilities(TestCase, TestQIFExportImportMixin):
    """An entry in a liability account.
    
    TestQIFExportImportMixin: make sure liability accounts are exported/imported correctly.
    """
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2008, 1, 1))
        self.add_account('Credit card', account_type=LIABILITY)
        self.add_entry('1/1/2008', 'Payment', increase='10')

    def test_amount(self):
        """The amount attribute is correct."""
        self.assertEqual(self.etable[0].increase, '10.00')
        

class TwoBoundEntries(TestCase):
    """2 entries in 2 accounts 'first' and 'second' that are part of the same transaction. There is 
    a 'third', empty account. 'second' is selected.
    """
    def setUp(self):
        self.create_instances()
        self.add_account('first')
        self.add_account('second')
        self.add_entry(description='transfer', transfer='first', increase='42')
        self.add_account('third')
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
    
    def test_change_amount(self):
        """The other side of the transaction follows"""
        # Because of MCT, a transfer between asset/liability accounts stopped balancing itself
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.decrease = '40'
        self.etable.save_edits()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable[0].increase, '40.00')
    
    def test_change_transfer(self):
        """Changing the transfer of an entry deletes the bound entry and creates a new one"""
        row = self.etable.selected_row
        row.transfer = 'third'
        self.etable.save_edits()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0] # first
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 0)
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2] # third
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 1)
    
    def test_change_transfer_backwards(self):
        """Entry binding works both ways"""
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.transfer = 'third'
        self.etable.save_edits()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 0)
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 1)
    
    def test_change_transfer_non_account(self):
        """The binding should be cancelled when the transfer is changed to a non-account. Also,
        don't try to unbind an entry from a deleted entry
        """
        row = self.etable.selected_row
        row.transfer = 'other'
        self.etable.save_edits()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0] # first
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 0)
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2] # third
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 0)
        # Make sure the entry don't try to unbind from 'first' again
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # second
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.transfer = 'yet-another'
        self.etable.save_edits() # shouldn't raise anything
    
    def test_delete_entries(self):
        """Deleting an entry also delets any bound entry"""
        self.etable.delete()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 0)
    

class NegativeBoundEntry(TestCase):
    """Account with one credit entry, bound to another account"""
    def setUp(self):
        self.create_instances()
        self.add_account('visa', account_type=LIABILITY)
        self.add_entry(transfer='clothes', increase='42')
    
    def test_make_balance_positive(self):
        """Even when making 'visa''s entry a debit, account types stay the same"""
        row = self.etable.selected_row
        row.decrease = '42' # we're decreasing the liability here
        self.etable.save_edits()
        self.document.select_income_statement()
        self.assertEqual(self.istatement.expenses.children_count, 3)
    

class OneEntryInPreviousRange(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_one_entry_in_previous_range()
    
    def test_attrs(self):
        row = self.etable[0]
        self.assertEqual(row.date, '01/02/2008')
        self.assertTrue(row.read_only)
    
    def test_make_account_income(self):
        """If we make the account an income account, the previous balance entry disappears"""
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.apanel.load()
        self.apanel.type_index = 2 # income
        self.apanel.save()
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 0)
    
    def test_new_entry_are_inserted_after_previous_balance_entry(self):
        """When a new entry's date is the same date as a Previous Balance entry, the entry is added
        after it
        """
        self.etable.add()
        self.assertEqual(self.etable[0].description, 'Previous Balance')
    

#--- Transactions: 2

class TwoEntriesInDifferentQuartersWithYearRange(TestCase):
    """One account, two entries, one in January 2007, one in April 2007. The latest entry is 
    selected. The range is Yearly, on 2007.
    """
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.add_account()
        self.add_entry('1/1/2007', 'first', increase='1')
        self.add_entry('1/4/2007', 'second', increase='2')
    
    def test_select_quarter_range(self):
        """The selected quarter range is the range containing the selected entry, Q2"""
        self.document.select_quarter_range()
        self.assertEqual(self.document.date_range, QuarterRange(date(2007, 4, 1)))
    
    def test_select_month_range(self):
        """The selected month range is the range containing the selected entry, April"""
        self.document.select_month_range()
        self.assertEqual(self.document.date_range, MonthRange(date(2007, 4, 1)))
    

class TwoEntriesInTwoMonthsRangeOnSecond(TestCase):
    """One account, two entries in different months. The month range is on the second.
    The selection is on the 2nd item (The first add_entry adds a Previous Balance, the second
    add_entry adds a second item and selects it.)
    """
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.add_entry('3/9/2007', 'first', increase='102.00')
        self.add_entry('10/10/2007', 'second', increase='42.00')
        self.document.date_range = MonthRange(date(2007, 10, 1))
        # When the second entry was added, the date was in the previous date range, making the
        # entry go *before* the Previous Entry, but we want the selection to be on the second item
        self.etable.select([1])
    
    def test_entries(self):
        """app.entries has 2 entries: a previous balance entry and the october entry."""
        self.assertEqual(len(self.etable), 2) # Previous balance
        self.assertEqual(self.etable[0].description, 'Previous Balance')
        self.assertEqual(self.etable[0].payee, '')
        self.assertEqual(self.etable[0].checkno, '')
        self.assertEqual(self.etable[0].increase, '')
        self.assertEqual(self.etable[0].decrease, '')
        self.assertEqual(self.etable[0].balance, '102.00')
        self.assertEqual(self.etable[1].description, 'second')
    
    def test_graph_data(self):
        """The Previous Balance is supposed to be a data point here"""
        expected = [('01/10/2007', '102.00'), ('10/10/2007', '102.00'), ('11/10/2007', '144.00'),
                    ('01/11/2007', '144.00')]
        self.assertEqual(self.graph_data(), expected)
    
    def test_next_date_range(self):
        """app.select_next_date_range() makes the date range go one month later"""
        self.document.date_range = MonthRange(date(2007, 9, 1))
        self.document.select_next_date_range()
        self.assertEqual(self.document.date_range, MonthRange(date(2007, 10, 1)))
    
    def test_prev_balance_entry_is_editable(self):
        """A PreviousBalanceEntry is read-only"""
        self.etable.select([0])
        self.assertFalse(self.etable.can_edit_column('date'))
        self.assertFalse(self.etable.can_edit_column('description'))
        self.assertFalse(self.etable.can_edit_column('transfer'))
        self.assertFalse(self.etable.can_edit_column('increase'))
        self.assertFalse(self.etable.can_edit_column('decrease'))
        self.assertFalse(self.etable.can_edit_column('balance'))
    
    def test_prev_date_range(self):
        """app.select_prev_date_range() makes the date range go one month earlier"""
        self.document.select_prev_date_range()
        self.assertEqual(self.document.date_range, MonthRange(date(2007, 9, 1)))
    
    def test_prev_date_range_while_in_edition(self):
        """Changing the date range while in edition mode saves the data first"""
        row = self.etable.selected_row
        row.description = 'foo'
        self.document.select_prev_date_range() # Save the entry *then* go in the prev date range
        self.etable.save_edits()
        self.assertEqual(self.etable[0].description, 'first')
    
    def test_selection(self):
        """The selection should be on the 2nd item, last added"""
        self.assertEqual(self.etable.selected_indexes[0], 1)
    
    def test_selection_is_kept_on_date_range_jump(self):
        """When save_entry causes a date range jump, the entry that was just saved stays selected"""
        # selected index is now 1
        row = self.etable.selected_row
        row.date = '2/9/2007' # Goes before 'first'
        self.etable.save_edits()
        # selected index has been changed to 0
        self.assertEqual(self.etable.selected_indexes, [0])
    

class TwoEntriesInRange(TestCase):
    """Two entries, both on October 2007, first entry is selected"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_entry('2/10/2007', 'first', increase='102')
        self.add_entry('4/10/2007', 'second', increase='42')
        self.etable.select([0])
    
    def test_date_edition_and_position(self):
        """After an entry has its date edited, its position among transactions
        of the same date is always last
        """
        # Previously, the transaction would keep its old position, so it could
        # happen that the newly edited transaction wouldn't go at the end
        row = self.etable.selected_row
        row.date = '4/10/2007' # same as 'second'
        self.etable.save_edits()
        self.assertEqual(self.etable[1].description, 'first')
    
    def test_date_range_change(self):
        """The currently selected entry stays selected"""
        self.document.select_year_range()
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].description, 'first')
    
    def test_delete_first_entry(self):
        """Make sure that the balance of the remaining entry is updated"""
        self.etable.delete()
        self.assertEqual(self.etable[0].balance, '42.00')
    
    def test_entry_order_after_edition(self):
        """Edition of an entry re-orders entries upon save_entry() if needed"""
        row = self.etable.selected_row
        row.date = '5/10/2007'
        self.etable.save_edits()
        self.assertEqual(self.etable[0].description, 'second')
        self.assertEqual(self.etable.selected_indexes, [1]) # Selection followed the entry
    
    def test_get_entry_attribute_on_other_than_selected(self):
        """get_entry_attribute_value() can return attributes from something else than the selected entry
        """
        self.assertEqual(self.etable[1].date, '04/10/2007')
    
    def test_graph_data(self):
        """The variation between 2 data points that are more than one day apart should not be linear
        There should be a falt line until one day before the next data point, then the balance
        variation should take place all on the same day.
        """
        expected = [('03/10/2007', '102.00'), ('04/10/2007', '102.00'), ('05/10/2007', '144.00'), 
                    ('01/11/2007', '144.00')]
        self.assertEqual(self.graph_data(), expected)
    
    def test_multiple_selection(self):
        """selected_entries() return back all indexes given to select_entries()"""
        self.etable.select([0, 1])
        self.assertEqual(self.etable.selected_indexes, [0, 1])
    
    def test_new_entry_balance(self):
        """Newly added entries' balance don't include balance in the future"""
        self.etable.add()
        self.assertEqual(self.etable.selected_indexes[0], 1) # The new entry is in the middle
        self.assertEqual(self.etable[1].balance, '102.00')
    
    def test_new_entry_date(self):
        """A newly added entry's date is the same date as the selected entry"""
        self.etable.add()
        self.assertEqual(self.etable[1].date, '02/10/2007')
    
    def test_revert_keeps_selection(self):
        """Selected index stays the same after reverting an entry edition"""
        row = self.etable.selected_row
        row.description = 'foo'
        self.etable.cancel_edits()
        self.assertEqual(self.etable.selected_indexes, [0])
    

class TwoEntriesInRangeBalanceGoesNegative(TestCase):
    """Two entries, both on October 2007. The balance first goes to -100, then at 100"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_entry('3/10/2007', 'first', decrease='100')
        self.add_entry('4/10/2007', 'second', increase='200')
    
    def test_graph_yaxis(self):
        self.assertEqual(self.balgraph.ymin, -100)
        self.assertEqual(self.balgraph.ymax, 100)
        self.assertEqual(list(self.balgraph.ytickmarks), range(-100, 101, 50))
        expected = [dict(text=str(x), pos=x) for x in range(-100, 101, 50)]
        self.assertEqual(list(self.balgraph.ylabels), expected)
    

class TwoEntryOnTheSameDate(TestCase):
    """Two entries, both having the same date. The first entry takes the balance very high, but the
    second entry is a credit that takes it back. The first entry is selected.
    """
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_entry('3/10/2007', 'foo', increase='10000')
        self.add_entry('3/10/2007', 'bar', decrease='9000')
        self.etable.select([0])
    
    def test_edit_entry_of_the_same_date(self):
        """Editing an entry when another entry has the same date does not change the display order
        of those entries
        """
        row = self.etable.selected_row
        row.description = 'baz'
        self.etable.save_edits()
        self.assertEqual(self.etable[0].description, 'baz')
        self.assertEqual(self.etable[1].description, 'bar')
    
    def test_new_entry_after_reorder(self):
        """Reordering entries does not affect the position of newly created
        entries.
        """
        # Previously, because of the 'position' of a new entry would be equal
        # to the number of entries on the same date. However, the max position
        # for a particular date can be higher than the number of entries on 
        # that date.
        self.etable.move([0], 2) # 'foo' goes after 'bar'. position = 2
        self.etable.move([0], 2) # 'bar' goes after 'foo'. position = 3
        self.add_entry('3/10/2007', description='baz')
        self.assertEqual(self.etable[2].description, 'baz')
    
    def test_graph_yaxis(self):
        """The balance went at 10000 with the first entry, but it went back to 1000 it with the
        second. The yaxis should only take the final 1000 into account
        """
        self.assertEqual(self.balgraph.ymin, 0)
        self.assertEqual(self.balgraph.ymax, 1000)


class TwoAccountsTwoEntriesInTheFirst(TestCase):
    """First account has 2 entries in it, the second is empty. The entries are in the date range.
    Second account is selected.
    """
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_account()
        self.add_entry('3/10/2007', 'first', increase='1')
        self.add_entry('4/10/2007', 'second', increase='1')
        self.add_account()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
    
    def test_last_entry_is_selected_on_account_selection(self):
        """On account selection, the last entry is selected"""
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].description, 'second')
    

class AssetIncomeWithDecrease(TestCase):
    """An asset and income account with a transaction decreasing them both"""
    def setUp(self):
        self.create_instances()
        self.add_account('Operations')
        self.document.date_range = MonthRange(date(2008, 3, 1))
        self.add_entry('1/3/2008', description='MacroSoft', transfer='Salary', increase='42')
        self.add_entry('2/3/2008', description='Error Adjustment', transfer='Salary', decrease='2')
    
    def test_asset_decrease(self):
        """The Error Adjustment transaction is an decrease in Operations"""
        self.assertEqual(self.etable[1].decrease, '2.00')
    
    def test_asset_increase(self):
        """The MacroSoft transaction is an increase in Operations"""
        self.assertEqual(self.etable[0].increase, '42.00')
    
    def test_income_balance(self):
        """Salary's entries' balances are positive"""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[0].balance, '42.00')
    
    def test_income_decrease(self):
        """The Error Adjustment transaction is an decrease in Salary"""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[1].decrease, '2.00')
    
    def test_income_increase(self):
        """The MacroSoft transaction is an increase in Salary"""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[0].increase, '42.00')
    
    def test_set_income_decrease(self):
        """Setting an income entry's decrease actually sets the right side"""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        row = self.etable.selected_row
        row.decrease = '4'
        self.assertEqual(self.etable[1].decrease, '4.00')
    
    def test_set_income_increase(self):
        """Setting an income entry's increase actually sets the right side"""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        row = self.etable.selected_row
        row.increase = '4'
        self.assertEqual(self.etable[1].increase, '4.00')
    

class LiabilityExpenseWithDecrease(TestCase):
    """An asset and income account with a transaction decreasing them both"""
    def setUp(self):
        self.create_instances()
        self.add_account('Visa', account_type=LIABILITY)
        self.document.date_range = MonthRange(date(2008, 3, 1))
        # Visa is a liabilies, so increase/decrease are inverted
        # Clothes is created as an expense
        self.add_entry('1/3/2008', description='Shoes', transfer='Clothes', increase='42.00')
        self.add_entry('2/3/2008', description='Rebate', transfer='Clothes', decrease='2')
    
    def test_expense_decrease(self):
        """The Rebate transaction is a decrease in Clothes"""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[1].decrease, '2.00')
    
    def test_expense_increase(self):
        """The Shoes transaction is an increase in Clothes"""
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[0].increase, '42.00')
    
    def test_income_balance(self):
        """Visa's entries' balances are positive"""
        self.assertEqual(self.etable[0].balance, '42.00')
    
    def test_liability_decrease(self):
        """The Rebate transaction is an decrease in Visa"""
        self.assertEqual(self.etable[1].decrease, '2.00')
    
    def test_liability_increase(self):
        """The Shoes transaction is an increase in Visa"""
        self.assertEqual(self.etable[0].increase, '42.00')
    
    def test_set_liability_decrease(self):
        """Setting an liability entry's decrease actually sets the right side"""
        # Last entry is selected
        row = self.etable.selected_row
        row.decrease = '4'
        self.assertEqual(self.etable[1].decrease, '4.00')
    
    def test_set_liability_increase(self):
        """Setting an liability entry's increase actually sets the right side"""
        # Last entry is selected
        row = self.etable.selected_row
        row.increase = '4'
        self.assertEqual(self.etable[1].increase, '4.00')
    

#--- Transactions: 3

class ThreeEntriesInThreeMonthsRangeOnThird(TestCase):
    """One account, three entries in different months. The month range is on the third.
    The selection is on the 2nd item (the first being the Previous Balance).
    """
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.date_range = MonthRange(date(2007, 11, 1))
        self.add_entry('3/9/2007', 'first', increase='1')
        self.add_entry('10/10/2007', 'second', increase='2')
        self.add_entry('1/11/2007', 'third', increase='3')
    
    def test_date_range_change(self):
        """The selected entry stays selected after a date range, even if its index changes (the 
        index of the third entry goes from 1 to 2.
        """
        self.document.select_year_range()
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].description, 'third')
    

class EntriesWithZeroVariation(TestCase):
    """The first entry is normal, but the second has a null amount, resulting in no balance variation"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_entry('1/10/2007', 'first', increase='100')
        self.add_entry('3/10/2007', 'third')
    
    def test_graph_data(self):
        """Entries with zero variation are ignored"""
        expected = [('02/10/2007', '100.00'), ('01/11/2007', '100.00')]
        self.assertEqual(self.graph_data(), expected)
    

class ThreeEntriesInTwoAccountTypes(TestCase):
    """3 entries in 2 accounts of different type."""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry(description='first')
        self.add_entry(description='second')
        self.add_account(account_type=INCOME)
        self.add_entry(description='third') # selected
    
    def test_delete_entries(self):
        """delete the entry in the selected type"""
        self.etable.delete()
        self.assertEqual(len(self.etable), 0)
    
    def test_entries_count(self):
        """depends on the selected account type"""
        self.assertEqual(len(self.etable), 1)
    
    def test_get_entry_attribute_value(self):
        """depends on the selected account type"""
        self.assertEqual(self.etable[0].description, 'third')
    

class ThreeEntriesInTheSameExpenseAccount(TestCase):
    """Three entries balanced in the same expense account."""
    def setUp(self):
        self.create_instances()
        self.document.select_year_range()
        self.add_account()
        self.add_entry('31/12/2007', 'entry0', transfer='Expense', decrease='42')
        self.add_entry('1/1/2008', 'entry1', transfer='Expense', decrease='100')
        self.add_entry('20/1/2008', 'entry2', transfer='Expense', decrease='200')
        self.add_entry('31/3/2008', 'entry3', transfer='Expense', decrease='150')
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0]
        self.istatement.show_selected_account()
    
    def test_change_first_weekday(self):
        # changing the first weekday affects the bar graphs as expected
        self.document.date_range = MonthRange(date(2008, 1, 1))
        self.clear_gui_calls()
        self.app.first_weekday = 1 # tuesday
        # The month conveniently starts on a tuesday, so the data now starts from the 1st of the month
        expected = [('01/01/2008', '08/01/2008', '100.00', '0.00'), 
                    ('15/01/2008', '22/01/2008', '200.00', '0.00')]
        self.assertEqual(self.bar_graph_data(), expected)
        self.check_gui_calls(self.bargraph_gui, refresh=1)
        self.app.first_weekday = 6 # sunday
        expected = [('30/12/2007', '06/01/2008', '142.00', '0.00'), 
                    ('20/01/2008', '27/01/2008', '200.00', '0.00')]
        self.assertEqual(self.bar_graph_data(), expected)
    
    def test_delete_multiple_selection(self):
        """delete_entries() when having multiple entries selected delete all selected entries"""
        self.etable.select([0, 2])
        self.etable.delete()
        self.assertEqual(self.entry_descriptions(), ['entry2'])
    
    def test_graph_data(self):
        # The expense graph is correct.
        expected = [('01/01/2008', '01/02/2008', '300.00', '0.00'), 
                    ('01/03/2008', '01/04/2008', '150.00', '0.00')]
        self.assertEqual(self.bar_graph_data(), expected)

    def test_graph_data_in_month_range(self):
        # The expense graph shows weekly totals when the month range is selected. The first bar
        # overflows the date range to complete the week.
        self.document.date_range = MonthRange(date(2008, 1, 1))
        expected = [('31/12/2007', '07/01/2008', '142.00', '0.00'), 
                    ('14/01/2008', '21/01/2008', '200.00', '0.00')]
        self.assertEqual(self.bar_graph_data(), expected)

    def test_graph_data_in_quarter_range(self):
        # The expense graph shows weekly totals when the quarter range is selected. The first bar
        # overflows the date range to complete the week.
        self.document.date_range = QuarterRange(date(2008, 1, 1))
        expected = [('31/12/2007', '07/01/2008', '142.00', '0.00'), 
                     ('14/01/2008', '21/01/2008', '200.00', '0.00'),
                     ('31/03/2008', '07/04/2008', '150.00', '0.00')]
        self.assertEqual(self.bar_graph_data(), expected)
    
    def test_xaxis_on_month_range(self):
        # The xaxis min/max follow the date range overflows
        self.document.date_range = MonthRange(date(2008, 1, 1))
        self.assertEqual(self.bargraph.xmin, date(2007, 12, 31).toordinal())
        self.assertEqual(self.bargraph.xmax, date(2008, 2, 4).toordinal())
    

#--- Transactions: a lot

class FourEntriesInRange(TestCase):
    """Four entries, all on October 2007, last entry is selected"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_entry('3/10/2007', 'first', increase='1')
        self.add_entry('4/10/2007', 'second', decrease='2')
        self.add_entry('5/10/2007', 'third', increase='3')
        self.add_entry('6/10/2007', 'fourth', decrease='4')
    
    def test_balances(self):
        """Balances are correct for all entries.
        """
        self.assertEqual(self.balances(), ['1.00', '-1.00', '2.00', '-2.00'])
    
    def test_delete_entries_last(self):
        """Deleting the last entry makes the selection goes one index before"""
        self.etable.delete()
        self.assertEqual(self.etable.selected_indexes[0], 2)
    
    def test_delete_entries_second(self):
        """Deleting an entry that is not the last does not change the selected index"""
        self.etable.select([1])
        self.etable.delete()
        self.assertEqual(self.etable.selected_indexes[0], 1)
    

class EightEntries(TestCase):
    """Eight entries setup for testing entry reordering."""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_account()
        self.document.date_range = MonthRange(date(2008, 1, 1))
        self.add_entry('1/1/2007', description='previous', increase='1')
        self.add_entry('1/1/2008', description='entry 1', increase='9')
        self.add_entry('2/1/2008', description='entry 2', increase='20')
        self.add_entry('2/1/2008', description='entry 3', increase='30')
        self.add_entry('2/1/2008', description='entry 4', increase='40')
        self.add_entry('2/1/2008', description='entry 5', increase='900')
        self.add_entry('3/1/2008', description='entry 6', increase='60')
        self.add_entry('3/1/2008', description='entry 7', increase='70')

    def test_can_reorder_entry(self):
        """Move is allowed only when it makes sense."""
        self.assertFalse(self.etable.can_move([0], 2)) # Can't move the previous balance entry
        self.assertFalse(self.etable.can_move([1], 3)) # Not the same date
        self.assertFalse(self.etable.can_move([3], 1)) # Likewise
        self.assertFalse(self.etable.can_move([2], 2)) # Moving to the same row doesn't change anything
        self.assertFalse(self.etable.can_move([2], 3)) # Moving to the next row doesn't change anything
        self.assertTrue(self.etable.can_move([2], 4))
        self.assertTrue(self.etable.can_move([2], 5))  # Can move to the end of the day
        self.assertFalse(self.etable.can_move([4], 5)) # Moving to the next row doesn't change anything
        self.assertTrue(self.etable.can_move([6], 8))  # Can move beyond the bounds of the entry list
        self.assertFalse(self.etable.can_move([7], 8)) # Moving yo the next row doesn't change anything
        self.assertFalse(self.etable.can_move([7], 9)) # Out of range destination by 2 doesn't cause a crash
    
    def test_can_reorder_entry_multiple(self):
        """Move is allowed only when it makes sense."""
        self.assertTrue(self.etable.can_move([2, 3], 5)) # This one is valid
        self.assertFalse(self.etable.can_move([2, 1], 5)) # from_indexes are on different days
        self.assertFalse(self.etable.can_move([2, 3], 4)) # Nothing moving (just next to the second index)
        self.assertFalse(self.etable.can_move([2, 3], 2)) # Nothing moving (in the middle of from_indexes)
        self.assertFalse(self.etable.can_move([2, 3], 3)) # same as above
        self.assertFalse(self.etable.can_move([3, 2], 3)) # same as above, but making sure order doesn't matter
        self.assertTrue(self.etable.can_move([2, 4], 4)) # Puts 2 between 3 and 4
        self.assertTrue(self.etable.can_move([2, 4], 2)) # Puts 4 between 2 and 3
        self.assertTrue(self.etable.can_move([2, 4], 3)) # same as above
    
    def test_move_entry_to_the_end_of_the_day(self):
        """Moving an entry to the end of the day works."""
        self.etable.move([2], 6)
        self.assertEqual(self.entry_descriptions()[1:6], ['entry 1', 'entry 3', 'entry 4', 'entry 5', 'entry 2'])
        self.assertEqual(self.balances()[1:6], ['10.00', '40.00', '80.00', '980.00', '1000.00'])
    
    def test_move_entry_to_the_end_of_the_list(self):
        """Moving an entry to the end of the list works."""
        self.etable.move([6], 8)
        self.assertEqual(self.entry_descriptions()[6:], ['entry 7', 'entry 6'])
        self.assertEqual(self.balances()[6:], ['1070.00', '1130.00'])
    
    def test_reorder_entry(self):
        """Moving an entry reorders the entries."""
        self.etable.move([2], 4)
        self.assertEqual(self.entry_descriptions()[1:5], ['entry 1', 'entry 3', 'entry 2', 'entry 4'])
        self.assertEqual(self.balances()[1:5], ['10.00', '40.00', '60.00', '100.00'])
    
    def test_reorder_entry_multiple(self):
        """Multiple entries can be re-ordered at once"""
        self.etable.move([2, 3], 5)
        self.assertEqual(self.entry_descriptions()[1:5], ['entry 1', 'entry 4', 'entry 2', 'entry 3'])
    
    def test_reorder_entry_makes_the_app_dirty(self):
        """calling reorder_entry() makes the app dirty"""
        self.save_file()
        self.etable.move([2], 4)
        self.assertTrue(self.document.is_dirty())
    
    def test_selection_follows(self):
        """The selection follows when we move the selected entry."""
        self.etable.select([2])
        self.etable.move([2], 4)
        self.assertEqual(self.etable.selected_indexes[0], 3)
        self.etable.move([3], 2)
        self.assertEqual(self.etable.selected_indexes[0], 2)
    
    def test_selection_follows_multiple(self):
        """The selection follows when we move the selected entries"""
        self.etable.select([2, 3])
        self.etable.move([2, 3], 5)
        self.assertEqual(self.etable.selected_indexes, [3, 4])
    
    def test_selection_stays(self):
        """The selection stays on the same entry if we don't move the selected entry."""
        self.etable.select([3])
        self.etable.move([2], 4)
        self.assertEqual(self.etable.selected_indexes[0], 2)
        self.etable.move([3], 2)
        self.assertEqual(self.etable.selected_indexes[0], 3)
        self.etable.select([5])
        self.etable.move([2], 4)
        self.assertEqual(self.etable.selected_indexes[0], 5)
    

class FourEntriesOnTheSameDate(TestCase):
    """Four entries in the same account on the same date"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.date_range = MonthRange(date(2008, 1, 1))
        self.add_entry('1/1/2008', description='entry 1', increase='42.00')
        self.add_entry('1/1/2008', description='entry 2', increase='42.00')
        self.add_entry('1/1/2008', description='entry 3', increase='42.00')
        self.add_entry('1/1/2008', description='entry 4', increase='42.00')
    
    def test_can_reorder_entry_multiple(self):
        """Some tests can't be done in EightEntries (and it's tricky to change this testcase now...)"""
        self.assertFalse(self.etable.can_move([0, 1, 2, 3], 2)) # Nothing moving (in the middle of from_indexes)
    
    def test_move_entries_up(self):
        """Moving more than one entry up does nothing"""
        self.etable.select([1, 2])
        self.etable.move_up()
        self.assertEqual(self.entry_descriptions(), ['entry 1', 'entry 2', 'entry 3', 'entry 4'])

    def test_move_entry_down(self):
        """Move an entry down a couple of times"""
        self.etable.select([2])
        self.etable.move_down()
        self.assertEqual(self.entry_descriptions(), ['entry 1', 'entry 2', 'entry 4', 'entry 3'])
        self.etable.move_down()
        self.assertEqual(self.entry_descriptions(), ['entry 1', 'entry 2', 'entry 4', 'entry 3'])

    def test_move_entry_up(self):
        """Move an entry up a couple of times"""
        self.etable.select([1])
        self.etable.move_up()
        self.assertEqual(self.entry_descriptions(), ['entry 2', 'entry 1', 'entry 3', 'entry 4'])
        self.etable.move_up()
        self.assertEqual(self.entry_descriptions(), ['entry 2', 'entry 1', 'entry 3', 'entry 4'])


class EntrySelectionOnAccountChange(TestCase):
    """I couldn't find a better name for a setup with multiple accounts, some transactions having
    the same date, some not. The setup is to test entry selection upon account selection change."""
    def setUp(self):
        self.create_instances()
        self.add_account('asset1')
        self.add_entry('1/1/2008', transfer='expense1', decrease='42.00')
        self.add_entry('4/1/2008', transfer='expense2', decrease='42.00')
        self.add_entry('11/1/2008', transfer='expense3', decrease='42.00')
        self.add_entry('22/1/2008', transfer='expense3', decrease='42.00')
        self.add_account('asset2')
        self.add_entry('1/1/2008', transfer='expense1', decrease='42.00')
        self.add_entry('12/1/2008', transfer='expense2', decrease='42.00')
        # selected account is asset2
    
    def test_keep_date(self):
        """Explicitely selecting a transaction make it so the nearest date is found as a fallback"""
        self.etable.select([0]) # the transaction from asset2 to expense1
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.expenses[1] # expense2
        self.istatement.show_selected_account()
        # The nearest date in expense2 is 2008/1/4
        self.assertEqual(self.etable.selected_indexes, [0])
        # Now select the 2008/1/12 date
        self.etable.select([1])
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.expenses[2] # expense3
        self.istatement.show_selected_account()
        # The 2008/1/11 date is nearer than the 2008/1/22 date, so it should be selected
        self.assertEqual(self.etable.selected_indexes, [0])
    
    def test_keep_transaction(self):
        """Explicitely selecting a transaction make it so it stays selected when possible"""
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.etable.select([0]) # the transaction from asset1 to expense1
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # We select an account where the transaction don't exist
        self.bsheet.show_selected_account()
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0]
        self.istatement.show_selected_account()
        # Even though we selected asset2, the transaction from asset1 should be selected
        self.assertEqual(self.etable.selected_indexes, [0])
    
    def test_save_entry(self):
        """Chaning an entry's date also changes the date in the explicit selection"""
        row = self.etable.selected_row
        row.date = '5/1/2008'
        self.etable.save_edits()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable.selected_indexes, [1]) #2008/1/4
    

class EntrySelectionOnDateRangeChange(TestCase):
    """Multiple entries in multiple date range to test the entry selection on date range change"""
    def setUp(self):
        self.create_instances()
        self.document.select_month_range()
        self.add_account()
        self.add_entry('2/2/2007')
        self.add_entry('2/1/2008')
        self.add_entry('3/1/2008')
        self.add_entry('4/1/2008')
        self.add_entry('1/2/2008')
        self.add_entry('2/2/2008')
        self.add_entry('3/2/2008')
        # date range is on 2008/2
        # Don't forget that there's a previous balance most of the time!
        self.etable.select([3]) # 2008/2/3
    
    def test_prev_range(self):
        """Explicit entry selection keeps the same delta with the date range's start when it 
        translates"""
        self.document.select_prev_date_range()
        self.assertEqual(self.etable.selected_indexes, [2]) # 2008/1/2
    
    def test_year_range(self):
        """Even in year range, the system stays the same for range change (keep the same distance
        with the range's start"""
        self.document.select_year_range()
        self.document.select_prev_date_range()
        self.etable.select([0]) # 2007/2/2, no previous balance
        self.document.select_next_date_range()
        self.assertEqual(self.etable.selected_indexes, [5]) # 2008/2/2
    
