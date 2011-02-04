# Created By: Virgil Dupras
# Created On: 2009-06-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op
from datetime import date, datetime
from operator import attrgetter

import pytest

from hscommon.path import Path
from hscommon.testcase import TestCase as TestCaseBase
from hscommon.testutil import eq_
from hscommon.testutil import CallLogger, TestApp as TestAppBase, with_app

from ..app import Application, AUTOSAVE_INTERVAL_PREFERENCE
from ..document import Document, ScheduleScope
from ..exception import FileFormatError
from ..const import PaneType
from ..gui.account_balance_graph import AccountBalanceGraph
from ..gui.account_flow_graph import AccountFlowGraph
from ..gui.account_lookup import AccountLookup
from ..gui.account_panel import AccountPanel
from ..gui.account_pie_chart import AssetsPieChart, LiabilitiesPieChart, IncomePieChart, ExpensesPieChart
from ..gui.account_reassign_panel import AccountReassignPanel
from ..gui.account_view import AccountView
from ..gui.balance_sheet import BalanceSheet
from ..gui.budget_panel import BudgetPanel
from ..gui.budget_table import BudgetTable
from ..gui.budget_view import BudgetView
from ..gui.completable_edit import CompletableEdit
from ..gui.completion_lookup import CompletionLookup
from ..gui.csv_options import CSVOptions
from ..gui.custom_date_range_panel import CustomDateRangePanel
from ..gui.date_range_selector import DateRangeSelector
from ..gui.empty_view import EmptyView
from ..gui.entry_table import EntryTable
from ..gui.export_panel import ExportPanel
from ..gui.export_account_table import ExportAccountTable
from ..gui.filter_bar import TransactionFilterBar, EntryFilterBar
from ..gui.general_ledger_table import GeneralLedgerTable
from ..gui.general_ledger_view import GeneralLedgerView
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
from ..gui.view_options import ViewOptions
from ..loader import base
from ..model.account import AccountType
from .. import document as document_module
from . import ensure_ratesdb_patched

def log(method):
    def wrapper(self, *args, **kw):
        result = method(self, *args, **kw)
        self.calls.append(method.__name__)
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
    def __init__(self):
        CallLogger.__init__(self)
        self.messages = []
    
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

class TestApp(TestAppBase):
    def __init__(self, app=None, doc=None, tmppath=None):
        make_gui = self.make_gui
        def make_table_gui(name, class_, view=None, parent=None, holder=None):
            gui = make_gui(name, class_, view, parent, holder)
            if holder is None:
                holder = self
            colview = CallLogger()
            setattr(holder, '{0}col_gui'.format(name), colview)
            gui.columns.view = colview
        
        ensure_ratesdb_patched()
        self._tmppath = tmppath
        if app is None:
            app = Application(ApplicationGUI())
        self.app = app
        self.app_gui = app.view
        if doc is None:
            doc = Document(DocumentGUI(), self.app)
        self.doc = doc
        self.doc_gui = doc.view
        make_gui('mainwindow', MainWindow, view=MainWindowGUI(), parent=self.doc)
        self.mw = self.mainwindow # shortcut. This one is often typed
        make_gui('nwview', NetWorthView)
        make_gui('pview', ProfitView)
        make_gui('tview', TransactionView)
        make_gui('aview', AccountView)
        make_gui('scview', ScheduleView)
        make_gui('bview', BudgetView)
        make_gui('glview', GeneralLedgerView)
        make_gui('emptyview', EmptyView)
        make_table_gui('etable', EntryTable, parent=self.aview)
        make_table_gui('ttable', TransactionTable, parent=self.tview)
        make_table_gui('sctable', ScheduleTable, parent=self.scview)
        make_table_gui('btable', BudgetTable, parent=self.bview)
        make_table_gui('gltable', GeneralLedgerTable, parent=self.glview)
        make_gui('apanel', AccountPanel)
        make_gui('scpanel', SchedulePanel)
        make_gui('tpanel', TransactionPanel)
        make_gui('mepanel', MassEditionPanel)
        make_gui('bpanel', BudgetPanel)
        make_gui('cdrpanel', CustomDateRangePanel)
        make_gui('arpanel', AccountReassignPanel)
        make_gui('expanel', ExportPanel)
        make_table_gui('table', ExportAccountTable, parent=self.expanel, holder=self.expanel)
        make_table_gui('stable', SplitTable, parent=self.tpanel)
        make_table_gui('scsplittable', SplitTable, parent=self.scpanel)
        make_gui('balgraph', AccountBalanceGraph, parent=self.aview)
        make_gui('bargraph', AccountFlowGraph, parent=self.aview)
        make_gui('nwgraph', NetWorthGraph, parent=self.nwview)
        make_gui('pgraph', ProfitGraph, parent=self.pview)
        make_table_gui('bsheet', BalanceSheet, parent=self.nwview)
        make_gui('apie', AssetsPieChart, parent=self.nwview)
        make_gui('lpie', LiabilitiesPieChart, parent=self.nwview)
        make_gui('ipie', IncomePieChart, parent=self.pview)
        make_gui('epie', ExpensesPieChart, parent=self.pview)
        make_table_gui('istatement', IncomeStatement, parent=self.pview)
        make_gui('sfield', SearchField)
        # There are 2 filter bars: one for etable, one for ttable
        make_gui('efbar', EntryFilterBar, parent=self.aview)
        make_gui('tfbar', TransactionFilterBar, parent=self.tview)
        make_gui('drsel', DateRangeSelector)
        make_gui('csvopt', CSVOptions, parent=self.doc)
        make_gui('iwin', ImportWindow, parent=self.doc)
        make_table_gui('itable', ImportTable, parent=self.iwin)
        make_gui('alookup', AccountLookup)
        make_gui('clookup', CompletionLookup)
        make_gui('vopts', ViewOptions)
        # set children
        children = [self.bsheet, self.nwgraph, self.apie, self.lpie]
        self.nwview.set_children(children)
        children = [self.istatement, self.pgraph, self.ipie, self.epie]
        self.pview.set_children(children)
        children = [self.ttable, self.tfbar]
        self.tview.set_children(children)
        children = [self.etable, self.balgraph, self.bargraph, self.efbar]
        self.aview.set_children(children)
        children = [self.sctable]
        self.scview.set_children(children)
        children = [self.btable]
        self.bview.set_children(children)
        children = [self.gltable]
        self.glview.set_children(children)
        # None between bview and empty view is the Cashculator view, which isn't tested
        children = [self.nwview, self.pview, self.tview, self.aview, self.scview, self.bview, None,
            self.glview, self.emptyview, self.apanel, self.tpanel, self.mepanel, self.scpanel,
            self.bpanel, self.cdrpanel, self.arpanel, self.expanel, self.alookup, self.clookup,
            self.drsel, self.vopts]
        self.mainwindow.set_children(children)
        self.doc.connect()
        self.mainwindow.connect()
        self.stable.connect()
        self.sfield.connect()
        self.iwin.connect()
        self.itable.connect()
        self.csvopt.connect()
        self.expanel.table.connect()
    
    def tmppath(self):
        if self._tmppath is None:
            self._tmppath = Path(str(pytest.ensuretemp('mgtest')))
        return self._tmppath
    
    def check_current_pane(self, pane_type, account_name=None):
        """Asserts that the currently selecte pane in the main window is of the specified type and,
        optionally, shows the correct account.
        """
        index = self.mw.current_pane_index
        eq_(self.mw.pane_type(index), pane_type)
        if account_name is not None:
            # This method is a little flimsy (testing account name through pane label), but it works
            # for now.
            eq_(self.mw.pane_label(index), account_name)
    
    @staticmethod
    def check_gui_calls(gui, *args, **kwargs):
        gui.check_gui_calls(*args, **kwargs)
    
    @staticmethod
    def check_gui_calls_partial(gui, *args, **kwargs):
        gui.check_gui_calls_partial(*args, **kwargs)
    
    def add_account(self, name=None, currency=None, account_type=AccountType.Asset, group_name=None,
            account_number=None):
        # This method simulates what a user would do to add an account with the specified attributes
        # Note that, undo-wise, this operation is not atomic.
        if account_type in (AccountType.Income, AccountType.Expense):
            self.mw.select_income_statement()
            sheet = self.istatement
            if account_type == AccountType.Income:
                sheet.selected = sheet.income
            else:
                sheet.selected = sheet.expenses
        else:
            self.mw.select_balance_sheet()
            sheet = self.bsheet
            if account_type == AccountType.Asset:
                sheet.selected = sheet.assets
            else:
                sheet.selected = sheet.liabilities
        if group_name:
            predicate = lambda n: n.name == group_name
            group_node = sheet.find(predicate, include_self=False)
            if group_node:
                sheet.selected = group_node
        self.mw.new_item()
        if currency or account_number:
            self.mw.edit_item()
            if name:
                self.apanel.name = name
            if currency:
                self.apanel.currency = currency
            if account_number:
                self.apanel.account_number = account_number
            self.apanel.save()
        elif name is not None:
            sheet.selected.name = name
            sheet.save_edits()
    
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
            decrease=None, checkno=None, reconciliation_date=None):
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
        if reconciliation_date is not None:
            row.reconciliation_date = reconciliation_date
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
        self.mw.select_transaction_table()
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
    
    def add_txn_with_splits(self, splits, date=None, description=None, payee=None, checkno=None):
        # If splits is not None, additional splits will be added to the txn. The format of the 
        # splits argument is [(account_name, memo, debit, credit)]. Don't forget that if they don't
        # balance, you end up with an imbalance split.
        self.add_txn(date=date, description=description, payee=payee, checkno=checkno)
        self.mw.edit_item()
        for index, (account, memo, debit, credit) in enumerate(splits):
            if index >= len(self.stable):
                self.stable.add()
            row = self.stable[index]
            row.account = account
            row.memo = memo
            row.debit = debit
            row.credit = credit
            self.stable.save_edits()
        self.tpanel.save()
    
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
    
    def etable_count(self):
        # Now that the entry table has a total row, it messes up all tests that check the length
        # of etable. Rather than having confusing expected numbers with a comment explaining why we
        # add one to the expected count, we use this method that subtract 1 to the len of etable.
        return len(self.etable) - 1 
    
    def navigate_to_date(self, year, month, day):
        # navigate the current date range until target_date is in it. We use year month day to avoid
        # having to import datetime.date in tests.
        assert self.doc.date_range.can_navigate
        self.doc.date_range = self.doc.date_range.around(date(year, month, day))
    
    def new_app_same_prefs(self):
        # Returns a new TestApp() but with the same app_gui as before, thus preserving preferences.
        app = Application(self.app_gui)
        return TestApp(app=app)
    
    def save_and_load(self):
        # saves the current document and returns a new app with that document loaded
        filepath = self.tmppath() + 'foo.xml'
        self.doc.save_to_xml(str(filepath))
        self.doc.close()
        newapp = TestApp(app=self.app)
        newapp.doc.load_from_xml(str(filepath))
        return newapp
    
    def save_file(self):
        filename = str(self.tmppath() + 'foo.xml')
        self.doc.save_to_xml(filename) # reset the dirty flag
        return filename
    
    def show_account(self, account_name):
        # Selects the account with `account_name` in the appropriate sheet and calls show_selected_account()
        predicate = lambda node: getattr(node, 'is_account', False) and node.name == account_name
        self.mw.select_balance_sheet()
        node = self.bsheet.find(predicate)
        if node is not None:
            self.bsheet.selected = node
            self.mw.show_account()
            return
        self.mw.select_income_statement()
        node = self.istatement.find(predicate)
        if node is not None:
            self.istatement.selected = node
            self.mw.show_account()
            return
        else:
            raise LookupError("Trying to show an account that doesn't exist")
    
    def transaction_descriptions(self):
        return [row.description for row in self.ttable.rows]
    
    #--- Shortcut for selecting a view type.
    def show_tview(self):
        self.mw.select_pane_of_type(PaneType.Transaction)
    
    def show_glview(self):
        self.mw.select_pane_of_type(PaneType.GeneralLedger)
    

class TestData:
    @classmethod
    def datadirpath(cls):
        return Path(__file__)[:-1] + 'testdata'
    
    @classmethod
    def filepath(cls, relative_path, *args):
        if args:
            relative_path = op.join([relative_path] + list(args))
        testpath = cls.datadirpath()
        result = str(testpath + relative_path)
        assert op.exists(result)
        return result
    

# TestCase exists for legacy reasons. The preferred way of creating tests is to use TestApp. As of
# now, not all convenience methods have been moved to TestApp, but if you need one, just move it
# from TestCase to there and make the old method call the one in TestApp.
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
            'efbar', 'tfbar', 'drsel', 'csvopt', 'iwin', 'itable', 'cdrpanel', 'nwview', 'pview',
            'tview', 'aview', 'scview', 'bview', 'mainwindow']
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
        self.mainwindow.show_account()
    
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
    
    def do_test_save_load(self):
        newdoc = self.save_and_load()
        newdoc.date_range = self.document.date_range
        newdoc._cook()
        compare_apps(self.document, newdoc)
    
    def do_test_qif_export_import(self):
        filepath = op.join(self.tmpdir(), 'foo.qif')
        self.mainwindow.export()
        self.ta.expanel.export_path = filepath
        self.ta.expanel.save()
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
        compare_apps(self.document, newdoc, qif_mode=True)
    
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
    
    def transaction_descriptions(self, *args, **kw):
        return self.ta.transaction_descriptions(*args, **kw)
    

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
    group_pairs = list(zip(sorted(first.groups, key=attrgetter('name')),
        sorted(second.groups, key=attrgetter('name'))))
    for group1, group2 in group_pairs:
        try:
            eq_(group1.name, group2.name)
            eq_(group1.type, group2.type)
        except AssertionError:
            raise
    eq_(len(first.accounts), len(second.accounts))
    account_pairs = list(zip(sorted(first.accounts, key=attrgetter('name')),
        sorted(second.accounts, key=attrgetter('name'))))
    for account1, account2 in account_pairs:
        try:
            eq_(account1.name, account2.name)
            eq_(account1.type, account2.type)
            if not qif_mode:
                eq_(account1.currency, account2.currency)
                eq_(account1.account_number, account2.account_number)
                eq_(account1.notes, account2.notes)
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

class CommonSetup(object):
    def setup_account_with_budget(self, is_expense=True, account_name='Some Expense', target_name=None):
        # 4 days left to the month, 100$ monthly budget
        self.mock_today(2008, 1, 27)
        self.drsel.select_today_date_range()
        account_type = AccountType.Expense if is_expense else AccountType.Income
        self.add_account_legacy(account_name, account_type=account_type)
        self.add_budget(account_name, target_name, '100')
        self.mainwindow.select_income_statement()
    
