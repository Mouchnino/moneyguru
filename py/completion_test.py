# Unit Name: moneyguru.completion_test
# Created By: Virgil Dupras
# Created On: 2008-06-15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import os.path as op
import time
from datetime import date

from .main_test import TestCase, TestSaveLoadMixin
from .model.date import MonthRange

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
    
    def test_current_completion(self):
        """There is no completion yet"""
        self.assertEqual(self.etable.current_completion(), None)
    

class OneEmptyAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
    
    def test_complete_transfer(self):
        """Don't lookup the selected account for transfer completion"""
        self.assert_(self.etable.complete('c', 'transfer') is None)
    

class EmptyAccountWithWhitespaceInName(TestCase):
    """One empty account named '  Foobar  ' and one account 'foobaz'"""
    def setUp(self):
        self.create_instances()
        self.add_account('  Foobar  ')
        self.add_account('foobaz')
    
    def test_complete_transfer(self):
        """transfer completion looking up account names ignores whitespaces (and case)"""
        self.assertEqual(self.etable.complete('f', 'transfer'), 'Foobar')
    

class ThreeEmptyAccounts(TestCase):
    """Three accounts, empty"""
    def setUp(self):
        self.create_instances()
        self.add_account('one')
        self.add_account('two')
        self.add_account('three') # This is the selected account (in second position)
    
    def test_complete_transfer(self):
        """When no entry match for transfer completion, lookup in accounts"""
        self.assertEqual(self.etable.complete('o', 'transfer'), 'one')
    
    def test_complete_empty_transfer(self):
        """Don't complete an empty transfer"""
        self.assertEqual(self.etable.complete('', 'transfer'), None)

    def test_complete_description(self):
        """description completion does *not* look into accounts"""
        self.assert_(self.etable.complete('o', 'description') is None)
    

class DifferentAccountTypes(TestCase):
    """Two accounts of asset type, and one account of income type."""
    def setUp(self):
        self.create_instances()
        self.add_account('one')
        self.add_account('two')
        self.add_entry(transfer='three')
    
    def test_complete_transfer_ignore_selected(self):
        """Ignore selected account in completion in cases where non-asset accounts are selected as
        well
        """
        self.assert_(self.etable.complete('th', 'transfer') is None)
    

class EntryInEditionMode(TestCase):
    """An empty account, but an entry is in edit mode in october 2007."""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.etable.add()
        row = self.etable.edited
        row.date = '1/10/2007'
        row.description = 'foobar'
        row.increase = '42'
    
    def test_complete(self):
        """Don't make completion match with the edited entry"""
        self.assert_(self.etable.complete('foo', 'description') is None)
    

class OneEntryYearRange2007(TestCase):
    """One account, one entry, which is in the yearly date range (2007). The entry has a transfer
    and a debit value set.
    """
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42')
    
    def test_amount_completion_uses_the_latest_entered(self):
        """Even if the date is earlier, we use this newly added entry because it's the latest 
        modified
        """
        self.add_entry('9/10/2007', 'Deposit', increase='12.34')
        self.etable.add()
        row = self.etable.edited
        row.date = '11/10/2007'
        row.description = 'Deposit'
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].increase, '12.34')
    
    def test_autofill_column_selection_for_description(self):
        """It's possible to pass a list of columns to be autofilled (instead of autofilling all)"""
        self.etable.add()
        self.etable.change_columns(['description', 'payee', 'amount'])
        row = self.etable.selected_row
        row.description = 'Deposit'
        self.assertEqual(self.etable[1].transfer, '')
    
    def test_autofill_column_selection_for_transfer(self):
        """It's possible to pass a list of columns to be autofilled (instead of autofilling all)"""
        self.etable.change_columns(['transfer', 'payee', 'amount'])
        self.etable.add()
        row = self.etable.selected_row
        row.transfer = 'Salary'
        self.assertEqual(self.etable[1].description, '')
    
    def test_autofill_column_selection_for_payee(self):
        """It's possible to pass a list of columns to be autofilled (instead of autofilling all)"""
        self.etable.change_columns(['payee', 'description', 'amount'])
        self.etable.add()
        row = self.etable.selected_row
        row.payee = 'Payee'
        self.assertEqual(self.etable[1].transfer, '')
    
    def test_autofill_convert_amount_field(self):
        #autofill_columns can be given 'increase' and 'decrease'. It will all be converted into 'amount'
        self.etable.change_columns(['description', 'increase', 'decrease'])
        self.etable.add()
        row = self.etable.selected_row
        row.description = 'Deposit'
        self.assertEqual(self.etable[1].increase, '42.00')
    
    def test_autofill_garbage_columns(self):
        """autofill ignores column that can be auto filled"""
        self.etable.change_columns(['description', 'payee', 'amount', 'foo', 'bar'])
        self.etable.add()
        row = self.etable.selected_row
        row.description = 'Deposit' # no crash
        self.assertEqual(self.etable[1].payee, 'Payee') # The rest of the columns were filled anyway
        self.assertEqual(self.etable[1].transfer, '') #... and only the selected ones
    
    def test_complete_case_insensitive(self):
        """The completion matching is case insensitive"""
        self.assertEqual(self.etable.complete('deposit', 'description'), 'Deposit')
        self.assertEqual(self.etable.complete('dEposit', 'description'), 'Deposit')
    
    def test_complete_exact(self):
        """Exact match returns the same value"""
        self.assertEqual(self.etable.complete('Deposit', 'description'), 'Deposit')
    
    def test_complete_goes_to_next(self):
        """As soon as a completion gets longer than the matched entry, find another one"""
        self.add_entry('1/10/2007', description='Dep')
        self.assertEqual(self.etable.complete('Dep', 'description'), 'Dep')
        self.assertEqual(self.etable.complete('Depo', 'description'), 'Deposit')
    
    def test_complete_latest_modified(self):
        """Always search the latest modified entries first for completion match"""
        self.add_entry('31/10/2007', 'DepositFoo')
        self.assertEqual(self.etable.complete('Deposit', 'description'), 'DepositFoo')
        self.etable.delete()
        self.assertEqual(self.etable.complete('Deposit', 'description'), 'Deposit')
    
    def test_complete_partial(self):
        """Partial match returns the attribute of the matched entry"""
        self.assertEqual(self.etable.complete('Dep', 'description'), 'Deposit')
    
    def test_complete_transfer(self):
        """MoneyGuru.complete() can do completion on more than one attribute"""
        self.assertEqual(self.etable.complete('sal', 'transfer'), 'Salary')
    
    def test_field_completion_is_case_sensitive(self):
        """When the case of a description/transfer value does not match an entry, completion do not
        occur
        """
        self.etable.add()
        row = self.etable.selected_row
        row.description = 'deposit'
        row.transfer = 'deposit'
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].increase, '')
    
    def test_field_completion_on_set_entry_transfer(self):
        """Setting a transfer autocompletes the amount and the description"""
        self.etable.add()
        row = self.etable.selected_row
        row.transfer = 'Salary'
        selected = self.etable.selected_indexes[0]
        self.assertEqual(self.etable[selected].increase, '42.00')
        self.assertEqual(self.etable[selected].description, 'Deposit')
        self.assertEqual(self.etable[selected].payee, 'Payee')
    
    def test_field_completion_on_set_entry_description(self):
        """Setting a description autocompletes the amount and the transfer"""
        self.etable.add()
        row = self.etable.selected_row
        row.description = 'Deposit'
        selected = self.etable.selected_indexes[0]
        self.assertEqual(self.etable[selected].increase, '42.00')
        self.assertEqual(self.etable[selected].transfer, 'Salary')
        self.assertEqual(self.etable[selected].payee, 'Payee')
    
    def test_field_completion_on_set_entry_payee(self):
        """Setting a transfer autocompletes the amount and the description"""
        self.etable.add()
        row = self.etable.selected_row
        row.payee = 'Payee'
        selected = self.etable.selected_indexes[0]
        self.assertEqual(self.etable[selected].increase, '42.00')
        self.assertEqual(self.etable[selected].description, 'Deposit')
        self.assertEqual(self.etable[selected].transfer, 'Salary')
    

class EntryWithBlankDescription(TestCase, TestSaveLoadMixin):
    """One account, one entry, which has a blank description"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry('10/10/2007', description='', transfer='Salary', increase='42')
    
    def test_field_completion_on_description(self):
        """Don't do a field completion on blank values"""
        self.etable.add()
        row = self.etable.selected_row
        row.description = ''
        selected = self.etable.selected_indexes[0]
        self.assertEqual(self.etable[selected].transfer, '')
        self.assertEqual(self.etable[selected].increase, '')
        self.assertEqual(self.etable[selected].decrease, '')
    
    def test_complete_empty_string(self):
        """complete() always returns None on empty strings"""
        self.assert_(self.etable.complete('', 'description') is None)
    

class EntryWithWhitespaceInDescription(TestCase):
    """One account, one entry, which has whitespace in its description"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry('10/10/2007', description='  foobar  ', increase='1')
    
    def test_completion_ignore_whitespaces(self):
        """Don't complete string based on whitespaces"""
        self.assert_(self.etable.complete(' ', 'description') is None)
    
    def test_completion_strip_whitespace(self):
        """Ignore whitespace when finding a completion match"""
        self.assertEqual(self.etable.complete('foo', 'description'), 'foobar')
    

class DifferentAccountTypes(TestCase):
    """Two accounts of asset type, and one account of income type."""
    def setUp(self):
        self.create_instances()
        self.add_account('one')
        self.add_account('two')
        self.add_entry(transfer='three')
    
    def test_complete_transfer(self):
        """Complete transfer with non-asset categories as well"""
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable.complete('th', 'transfer'), 'three')
    

class TwoEntriesInRange(TestCase):
    """Two entries, both on October 2007, first entry is selected"""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_entry('2/10/2007', 'first', increase='102.00')
        self.add_entry('4/10/2007', 'second', increase='42.00')
        self.etable.select([0])
    
    def test_amount_completion(self):
        """Upon setting description, set the amount to the amount of the first matching entry with
        the same description
        """
        self.etable.add()
        row = self.etable.selected_row
        row.description = 'first'
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].increase, '102.00')
    
    def test_amount_completion_already_set(self):
        """If the amount is already set, don't complete it"""
        row = self.etable.selected_row
        row.description = 'second'
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].increase, '102.00')
    

class ThreeEntriesInTwoAccountTypes(TestCase):
    """3 entries in 2 accounts of different type."""
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry(description='first')
        self.add_entry(description='second')
        self.add_account()
        self.add_entry(description='third') # selected
    
    def test_complete(self):
        # Even in the entry table, completion from other accounts show up
        self.assertEqual(self.etable.complete('f', 'description'), 'first')
    

class FourEntriesWithSomeDescriptionAndCategoryCollision(TestCase):
    """Four entries. Mostly for completion, I can't see any other use. The first is a 'booby trap'.
    (simply having the completion iterate the list made all tests pass). The second is the base
    entry. The third has the same description but a different transfer. The fourth has a different 
    transfer but the same description. All have different amounts and dates. Second entry is 
    selected. Also, time.time() is mocked so that the time of the setUp is earlier than the time
    of the tests.
    """
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.mock(time, 'time', lambda: 42)
        self.add_entry('2/10/2007', description='description', payee='payee', transfer='category', increase='42')
        self.mock(time, 'time', lambda: 43)
        self.add_entry('3/10/2007', description='desc1', payee='pay1', transfer='cat1', increase='1')
        self.mock(time, 'time', lambda: 44)
        self.add_entry('4/10/2007', description='desc1', payee='pay1', transfer='cat2', increase='2')
        self.mock(time, 'time', lambda: 45)
        self.add_entry('5/10/2007', description='desc2', payee='pay1', transfer='cat1', increase='3')
        self.etable.select([1])
        self.mock(time, 'time', lambda: 46)
    
    def assert_completion_order_changed(self):
        """complete() returns descriptions for the second entry, and field completion also is based
        on the second entry.
        """
        self.assertEqual(self.etable.complete('d', 'description'), 'desc1')
        self.assertEqual(self.etable.complete('c', 'transfer'), 'cat1')
        self.assertEqual(self.etable.complete('p', 'payee'), 'pay1')
        self.etable.add()
        row = self.etable.selected_row
        row.description = 'desc1'
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].payee, 'pay1')
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].transfer, 'cat1')
        self.etable.add()
        row = self.etable.selected_row
        row.transfer = 'cat1'
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].description, 'desc1')
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].payee, 'pay1')
        self.etable.add()
        row = self.etable.selected_row
        row.payee = 'pay1'
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].description, 'desc1')
        self.assertEqual(self.etable[self.etable.selected_indexes[0]].transfer, 'cat1')
    
    def test_edit_transfer_changes_completion_list_order(self):
        """A transfer edit on the second entry makes it the first candidate for completion"""
        row = self.etable.selected_row
        row.transfer = 'cat12'
        self.etable.save_edits()
        row = self.etable.selected_row
        row.transfer = 'cat1'
        self.etable.save_edits()
        self.assert_completion_order_changed()
    
    def test_edit_credit_changes_completion_list_order(self):
        """A credit edit on the second entry makes it the first candidate for completion"""
        row = self.etable.selected_row
        row.decrease = '1'
        self.etable.save_edits()
        self.assert_completion_order_changed()
    
    def test_edit_date_changes_completion_list_order(self):
        """A date edit on the second entry makes it the first candidate for completion"""
        row = self.etable.selected_row
        row.date = '2/10/2007'
        self.etable.save_edits()
        self.assert_completion_order_changed()
    
    def test_edit_debit_changes_completion_list_order(self):
        """A debit edit on the second entry makes it the first candidate for completion"""
        row = self.etable.selected_row
        row.increase = '8'
        self.etable.save_edits()
        self.assert_completion_order_changed()
    
    def test_edit_description_changes_completion_list_order(self):
        """A description edit on the second entry makes it the first candidate for completion"""
        row = self.etable.selected_row
        row.description = 'other desc' # Make sure that edition takes place
        row.description = 'desc1'
        self.etable.save_edits()
        self.assert_completion_order_changed()
    
    def test_edit_ttable_changes_completion_list_order(self):
        # Changing a txn in the ttable updates the mtime
        self.document.select_transaction_table()
        self.ttable.selected_row.amount = '1'
        self.ttable.save_edits()
        self.document.select_entry_table()
        self.assert_completion_order_changed()
    
    def test_next_completion_after_description(self):
        """next_completion() after a complete_description() returns the next matching description"""
        self.etable.complete('d', 'description') # desc 2
        self.assertEqual(self.etable.next_completion(), 'description')
    
    def test_next_completion_after_null_completion(self):
        """After a completion that returns nothing, next_completion() just returns None"""
        self.etable.complete('nothing', 'description')
        self.assert_(self.etable.next_completion() is None)
    
    def test_next_completion_after_transfer(self):
        """next_completion() after a complete_transfer() returns the next matching transfer"""
        self.etable.complete('c', 'transfer') # cat1
        self.assertEqual(self.etable.next_completion(), 'category')
    
    def test_next_completion_rollover(self):
        """next_completion() 3 times rolls over"""
        self.etable.complete('d', 'description')
        self.etable.next_completion()
        self.etable.next_completion()
        self.assertEqual(self.etable.next_completion(), 'desc2')
    
    def test_next_completion_rollover_plus_one(self):
        """An easy way out for all the other tests was to use negative indexing. But it stops 
        working here
        """
        self.etable.complete('d', 'description')
        self.etable.next_completion()
        self.etable.next_completion()
        self.etable.next_completion()
        self.assertEqual(self.etable.next_completion(), 'description')
    
    def test_next_completion_twice(self):
        """next_completion() twice returns the second next completion, skipping duplicates"""
        self.etable.complete('d', 'description')
        self.etable.next_completion()
        self.assertEqual(self.etable.next_completion(), 'desc1')
    
    def test_previous_completion_after_description(self):
        """previous_completion() after a complete_description() returns the previous matching description"""
        self.etable.complete('d', 'description') # desc 2
        self.assertEqual(self.etable.prev_completion(), 'desc1')
        self.assertEqual(self.etable.current_completion(), 'desc1')
    
    def test_previous_completion_after_null_completion(self):
        """After a completion that returns nothing, previous_completion() just returns None"""
        self.etable.complete('nothing', 'description')
        self.assert_(self.etable.prev_completion() is None)
    
    def test_previous_completion_after_set_description(self):
        """previous_completion() returns nothing after set_entry_description()"""
        self.etable.complete('d', 'description')
        row = self.etable.selected_row
        row.description = 'dabble'
        self.assertEqual(self.etable.prev_completion(), None)
    
    def test_previous_completion_after_set_payee(self):
        """previous_completion() returns nothing after set_entry_payee()"""
        self.etable.complete('p', 'payee')
        row = self.etable.selected_row
        row.payee = 'police'
        self.assertEqual(self.etable.prev_completion(), None)
    
    def test_previous_completion_after_set_transfer(self):
        """previous_complteion() returns nothing after set_entry_transfer()"""
        self.etable.complete('c', 'transfer')
        row = self.etable.selected_row
        row.transfer = 'cow'
        self.assertEqual(self.etable.prev_completion(), None)

    def test_previous_completion_after_transfer(self):
        """previous_completion() after a complete_transfer() returns the previous matching transfer"""
        self.etable.complete('c', 'transfer') # cat1
        self.assertEqual(self.etable.prev_completion(), 'cat2')
    
    def test_previous_completion_rollover(self):
        """previous_completion() 3 times rolls over"""
        self.etable.complete('d', 'description')
        self.etable.prev_completion()
        self.etable.prev_completion()
        self.assertEqual(self.etable.prev_completion(), 'desc2')
    
    def test_previous_completion_twice(self):
        """previous_completion() twice returns the second previous completion, skipping duplicates"""
        self.etable.complete('d', 'description')
        self.etable.prev_completion()
        self.assertEqual(self.etable.prev_completion(), 'description')
    
    def test_persistence_of_completion(self):
        """Completion (including its order) is persistent"""
        self.mock_today(2007, 10, 6) # the test fails otherwise
        row = self.etable.selected_row
        row.transfer = 'cat12'
        self.etable.save_edits()
        row = self.etable.selected_row
        row.transfer = 'cat1'
        self.etable.save_edits()
        filepath = op.join(self.tmpdir(), 'foo.xml')
        self.document.save_to_xml(filepath)
        del self.document
        self.create_instances()
        self.add_account()
        self.etable.add()
        row = self.etable.selected_row
        row.description = 'Duh, that shouldn\'t be here!'
        self.etable.save_edits()
        self.document.load_from_xml(filepath)
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assert_completion_order_changed()
    
