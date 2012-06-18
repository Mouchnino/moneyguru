# Created By: Eric Mc Sween
# Created On: 2008-01-02
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
from datetime import date

from pytest import raises
from hscommon import io
from hscommon.currency import EUR
from hscommon.path import Path
from hscommon.testutil import eq_

from .base import ApplicationGUI, TestApp, with_app, testdata
from ..app import Application
from ..document import Document, AUTOSAVE_BUFFER_COUNT
from ..exception import FileFormatError
from ..gui.entry_table import EntryTable
from ..loader import base
from ..model.account import AccountType
from ..model.date import MonthRange, QuarterRange, YearRange

#--- No Setup
def test_can_use_another_amount_format():
    app = TestApp(app=Application(ApplicationGUI(), decimal_sep=',', grouping_sep=' '))
    app.add_account()
    app.show_account()
    app.add_entry(increase='1234567890.99')
    eq_(app.etable[0].increase, '1 234 567 890,99')

def test_can_use_another_date_format():
    app = TestApp(Application(ApplicationGUI(), date_format='MM-dd-yyyy'))
    app.add_account()
    app.show_account()
    app.add_entry(date='2-15-2008')
    eq_(app.etable[0].date, '02-15-2008')

def test_auto_decimal_place_option():
    # When auto_decimal_place is True, decimal point is automatically placed in an amount without it.
    # This test is just there to makesure that the option correctly triggers the feature. The rest
    # of the tests are directly in model.amount_test.
    app = TestApp()
    app.app.auto_decimal_place = True
    app.add_txn(amount='1234')
    eq_(app.ttable[0].amount, '12.34')

def test_close_document():
    # when the document is closed, the date range type and the first weekday are saved to 
    # preferences.
    app = TestApp()
    app.drsel.select_year_range()
    app.app.autosave_interval = 8
    app.app.auto_decimal_place = True
    app.doc.close()
    newapp = Application(app.app_gui)
    newdoc = Document(newapp)
    newdoc.view = app.doc_gui
    newapp = TestApp(app=newapp, doc=newdoc)
    assert isinstance(newdoc.date_range, YearRange)
    eq_(newapp.app.autosave_interval, 8)
    eq_(newapp.app.auto_decimal_place, True)

def test_graph_yaxis():
    app = TestApp()
    app.show_nwview()
    eq_(app.nwgraph.ymin, 0)
    eq_(app.nwgraph.ymax, 100)
    eq_(list(app.nwgraph.ytickmarks), list(range(0, 101, 20)))
    eq_(list(app.nwgraph.ylabels), [dict(text=str(x), pos=x) for x in range(0, 101, 20)])

@with_app(TestApp)
def test_invalid_date_input(app):
    # Don't crash on invalid date input. Normally, the date widget is not supposed to result in
    # invalid dates, but there have been such cases before.
    app.show_tview()
    app.ttable.add()
    app.ttable[0].date = 'invalid' # no crash

def test_load_inexistant(tmpdir):
    # Raise FileFormatError when filename doesn't exist
    app = TestApp()
    filename = str(tmpdir.join('does_not_exist.xml'))
    with raises(FileFormatError):
        app.doc.load_from_xml(filename)

def test_load_invalid():
    # Raises FileFormatError, which gives a message kind of like: <filename> is not a moneyGuru
    # file.
    app = TestApp()
    filename = testdata.filepath('randomfile')
    try:
        app.doc.load_from_xml(filename)
    except FileFormatError as e:
        assert filename in str(e)
    else:
        raise AssertionError()

def test_load_empty(monkeypatch):
    # When loading an empty file (we mock it here), make sure no exception occur.
    app = TestApp()
    monkeypatch.setattr(base.Loader, 'parse', lambda self, filename: None)
    monkeypatch.setattr(base.Loader, 'load', lambda self: None)
    app.doc.load_from_xml('filename does not matter here')

def test_modified_flag():
    # The modified flag is initially False.
    app = TestApp()
    assert not app.doc.is_dirty()

#--- Range on October 2007
def app_range_on_october2007(monkeypatch):
    monkeypatch.patch_today(2007, 10, 1)
    app = TestApp()
    app.drsel.select_month_range()
    app.show_nwview()
    return app

@with_app(app_range_on_october2007)
def test_graph_xaxis(app):
    eq_(app.nwgraph.xmax - app.nwgraph.xmin, 31)
    eq_(app.nwgraph.xtickmarks, [app.nwgraph.xmin + x - 1 for x in [1, 32]])
    [label] = app.nwgraph.xlabels # there is only one
    eq_(label['text'], 'October')
    app.drsel.select_quarter_range()
    eq_(app.nwgraph.xmax - app.nwgraph.xmin, 92)
    eq_(app.nwgraph.xtickmarks, [app.nwgraph.xmin + x for x in [0, 31, 61, 92]])
    expected = [dict(text=text, pos=app.nwgraph.xmin + pos) 
        for (text, pos) in [('October', 15.5), ('November', 31 + 15), ('December', 61 + 15.5)]]
    eq_(app.nwgraph.xlabels, expected)
    app.drsel.select_year_range()
    expected = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    eq_([d['text'] for d in app.nwgraph.xlabels], expected)

class TestRangeOnJuly2006:
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2006, 7, 1))
        app.show_nwview()
        return app
    
    @with_app(do_setup)
    def test_graph_xaxis(self, app):
        eq_(app.nwgraph.xtickmarks, [app.nwgraph.xmin + x - 1 for x in [1, 32]])
    

class TestRangeOnYearToDate:
    def do_setup(self, monkeypatch):
        app = TestApp()
        monkeypatch.patch_today(2008, 11, 12)
        app.drsel.select_year_to_date_range()
        app.show_nwview()
        return app
    
    @with_app(do_setup)
    def test_graph_xaxis(self, app):
        # The graph xaxis shows abbreviated month names
        expected = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
        eq_([d['text'] for d in app.nwgraph.xlabels], expected)
    

class TestOneEmptyAccountRangeOnOctober2007:
    # One empty account, range on October 2007
    def do_setup(self):
        app = TestApp()
        app.add_account('Checking', EUR)
        app.show_account()
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_autosave(self, app, tmpdir):
        # Testing the interval between autosaves would require some complicated mocking. We're just
        # going to cheat here and call 'must_autosave' directly.
        cache_path = Path(str(tmpdir))
        app.app.cache_path = cache_path
        app.doc.must_autosave()
        eq_(len(io.listdir(cache_path)), 1)
        app.check_gui_calls_partial(app.etable_gui, not_expected=['stop_edition'])
        assert app.doc.is_dirty
        # test that the autosave file rotation works
        for i in range(AUTOSAVE_BUFFER_COUNT):
            app.doc.must_autosave()
        # The extra autosave file has been deleted
        eq_(len(io.listdir(cache_path)), AUTOSAVE_BUFFER_COUNT)
    
    @with_app(do_setup)
    def test_balance_recursion_limit(self, app):
        # Balance calculation don't cause recursion errors when there's a lot of them.
        sys.setrecursionlimit(100)
        for i in range(100):
            app.add_entry('1/10/2007')
        try:
            app.etable[-1].balance
        except RuntimeError:
            raise AssertionError()
        finally:
            sys.setrecursionlimit(1000)
    
    @with_app(do_setup)
    def test_modified_flag(self, app):
        # Adding an account is a modification.
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_save(self, app, tmpdir):
        # Saving puts the modified flag back to false.
        app.doc.save_to_xml(str(tmpdir.join('foo.xml')))
        assert not app.doc.is_dirty()
    

class TestThreeAccountsAndOneEntry:
    def do_setup(self):
        app = TestApp()
        app.add_accounts('one', 'two')
        app.show_account()
        app.add_entry(transfer='three', increase='42')
        return app
    
    @with_app(do_setup)
    def test_bind_entry_to_income_expense_accounts(self, app):
        # Adding an entry with a transfer named after an existing income creates a bound entry in
        # that account.
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        app.add_entry(transfer='three')
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        eq_(app.etable_count(), 2)
    

class TestEntryInEditionMode:
    # An empty account, but an entry is in edit mode in october 2007.
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.show_account()
        app.save_file()
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        app.etable.add()
        row = app.etable.edited
        row.date = '1/10/2007'
        row.description = 'foobar'
        row.increase = '42.00'
        return app
    
    @with_app(do_setup)
    def test_add_entry(self, app):
        # Make sure that the currently edited entry is saved before another one is added.
        app.etable.add()
        eq_(app.etable_count(), 2)
        eq_(app.etable[0].date, '01/10/2007')
        eq_(app.etable[0].description, 'foobar')
        eq_(app.etable[0].increase, '42.00')
    
    @with_app(do_setup)    
    def test_delete_entries(self, app):
        # Calling delete_entries() while in edition mode removes the edited entry and put the app
        # out of edition mode.
        app.etable.delete()
        eq_(app.etable_count(), 0)
        app.etable.save_edits() # Shouldn't raise anything
    
    @with_app(do_setup)
    def test_increase_and_decrease(self, app):
        # Test the increase/decrease amount mechanism.
        row = app.etable.selected_row
        eq_(row.increase, '42.00')
        eq_(row.decrease, '')
        row.decrease = '50'
        eq_(row.increase, '')
        eq_(row.decrease, '50.00')
        row.increase = '-12.42'
        eq_(row.increase, '')
        eq_(row.decrease, '12.42')
    
    @with_app(do_setup)
    def test_revert_entry(self, app):
        # Reverting a newly added entry deletes it.
        app.etable.cancel_edits()
        eq_(app.etable_count(), 0)
        assert not app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_selected_entry_index(self, app):
        # entries.selected_index follows every entry that is added.
        eq_(app.etable.selected_indexes, [0])
    
    @with_app(do_setup)
    def test_set_debit_to_zero_with_zero_credit(self, app):
        # Setting debit to zero when the credit is already zero sets the amount to zero.
        row = app.etable.selected_row
        row.increase = ''
        eq_(app.etable[0].increase, '')
       
    @with_app(do_setup) 
    def test_set_credit_to_zero_with_non_zero_debit(self, app):
        # Setting credit to zero when the debit being non-zero does nothing.
        row = app.etable.selected_row
        row.decrease = ''
        eq_(app.etable[0].increase, '42.00')
    

class TestOneEntryYearRange2007:
    # One account, one entry, which is in the yearly date range (2007). The entry has a transfer
    # and a debit value set.
    def do_setup(self):
        app = TestApp()
        app.add_account('Checking')
        app.show_account()
        app.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00', checkno='42')
        app.doc.date_range = YearRange(date(2007, 1, 1))
        return app
    
    def _test_entry_attribute_get_set(self, app, column, value='some_value'):
        # Test that the get/set mechanism works correctly (sets the edition flag appropriately and 
        # set the value underneath).
        row = app.etable.selected_row
        setattr(row, column, value) # Sets the flag
        app.etable.save_edits()
        # Make sure that the values really made it down in the model by using a spanking new gui
        etable = EntryTable(app.aview)
        etable.view = app.etable_gui
        etable.columns.view = app.etable_gui
        etable.connect()
        etable.show()
        eq_(getattr(etable[0], column), value)
        app.save_file()
        row = app.etable.selected_row
        setattr(row, column, value) # Doesn't set the flag
        app.etable.save_edits() # Shouldn't do anything
        assert not app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_change_transfer(self, app):
        # The 'Salary' account must be deleted when the bound entry is deleted.
        row = app.etable.selected_row
        row.transfer = 'foobar'
        app.etable.save_edits()
        eq_(app.account_names(), ['Checking', 'foobar'])
    
    @with_app(do_setup)
    def test_create_income_account(self, app):
        # Adding an entry in the Salary transfer added a Salary income account with a bound entry
        # in it.
        eq_(app.account_names(), ['Checking', 'Salary'])
        eq_(app.bsheet.assets.children_count, 3)
        eq_(app.bsheet.liabilities.children_count, 2)
        app.show_pview()
        eq_(app.istatement.income.children_count, 3)
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        eq_(app.etable_count(), 1)
        eq_(app.etable[0].description, 'Deposit')
    
    @with_app(do_setup)
    def test_delete_entries(self, app):
        # Deleting an entry updates the graph and makes the Salary account go away.
        app.etable.delete()
        eq_(list(app.balgraph.data), [])
        eq_(app.account_names(), ['Checking'])
    
    @with_app(do_setup)
    def test_delete_entries_with_Salary_selected(self, app):
        # Deleting the last entry of an income account does not remove that account.
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        app.etable.delete()
        eq_(app.account_names(), ['Checking', 'Salary'])
    
    @with_app(do_setup)
    def test_edit_then_revert(self, app):
        # Reverting an existing entry put the old values back.
        row = app.etable.selected_row
        row.date = '11/10/2007'
        row.description = 'edited'
        row.transfer = 'edited'
        row.increase = '43'
        app.etable.cancel_edits()
        eq_(app.etable[0].date, '10/10/2007')
        eq_(app.etable[0].description, 'Deposit')
        eq_(app.etable[0].transfer, 'Salary')
        eq_(app.etable[0].increase, '42.00')
    
    @with_app(do_setup)
    def test_entry_checkno_get_set(self, app):
        self._test_entry_attribute_get_set(app, 'checkno')
    
    @with_app(do_setup)
    def test_entry_debit(self, app):
        # The entry is a debit.
        eq_(app.etable[0].increase, '42.00')
    
    @with_app(do_setup)
    def test_entry_decrease_get_set(self, app):
        self._test_entry_attribute_get_set(app, 'decrease', '12.00')
    
    @with_app(do_setup)
    def test_entry_increase_get_set(self, app):
        self._test_entry_attribute_get_set(app, 'increase', '12.00')
    
    @with_app(do_setup)
    def test_entry_is_editable(self, app):
        # An Entry has everything but balance editable.
        editable_columns = ['date', 'description', 'payee', 'transfer', 'increase', 'decrease', 'checkno']
        for colname in editable_columns:
            assert app.etable.can_edit_cell(colname, 0)
        assert not app.etable.can_edit_cell('balance', 0) 
        assert not app.etable[0].can_reconcile() # Only in reconciliation mode
    
    @with_app(do_setup)
    def test_entry_is_editable_of_opposite(self, app):
        # The other side of an Entry has the same edition rights as the Entry.
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        editable_columns = ['date', 'description', 'payee', 'transfer', 'increase', 'decrease', 'checkno']
        for colname in editable_columns:
            assert app.etable.can_edit_cell(colname, 0)
        assert not app.etable.can_edit_cell('balance', 0)
        assert not app.etable[0].can_reconcile() # Only in reconciliation mode
    
    @with_app(do_setup)
    def test_entry_payee_get_set(self, app):
        self._test_entry_attribute_get_set(app, 'payee')
    
    @with_app(do_setup)
    def test_entry_transfer_get_set(self, app):
        self._test_entry_attribute_get_set(app, 'transfer')
    
    @with_app(do_setup)
    def test_graph(self, app):
        # The 'Checking' account has a line graph. The 'Salary' account has a bar graph.
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        eq_(app.bar_graph_data(), [('01/10/2007', '01/11/2007', '42.00', '0.00')])
        eq_(app.bargraph.title, 'Salary')
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        eq_(app.graph_data(), [('11/10/2007', '42.00'), ('01/01/2008', '42.00')])
    
    @with_app(do_setup)
    def test_new_entry_balance(self, app):
        # A newly added entry has a blank balance.
        app.etable.add()
        eq_(app.etable[1].balance, '')
    
    @with_app(do_setup)
    def test_new_entry_date(self, app):
        # A newly added entry has the same date as the selected entry.
        app.etable.add()
        eq_(app.etable[1].date, '10/10/2007')
    

class TestTwoBoundEntries:
    # 2 entries in 2 accounts 'first' and 'second' that are part of the same transaction. There is 
    # a 'third', empty account. 'second' is selected.
    def do_setup(self):
        app = TestApp()
        app.add_account('first')
        app.add_account('second')
        app.show_account()
        app.add_entry(description='transfer', transfer='first', increase='42')
        app.add_account('third')
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[1]
        app.show_account()
        return app
    
    @with_app(do_setup)
    def test_change_amount(self, app):
        # The other side of the transaction follows
        # Because of MCT, a transfer between asset/liability accounts stopped balancing itself
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        row = app.etable.selected_row
        row.decrease = '40'
        app.etable.save_edits()
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[1]
        app.show_account()
        eq_(app.etable[0].increase, '40.00')
    
    @with_app(do_setup)
    def test_change_transfer(self, app):
        # Changing the transfer of an entry deletes the bound entry and creates a new one
        row = app.etable.selected_row
        row.transfer = 'third'
        app.etable.save_edits()
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0] # first
        app.show_account()
        eq_(app.etable_count(), 0)
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[2] # third
        app.show_account()
        eq_(app.etable_count(), 1)
    
    @with_app(do_setup)
    def test_change_transfer_backwards(self, app):
        # Entry binding works both ways
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        row = app.etable.selected_row
        row.transfer = 'third'
        app.etable.save_edits()
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[1]
        app.show_account()
        eq_(app.etable_count(), 0)
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[2]
        app.show_account()
        eq_(app.etable_count(), 1)
    
    @with_app(do_setup)
    def test_change_transfer_non_account(self, app):
        # The binding should be cancelled when the transfer is changed to a non-account. Also,
        # don't try to unbind an entry from a deleted entry
        row = app.etable.selected_row
        row.transfer = 'other'
        app.etable.save_edits()
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0] # first
        app.show_account()
        eq_(app.etable_count(), 0)
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[2] # third
        app.show_account()
        eq_(app.etable_count(), 0)
        # Make sure the entry don't try to unbind from 'first' again
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[1] # second
        app.show_account()
        row = app.etable.selected_row
        row.transfer = 'yet-another'
        app.etable.save_edits() # shouldn't raise anything
    
    @with_app(do_setup)
    def test_clear_document(self, app):
        # Document.clear() removes all transactions and accounts and sends 'document_changed'.
        # Also, since the currently shown account in etable has been deleted, the current view
        # in the main window is kicked back to the bsheet.
        app.clear_gui_calls()
        app.doc.clear()
        eq_(app.mainwindow.current_pane_index, 0)
        eq_(app.account_node_subaccount_count(app.bsheet.assets), 0)
        app.show_tview()
        eq_(app.ttable.row_count, 0)
    
    @with_app(do_setup)
    def test_delete_entries(self, app):
        # Deleting an entry also delets any bound entry
        app.etable.delete()
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        eq_(app.etable_count(), 0)
    

class TestNegativeBoundEntryTest:
    # Account with one credit entry, bound to another account
    def do_setup(self):
        app = TestApp()
        app.add_account('visa', account_type=AccountType.Liability)
        app.show_account()
        app.add_entry(transfer='clothes', increase='42')
        return app
    
    @with_app(do_setup)
    def test_make_balance_positive(self, app):
        # Even when making 'visa''s entry a debit, account types stay the same
        row = app.etable.selected_row
        row.decrease = '42' # we're decreasing the liability here
        app.etable.save_edits()
        app.show_pview()
        eq_(app.istatement.expenses.children_count, 3)
    

class TestOneEntryInPreviousRange:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        app.add_account()
        app.show_account()
        app.add_entry('1/1/2008')
        app.drsel.select_next_date_range()
        return app
    
    @with_app(do_setup)
    def test_attrs(self, app):
        row = app.etable[0]
        eq_(row.date, '01/02/2008')
        assert not row.can_edit()
    
    @with_app(do_setup)
    def test_make_account_income(self, app):
        # If we make the account an income account, the previous balance entry disappears
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.mainwindow.edit_item()
        app.apanel.type_list.select(2) # income
        app.apanel.save()
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        eq_(app.etable_count(), 0)
    
    @with_app(do_setup)
    def test_new_entry_are_inserted_after_previous_balance_entry(self, app):
        # When a new entry's date is the same date as a Previous Balance entry, the entry is added
        # after it
        app.etable.add()
        eq_(app.etable[0].description, 'Previous Balance')
    

class TestTwoEntriesInTwoMonthsRangeOnSecond:
    # One account, two entries in different months. The month range is on the second.
    # The selection is on the 2nd item (The first add_entry adds a Previous Balance, the second
    # add_entry adds a second item and selects it.)
    def do_setup(self):
        app = TestApp()
        app.add_account('Checking')
        app.show_account()
        app.add_entry('3/9/2007', 'first', increase='102.00')
        app.add_entry('10/10/2007', 'second', increase='42.00')
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        # When the second entry was added, the date was in the previous date range, making the
        # entry go *before* the Previous Entry, but we want the selection to be on the second item
        app.etable.select([1])
        return app
    
    @with_app(do_setup)
    def test_entries(self, app):
        # app.entries has 2 entries: a previous balance entry and the october entry.
        eq_(app.etable_count(), 2) # Previous balance
        eq_(app.etable[0].description, 'Previous Balance')
        eq_(app.etable[0].payee, '')
        eq_(app.etable[0].checkno, '')
        eq_(app.etable[0].increase, '')
        eq_(app.etable[0].decrease, '')
        eq_(app.etable[0].balance, '102.00')
        eq_(app.etable[1].description, 'second')
    
    @with_app(do_setup)
    def test_graph_data(self, app):
        # The Previous Balance is supposed to be a data point here
        expected = [('01/10/2007', '102.00'), ('10/10/2007', '102.00'), ('11/10/2007', '144.00'),
                    ('01/11/2007', '144.00')]
        eq_(app.graph_data(), expected)
    
    @with_app(do_setup)
    def test_prev_balance_entry_is_not_editable(self, app):
        # A PreviousBalanceEntry is read-only.
        app.etable.select([0])
        columns = ['date', 'description', 'payee', 'transfer', 'increase', 'decrease', 'checkno']
        for colname in columns:
            assert not app.etable.can_edit_cell(colname, 0)
    
    @with_app(do_setup)
    def test_prev_date_range_while_in_edition(self, app):
        # Changing the date range while in edition mode saves the data first
        row = app.etable.selected_row
        row.description = 'foo'
        app.drsel.select_prev_date_range() # Save the entry *then* go in the prev date range
        app.etable.save_edits()
        eq_(app.etable[0].description, 'first')
    
    @with_app(do_setup)
    def test_selection(self, app):
        # The selection should be on the 2nd item, last added
        eq_(app.etable.selected_indexes[0], 1)
    
    @with_app(do_setup)
    def test_selection_is_kept_on_date_range_jump(self, app):
        # When save_entry causes a date range jump, the entry that was just saved stays selected
        # selected index is now 1
        row = app.etable.selected_row
        row.date = '2/9/2007' # Goes before 'first'
        app.etable.save_edits()
        # selected index has been changed to 0
        eq_(app.etable.selected_indexes, [0])
    

class TestTwoEntriesInRange:
    # Two entries, both on October 2007, first entry is selected
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.show_account()
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        app.add_entry('2/10/2007', 'first', increase='102')
        app.add_entry('4/10/2007', 'second', increase='42')
        app.etable.select([0])
        return app
    
    @with_app(do_setup)
    def test_date_edition_and_position(self, app):
        # After an entry has its date edited, its position among transactions
        # of the same date is always last
        # Previously, the transaction would keep its old position, so it could
        # happen that the newly edited transaction wouldn't go at the end
        row = app.etable.selected_row
        row.date = '4/10/2007' # same as 'second'
        app.etable.save_edits()
        eq_(app.etable[1].description, 'first')
    
    @with_app(do_setup)
    def test_date_range_change(self, app):
        # The currently selected entry stays selected
        app.drsel.select_year_range()
        eq_(app.etable[app.etable.selected_indexes[0]].description, 'first')
    
    @with_app(do_setup)
    def test_delete_first_entry(self, app):
        # Make sure that the balance of the remaining entry is updated
        app.etable.delete()
        eq_(app.etable[0].balance, '42.00')
    
    @with_app(do_setup)
    def test_entry_order_after_edition(self, app):
        # Edition of an entry re-orders entries upon save_entry() if needed
        row = app.etable.selected_row
        row.date = '5/10/2007'
        app.etable.save_edits()
        eq_(app.etable[0].description, 'second')
        eq_(app.etable.selected_indexes, [1]) # Selection followed the entry
    
    @with_app(do_setup)
    def test_get_entry_attribute_on_other_than_selected(self, app):
        # get_entry_attribute_value() can return attributes from something else than the selected entry
        eq_(app.etable[1].date, '04/10/2007')
    
    @with_app(do_setup)
    def test_graph_data(self, app):
        # The variation between 2 data points that are more than one day apart should not be linear
        # There should be a falt line until one day before the next data point, then the balance
        # variation should take place all on the same day.
        expected = [('03/10/2007', '102.00'), ('04/10/2007', '102.00'), ('05/10/2007', '144.00'), 
                    ('01/11/2007', '144.00')]
        eq_(app.graph_data(), expected)
    
    @with_app(do_setup)
    def test_multiple_selection(self, app):
        # selected_entries() return back all indexes given to select_entries()
        app.etable.select([0, 1])
        eq_(app.etable.selected_indexes, [0, 1])
    
    @with_app(do_setup)
    def test_new_entry_date(self, app):
        # A newly added entry's date is the same date as the selected entry
        app.etable.add()
        eq_(app.etable[1].date, '02/10/2007')
    
    @with_app(do_setup)
    def test_revert_keeps_selection(self, app):
        # Selected index stays the same after reverting an entry edition
        row = app.etable.selected_row
        row.description = 'foo'
        app.etable.cancel_edits()
        eq_(app.etable.selected_indexes, [0])
    

class TestTwoEntryOnTheSameDate:
    # Two entries, both having the same date. The first entry takes the balance very high, but the
    # second entry is a credit that takes it back. The first entry is selected.
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.show_account()
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        app.add_entry('3/10/2007', 'foo', increase='10000')
        app.add_entry('3/10/2007', 'bar', decrease='9000')
        app.etable.select([0])
        return app
    
    @with_app(do_setup)
    def test_edit_entry_of_the_same_date(self, app):
        # Editing an entry when another entry has the same date does not change the display order
        # of those entries
        row = app.etable.selected_row
        row.description = 'baz'
        app.etable.save_edits()
        eq_(app.etable[0].description, 'baz')
        eq_(app.etable[1].description, 'bar')
    
    @with_app(do_setup)
    def test_new_entry_after_reorder(self, app):
        # Reordering entries does not affect the position of newly created
        # entries.
        # Previously, because of the 'position' of a new entry would be equal
        # to the number of entries on the same date. However, the max position
        # for a particular date can be higher than the number of entries on 
        # that date.
        app.etable.move([0], 2) # 'foo' goes after 'bar'. position = 2
        app.etable.move([0], 2) # 'bar' goes after 'foo'. position = 3
        app.add_entry('3/10/2007', description='baz')
        eq_(app.etable[2].description, 'baz')
    

class TestTwoAccountsTwoEntriesInTheFirst:
    # First account has 2 entries in it, the second is empty. The entries are in the date range.
    # Second account is selected.
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        app.add_account()
        app.show_account()
        app.add_entry('3/10/2007', 'first', increase='1')
        app.add_entry('4/10/2007', 'second', increase='1')
        app.add_account()
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        return app
    
    @with_app(do_setup)
    def test_last_entry_is_selected_on_account_selection(self, app):
        # On account selection, the last entry is selected
        eq_(app.etable[app.etable.selected_indexes[0]].description, 'second')
    

class TestAssetIncomeWithDecrease:
    # An asset and income account with a transaction decreasing them both
    def do_setup(self):
        app = TestApp()
        app.add_account('Operations')
        app.show_account()
        app.doc.date_range = MonthRange(date(2008, 3, 1))
        app.add_entry('1/3/2008', description='MacroSoft', transfer='Salary', increase='42')
        app.add_entry('2/3/2008', description='Error Adjustment', transfer='Salary', decrease='2')
        return app
    
    @with_app(do_setup)
    def test_asset_decrease(self, app):
        # The Error Adjustment transaction is an decrease in Operations
        eq_(app.etable[1].decrease, '2.00')
    
    @with_app(do_setup)
    def test_asset_increase(self, app):
        # The MacroSoft transaction is an increase in Operations
        eq_(app.etable[0].increase, '42.00')
    
    @with_app(do_setup)
    def test_income_balance(self, app):
        # Salary's entries' balances are positive
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        eq_(app.etable[0].balance, '42.00')
    
    @with_app(do_setup)
    def test_income_decrease(self, app):
        # The Error Adjustment transaction is an decrease in Salary
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        eq_(app.etable[1].decrease, '2.00')
    
    @with_app(do_setup)
    def test_income_increase(self, app):
        # The MacroSoft transaction is an increase in Salary
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        eq_(app.etable[0].increase, '42.00')
    
    @with_app(do_setup)
    def test_set_income_decrease(self, app):
        # Setting an income entry's decrease actually sets the right side
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        row = app.etable.selected_row
        row.decrease = '4'
        eq_(app.etable[1].decrease, '4.00')
    
    @with_app(do_setup)
    def test_set_income_increase(self, app):
        # Setting an income entry's increase actually sets the right side
        app.show_pview()
        app.istatement.selected = app.istatement.income[0]
        app.show_account()
        row = app.etable.selected_row
        row.increase = '4'
        eq_(app.etable[1].increase, '4.00')
    

class TestLiabilityExpenseWithDecrease:
    # An asset and income account with a transaction decreasing them both
    def do_setup(self):
        app = TestApp()
        app.add_account('Visa', account_type=AccountType.Liability)
        app.show_account()
        app.doc.date_range = MonthRange(date(2008, 3, 1))
        # Visa is a liabilies, so increase/decrease are inverted
        # Clothes is created as an expense
        app.add_entry('1/3/2008', description='Shoes', transfer='Clothes', increase='42.00')
        app.add_entry('2/3/2008', description='Rebate', transfer='Clothes', decrease='2')
        return app
    
    @with_app(do_setup)
    def test_expense_decrease(self, app):
        # The Rebate transaction is a decrease in Clothes
        app.show_pview()
        app.istatement.selected = app.istatement.expenses[0]
        app.show_account()
        eq_(app.etable[1].decrease, '2.00')
    
    @with_app(do_setup)
    def test_expense_increase(self, app):
        # The Shoes transaction is an increase in Clothes
        app.show_pview()
        app.istatement.selected = app.istatement.expenses[0]
        app.show_account()
        eq_(app.etable[0].increase, '42.00')
    
    @with_app(do_setup)
    def test_income_balance(self, app):
        # Visa's entries' balances are positive
        eq_(app.etable[0].balance, '42.00')
    
    @with_app(do_setup)
    def test_liability_decrease(self, app):
        # The Rebate transaction is an decrease in Visa
        eq_(app.etable[1].decrease, '2.00')
    
    @with_app(do_setup)
    def test_liability_increase(self, app):
        # The Shoes transaction is an increase in Visa
        eq_(app.etable[0].increase, '42.00')
    
    @with_app(do_setup)
    def test_set_liability_decrease(self, app):
        # Setting an liability entry's decrease actually sets the right side
        # Last entry is selected
        row = app.etable.selected_row
        row.decrease = '4'
        eq_(app.etable[1].decrease, '4.00')
    
    @with_app(do_setup)
    def test_set_liability_increase(self, app):
        # Setting an liability entry's increase actually sets the right side
        # Last entry is selected
        row = app.etable.selected_row
        row.increase = '4'
        eq_(app.etable[1].increase, '4.00')
    

class TestThreeEntriesInThreeMonthsRangeOnThird:
    # One account, three entries in different months. The month range is on the third.
    # The selection is on the 2nd item (the first being the Previous Balance).
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.show_account()
        app.doc.date_range = MonthRange(date(2007, 11, 1))
        app.add_entry('3/9/2007', 'first', increase='1')
        app.add_entry('10/10/2007', 'second', increase='2')
        app.add_entry('1/11/2007', 'third', increase='3')
        return app
    
    @with_app(do_setup)
    def test_date_range_change(self, app):
        # The selected entry stays selected after a date range, even if its index changes (the 
        # index of the third entry goes from 1 to 2.
        app.drsel.select_year_range()
        eq_(app.etable[app.etable.selected_indexes[0]].description, 'third')
    

class TestEntriesWithZeroVariation:
    # The first entry is normal, but the second has a null amount, resulting in no balance variation
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.show_account()
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        app.add_entry('1/10/2007', 'first', increase='100')
        app.add_entry('3/10/2007', 'third')
        return app
    
    @with_app(do_setup)
    def test_graph_data(self, app):
        # Entries with zero variation are ignored
        expected = [('02/10/2007', '100.00'), ('01/11/2007', '100.00')]
        eq_(app.graph_data(), expected)
    

class TestThreeEntriesInTwoAccountTypes:
    # 3 entries in 2 accounts of different type.
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.show_account()
        app.add_entry(description='first')
        app.add_entry(description='second')
        app.add_account(account_type=AccountType.Income)
        app.show_account()
        app.add_entry(description='third') # selected
        return app
    
    @with_app(do_setup)
    def test_delete_entries(self, app):
        # delete the entry in the selected type
        app.etable.delete()
        eq_(app.etable_count(), 0)
    
    @with_app(do_setup)
    def test_entries_count(self, app):
        # depends on the selected account type
        eq_(app.etable_count(), 1)
    
    @with_app(do_setup)
    def test_get_entry_attribute_value(self, app):
        # depends on the selected account type
        eq_(app.etable[0].description, 'third')
    

class TestThreeEntriesInTheSameExpenseAccount:
    # Three entries balanced in the same expense account.
    def do_setup(self):
        app = TestApp()
        app.drsel.select_year_range()
        app.add_account()
        app.show_account()
        app.add_entry('31/12/2007', 'entry0', transfer='Expense', decrease='42')
        app.add_entry('1/1/2008', 'entry1', transfer='Expense', decrease='100')
        app.add_entry('20/1/2008', 'entry2', transfer='Expense', decrease='200')
        app.add_entry('31/3/2008', 'entry3', transfer='Expense', decrease='150')
        app.show_pview()
        app.istatement.selected = app.istatement.expenses[0]
        app.show_account()
        return app
    
    @with_app(do_setup)
    def test_delete_multiple_selection(self, app):
        # delete_entries() when having multiple entries selected delete all selected entries
        app.etable.select([0, 2])
        app.etable.delete()
        # [:-1]: ignore total line
        eq_(app.entry_descriptions()[:-1], ['entry2'])
    
    @with_app(do_setup)
    def test_graph_data(self, app):
        # The expense graph is correct.
        expected = [('01/01/2008', '01/02/2008', '300.00', '0.00'), 
                    ('01/03/2008', '01/04/2008', '150.00', '0.00')]
        eq_(app.bar_graph_data(), expected)

    @with_app(do_setup)
    def test_graph_data_in_month_range(self, app):
        # The expense graph shows weekly totals when the month range is selected. The first bar
        # overflows the date range to complete the week.
        app.doc.date_range = MonthRange(date(2008, 1, 1))
        expected = [('31/12/2007', '07/01/2008', '142.00', '0.00'), 
                    ('14/01/2008', '21/01/2008', '200.00', '0.00')]
        eq_(app.bar_graph_data(), expected)
    
    @with_app(do_setup)
    def test_graph_data_in_quarter_range(self, app):
        # The expense graph shows weekly totals when the quarter range is selected. The first bar
        # overflows the date range to complete the week.
        app.doc.date_range = QuarterRange(date(2008, 1, 1))
        expected = [('31/12/2007', '07/01/2008', '142.00', '0.00'), 
                     ('14/01/2008', '21/01/2008', '200.00', '0.00'),
                     ('31/03/2008', '07/04/2008', '150.00', '0.00')]
        eq_(app.bar_graph_data(), expected)
    
    @with_app(do_setup)
    def test_xaxis_on_month_range(self, app):
        # The xaxis min/max follow the date range overflows
        start = date(2008, 1, 1)
        app.doc.date_range = MonthRange(start)
        eq_(app.bargraph.xmin, date(2007, 12, 31).toordinal() - start.toordinal())
        eq_(app.bargraph.xmax, date(2008, 2, 4).toordinal() - start.toordinal())
    

class TestFourEntriesInRange:
    # Four entries, all on October 2007, last entry is selected
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.show_account()
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        app.add_entry('3/10/2007', 'first', increase='1')
        app.add_entry('4/10/2007', 'second', decrease='2')
        app.add_entry('5/10/2007', 'third', increase='3')
        app.add_entry('6/10/2007', 'fourth', decrease='4')
        return app
    
    @with_app(do_setup)
    def test_balances(self, app):
        # Balances are correct for all entries.
        # [:-1] is because we ignore total row
        eq_(app.balances()[:-1], ['1.00', '-1.00', '2.00', '-2.00'])
    
    @with_app(do_setup)
    def test_delete_entries_last(self, app):
        # Deleting the last entry makes the selection goes one index above, even though there's a
        # total row below.
        app.etable.delete()
        eq_(app.etable.selected_index, 2)
    
    @with_app(do_setup)
    def test_delete_entries_second(self, app):
        # Deleting an entry that is not the last does not change the selected index
        app.etable.select([1])
        app.etable.delete()
        eq_(app.etable.selected_indexes[0], 1)
    

class TestEightEntries:
    # Eight entries setup for testing entry reordering.
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.add_account()
        app.show_account()
        app.doc.date_range = MonthRange(date(2008, 1, 1))
        app.add_entry('1/1/2007', description='previous', increase='1')
        app.add_entry('1/1/2008', description='entry 1', increase='9')
        app.add_entry('2/1/2008', description='entry 2', increase='20')
        app.add_entry('2/1/2008', description='entry 3', increase='30')
        app.add_entry('2/1/2008', description='entry 4', increase='40')
        app.add_entry('2/1/2008', description='entry 5', increase='900')
        app.add_entry('3/1/2008', description='entry 6', increase='60')
        app.add_entry('3/1/2008', description='entry 7', increase='70')
        return app
    
    @with_app(do_setup)
    def test_can_reorder_entry(self, app):
        # Move is allowed only when it makes sense.
        assert not app.etable.can_move([0], 2) # Can't move the previous balance entry
        assert not app.etable.can_move([1], 3) # Not the same date
        assert not app.etable.can_move([3], 1) # Likewise
        assert not app.etable.can_move([2], 2) # Moving to the same row doesn't change anything
        assert not app.etable.can_move([2], 3) # Moving to the next row doesn't change anything
        assert app.etable.can_move([2], 4)
        assert app.etable.can_move([2], 5)  # Can move to the end of the day
        assert not app.etable.can_move([4], 5) # Moving to the next row doesn't change anything
        assert app.etable.can_move([6], 8)  # Can move beyond the bounds of the entry list
        assert not app.etable.can_move([7], 8) # Moving yo the next row doesn't change anything
        assert not app.etable.can_move([7], 9) # Out of range destination by 2 doesn't cause a crash
    
    @with_app(do_setup)
    def test_can_reorder_entry_multiple(self, app):
        # Move is allowed only when it makes sense.
        assert app.etable.can_move([2, 3], 5) # This one is valid
        assert not app.etable.can_move([2, 1], 5) # from_indexes are on different days
        assert not app.etable.can_move([2, 3], 4) # Nothing moving (just next to the second index)
        assert not app.etable.can_move([2, 3], 2) # Nothing moving (in the middle of from_indexes)
        assert not app.etable.can_move([2, 3], 3) # same as above
        assert not app.etable.can_move([3, 2], 3) # same as above, but making sure order doesn't matter
        assert app.etable.can_move([2, 4], 4) # Puts 2 between 3 and 4
        assert app.etable.can_move([2, 4], 2) # Puts 4 between 2 and 3
        assert app.etable.can_move([2, 4], 3) # same as above
    
    @with_app(do_setup)
    def test_move_entry_to_the_end_of_the_day(self, app):
        # Moving an entry to the end of the day works.
        app.etable.move([2], 6)
        eq_(app.entry_descriptions()[1:6], ['entry 1', 'entry 3', 'entry 4', 'entry 5', 'entry 2'])
        eq_(app.balances()[1:6], ['10.00', '40.00', '80.00', '980.00', '1000.00'])
    
    @with_app(do_setup)
    def test_move_entry_to_the_end_of_the_list(self, app):
        # Moving an entry to the end of the list works.
        app.etable.move([6], 8)
        eq_(app.entry_descriptions()[6:8], ['entry 7', 'entry 6'])
        eq_(app.balances()[6:8], ['1070.00', '1130.00'])
    
    @with_app(do_setup)
    def test_reorder_entry(self, app):
        # Moving an entry reorders the entries.
        app.etable.move([2], 4)
        eq_(app.entry_descriptions()[1:5], ['entry 1', 'entry 3', 'entry 2', 'entry 4'])
        eq_(app.balances()[1:5], ['10.00', '40.00', '60.00', '100.00'])
    
    @with_app(do_setup)
    def test_reorder_entry_multiple(self, app):
        # Multiple entries can be re-ordered at once
        app.etable.move([2, 3], 5)
        eq_(app.entry_descriptions()[1:5], ['entry 1', 'entry 4', 'entry 2', 'entry 3'])
    
    @with_app(do_setup)
    def test_reorder_entry_makes_the_app_dirty(self, app):
        # calling reorder_entry() makes the app dirty
        app.save_file()
        app.etable.move([2], 4)
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_selection_follows(self, app):
        # The selection follows when we move the selected entry.
        app.etable.select([2])
        app.etable.move([2], 4)
        eq_(app.etable.selected_indexes[0], 3)
        app.etable.move([3], 2)
        eq_(app.etable.selected_indexes[0], 2)
    
    @with_app(do_setup)
    def test_selection_follows_multiple(self, app):
        # The selection follows when we move the selected entries
        app.etable.select([2, 3])
        app.etable.move([2, 3], 5)
        eq_(app.etable.selected_indexes, [3, 4])
    
    @with_app(do_setup)
    def test_selection_stays(self, app):
        # The selection stays on the same entry if we don't move the selected entry.
        app.etable.select([3])
        app.etable.move([2], 4)
        eq_(app.etable.selected_indexes[0], 2)
        app.etable.move([3], 2)
        eq_(app.etable.selected_indexes[0], 3)
        app.etable.select([5])
        app.etable.move([2], 4)
        eq_(app.etable.selected_indexes[0], 5)
    

class TestFourEntriesOnTheSameDate:
    # Four entries in the same account on the same date
    def do_setup(self):
        app = TestApp()
        app.add_account()
        app.show_account()
        app.doc.date_range = MonthRange(date(2008, 1, 1))
        app.add_entry('1/1/2008', description='entry 1', increase='42.00')
        app.add_entry('1/1/2008', description='entry 2', increase='42.00')
        app.add_entry('1/1/2008', description='entry 3', increase='42.00')
        app.add_entry('1/1/2008', description='entry 4', increase='42.00')
        return app
    
    @with_app(do_setup)
    def test_can_reorder_entry_multiple(self, app):
        # Some tests can't be done in EightEntries (and it's tricky to change this testcase now...)
        assert not app.etable.can_move([0, 1, 2, 3], 2) # Nothing moving (in the middle of from_indexes)
    
    @with_app(do_setup)
    def test_move_entries_up(self, app):
        # Moving more than one entry up does nothing
        app.etable.select([1, 2])
        app.etable.move_up()
        # [:-1]: ignore total line
        eq_(app.entry_descriptions()[:-1], ['entry 1', 'entry 2', 'entry 3', 'entry 4'])
    
    @with_app(do_setup)
    def test_move_entry_down(self, app):
        # Move an entry down a couple of times
        app.etable.select([2])
        app.etable.move_down()
        # [:-1]: ignore total line
        eq_(app.entry_descriptions()[:-1], ['entry 1', 'entry 2', 'entry 4', 'entry 3'])
        app.etable.move_down()
        eq_(app.entry_descriptions()[:-1], ['entry 1', 'entry 2', 'entry 4', 'entry 3'])
    
    @with_app(do_setup)
    def test_move_entry_up(self, app):
        # Move an entry up a couple of times
        app.etable.select([1])
        app.etable.move_up()
        # [:-1]: ignore total line
        eq_(app.entry_descriptions()[:-1], ['entry 2', 'entry 1', 'entry 3', 'entry 4'])
        app.etable.move_up()
        eq_(app.entry_descriptions()[:-1], ['entry 2', 'entry 1', 'entry 3', 'entry 4'])
    
    @with_app(do_setup)
    def test_save_load_preserve_positions(self, app):
        # After a save and load, moving entries around still works correctly (previously, all
        # positions would be set to 1 open loading).
        newapp = app.save_and_load() # no crash
        newapp.doc.date_range = MonthRange(date(2008, 1, 1))
        newapp.show_tview()
        newapp.ttable.select([3])
        newapp.ttable.move_up()
        eq_(newapp.transaction_descriptions(), ['entry 1', 'entry 2', 'entry 4', 'entry 3'])
    

class TestEntrySelectionOnAccountChange:
    # I couldn't find a better name for a setup with multiple accounts, some transactions having
    # the same date, some not. The setup is to test entry selection upon account selection change.
    def do_setup(self):
        app = TestApp()
        app.add_account('asset1')
        app.show_account()
        app.add_entry('1/1/2008', transfer='expense1', decrease='42.00')
        app.add_entry('4/1/2008', transfer='expense2', decrease='42.00')
        app.add_entry('11/1/2008', transfer='expense3', decrease='42.00')
        app.add_entry('22/1/2008', transfer='expense3', decrease='42.00')
        app.add_account('asset2')
        app.show_account()
        app.add_entry('1/1/2008', transfer='expense1', decrease='42.00')
        app.add_entry('12/1/2008', transfer='expense2', decrease='42.00')
        # selected account is asset2
        return app
    
    @with_app(do_setup)
    def test_keep_date(self, app):
        # Explicitely selecting a transaction make it so the nearest date is found as a fallback
        app.etable.select([0]) # the transaction from asset2 to expense1
        app.show_pview()
        app.istatement.selected = app.istatement.expenses[1] # expense2
        app.show_account()
        # The nearest date in expense2 is 2008/1/4
        eq_(app.etable.selected_indexes, [0])
        # Now select the 2008/1/12 date
        app.etable.select([1])
        app.show_pview()
        app.istatement.selected = app.istatement.expenses[2] # expense3
        aview = app.show_account()
        # The 2008/1/11 date is nearer than the 2008/1/22 date, so it should be selected
        eq_(aview.etable.selected_indexes, [0])
    
    @with_app(do_setup)
    def test_keep_transaction(self, app):
        # Explicitly selecting a transaction make it so it stays selected when possible.
        app.show_account('asset1')
        app.etable.select([0]) # the transaction from asset1 to expense1
        app.show_account('asset2') # the transaction doesn't exist there.
        app.show_account('expense1')
        # Even though we selected asset2, the transaction from asset1 should be selected
        eq_(app.etable.selected_indexes, [0])
    
    @with_app(do_setup)
    def test_save_entry(self, app):
        # Chaning an entry's date also changes the date in the explicit selection
        row = app.etable.selected_row
        row.date = '5/1/2008'
        app.etable.save_edits()
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        eq_(app.etable.selected_indexes, [1]) #2008/1/4
    

class TestEntrySelectionOnDateRangeChange:
    # Multiple entries in multiple date range to test the entry selection on date range change
    def do_setup(self):
        app = TestApp()
        app.drsel.select_month_range()
        app.add_account()
        app.show_account()
        app.add_entry('2/2/2007')
        app.add_entry('2/1/2008')
        app.add_entry('3/1/2008')
        app.add_entry('4/1/2008')
        app.add_entry('1/2/2008')
        app.add_entry('2/2/2008')
        app.add_entry('3/2/2008')
        # date range is on 2008/2
        # Don't forget that there's a previous balance most of the time!
        app.etable.select([3]) # 2008/2/3
        return app
    
    @with_app(do_setup)
    def test_prev_range(self, app):
        # Explicit entry selection keeps the same delta with the date range's start when it 
        # translates
        app.drsel.select_prev_date_range()
        eq_(app.etable.selected_indexes, [2]) # 2008/1/2
    
    @with_app(do_setup)
    def test_year_range(self, app):
        # Even in year range, the system stays the same for range change (keep the same distance
        # with the range's start
        app.drsel.select_year_range()
        app.drsel.select_prev_date_range()
        app.etable.select([0]) # 2007/2/2, no previous balance
        app.drsel.select_next_date_range()
        eq_(app.etable.selected_indexes, [5]) # 2008/2/2
    

class TestExampleDocumentLoadTest:
    def do_setup(self, monkeypatch):
        # We're creating a couple of transactions with the latest being 4 months ago (in april).
        monkeypatch.patch_today(2009, 8, 27)
        app = TestApp()
        app.add_account()
        app.show_account()
        app.add_entry('01/03/2008')
        app.add_entry('29/10/2008') # this one will end up in february, but overflow
        app.add_entry('01/03/2009')
        app.add_entry('15/04/2009')
        app.add_entry('28/04/2009') # will be deleted because in the future
        app.show_scview()
        app.mainwindow.new_item()
        app.scpanel.start_date = '03/03/2009'
        app.scpanel.stop_date = '04/05/2009'
        app.scpanel.repeat_type_index = 2 # monthly
        app.scpanel.save()
        return app
    
    @with_app(do_setup)
    def test_adjust_example_file(self, app):
        # When loading as an example file, an offset is correctly applied to transactions.
        app.doc.adjust_example_file()
        app.show_tview()
        # There are 3 normal txns (the last one is deleted because it's in the future)
        # and 1 schedule spawns (only future spawns are kept)
        eq_(app.ttable.row_count, 4)
        eq_(app.ttable[0].date, '01/03/2009') # from 29/09/2008, it was in feb, but overflowed
        eq_(app.ttable[1].date, '01/07/2009') # from 01/03/2009
        eq_(app.ttable[2].date, '15/08/2009') # from 15/04/2009
        eq_(app.ttable[3].date, '03/09/2009') # spawn
    
