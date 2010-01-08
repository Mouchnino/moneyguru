# Created By: Eric Mc Sween
# Created On: 2008-07-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_

from hsutil.currency import EUR

from ..base import TestCase, CommonSetup, TestQIFExportImportMixin
from ...document import FilterType
from ...model.account import LIABILITY, INCOME, EXPENSE
from ...model.date import YearRange

class OneAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.show_selected_account()
        self.clear_gui_calls()
    
    def test_add_empty_entry_and_save(self):
        # An empty entry really gets saved.
        self.etable.add()
        self.etable.save_edits()
        self.document.select_prev_date_range()
        self.document.select_next_date_range()
        eq_(len(self.etable), 1)
    
    def test_add_entry(self):
        # Before adding a new entry, make sure the entry table is not in edition mode. Then, start 
        # editing the new entry.
        self.etable.add()
        self.check_gui_calls(self.etable_gui, ['stop_editing', 'refresh', 'start_editing'])
    
    def test_add_twice_then_save(self):
        # Calling add() while in edition calls save_edits().
        # etable didn't have the same problem as ttable, but it did have this coverage missing
        # (commenting out the code didn't make tests fail)
        self.etable.add()
        self.etable.add()
        self.etable.save_edits()
        eq_(len(self.etable), 2)
    
    def test_delete(self):
        # Don't crash when trying to remove a transaction from an empty list.
        self.etable.delete() # no crash
    
    def test_selected_entry_index(self):
        # selected_indexes is empty when there is no entry.
        eq_(self.etable.selected_indexes, [])
    
    def test_should_show_balance_column(self):
        # When an asset account is selected, we show the balance column.
        assert self.etable.should_show_balance_column()
    
    def test_show_transfer_account(self):
        # show_transfer_account() when the table is empty doesn't do anything
        self.etable.show_transfer_account() # no crash
    

class ThreeAccounts(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_accounts('one', 'two', 'three') # three is the selected account (in second position)
    
    def test_add_transfer_entry(self):
        # Add a balancing entry to the account of the entry's transfer.
        self.add_entry(transfer='one', increase='42.00')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        eq_(len(self.etable), 1)
    

class LiabilityAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account(account_type=LIABILITY)
        self.document.show_selected_account()
    
    def test_should_show_balance_column(self):
        # When a liability account is selected, we show the balance column.
        assert self.etable.should_show_balance_column()
    

class IncomeAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account(account_type=INCOME)
        self.document.show_selected_account()
    
    def test_should_show_balance_column(self):
        # When an income account is selected, we don't show the balance column.
        assert not self.etable.should_show_balance_column()
    

class ExpenseAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account(account_type=EXPENSE)
        self.document.show_selected_account()
    
    def test_should_show_balance_column(self):
        # When an expense account is selected, we don't show the balance column.
        assert not self.etable.should_show_balance_column()
    

class OneEntryInEdition(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.etable.add()
        self.clear_gui_calls()
    
    def test_cancel_edits(self):
        """cancel_edits() calls view.refresh() and stop_editing()"""
        self.etable.cancel_edits()
        # We can't test the order of the gui calls, but stop_editing must happen first
        self.check_gui_calls(self.etable_gui, ['refresh', 'stop_editing'])
    
    def test_save(self):
        # Saving the document ends the edition mode and save the edits
        filepath = unicode(self.tmppath() + 'foo')
        self.document.save_to_xml(filepath)
        self.check_gui_calls(self.etable_gui, ['stop_editing', 'refresh', 'show_selected_row'])
        self.assertTrue(self.etable.edited is None)
        self.assertEqual(len(self.etable), 1)
    

class OneEntry(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.select_month_range()
        self.add_account('first')
        self.document.show_selected_account()
        self.add_entry('11/07/2008', 'description', 'payee', transfer='second', decrease='42')
        self.clear_gui_calls()
    
    def test_autofill_only_the_right_side(self):
        """When editing an attribute, only attributes to the right of it are autofilled"""
        self.etable.change_columns(['description', 'payee', 'transfer', 'increase', 'decrease'])
        self.etable.add()
        row = self.etable.selected_row
        row.payee = 'payee'
        self.assertEqual(row.description, '')
    
    def test_add_then_delete(self):
        """calling delete() while being in edition mode just cancels the current edit. it does *not*
        delete the other entry as well"""
        self.etable.add()
        self.etable.delete()
        self.assertEqual(len(self.etable), 1)
        self.assertTrue(self.etable.edited is None)
    
    def test_can_reconcile_expense(self):
        # income/expense entires can't be reconciled
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0] # second
        self.istatement.show_selected_account()
        self.assertFalse(self.etable[0].can_reconcile())
    
    def test_change_entry_gui_calls(self):
        """Changing an entry results in a refresh and a show_selected_row call"""
        row = self.etable[0]
        row.date = '12/07/2008'
        self.clear_gui_calls()
        self.etable.save_edits()
        self.check_gui_calls(self.etable_gui, ['refresh', 'show_selected_row'])
    
    def test_change_transfer(self):
        """Auto-creating an account refreshes the account tree."""
        row = self.etable.selected_row
        row.transfer = 'Some new name'
        self.etable.save_edits()
    
    def test_delete(self):
        """Before deleting an entry, make sure the entry table is not in edition mode."""
        self.etable.delete()
        self.check_gui_calls(self.etable_gui, ['stop_editing', 'refresh']) # Delete also refreshes.
    
    def test_set_invalid_amount(self):
        # setting an invalid amount reverts to the old amount
        self.etable[0].increase = 'foo' # no exception
        self.assertEqual(self.etable[0].increase, '')
        self.assertEqual(self.etable[0].decrease, '42.00')
        self.etable[0].decrease = 'foo' # no exception
        self.assertEqual(self.etable[0].increase, '')
        self.assertEqual(self.etable[0].decrease, '42.00')
    
    def test_show_transfer_account(self):
        # show_transfer_account() changes the shown account to 'second'
        self.etable.show_transfer_account()
        eq_(self.document.shown_account.name, 'second')
    
    def test_show_transfer_account_twice(self):
        # calling show_transfer_account() again brings the account view on 'first'
        self.etable.show_transfer_account()
        self.clear_gui_calls()
        self.etable.show_transfer_account()
        eq_(self.document.shown_account.name, 'first')
    

class EntryWithoutTransfer(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.show_selected_account()
        self.add_entry(description='foobar', decrease='130')
    
    def test_entry_transfer(self):
        # Instead of showing 'Imbalance', the transfer column shows nothing.
        eq_(self.etable[0].transfer, '')
    

class EntryWithCredit(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.show_selected_account()
        self.add_entry(decrease='42.00')
    
    def test_set_decrease_to_zero_with_zero_increase(self):
        # Setting decrease to zero when the increase is already zero sets the amount to zero.
        row = self.etable.selected_row
        row.decrease = ''
        eq_(self.etable[0].decrease, '')
        
    def test_set_increase_to_zero_with_non_zero_decrease(self):
        # Setting increase to zero when the decrease being non-zero does nothing.
        row = self.etable.selected_row
        row.increase = ''
        eq_(self.etable[0].decrease, '42.00')
    
    def test_amount(self):
        # The amount attribute is correct.
        eq_(self.etable[0].decrease, '42.00')
    

class EntryInLiabilities(TestCase, TestQIFExportImportMixin):
    # An entry in a liability account.
    # TestQIFExportImportMixin: make sure liability accounts are exported/imported correctly.
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2008, 1, 1))
        self.add_account('Credit card', account_type=LIABILITY)
        self.document.show_selected_account()
        self.add_entry('1/1/2008', 'Payment', increase='10')
    
    def test_amount(self):
        # The amount attribute is correct.
        eq_(self.etable[0].increase, '10.00')
    

class EURAccountEUREntries(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy(currency=EUR)
        self.add_entry(increase='42') # EUR
        self.add_entry(decrease='42') # EUR
    
    def test_amounts_display(self):
        """The amounts' currency are explicitly displayed"""
        self.assertEqual(self.etable[0].increase, 'EUR 42.00')
        self.assertEqual(self.etable[0].balance, 'EUR 42.00')
        self.assertEqual(self.etable[1].decrease, 'EUR 42.00')
        self.assertEqual(self.etable[1].balance, 'EUR 0.00')
    

class TwoEntries(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_entry('11/07/2008', 'first', increase='42')
        self.add_entry('12/07/2008', 'second', decrease='12')
        self.clear_gui_calls()
    
    def test_search(self):
        # Searching when on etable doesn't switch to the ttable, and shows the results in etable
        self.sfield.query = 'second'
        self.check_gui_calls_partial(self.mainwindow_gui, not_expected=['show_transaction_table'])
        eq_(len(self.etable), 1)
        eq_(self.etable[0].description, 'second')
    
    def test_selection(self):
        """EntryTable stays in sync with TransactionTable"""
        self.mainwindow.select_transaction_table()
        self.ttable.select([0])
        self.clear_gui_calls()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable.selected_indexes, [0])
        self.check_gui_calls(self.etable_gui, ['refresh', 'show_selected_row'])
    
    def test_totals(self):
        # the totals line shows the total amount of increases and decreases
        expected = "Showing 2 out of 2. Total increase: 42.00 Total decrease: 12.00"
        self.assertEqual(self.etable.totals, expected)
    
    def test_totals_with_filter(self):
        # when a filter is applied, the number of transaction shown is smaller than the total amount
        self.efbar.filter_type = FilterType.Reconciled
        expected = "Showing 0 out of 2. Total increase: 0.00 Total decrease: 0.00"
        eq_(self.etable.totals, expected)
    
    def test_totals_with_unicode_amount_format(self):
        # it seems that some people have some weird separator in their settings, and there was a
        # UnicodeEncodeError in the totals formatting.
        self.app._decimal_sep = u'\xa0'
        expected = u"Showing 2 out of 2. Total increase: 42\xa000 Total decrease: 12\xa000"
        self.assertEqual(self.etable.totals, expected)
    

class TwoEntriesOneOutOfRange(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.add_account_legacy()
        self.add_entry('11/06/2008', 'first')
        self.add_entry('11/07/2008', 'second')
    
    def test_selection_after_date_range_change(self):
        """The selection in the document is correctly updated when the date range changes"""
        # The tpanel loads the document selection, so this is why we test through it.
        self.document.select_prev_date_range()
        self.tpanel.load()
        self.assertEqual(self.tpanel.description, 'first')
    

class TwoEntriesInTwoAccounts(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_entry('11/07/2008', 'first')
        self.add_account_legacy()
        self.add_entry('12/07/2008', 'second')
    
    def test_selection_after_connect(self):
        """The selection in the document is correctly updated when the selected account changes"""
        # The tpanel loads the document selection, so this is why we test through it.
        self.mainwindow.select_transaction_table()
        self.ttable.select([0]) # first
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.tpanel.load()
        self.assertEqual(self.tpanel.description, 'second')
    
class TwoEntriesInReconciliationMode(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_entry(increase='1')
        self.add_entry(increase='2')
        self.document.toggle_reconciliation_mode()
        self.clear_gui_calls()
        self.etable[0].toggle_reconciled()
        
    def test_reconciled(self):
        """An entry is not reconciled until reonciliation mode goes off"""
        self.assertFalse(self.etable[0].reconciled)
        self.document.toggle_reconciliation_mode()
        self.assertTrue(self.etable[0].reconciled)
    

class TwoEntriesInReconciliationModeOneReconciled(TestCase):
    #Two entries with committed reconciliation.
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.show_selected_account()
        self.add_entry(increase='1')
        self.add_entry(increase='2')
        self.document.toggle_reconciliation_mode()
        self.etable[0].toggle_reconciled()
        self.document.toggle_reconciliation_mode() # commit reconciliation
        self.document.toggle_reconciliation_mode()
    
    def test_reconciled(self):
        """The first entry has been reconciled and its pending status put to False"""
        self.assertTrue(self.etable[0].reconciled)
        self.assertFalse(self.etable[0].reconciliation_pending)
    
    def test_toggle_both(self):
        """reconciled entries count as 'pending' when comes the time to determine the new value"""
        self.etable.select([0, 1])
        self.etable.toggle_reconciled() # we put the 2nd entry as "pending"
        self.assertTrue(self.etable[0].reconciled) # haven't been touched
        self.assertFalse(self.etable[0].reconciliation_pending) # haven't been touched
        self.assertTrue(self.etable[1].reconciliation_pending)
    
    def test_toggle_both_twice(self):
        """reconciled entries can be unreconciled through toggle_reconciled()"""
        self.etable.select([0, 1])
        self.etable.toggle_reconciled()
        self.etable.toggle_reconciled() # now, both entries are unreconciled
        # We haven't committed reconciliation yet so we're still reconciled
        assert self.etable[0].reconciled
        assert not self.etable[0].reconciliation_pending
        assert not self.etable[1].reconciliation_pending
    

class TwoEntriesTwoCurrencies(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_entry(increase='1')
        self.add_entry(increase='2 cad')
    
    def test_can_reconcile(self):
        """an entry with a foreign currency can't be reconciled"""
        self.document.toggle_reconciliation_mode()
        self.assertFalse(self.etable[1].can_reconcile())
    
    def test_toggle_reconcilitation_on_both(self):
        """When both entries are selected and toggle_reconciliation is called, only the first one
        is toggled.
        """
        self.document.toggle_reconciliation_mode()
        self.etable.select([0, 1])
        self.etable.toggle_reconciled()
        self.assertTrue(self.etable[0].reconciliation_pending)
        self.assertFalse(self.etable[1].reconciliation_pending)
    

class ThreeEntriesDifferentDate(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_entry('01/08/2008')
        self.add_entry('02/08/2008')
        # The date has to be "further" so select_nearest_date() doesn't pick it
        self.add_entry('04/08/2008')
    
    def test_delete_second(self):
        # When deleting the second entry, the entry after it ends up selected.
        self.etable.select([1])
        self.etable.delete()
        self.assertEqual(self.etable.selected_indexes, [1])
    

class SplitTransaction(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('first')
        self.add_entry('08/11/2008', description='foobar', transfer='second', increase='42')
        self.tpanel.load()
        self.stable.select([0])
        self.stable.selected_row.debit = '20'
        self.stable.save_edits()
        self.stable.select([2])
        self.stable.selected_row.account = 'third'
        self.stable.save_edits()
        self.tpanel.save()
    
    def test_autofill(self):
        # when the entry is part of a split, don't autofill the transfer
        self.etable.add()
        self.etable.edited.description = 'foobar'
        self.assertEqual(self.etable.edited.transfer, '')
    
    def test_show_transfer_account(self):
        # show_transfer_account() cycles through all splits of the entry
        self.etable.show_transfer_account()
        eq_(self.document.shown_account.name, 'second')
        self.etable.show_transfer_account()
        eq_(self.document.shown_account.name, 'third')
        self.etable.show_transfer_account()
        eq_(self.document.shown_account.name, 'first')

class TwoSplitsInTheSameAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('first')
        self.add_entry('08/11/2008', description='foobar', transfer='second', increase='42')
        self.tpanel.load()
        self.stable.select([0])
        self.stable.selected_row.debit = '20'
        self.stable.save_edits()
        self.stable.select([2])
        self.stable.selected_row.account = 'first'
        self.stable.save_edits()
        self.tpanel.save()
    
    def test_delete_both_entries(self):
        # There would be a crash when deleting two entries belonging to the same txn
        self.etable.select([0, 1])
        self.etable.delete() # no crash
        eq_(len(self.etable), 0)
    

class WithPreviousEntry(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_one_entry_in_previous_range()
    
    def test_totals(self):
        # the totals line ignores the previous entry line
        expected = "Showing 0 out of 0. Total increase: 0.00 Total decrease: 0.00"
        self.assertEqual(self.etable.totals, expected)
    

class WithBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget()
        self.mainwindow.select_entry_table()
    
    def test_budget_spawns(self):
        # When a budget is set budget transaction spawns show up in wtable, at the end of each month.
        eq_(len(self.etable), 12)
        assert self.etable[0].is_budget
        # Budget spawns can't be edited
        assert not self.etable.can_edit_cell('date', 0)
    
