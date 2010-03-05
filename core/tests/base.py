# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-06-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op
from datetime import date, datetime
from operator import attrgetter

from nose.tools import nottest, istest, eq_

from hsutil.path import Path
from hsutil.testcase import TestCase as TestCaseBase

from ..app import Application, AUTOSAVE_INTERVAL_PREFERENCE
from ..document import Document, ScheduleScope
from ..exception import FileFormatError
from ..gui.account_lookup import AccountLookup
from ..gui.account_panel import AccountPanel
from ..gui.account_pie_chart import AssetsPieChart, LiabilitiesPieChart, IncomePieChart, ExpensesPieChart
from ..gui.account_reassign_panel import AccountReassignPanel
from ..gui.account_view import AccountView
from ..gui.balance_graph import BalanceGraph
from ..gui.balance_sheet import BalanceSheet
from ..gui.bar_graph import BarGraph
from ..gui.budget_panel import BudgetPanel
from ..gui.budget_table import BudgetTable
from ..gui.budget_view import BudgetView
from ..gui.completable_edit import CompletableEdit
from ..gui.completion_lookup import CompletionLookup
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
from ..gui.networth_view import NetWorthView
from ..gui.profit_graph import ProfitGraph
from ..gui.profit_view import ProfitView
from ..gui.schedule_panel import SchedulePanel
from ..gui.schedule_table import ScheduleTable
from ..gui.schedule_view import ScheduleView
from ..gui.search_field import SearchField
from ..gui.split_table import SplitTable
from ..gui.transaction_panel import TransactionPanel
from ..gui.transaction_table import TransactionTable
from ..gui.transaction_view import TransactionView
from ..loader import base
from ..model.account import AccountType
from ..model.date import MonthRange
from .. import document as document_module

class CallLogger(object):
    """This is a dummy object that logs all calls made to it.
    
    It is used to simulate the GUI layer.
    """
    def __init__(self):
        self.calls = []
    
    def __getattr__(self, func_name):
        def func(*args, **kw):
            self.calls.append(func_name)
        return func
    
    def clear_calls(self):
        del self.calls[:]
    

def log(method):
    def wrapper(self, *args, **kw):
        result = method(self, *args, **kw)
        self.calls.append(method.func_name)
        return result
    
    return wrapper

class ApplicationGUI(CallLogger):
    def __init__(self):
        CallLogger.__init__(self)
        # We don't want the autosave thread to mess up with testunits
        self.defaults = {AUTOSAVE_INTERVAL_PREFERENCE: 0}
    
    def get_default(self, key): # We don't want to log this one. It disturbs other test and is pointless to log
        return self.defaults.get(key)
    
    @log
    def set_default(self, key, value):
        self.defaults[key] = value
    

class DocumentGUI(CallLogger):
    def __init__(self):
        CallLogger.__init__(self)
        self.query_for_schedule_scope_result = ScheduleScope.Local
    
    @log
    def query_for_schedule_scope(self):
        return self.query_for_schedule_scope_result
    

class MainWindowGUI(CallLogger):
    def __init__(self, cdrpanel, arpanel):
        CallLogger.__init__(self)
        self.messages = []
        self.cdrpanel = cdrpanel
        self.arpanel = arpanel
    
    @log
    def show_account_reassign_panel(self):
        self.arpanel.load()
    
    @log
    def show_custom_date_range_panel(self):
        self.cdrpanel.load()
    
    @log
    def show_message(self, message):
        self.messages.append(message)
    

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

@nottest
class TestApp(object):
    def __init__(self, app=None, doc=None, tmppath=None):
        self.tmppath = tmppath
        if app is None:
            app = Application(ApplicationGUI())
        self.app = app
        self.app_gui = app.view
        if doc is None:
            doc = Document(DocumentGUI(), self.app)
        self.doc = doc
        self.doc_gui = doc.view
        self.arpanel_gui = CallLogger()
        self.arpanel = AccountReassignPanel(self.arpanel_gui, self.doc)
        self.cdrpanel_gui = CallLogger()
        self.cdrpanel = CustomDateRangePanel(self.cdrpanel_gui, self.doc)
        self.mainwindow_gui = MainWindowGUI(self.cdrpanel, self.arpanel)
        self.mainwindow = MainWindow(self.mainwindow_gui, self.doc)
        self.mw = self.mainwindow # shortcut. This one is often typed
        self.apanel_gui = CallLogger()
        self.apanel = AccountPanel(self.apanel_gui, self.mw)
        self.etable_gui = CallLogger()
        self.etable = EntryTable(self.etable_gui, self.mw)
        self.ttable_gui = CallLogger()
        self.ttable = TransactionTable(self.ttable_gui, self.mw)
        self.sctable_gui = CallLogger()
        self.sctable = ScheduleTable(self.sctable_gui, self.mw)
        self.btable_gui = CallLogger()
        self.btable = BudgetTable(self.btable_gui, self.mw)
        self.scpanel_gui = CallLogger()
        self.scpanel = SchedulePanel(self.scpanel_gui, self.mw)
        self.tpanel_gui = CallLogger()
        self.tpanel = TransactionPanel(self.tpanel_gui, self.mw)
        self.mepanel_gui = CallLogger()
        self.mepanel = MassEditionPanel(self.mepanel_gui, self.mw)
        self.bpanel_gui = CallLogger()
        self.bpanel = BudgetPanel(self.bpanel_gui, self.mw)
        self.stable_gui = CallLogger()
        self.stable = SplitTable(self.stable_gui, self.tpanel)
        self.scsplittable_gui = CallLogger()
        self.scsplittable = SplitTable(self.scsplittable_gui, self.scpanel)
        self.balgraph_gui = CallLogger()
        self.balgraph = BalanceGraph(self.balgraph_gui, self.mw)
        self.bargraph_gui = CallLogger()
        self.bargraph = BarGraph(self.bargraph_gui, self.mw)
        self.nwgraph_gui = CallLogger()
        self.nwgraph = NetWorthGraph(self.nwgraph_gui, self.mw)
        self.pgraph_gui = CallLogger()
        self.pgraph = ProfitGraph(self.pgraph_gui, self.mw)
        self.bsheet_gui = CallLogger()
        self.bsheet = BalanceSheet(self.bsheet_gui, self.mw)
        self.apie_gui = CallLogger()
        self.apie = AssetsPieChart(self.apie_gui, self.mw)
        self.lpie_gui = CallLogger()
        self.lpie = LiabilitiesPieChart(self.lpie_gui, self.mw)
        self.ipie_gui = CallLogger()
        self.ipie = IncomePieChart(self.ipie_gui, self.mw)
        self.epie_gui = CallLogger()
        self.epie = ExpensesPieChart(self.epie_gui, self.mw)
        self.istatement_gui = CallLogger()
        self.istatement = IncomeStatement(self.istatement_gui, self.mw)
        self.sfield_gui = CallLogger()
        self.sfield = SearchField(self.sfield_gui, self.mw)
        # There are 2 filter bars: one for etable, one for ttable
        self.efbar_gui = CallLogger()
        self.efbar = EntryFilterBar(self.efbar_gui, self.mw)
        self.tfbar_gui = CallLogger()
        self.tfbar = FilterBar(self.tfbar_gui, self.mw)
        self.csvopt_gui = CallLogger()
        self.csvopt = CSVOptions(self.csvopt_gui, self.doc)
        self.iwin_gui = CallLogger()
        self.iwin = ImportWindow(self.iwin_gui, self.doc)
        self.itable_gui = CallLogger()
        self.itable = ImportTable(self.itable_gui, self.iwin)
        self.alookup_gui = CallLogger()
        self.alookup = AccountLookup(self.alookup_gui, self.mw)
        self.clookup_gui = CallLogger()
        self.clookup = CompletionLookup(self.clookup_gui, self.mw)
        self.nwview_gui = CallLogger()
        children = [self.bsheet, self.nwgraph, self.apie, self.lpie]
        self.nwview = NetWorthView(self.nwview_gui, self.mw, children)
        self.pview_gui = CallLogger()
        children = [self.istatement, self.pgraph, self.ipie, self.epie]
        self.pview = ProfitView(self.pview_gui, self.mw, children)
        self.tview_gui = CallLogger()
        children = [self.ttable, self.tfbar]
        self.tview = TransactionView(self.tview_gui, self.mw, children)
        self.aview_gui = CallLogger()
        children = [self.etable, self.balgraph, self.bargraph, self.efbar]
        self.aview = AccountView(self.aview_gui, self.mw, children)
        self.scview_gui = CallLogger()
        children = [self.sctable]
        self.scview = ScheduleView(self.scview_gui, self.mw, children)
        self.bview_gui = CallLogger()
        children = [self.btable]
        self.bview = BudgetView(self.bview_gui, self.mw, children)
        children = [self.nwview, self.pview, self.tview, self.aview, self.scview, self.bview,
            self.apanel, self.tpanel, self.mepanel, self.scpanel, self.bpanel, self.alookup,
            self.clookup]
        self.mainwindow.set_children(children)
        self.doc.connect()
        self.mainwindow.connect()
        self.stable.connect()
        self.sfield.connect()
        self.iwin.connect()
        self.itable.connect()
        self.csvopt.connect()
    
    @staticmethod
    def check_gui_calls(gui, expected, verify_order=False):
        """Checks that the expected calls have been made to 'gui', then clears the log.
        
        `expected` is an iterable of strings representing method names.
        If `verify_order` is True, the order of the calls matters.
        """
        if verify_order:
            eq_(gui.calls, expected)
        else:
            eq_(set(gui.calls), set(expected))
        gui.clear_calls()
    
    @staticmethod
    def check_gui_calls_partial(gui, expected=None, not_expected=None):
        """Checks that the expected calls have been made to 'gui', then clears the log.
        
        `expected` is an iterable of strings representing method names. Order doesn't matter.
        Moreover, if calls have been made that are not in expected, no failure occur.
        `not_expected` can be used for a more explicit check (rather than calling `check_gui_calls`
        with an empty `expected`) to assert that calls have *not* been made.
        """
        calls = set(gui.calls)
        if expected is not None:
            expected = set(expected)
            not_called = expected - calls
            assert not not_called, u"These calls haven't been made: {0}".format(not_called)
        if not_expected is not None:
            not_expected = set(not_expected)
            called = not_expected & calls
            assert not called, u"These calls shouldn't have been made: {0}".format(called)
        gui.clear_calls()
    
    def clear_gui_calls(self):
        for attr in dir(self):
            if attr.endswith('_gui'):
                gui = getattr(self, attr)
                if hasattr(gui, 'calls'): # We might have test methods ending with '_gui'
                    gui.clear_calls()
    
    def add_account(self, name=None, currency=None, account_type=AccountType.Asset, group_name=None,
            account_number=None):
        # I wanted to use the panel here, it messes with the undo tests, we'll have to fix this eventually
        group = self.doc.groups.find(group_name, account_type) if group_name else None
        account = self.doc.new_account(account_type, group)
        attrs = {}
        if name is not None:
            attrs['name'] = name
        if currency is not None:
            attrs['currency'] = currency
        if account_number is not None:
            attrs['account_number'] = account_number
        if attrs:
            self.doc.change_account(account, **attrs)
        self.doc.select_account(account)
    
    def add_accounts(self, *names):
        # add a serie of simple accounts, *names being names for each account
        for name in names:
            self.add_account(name)
    
    def add_budget(self, account_name, target_name, str_amount, start_date=None, repeat_type_index=2,
            repeat_every=1, stop_date=None):
        # if no target, set target_name to None
        self.mainwindow.select_budget_table()
        self.mainwindow.new_item()
        if start_date is None:
            start_date = self.app.format_date(date(date.today().year, date.today().month, 1))
        self.bpanel.start_date = start_date
        self.bpanel.repeat_type_index = repeat_type_index
        self.bpanel.repeat_every = repeat_every
        if stop_date is not None:
            self.bpanel.stop_date = stop_date
        account_index = self.bpanel.account_options.index(account_name)
        self.bpanel.account_index = account_index
        target_index = self.bpanel.target_options.index(target_name) if target_name else 0
        self.bpanel.target_index = target_index
        self.bpanel.amount = str_amount
        self.bpanel.save()
    
    def add_entry(self, date=None, description=None, payee=None, transfer=None, increase=None, 
            decrease=None, checkno=None):
        # This whole "if not None" thing allows to simulate a user tabbing over fields leaving the
        # default value.
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
    
    def add_group(self, name=None, account_type=AccountType.Asset):
        group = self.doc.new_group(account_type)
        if name is not None:
            self.doc.change_group(group, name=name)
    
    def add_schedule(self, start_date=None, description='', account=None, amount='0',
            repeat_type_index=0, repeat_every=1, stop_date=None):
        if start_date is None:
            start_date = self.app.format_date(date(date.today().year, date.today().month, 1))
        self.mainwindow.select_schedule_table()
        self.scpanel.new()
        self.scpanel.start_date = start_date
        self.scpanel.description = description
        self.scpanel.repeat_type_index = repeat_type_index
        self.scpanel.repeat_every = repeat_every
        if stop_date is not None:
            self.scpanel.stop_date = stop_date
        if account:
            self.scsplittable.add()
            self.scsplittable.edited.account = account
            if self.app.parse_amount(amount) >= 0:
                self.scsplittable.edited.debit = amount
            else:
                self.scsplittable.edited.credit = amount
            self.scsplittable.save_edits()
        self.scpanel.save()
    
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
        account_sort = {
            AccountType.Asset:0,
            AccountType.Liability: 1,
            AccountType.Income: 2,
            AccountType.Expense: 3,
        }
        accounts = list(self.doc.accounts)
        accounts.sort(key=lambda a: (account_sort[a.type], a))
        return [a.name for a in accounts]
    
    def account_node_subaccount_count(self, node):
        # In the balance sheet and the income statement testing for emptyness becomes cumbersome
        # because of the 2 total nodes (1 total, 1 blank) that are always there, even if empty. To
        # avoid putting a comment next to each len() test, just use this method.
        return len(node) - 2
    
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
    
    def completable_edit(self, attrname):
        ce = CompletableEdit(CallLogger(), self.mw)
        ce.attrname = attrname
        return ce
    
    def save_file(self):
        assert self.tmppath is not None
        filename = self.tmppath + 'foo.xml'
        self.doc.save_to_xml(unicode(filename)) # reset the dirty flag
    
    def show_account(self, account_name):
        # Selects the account with `account_name` in the appropriate sheet and calls show_selected_account()
        predicate = lambda node: getattr(node, 'is_account', False) and node.name == account_name
        self.mainwindow.select_balance_sheet()
        node = self.bsheet.find(predicate)
        if node is not None:
            self.bsheet.selected = node
            self.doc.show_selected_account()
            return
        self.mainwindow.select_income_statement()
        node = self.istatement.find(predicate)
        if node is not None:
            self.istatement.selected = node
            self.doc.show_selected_account()
            return
        else:
            raise LookupError("Trying to show an account that doesn't exist")
    

def with_app(appfunc):
    # This decorator sends the app resulting from the `appfunc` call as an argument to the decorated
    # `func`. `appfunc` must return a TestApp instance. Additionally, `appfunc` can also return a
    # tuple (app, patcher). In this case, the patcher will perform unpatching after having called
    # the decorated func.
    def decorator(func):
        def wrapper(): # a test is not supposed to take args
            appresult = appfunc()
            if isinstance(appresult, tuple):
                app, patcher = appresult
            else:
                app = appresult
                patcher = None
            assert isinstance(app, TestApp)
            try:
                func(app)
            finally:
                if patcher is not None:
                    patcher.unpatch()
        
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator

# TestCase exists for legacy reasons. The preferred way of creating tests is to use TestApp. As of
# now, not all convenience methods have been moved to TestApp, but if you need one, just move it
# from TestCase to there and make the old method call the one in TestApp.
@istest # nose is sometimes confused. This is to make sure that no test is ignored.
class TestCase(TestCaseBase):
    cls_tested_module = document_module # for mocks
    
    @classmethod
    def datadirpath(cls):
        return Path(__file__)[:-1] + 'testdata'
    
    def check_gui_calls(self, *args, **kw):
        self.ta.check_gui_calls(*args, **kw)
    
    def check_gui_calls_partial(self, *args, **kw):
        self.ta.check_gui_calls_partial(*args, **kw)
    
    def clear_gui_calls(self, *args, **kw):
        self.ta.clear_gui_calls(*args, **kw)
    
    def create_instances(self):
        """Creates a Document instance along with all gui layers attached to it.
        
        If you want to create an Application or a Document instance with non-blank args, create it 
        first then call create_instance.
        """
        self.ta = TestApp(app=getattr(self, 'app', None), doc=getattr(self, 'document', None))
        self.document = self.ta.doc
        self.document_gui = self.ta.doc_gui
        names = ['app', 'apanel', 'arpanel', 'etable', 'ttable', 'sctable', 'btable', 'scpanel',
            'tpanel', 'mepanel', 'bpanel', 'stable', 'scsplittable', 'balgraph', 'bargraph',
            'nwgraph', 'pgraph', 'bsheet', 'apie', 'lpie', 'ipie', 'epie', 'istatement', 'sfield',
            'efbar', 'tfbar', 'csvopt', 'iwin', 'itable', 'cdrpanel', 'nwview', 'pview', 'tview',
            'aview', 'scview', 'bview', 'mainwindow']
        for name in names:
            guiname = name + '_gui'
            setattr(self, name, getattr(self.ta, name))
            setattr(self, guiname, getattr(self.ta, guiname))
    
    def account_names(self, *args, **kw):
        return self.ta.account_names(*args, **kw)
    
    def add_account(self, *args, **kw):
        self.ta.add_account(*args, **kw)
    
    def add_account_legacy(self, *args, **kwargs):
        # In the early development stages, moneyGuru's account were on a left section and when an
        # account would be selected, its entries would show on the right. This means that a lot of
        # early tests assume that adding an account (which selects it) means that an entry could be
        # added right away. Then, a gui change was made, and the current "view" scheme was adopted.
        # No longer would entries automatically be visible when an account was added, thus making a
        # lot of tests fail. For simplicity, I had TestCase.add_account() automatically perform a
        # show_selected_account() call, which made tests pass. However, with the new view based gui,
        # I soon had to create tests that require the current view to stay on the sheet on which it
        # was created. There was a "select" argument to add_account, but I was always forgetting
        # about it, thus leading to most add_account() calls being followed by workarounds for the
        # fact that the Entry view was selected. This would lead to generally uglier tests. This
        # went for *way* too long. I'm now creating add_account_legacy method so that the default
        # behavior is not the legacy one anymore. To avoid invalidating or messing with any tests,
        # I made all existing tests (except those with an explicit "select=False") call
        # add_account_legacy(), but this shouldn't be used anymore. From now on, when adding tests
        # around such calls, calls to add_account_legacy() should be replaced by an add_account()
        # call followed or not by a show_selected_account(), depending on the carefully evaluated
        # situation. Such carefulness can hardly be achieved in a mass re-factoring, so it has to be
        # made progressively.
        self.add_account(*args, **kwargs)
        self.document.show_selected_account()
    
    def add_accounts(self, *args, **kw):
        self.ta.add_accounts(*args, **kw)
    
    def add_budget(self, *args, **kw):
        self.ta.add_budget(*args, **kw)
    
    def add_entry(self, *args, **kw):
        self.ta.add_entry(*args, **kw)
    
    def add_group(self, *args, **kw):
        self.ta.add_group(*args, **kw)
    
    def add_schedule(self, *args, **kw):
        self.ta.add_schedule(*args, **kw)
    
    def add_txn(self, *args, **kw):
        self.ta.add_txn(*args, **kw)
    
    def account_node_subaccount_count(self, *args, **kw):
        return self.ta.account_node_subaccount_count(*args, **kw)
    
    def balances(self):
        return [self.etable[i].balance for i in range(len(self.etable))]
    
    def bar_graph_data(self, *args, **kw):
        return self.ta.bar_graph_data(*args, **kw)
    
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
    
    def notify_first(self, listener, broadcaster):
        """Changes `broadcaster` listeners to make sure `listener` is notified first.
        
        Sometimes, we have to re-create situations where a listener is notified of an event before
        another. The Broadcaster doesn't guarantee any order. Therefore, to perform such test we
        have to fiddle with the broadcaster's listener collection, which is what we do here.
        """
        class MySet(set):
            notify_first = listener
            def __iter__(self):
                yield self.notify_first
                for item in set.__iter__(self):
                    if item is not self.notify_first:
                        yield item
        
        assert listener in broadcaster.listeners
        broadcaster.listeners = MySet(broadcaster.listeners)
    
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
            newapp = Application(ApplicationGUI(), default_currency=self.app.default_currency)
        else:
            newapp = self.app
        newdoc = Document(DocumentGUI(), newapp)
        newdoc.new_account(AccountType.Asset, None) # shouldn't be there after the load
        newdoc.load_from_xml(filepath)
        self.document._cook() # Make sure the balances have been converted using the latest fetched rates
        return newdoc
    
    def show_account(self, *args, **kw):
        self.ta.show_account(*args, **kw)
    
    def transaction_descriptions(self):
        return [row.description for row in self.ttable]
    

def compare_apps(first, second, qif_mode=False):
    def compare_txns(txn1, txn2):
        try: # XXX Why is there a try/except here? To catch silently some exeptions?
            eq_(txn1.date, txn2.date)
            eq_(txn1.description, txn2.description)
            eq_(txn1.payee, txn2.payee)
            eq_(txn1.checkno, txn2.checkno)
            if not qif_mode:
                eq_(txn1.notes, txn2.notes)
            eq_(len(txn1.splits), len(txn2.splits))
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
                eq_(account1, account2)
                if qif_mode:
                    if split1.amount and split2.amount:
                        eq_(split1.amount.value, split2.amount.value)
                    else:
                        eq_(split1.amount, split2.amount)
                else:
                    eq_(split1.memo, split2.memo)
                    eq_(split1.amount, split2.amount)
                eq_(split1.reconciled, split2.reconciled)
            except AssertionError:
                raise
    
    eq_(len(first.groups), len(second.groups))
    group_pairs = zip(sorted(first.groups, key=attrgetter('name')),
        sorted(second.groups, key=attrgetter('name')))
    for group1, group2 in group_pairs:
        try:
            eq_(group1.name, group2.name)
            eq_(group1.type, group2.type)
        except AssertionError:
            raise
    eq_(len(first.accounts), len(second.accounts))
    account_pairs = zip(sorted(first.accounts, key=attrgetter('name')),
        sorted(second.accounts, key=attrgetter('name')))
    for account1, account2 in account_pairs:
        try:
            eq_(account1.name, account2.name)
            eq_(account1.type, account2.type)
            if not qif_mode:
                eq_(account1.currency, account2.currency)
            eq_(len(account1.entries), len(account2.entries))
        except AssertionError:
            raise
    eq_(len(first.transactions), len(second.transactions))
    for txn1, txn2 in zip(first.transactions, second.transactions):
        compare_txns(txn1, txn2)
    eq_(len(first.schedules), len(second.schedules))
    for rec1, rec2 in zip(first.schedules, second.schedules):
        eq_(rec1.repeat_type, rec2.repeat_type)
        eq_(rec1.repeat_every, rec2.repeat_every)
        compare_txns(rec1.ref, rec2.ref)
        eq_(rec1.stop_date, rec2.stop_date)
        eq_(len(rec1.date2exception), len(rec2.date2exception))
        for date in rec1.date2exception:
            exc1 = rec1.date2exception[date]
            exc2 = rec2.date2exception[date]
            if exc1 is None:
                assert exc2 is None
            else:
                compare_txns(exc1, exc2)
        eq_(len(rec1.date2globalchange), len(rec2.date2globalchange))
        for date in rec1.date2globalchange:
            txn1 = rec1.date2globalchange[date]
            txn2 = rec2.date2globalchange[date]
            compare_txns(txn1, txn2)
    for budget1, budget2 in zip(first.budgets, second.budgets):
        eq_(budget1.account.name, budget2.account.name)
        if budget1.target is None:
            assert budget2.target is None
        else:
            eq_(budget1.target.name, budget2.target.name)
        eq_(budget1.amount, budget2.amount)
        eq_(budget1.notes, budget2.notes)
        eq_(budget1.repeat_type, budget2.repeat_type)
        eq_(budget1.start_date, budget2.start_date)
        eq_(budget1.stop_date, budget2.stop_date)
        eq_(budget1.repeat_every, budget2.repeat_every)

@nottest
class TestAppCompareMixin(object):
    # qif_mode: don't compare reconciliation status and, don't compare memos
    def _compareapps(self, first, second, qif_mode=False):
        compare_apps(first, second, qif_mode)

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
        newapp = Application(ApplicationGUI(), default_currency=self.app.default_currency)
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
    
    def setup_one_entry_in_previous_range(self):
        # One entry with a date before the start of the current range. The only entry in the entry list
        # is a previous balance
        self.add_account_legacy()
        self.add_entry('1/1/2008')
        self.document.date_range = MonthRange(date(2008, 2, 1))
    
    def setup_scheduled_transaction(self, start_date='13/09/2008', description='foobar', 
            account=None, debit=None, repeat_type_index=0, repeat_every=1, stop_date=None):
        # 0 = daily, 1 = weekly, etc..
        # This setup also wraps a monthly range around the newly created schedule
        self.document.date_range = MonthRange(self.app.parse_date(start_date))
        self.mainwindow.select_schedule_table()
        self.scpanel.new()
        self.scpanel.start_date = start_date
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
    
    def setup_account_with_budget(self, is_expense=True, account_name='Some Expense', target_name=None):
        # 4 days left to the month, 100$ monthly budget
        self.mock_today(2008, 1, 27)
        self.document.select_today_date_range()
        account_type = AccountType.Expense if is_expense else AccountType.Income
        self.add_account_legacy(account_name, account_type=account_type)
        self.add_budget(account_name, target_name, '100')
        self.mainwindow.select_income_statement()
    
