# -*- coding: utf-8 -*-
# Created By: Eric Mc Sween
# Created On: 2008-01-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op
import sys
from datetime import date

from nose.tools import eq_, assert_raises

from hsutil import io
from hsutil.currency import EUR
from hsutil.testutil import Patcher, with_tmpdir

from .base import TestCase, CommonSetup, ApplicationGUI, TestApp, with_app
from ..app import FIRST_WEEKDAY_PREFERENCE, AHEAD_MONTHS_PREFERENCE
from ..app import Application
from ..document import Document, AUTOSAVE_BUFFER_COUNT
from ..exception import FileFormatError
from ..gui.entry_table import EntryTable
from ..loader import base
from ..model.account import AccountType
from ..model.date import MonthRange, QuarterRange, YearRange

#--- No Setup
def test_app_loads_correct_pref_types():
    # If the type loaded by Application from the prefs is not the correct one, we get a crash
    # when the value goes back to the GUI, when it's depythonified.
    gui = ApplicationGUI()
    gui.defaults = {
        FIRST_WEEKDAY_PREFERENCE: 'not an int',
        AHEAD_MONTHS_PREFERENCE: 'not an int',
    }
    app = TestApp(app=Application(gui))
    # because none of the prefs are of the correct type, use default values
    eq_(app.app.first_weekday, 0)
    eq_(app.app.ahead_months, 2)

def test_app_tries_to_convert_different_types():
    # The prefs might be stored as a different, but compatible type (for example, an int instead
    # of a bool. Try to convert the value before falling back to the default value.
    gui = ApplicationGUI()
    gui.defaults = {
        AHEAD_MONTHS_PREFERENCE: '6',
    }
    app = TestApp(app=Application(gui))
    eq_(app.app.ahead_months, 6)

def test_can_use_another_amount_format():
    app = TestApp(app=Application(ApplicationGUI(), decimal_sep=',', grouping_sep=' '))
    app.add_account()
    app.mainwindow.show_account()
    app.add_entry(increase='1234567890.99')
    eq_(app.etable[0].increase, '1 234 567 890,99')

def test_can_use_another_date_format():
    app = TestApp(Application(ApplicationGUI(), date_format='MM-dd-yyyy'))
    app.add_account()
    app.mainwindow.show_account()
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
    app.app.first_weekday = 1
    app.app.ahead_months = 5
    app.app.year_start_month = 4
    app.app.autosave_interval = 8
    app.app.auto_decimal_place = True
    app.doc.close()
    newapp = Application(app.app_gui)
    newdoc = Document(app.doc_gui, newapp)
    assert isinstance(newdoc.date_range, YearRange)
    eq_(newapp.first_weekday, 1)
    eq_(newapp.ahead_months, 5)
    eq_(newapp.year_start_month, 4)
    eq_(newapp.autosave_interval, 8)
    eq_(newapp.auto_decimal_place, True)

def test_graph_yaxis():
    app = TestApp()
    eq_(app.nwgraph.ymin, 0)
    eq_(app.nwgraph.ymax, 100)
    eq_(list(app.nwgraph.ytickmarks), range(0, 101, 20))
    eq_(list(app.nwgraph.ylabels), [dict(text=str(x), pos=x) for x in range(0, 101, 20)])

@with_tmpdir
def test_load_inexistant(tmppath):
    # Raise FileFormatError when filename doesn't exist
    app = TestApp()
    filename = unicode(tmppath + 'does_not_exist.xml')
    assert_raises(FileFormatError, app.doc.load_from_xml, filename)

def test_load_invalid():
    # Raises FileFormatError, which gives a message kind of like: <filename> is not a moneyGuru
    # file.
    app = TestApp()
    filename = TestCase.filepath('randomfile')
    try:
        app.doc.load_from_xml(filename)
    except FileFormatError as e:
        assert filename in str(e)
    else:
        raise AssertionError()

def test_load_empty():
    # When loading an empty file (we mock it here), make sure no exception occur.
    app = TestApp()
    with Patcher() as p:
        p.patch(base.Loader, 'parse', lambda self, filename: None)
        p.patch(base.Loader, 'load', lambda self: None)
        app.doc.load_from_xml('filename does not matter here')

def test_modified_flag():
    # The modified flag is initially False.
    app = TestApp()
    assert not app.doc.is_dirty()

#--- Range on October 2007
def app_range_on_october2007():
    p = Patcher()
    p.patch_today(2007, 10, 1)
    app = TestApp()
    app.drsel.select_month_range()
    return app, p

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

class RangeOnJuly2006(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2006, 7, 1))
    
    def test_graph_xaxis(self):
        eq_(self.nwgraph.xtickmarks, [self.nwgraph.xmin + x - 1 for x in [1, 32]])
    

class RangeOnYearToDate(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2008, 11, 12)
        self.drsel.select_year_to_date_range()
    
    def test_graph_xaxis(self):
        # The graph xaxis shows abbreviated month names
        expected = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
        eq_([d['text'] for d in self.nwgraph.xlabels], expected)
    

class OneEmptyAccountRangeOnOctober2007(TestCase):
    """One empty account, range on October 2007"""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('Checking', EUR)
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.clear_gui_calls()
    
    def test_autosave(self):
        # Testing the interval between autosaves would require some complicated mocking. We're just
        # going to cheat here and call 'must_autosave' directly.
        cache_path = self.tmppath()
        self.app.cache_path = cache_path
        self.document.must_autosave()
        eq_(len(io.listdir(cache_path)), 1)
        self.check_gui_calls_partial(self.etable_gui, not_expected=['stop_edition'])
        assert self.document.is_dirty
        # test that the autosave file rotation works
        for i in range(AUTOSAVE_BUFFER_COUNT):
            self.document.must_autosave()
        # The extra autosave file has been deleted
        eq_(len(io.listdir(cache_path)), AUTOSAVE_BUFFER_COUNT)
    
    def test_balance_recursion_limit(self):
        # Balance calculation don't cause recursion errors when there's a lot of them.
        sys.setrecursionlimit(100)
        for i in range(100):
            self.add_entry('1/10/2007')
        try:
            self.etable[-1].balance
        except RuntimeError:
            raise AssertionError()
        finally:
            sys.setrecursionlimit(1000)
    
    def test_modified_flag(self):
        # Adding an account is a modification.
        assert self.document.is_dirty()
    
    def test_save(self):
        # Saving puts the modified flag back to false.
        self.document.save_to_xml(op.join(self.tmpdir(), 'foo.xml'))
        assert not self.document.is_dirty()
    

class OneGroup(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_group()
    
    def test_should_show_balance_column(self):
        # When a group is selected, False is returned (not None).
        assert not self.etable.should_show_balance_column()
        assert isinstance(self.etable.should_show_balance_column(), bool)
    

class ThreeAccountsAndOneEntry(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.add_accounts('one', 'two')
        self.mainwindow.show_account()
        self.add_entry(transfer='three', increase='42')
    
    def test_bind_entry_to_income_expense_accounts(self):
        # Adding an entry with a transfer named after an existing income creates a bound entry in
        # that account.
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.add_entry(transfer='three')
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        eq_(self.ta.etable_count(), 2)
    

class EntryInEditionMode(TestCase):
    # An empty account, but an entry is in edit mode in october 2007.
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.save_file()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.etable.add()
        row = self.etable.edited
        row.date = '1/10/2007'
        row.description = 'foobar'
        row.increase = '42.00'
    
    def test_add_entry(self):
        # Make sure that the currently edited entry is saved before another one is added.
        self.etable.add()
        eq_(self.ta.etable_count(), 2)
        eq_(self.etable[0].date, '01/10/2007')
        eq_(self.etable[0].description, 'foobar')
        eq_(self.etable[0].increase, '42.00')
        
    def test_delete_entries(self):
        # Calling delete_entries() while in edition mode removes the edited entry and put the app
        # out of edition mode.
        self.etable.delete()
        eq_(self.ta.etable_count(), 0)
        self.etable.save_edits() # Shouldn't raise anything
    
    def test_increase_and_decrease(self):
        # Test the increase/decrease amount mechanism.
        row = self.etable.selected_row
        eq_(row.increase, '42.00')
        eq_(row.decrease, '')
        row.decrease = '50'
        eq_(row.increase, '')
        eq_(row.decrease, '50.00')
        row.increase = '-12.42'
        eq_(row.increase, '')
        eq_(row.decrease, '12.42')
    
    def test_revert_entry(self):
        # Reverting a newly added entry deletes it.
        self.etable.cancel_edits()
        eq_(self.ta.etable_count(), 0)
        assert not self.document.is_dirty()
    
    def test_selected_entry_index(self):
        # entries.selected_index follows every entry that is added.
        eq_(self.etable.selected_indexes, [0])
    
    def test_set_debit_to_zero_with_zero_credit(self):
        # Setting debit to zero when the credit is already zero sets the amount to zero.
        row = self.etable.selected_row
        row.increase = ''
        eq_(self.etable[0].increase, '')
        
    def test_set_credit_to_zero_with_non_zero_debit(self):
        # Setting credit to zero when the debit being non-zero does nothing.
        row = self.etable.selected_row
        row.decrease = ''
        eq_(self.etable[0].increase, '42.00')
    

class OneEntryYearRange2007(TestCase):
    # One account, one entry, which is in the yearly date range (2007). The entry has a transfer
    # and a debit value set.
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.mainwindow.show_account()
        self.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00', checkno='42')
        self.document.date_range = YearRange(date(2007, 1, 1))
    
    def _test_entry_attribute_get_set(self, column, value='some_value'):
        # Test that the get/set mechanism works correctly (sets the edition flag appropriately and 
        # set the value underneath).
        row = self.etable.selected_row
        setattr(row, column, value) # Sets the flag
        self.etable.save_edits()
        # Make sure that the values really made it down in the model by using a spanking new gui
        etable = EntryTable(self.etable_gui, self.aview)
        etable.connect()
        etable.show()
        eq_(getattr(etable[0], column), value)
        self.save_file()
        row = self.etable.selected_row
        setattr(row, column, value) # Doesn't set the flag
        self.etable.save_edits() # Shouldn't do anything
        assert not self.document.is_dirty()
    
    def test_change_transfer(self):
        # The 'Salary' account must be deleted when the bound entry is deleted.
        row = self.etable.selected_row
        row.transfer = 'foobar'
        self.etable.save_edits()
        eq_(self.account_names(), ['Checking', 'foobar'])
    
    def test_create_income_account(self):
        # Adding an entry in the Salary transfer added a Salary income account with a bound entry
        # in it.
        eq_(self.account_names(), ['Checking', 'Salary'])
        eq_(self.bsheet.assets.children_count, 3)
        eq_(self.bsheet.liabilities.children_count, 2)
        self.mainwindow.select_income_statement()
        eq_(self.istatement.income.children_count, 3)
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        eq_(self.ta.etable_count(), 1)
        eq_(self.etable[0].description, 'Deposit')
    
    def test_delete_entries(self):
        # Deleting an entry updates the graph and makes the Salary account go away.
        self.etable.delete()
        eq_(list(self.balgraph.data), [])
        eq_(self.account_names(), ['Checking'])
    
    def test_delete_entries_with_Salary_selected(self):
        # Deleting the last entry of an income account does not remove that account.
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.etable.delete()
        eq_(self.account_names(), ['Checking', 'Salary'])
    
    def test_edit_then_revert(self):
        # Reverting an existing entry put the old values back.
        row = self.etable.selected_row
        row.date = '11/10/2007'
        row.description = 'edited'
        row.transfer = 'edited'
        row.increase = '43'
        self.etable.cancel_edits()
        eq_(self.etable[0].date, '10/10/2007')
        eq_(self.etable[0].description, 'Deposit')
        eq_(self.etable[0].transfer, 'Salary')
        eq_(self.etable[0].increase, '42.00')
    
    def test_entry_checkno_get_set(self):
        self._test_entry_attribute_get_set('checkno')
    
    def test_entry_debit(self):
        # The entry is a debit.
        eq_(self.etable[0].increase, '42.00')
    
    def test_entry_decrease_get_set(self):
        self._test_entry_attribute_get_set('decrease', '12.00')
    
    def test_entry_increase_get_set(self):
        self._test_entry_attribute_get_set('increase', '12.00')
    
    def test_entry_is_editable(self):
        # An Entry has everything but balance editable.
        editable_columns = ['date', 'description', 'payee', 'transfer', 'increase', 'decrease', 'checkno']
        for colname in editable_columns:
            assert self.etable.can_edit_cell(colname, 0)
        assert not self.etable.can_edit_cell('balance', 0) 
        assert not self.etable[0].can_reconcile() # Only in reconciliation mode
    
    def test_entry_is_editable_of_opposite(self):
        # The other side of an Entry has the same edition rights as the Entry.
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        editable_columns = ['date', 'description', 'payee', 'transfer', 'increase', 'decrease', 'checkno']
        for colname in editable_columns:
            assert self.etable.can_edit_cell(colname, 0)
        assert not self.etable.can_edit_cell('balance', 0)
        assert not self.etable[0].can_reconcile() # Only in reconciliation mode
    
    def test_entry_payee_get_set(self):
        self._test_entry_attribute_get_set('payee')
    
    def test_entry_transfer_get_set(self):
        self._test_entry_attribute_get_set('transfer')
    
    def test_graph(self):
        # The 'Checking' account has a line graph. The 'Salary' account has a bar graph.
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        eq_(self.bar_graph_data(), [('01/10/2007', '01/11/2007', '42.00', '0.00')])
        eq_(self.bargraph.title, 'Salary')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        eq_(self.graph_data(), [('11/10/2007', '42.00'), ('01/01/2008', '42.00')])
    
    def test_new_entry_balance(self):
        # A newly added entry has a correct balance.
        self.etable.add()
        eq_(self.etable[1].balance, '42.00')
    
    def test_new_entry_date(self):
        # A newly added entry has the same date as the selected entry.
        self.etable.add()
        eq_(self.etable[1].date, '10/10/2007')
    

class TwoBoundEntries(TestCase):
    """2 entries in 2 accounts 'first' and 'second' that are part of the same transaction. There is 
    a 'third', empty account. 'second' is selected.
    """
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('first')
        self.add_account_legacy('second')
        self.add_entry(description='transfer', transfer='first', increase='42')
        self.add_account_legacy('third')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
    
    def test_change_amount(self):
        """The other side of the transaction follows"""
        # Because of MCT, a transfer between asset/liability accounts stopped balancing itself
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.decrease = '40'
        self.etable.save_edits()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable[0].increase, '40.00')
    
    def test_change_transfer(self):
        """Changing the transfer of an entry deletes the bound entry and creates a new one"""
        row = self.etable.selected_row
        row.transfer = 'third'
        self.etable.save_edits()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0] # first
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 0)
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2] # third
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 1)
    
    def test_change_transfer_backwards(self):
        """Entry binding works both ways"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.transfer = 'third'
        self.etable.save_edits()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 0)
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2]
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 1)
    
    def test_change_transfer_non_account(self):
        """The binding should be cancelled when the transfer is changed to a non-account. Also,
        don't try to unbind an entry from a deleted entry
        """
        row = self.etable.selected_row
        row.transfer = 'other'
        self.etable.save_edits()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0] # first
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 0)
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2] # third
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 0)
        # Make sure the entry don't try to unbind from 'first' again
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # second
        self.bsheet.show_selected_account()
        row = self.etable.selected_row
        row.transfer = 'yet-another'
        self.etable.save_edits() # shouldn't raise anything
    
    def test_clear_document(self):
        # Document.clear() removes all transactions and accounts and sends 'document_changed'.
        # Also, since the currently shown account in etable has been deleted, the current view
        # in the main window is kicked back to the bsheet.
        self.clear_gui_calls()
        self.document.clear()
        eq_(self.mainwindow.current_pane_index, 0)
        eq_(self.account_node_subaccount_count(self.bsheet.assets), 0)
        self.mainwindow.select_transaction_table()
        eq_(self.ttable.row_count, 0)
    
    def test_delete_entries(self):
        """Deleting an entry also delets any bound entry"""
        self.etable.delete()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 0)
    

class NegativeBoundEntry(TestCase):
    """Account with one credit entry, bound to another account"""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('visa', account_type=AccountType.Liability)
        self.add_entry(transfer='clothes', increase='42')
    
    def test_make_balance_positive(self):
        """Even when making 'visa''s entry a debit, account types stay the same"""
        row = self.etable.selected_row
        row.decrease = '42' # we're decreasing the liability here
        self.etable.save_edits()
        self.mainwindow.select_income_statement()
        self.assertEqual(self.istatement.expenses.children_count, 3)
    

class OneEntryInPreviousRange(TestCase):
    def setUp(self):
        self.create_instances()
        self.drsel.select_month_range()
        self.add_account()
        self.mainwindow.show_account()
        self.add_entry('1/1/2008')
        self.drsel.select_next_date_range()
    
    def test_attrs(self):
        row = self.etable[0]
        self.assertEqual(row.date, '01/02/2008')
        assert not row.can_edit()
    
    def test_make_account_income(self):
        """If we make the account an income account, the previous balance entry disappears"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.apanel.load()
        self.apanel.type_index = 2 # income
        self.apanel.save()
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 0)
    
    def test_new_entry_are_inserted_after_previous_balance_entry(self):
        """When a new entry's date is the same date as a Previous Balance entry, the entry is added
        after it
        """
        self.etable.add()
        self.assertEqual(self.etable[0].description, 'Previous Balance')
    

class TwoEntriesInTwoMonthsRangeOnSecond(TestCase):
    # One account, two entries in different months. The month range is on the second.
    # The selection is on the 2nd item (The first add_entry adds a Previous Balance, the second
    # add_entry adds a second item and selects it.)
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.mainwindow.show_account()
        self.add_entry('3/9/2007', 'first', increase='102.00')
        self.add_entry('10/10/2007', 'second', increase='42.00')
        self.document.date_range = MonthRange(date(2007, 10, 1))
        # When the second entry was added, the date was in the previous date range, making the
        # entry go *before* the Previous Entry, but we want the selection to be on the second item
        self.etable.select([1])
    
    def test_entries(self):
        """app.entries has 2 entries: a previous balance entry and the october entry."""
        self.assertEqual(self.ta.etable_count(), 2) # Previous balance
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
    
    def test_prev_balance_entry_is_not_editable(self):
        # A PreviousBalanceEntry is read-only.
        self.etable.select([0])
        columns = ['date', 'description', 'payee', 'transfer', 'increase', 'decrease', 'checkno']
        for colname in columns:
            assert not self.etable.can_edit_cell(colname, 0)
    
    def test_prev_date_range_while_in_edition(self):
        """Changing the date range while in edition mode saves the data first"""
        row = self.etable.selected_row
        row.description = 'foo'
        self.drsel.select_prev_date_range() # Save the entry *then* go in the prev date range
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
        self.add_account_legacy()
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
        self.drsel.select_year_range()
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
        self.add_account_legacy()
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
        self.add_account_legacy()
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
        self.add_account_legacy()
        self.add_entry('3/10/2007', 'first', increase='1')
        self.add_entry('4/10/2007', 'second', increase='1')
        self.add_account_legacy()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
    
    def test_last_entry_is_selected_on_account_selection(self):
        """On account selection, the last entry is selected"""
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].description, 'second')
    

class AssetIncomeWithDecrease(TestCase):
    """An asset and income account with a transaction decreasing them both"""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('Operations')
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
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[0].balance, '42.00')
    
    def test_income_decrease(self):
        """The Error Adjustment transaction is an decrease in Salary"""
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[1].decrease, '2.00')
    
    def test_income_increase(self):
        """The MacroSoft transaction is an increase in Salary"""
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[0].increase, '42.00')
    
    def test_set_income_decrease(self):
        """Setting an income entry's decrease actually sets the right side"""
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        row = self.etable.selected_row
        row.decrease = '4'
        self.assertEqual(self.etable[1].decrease, '4.00')
    
    def test_set_income_increase(self):
        """Setting an income entry's increase actually sets the right side"""
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0]
        self.istatement.show_selected_account()
        row = self.etable.selected_row
        row.increase = '4'
        self.assertEqual(self.etable[1].increase, '4.00')
    

class LiabilityExpenseWithDecrease(TestCase):
    """An asset and income account with a transaction decreasing them both"""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('Visa', account_type=AccountType.Liability)
        self.document.date_range = MonthRange(date(2008, 3, 1))
        # Visa is a liabilies, so increase/decrease are inverted
        # Clothes is created as an expense
        self.add_entry('1/3/2008', description='Shoes', transfer='Clothes', increase='42.00')
        self.add_entry('2/3/2008', description='Rebate', transfer='Clothes', decrease='2')
    
    def test_expense_decrease(self):
        """The Rebate transaction is a decrease in Clothes"""
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0]
        self.istatement.show_selected_account()
        self.assertEqual(self.etable[1].decrease, '2.00')
    
    def test_expense_increase(self):
        """The Shoes transaction is an increase in Clothes"""
        self.mainwindow.select_income_statement()
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
    

class ThreeEntriesInThreeMonthsRangeOnThird(TestCase):
    """One account, three entries in different months. The month range is on the third.
    The selection is on the 2nd item (the first being the Previous Balance).
    """
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.document.date_range = MonthRange(date(2007, 11, 1))
        self.add_entry('3/9/2007', 'first', increase='1')
        self.add_entry('10/10/2007', 'second', increase='2')
        self.add_entry('1/11/2007', 'third', increase='3')
    
    def test_date_range_change(self):
        """The selected entry stays selected after a date range, even if its index changes (the 
        index of the third entry goes from 1 to 2.
        """
        self.drsel.select_year_range()
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].description, 'third')
    

class EntriesWithZeroVariation(TestCase):
    """The first entry is normal, but the second has a null amount, resulting in no balance variation"""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
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
        self.add_account_legacy()
        self.add_entry(description='first')
        self.add_entry(description='second')
        self.add_account_legacy(account_type=AccountType.Income)
        self.add_entry(description='third') # selected
    
    def test_delete_entries(self):
        """delete the entry in the selected type"""
        self.etable.delete()
        self.assertEqual(self.ta.etable_count(), 0)
    
    def test_entries_count(self):
        """depends on the selected account type"""
        self.assertEqual(self.ta.etable_count(), 1)
    
    def test_get_entry_attribute_value(self):
        """depends on the selected account type"""
        self.assertEqual(self.etable[0].description, 'third')
    

class ThreeEntriesInTheSameExpenseAccount(TestCase):
    """Three entries balanced in the same expense account."""
    def setUp(self):
        self.create_instances()
        self.drsel.select_year_range()
        self.add_account_legacy()
        self.add_entry('31/12/2007', 'entry0', transfer='Expense', decrease='42')
        self.add_entry('1/1/2008', 'entry1', transfer='Expense', decrease='100')
        self.add_entry('20/1/2008', 'entry2', transfer='Expense', decrease='200')
        self.add_entry('31/3/2008', 'entry3', transfer='Expense', decrease='150')
        self.mainwindow.select_income_statement()
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
        eq_(self.bar_graph_data(), expected)
        self.check_gui_calls(self.bargraph_gui, ['refresh'])
        self.app.first_weekday = 6 # sunday
        expected = [('30/12/2007', '06/01/2008', '142.00', '0.00'), 
                    ('20/01/2008', '27/01/2008', '200.00', '0.00')]
        eq_(self.bar_graph_data(), expected)
    
    def test_delete_multiple_selection(self):
        """delete_entries() when having multiple entries selected delete all selected entries"""
        self.etable.select([0, 2])
        self.etable.delete()
        # [:-1]: ignore total line
        self.assertEqual(self.entry_descriptions()[:-1], ['entry2'])
    
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
    

class FourEntriesInRange(TestCase):
    """Four entries, all on October 2007, last entry is selected"""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_entry('3/10/2007', 'first', increase='1')
        self.add_entry('4/10/2007', 'second', decrease='2')
        self.add_entry('5/10/2007', 'third', increase='3')
        self.add_entry('6/10/2007', 'fourth', decrease='4')
    
    def test_balances(self):
        """Balances are correct for all entries.
        """
        # [:-1] is because we ignore total row
        self.assertEqual(self.balances()[:-1], ['1.00', '-1.00', '2.00', '-2.00'])
    
    def test_delete_entries_last(self):
        # Deleting the last entry makes the selection goes one index above, even though there's a
        # total row below.
        self.etable.delete()
        self.assertEqual(self.etable.selected_index, 2)
    
    def test_delete_entries_second(self):
        """Deleting an entry that is not the last does not change the selected index"""
        self.etable.select([1])
        self.etable.delete()
        self.assertEqual(self.etable.selected_indexes[0], 1)
    

class EightEntries(TestCase):
    """Eight entries setup for testing entry reordering."""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_account_legacy()
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
        self.assertEqual(self.entry_descriptions()[6:8], ['entry 7', 'entry 6'])
        self.assertEqual(self.balances()[6:8], ['1070.00', '1130.00'])
    
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
        self.add_account_legacy()
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
        # [:-1]: ignore total line
        self.assertEqual(self.entry_descriptions()[:-1], ['entry 1', 'entry 2', 'entry 3', 'entry 4'])

    def test_move_entry_down(self):
        """Move an entry down a couple of times"""
        self.etable.select([2])
        self.etable.move_down()
        # [:-1]: ignore total line
        self.assertEqual(self.entry_descriptions()[:-1], ['entry 1', 'entry 2', 'entry 4', 'entry 3'])
        self.etable.move_down()
        self.assertEqual(self.entry_descriptions()[:-1], ['entry 1', 'entry 2', 'entry 4', 'entry 3'])

    def test_move_entry_up(self):
        """Move an entry up a couple of times"""
        self.etable.select([1])
        self.etable.move_up()
        # [:-1]: ignore total line
        self.assertEqual(self.entry_descriptions()[:-1], ['entry 2', 'entry 1', 'entry 3', 'entry 4'])
        self.etable.move_up()
        self.assertEqual(self.entry_descriptions()[:-1], ['entry 2', 'entry 1', 'entry 3', 'entry 4'])
    
    def test_save_load_preserve_positions(self):
        # After a save and load, moving entries around still works correctly (previously, all
        # positions would be set to 1 open loading).
        self.document = self.save_and_load() # no crash
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 1, 1))
        self.mainwindow.select_transaction_table()
        self.ttable.select([3])
        self.ttable.move_up()
        eq_(self.transaction_descriptions(), ['entry 1', 'entry 2', 'entry 4', 'entry 3'])
    

class EntrySelectionOnAccountChange(TestCase):
    """I couldn't find a better name for a setup with multiple accounts, some transactions having
    the same date, some not. The setup is to test entry selection upon account selection change."""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('asset1')
        self.add_entry('1/1/2008', transfer='expense1', decrease='42.00')
        self.add_entry('4/1/2008', transfer='expense2', decrease='42.00')
        self.add_entry('11/1/2008', transfer='expense3', decrease='42.00')
        self.add_entry('22/1/2008', transfer='expense3', decrease='42.00')
        self.add_account_legacy('asset2')
        self.add_entry('1/1/2008', transfer='expense1', decrease='42.00')
        self.add_entry('12/1/2008', transfer='expense2', decrease='42.00')
        # selected account is asset2
    
    def test_keep_date(self):
        """Explicitely selecting a transaction make it so the nearest date is found as a fallback"""
        self.etable.select([0]) # the transaction from asset2 to expense1
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.expenses[1] # expense2
        self.istatement.show_selected_account()
        # The nearest date in expense2 is 2008/1/4
        self.assertEqual(self.etable.selected_indexes, [0])
        # Now select the 2008/1/12 date
        self.etable.select([1])
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.expenses[2] # expense3
        self.istatement.show_selected_account()
        # The 2008/1/11 date is nearer than the 2008/1/22 date, so it should be selected
        self.assertEqual(self.etable.selected_indexes, [0])
    
    def test_keep_transaction(self):
        # Explicitly selecting a transaction make it so it stays selected when possible.
        self.show_account('asset1')
        self.etable.select([0]) # the transaction from asset1 to expense1
        self.show_account('asset2') # the transaction doesn't exist there.
        self.show_account('expense1')
        # Even though we selected asset2, the transaction from asset1 should be selected
        self.assertEqual(self.etable.selected_indexes, [0])
    
    def test_save_entry(self):
        """Chaning an entry's date also changes the date in the explicit selection"""
        row = self.etable.selected_row
        row.date = '5/1/2008'
        self.etable.save_edits()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable.selected_indexes, [1]) #2008/1/4
    

class EntrySelectionOnDateRangeChange(TestCase):
    """Multiple entries in multiple date range to test the entry selection on date range change"""
    def setUp(self):
        self.create_instances()
        self.drsel.select_month_range()
        self.add_account_legacy()
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
        self.drsel.select_prev_date_range()
        self.assertEqual(self.etable.selected_indexes, [2]) # 2008/1/2
    
    def test_year_range(self):
        """Even in year range, the system stays the same for range change (keep the same distance
        with the range's start"""
        self.drsel.select_year_range()
        self.drsel.select_prev_date_range()
        self.etable.select([0]) # 2007/2/2, no previous balance
        self.drsel.select_next_date_range()
        self.assertEqual(self.etable.selected_indexes, [5]) # 2008/2/2
    

class ExampleDocumentLoadTest(TestCase):
    def setUp(self):
        # We're creating a couple of transactions with the latest being 4 months ago (in april).
        self.mock_today(2009, 8, 27)
        self.create_instances()
        self.add_account_legacy()
        self.add_entry('01/03/2008')
        self.add_entry('29/10/2008') # this one will end up in february, but overflow
        self.add_entry('01/03/2009')
        self.add_entry('15/04/2009')
        self.add_entry('28/04/2009') # will be deleted because in the future
        self.mainwindow.select_schedule_table()
        self.mainwindow.new_item()
        self.scpanel.start_date = '03/03/2009'
        self.scpanel.stop_date = '04/05/2009'
        self.scpanel.repeat_type_index = 2 # monthly
        self.scpanel.save()
    
    def test_adjust_example_file(self):
        # When loading as an example file, an offset is correctly applied to transactions.
        self.document.adjust_example_file()
        self.mainwindow.select_transaction_table()
        # There are 3 normal txns (the last one is deleted because it's in the future)
        # and 1 schedule spawns (only future spawns are kept)
        eq_(self.ttable.row_count, 4)
        eq_(self.ttable[0].date, '01/03/2009') # from 29/09/2008, it was in feb, but overflowed
        eq_(self.ttable[1].date, '01/07/2009') # from 01/03/2009
        eq_(self.ttable[2].date, '15/08/2009') # from 15/04/2009
        eq_(self.ttable[3].date, '03/09/2009') # spawn
    
