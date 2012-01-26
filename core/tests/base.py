# Created By: Virgil Dupras
# Created On: 2009-06-04
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op
from datetime import date, datetime
from operator import attrgetter

import pytest

from hscommon.path import Path
from hscommon.testutil import eq_, CallLogger, TestApp as TestAppBase, with_app, TestData
from hscommon.gui.base import GUIObject

from ..app import Application, AUTOSAVE_INTERVAL_PREFERENCE
from ..document import Document, ScheduleScope
from ..exception import FileFormatError
from ..const import PaneType
from ..gui.completable_edit import CompletableEdit
from ..gui.csv_options import CSVOptions
from ..gui.import_window import ImportWindow
from ..gui.main_window import MainWindow
from ..loader import base
from ..model.account import AccountType

testdata = TestData(op.join(op.dirname(__file__), 'testdata'))

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
    def __init__(self, testapp):
        CallLogger.__init__(self)
        self.messages = []
        self.testapp = testapp
    
    @log
    def show_message(self, message):
        self.messages.append(message)
    
    # Link the view of lazily loaded elements.
    @log
    def refresh_panes(self):
        print(repr(self), repr(self.testapp))
        app = self.testapp
        for i in range(app.mw.pane_count):
            app.link_gui(app.mw.pane_view(i))
    

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
        TestAppBase.__init__(self)
        make_gui = self.make_gui
        link_gui = self.link_gui
        self._tmppath = tmppath
        if app is None:
            app = Application(self.make_logger(ApplicationGUI))
        self.app = app
        self.app_gui = app.view
        if doc is None:
            doc = Document(self.app)
            doc.view = self.make_logger(DocumentGUI)
        self.doc = doc
        self.doc_gui = doc.view
        self.mainwindow = MainWindow(self.doc)
        # we set mainwindow's view at the end because it triggers daterangeselector refreshes
        # which needs to have its own view set first.
        # XXX The way our GUI instances are created in TestApp is incompatible with the lazy view
        # creation path that moneyGuru is engaged in. Changing all tests is way too big a task,
        # but we can at least make new tests comply with lazy view creation. Ideally, all these
        # "nwview", "ttable" and others wouldn't exist in TestApp, we'd get a view instance by the
        # return value of TestApp.show_*view() and access its child GUI objects through that
        # reference.
        self.mw = self.mainwindow # shortcut. This one is often typed
        self.default_parent = self.mw
        self.nwview = link_gui(self.mw.nwview)
        self.pview = link_gui(self.mw.pview)
        self.tview = link_gui(self.mw.tview)
        self.aview = link_gui(self.mw.aview)
        self.scview = link_gui(self.mw.scview)
        self.bview = link_gui(self.mw.bview)
        self.glview = link_gui(self.mw.glview)
        self.etable = link_gui(self.aview.etable)
        self.etable_gui = self.etable.view
        self.ttable = link_gui(self.tview.ttable)
        self.ttable_gui = self.ttable.view
        self.sctable = link_gui(self.scview.table)
        self.btable = link_gui(self.bview.table)
        self.gltable = link_gui(self.glview.gltable)
        self.apanel = link_gui(self.mw.account_panel)
        self.scpanel = link_gui(self.mw.schedule_panel)
        self.scsplittable = link_gui(self.scpanel.split_table)
        self.tpanel = link_gui(self.mw.transaction_panel)
        self.stable = link_gui(self.tpanel.split_table)
        self.mepanel = link_gui(self.mw.mass_edit_panel)
        self.bpanel = link_gui(self.mw.budget_panel)
        self.cdrpanel = link_gui(self.mw.custom_daterange_panel)
        self.arpanel = link_gui(self.mw.account_reassign_panel)
        self.expanel = link_gui(self.mw.export_panel)
        self.balgraph = link_gui(self.aview.balgraph)
        self.balgraph_gui = self.balgraph.view
        self.bargraph = link_gui(self.aview.bargraph)
        self.bargraph_gui = self.bargraph.view
        self.nwgraph = link_gui(self.nwview.nwgraph)
        self.nwgraph_gui = self.nwgraph.view
        self.pgraph = link_gui(self.pview.pgraph)
        self.bsheet = link_gui(self.nwview.bsheet)
        self.bsheet_gui = self.bsheet.view
        self.istatement = link_gui(self.pview.istatement)
        self.istatement_gui = self.istatement.view
        self.apie = link_gui(self.nwview.apie)
        self.lpie = link_gui(self.nwview.lpie)
        self.ipie = link_gui(self.pview.ipie)
        self.epie = link_gui(self.pview.epie)
        self.sfield = link_gui(self.mw.search_field)
        self.efbar = link_gui(self.aview.filter_bar)
        self.tfbar = link_gui(self.tview.filter_bar)
        self.drsel = link_gui(self.mw.daterange_selector)
        make_gui('csvopt', CSVOptions, parent=self.doc)
        make_gui('iwin', ImportWindow, parent=self.doc)
        self.itable = link_gui(self.iwin.import_table)
        self.alookup = link_gui(self.mw.account_lookup)
        self.clookup = link_gui(self.mw.completion_lookup)
        self.doc.connect()
        self.mw.view = self.make_logger(MainWindowGUI, self)
        self.mainwindow_gui = self.mw.view
        self.mw.connect()
    
    def link_gui(self, gui):
        if gui.view is None:
            gui.view = self.make_logger()
        # link sub GUIs too
        for elem in vars(gui).values():
            if elem is gui or elem is self.mw:
                continue
            if isinstance(elem, GUIObject) and elem.view is None:
                elem.view = self.make_logger()
        return gui
    
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
        self.bpanel.repeat_type_list.select(repeat_type_index)
        self.bpanel.repeat_every = repeat_every
        if stop_date is not None:
            self.bpanel.stop_date = stop_date
        account_index = self.bpanel.account_list.index(account_name)
        self.bpanel.account_list.select(account_index)
        target_index = self.bpanel.target_list.index(target_name) if target_name else 0
        self.bpanel.target_list.select(target_index)
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
        self.scpanel.repeat_type_list.select(repeat_type_index)
        self.scpanel.repeat_every = repeat_every
        if stop_date is not None:
            self.scpanel.stop_date = stop_date
        if account:
            self.scsplittable.add()
            self.scsplittable.edited.account = account
            if self.doc.parse_amount(amount) >= 0:
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
        self.doc.close()
        app = Application(self.app_gui)
        doc = Document(self.app)
        doc.view = self.doc_gui
        return TestApp(app=app, doc=doc)
    
    def completable_edit(self, attrname):
        ce = CompletableEdit(self.mw)
        ce.view = self.make_logger()
        ce.attrname = attrname
        return ce
    
    def do_test_save_load(self):
        newapp = self.save_and_load()
        newapp.doc.date_range = self.doc.date_range
        newapp.doc._cook()
        compare_apps(self.doc, newapp.doc)
    
    def do_test_qif_export_import(self):
        filepath = str(self.tmppath() + 'foo.qif')
        self.mainwindow.export()
        self.expanel.export_path = filepath
        self.expanel.save()
        newapp = Application(ApplicationGUI(), default_currency=self.doc.default_currency)
        newdoc = Document(newapp)
        newdoc.view = self.make_logger(DocumentGUI)
        iwin = ImportWindow(newdoc)
        self.link_gui(iwin)
        iwin.connect()
        try:
            newdoc.parse_file_for_import(filepath)
            while iwin.panes:
                iwin.import_selected_pane()
        except FileFormatError:
            pass
        compare_apps(self.doc, newdoc, qif_mode=True)
    
    def entry_descriptions(self):
        return [self.etable[i].description for i in range(len(self.etable))]
    
    def etable_count(self):
        # Now that the entry table has a total row, it messes up all tests that check the length
        # of etable. Rather than having confusing expected numbers with a comment explaining why we
        # add one to the expected count, we use this method that subtract 1 to the len of etable.
        return len(self.etable) - 1 
    
    def fake_import(self, account_name, transactions):
        # When you want to test the post-parsing import process, rather than going through the hoops,
        # use this methods. 'transactions' is a list of dicts, the dicts being attribute values.
        # dates are strings in '%d/%m/%Y'.
        self.doc.loader = DictLoader(self.doc.default_currency, account_name, transactions)
        self.doc.loader.load()
        self.doc.notify('file_loaded_for_import')
    
    def graph_data(self):
        return [(date.fromordinal(x).strftime('%d/%m/%Y'), '%2.2f' % y) for (x, y) in self.balgraph.data]
    
    def navigate_to_date(self, year, month, day):
        # navigate the current date range until target_date is in it. We use year month day to avoid
        # having to import datetime.date in tests.
        assert self.doc.date_range.can_navigate
        self.doc.date_range = self.doc.date_range.around(date(year, month, day))
    
    def new_app_same_prefs(self):
        # Returns a new TestApp() but with the same app_gui as before, thus preserving preferences.
        app = Application(self.app_gui)
        return TestApp(app=app)
    
    def nw_graph_data(self):
        return [(date.fromordinal(x).strftime('%d/%m/%Y'), '%2.2f' % y) for (x, y) in self.nwgraph.data]
    
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
    
    def select_account(self, account_name):
        # Selects the account with `account_name` in the appropriate sheet
        predicate = lambda node: getattr(node, 'is_account', False) and node.name == account_name
        self.mw.select_balance_sheet()
        node = self.bsheet.find(predicate)
        if node is not None:
            self.bsheet.selected = node
            return
        self.mw.select_income_statement()
        node = self.istatement.find(predicate)
        if node is not None:
            self.istatement.selected = node
            return
        else:
            raise LookupError("Trying to show an account that doesn't exist")
        
    def show_account(self, account_name):
        # Selects the account with `account_name` in the appropriate sheet and calls show_selected_account()
        self.select_account(account_name)
        self.mw.show_account()
    
    def set_column_visible(self, colname, visible):
        # Toggling column from the UI is rather simple for a human, but not for a program. The
        # column menu is filled with display names and colname is an identifier.
        assert self.mw._current_pane.view.columns is not None
        items = self.mw.column_menu_items()
        if colname == 'debit_credit':
            # This is a special one
            display = "Debit/Credit"
        else:
            display = self.mw._current_pane.view.columns.column_display(colname)
        itemdisplays = [item[0] for item in items]
        assert display in itemdisplays
        index = itemdisplays.index(display)
        # Now that we have our index, just toggle the menu item if the marked flag isn't what our
        # visible flag is.
        marked = items[index][1]
        if marked != visible:
            self.mw.toggle_column_menu_item(index)
    
    def transaction_descriptions(self):
        return [row.description for row in self.ttable.rows]
    
    #--- Shortcut for selecting a view type.
    def current_view(self):
        return self.mw.pane_view(self.mw.current_pane_index)
    
    def new_tab(self):
        self.mw.new_tab()
        return self.current_view()
    
    def show_nwview(self):
        self.mw.select_pane_of_type(PaneType.NetWorth)
        return self.current_view()
    
    def show_pview(self):
        self.mw.select_pane_of_type(PaneType.Profit)
        return self.current_view()
    
    def show_tview(self):
        self.mw.select_pane_of_type(PaneType.Transaction)
        return self.current_view()
    
    def show_glview(self):
        self.mw.select_pane_of_type(PaneType.GeneralLedger)
        return self.current_view()
    
    def show_dpview(self):
        self.mw.select_pane_of_type(PaneType.DocProps)
        return self.current_view()
    

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
