# Created By: Eric Mc Sween
# Created On: 2008-07-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.currency import EUR

from ..base import TestCase, CommonSetup
from ...const import UNRECONCILIATION_ABORT, UNRECONCILIATION_CONTINUE_DONT_UNRECONCILE
from ...document import FILTER_RECONCILED

class OneAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.clear_gui_calls()

    def test_add_entry(self):
        """Before adding a new entry, make sure the entry table is not in edition mode. Then, start editing the new entry."""
        self.etable.add()
        self.check_gui_calls(self.etable_gui, stop_editing=1, refresh=1, start_editing=1)
    
    def test_add_twice_then_save(self):
        """Calling add() while in edition calls save_edits()"""
        # etable didn't have the same problem as ttable, but it did have this coverage missing
        # (commenting out the code didn't make tests fail)
        self.etable.add()
        self.etable.add()
        self.etable.save_edits()
        self.assertEqual(len(self.etable), 2)
    

class OneEntryInEdition(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.etable.add()
        self.clear_gui_calls()
    
    def test_cancel_edits(self):
        """cancel_edits() calls view.refresh() and stop_editing()"""
        self.etable.cancel_edits()
        # We can't test the order of the gui calls, but stop_editing must happen first
        self.check_gui_calls(self.etable_gui, refresh=1, stop_editing=1)
    
    def test_save(self):
        # Saving the document ends the edition mode and save the edits
        filepath = unicode(self.tmppath() + 'foo')
        self.document.save_to_xml(filepath)
        # there are 2 refreshes because we also commit reconciliation
        self.check_gui_calls(self.etable_gui, stop_editing=1, refresh=2, show_selected_row=1)
        self.assertTrue(self.etable.edited is None)
        self.assertEqual(len(self.etable), 1)
    

class OneEntry(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.setup_one_entry()
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
        self.document.select_income_statement()
        self.istatement.selected = self.istatement.expenses[0] # second
        self.istatement.show_selected_account()
        self.assertFalse(self.etable[0].can_reconcile())
    
    def test_change_entry_gui_calls(self):
        """Changing an entry results in a refresh and a show_selected_row call"""
        row = self.etable[0]
        row.date = '12/07/2008'
        self.clear_gui_calls()
        self.etable.save_edits()
        self.check_gui_calls(self.etable_gui, refresh=1, show_selected_row=1)
    
    def test_change_transfer(self):
        """Auto-creating an account refreshes the account tree."""
        row = self.etable.selected_row
        row.transfer = 'Some new name'
        self.etable.save_edits()
    
    def test_delete(self):
        """Before deleting an entry, make sure the entry table is not in edition mode."""
        self.etable.delete()
        self.check_gui_calls(self.etable_gui, stop_editing=1, refresh=1) # Delete also refreshes.
    
    def test_set_invalid_amount(self):
        # setting an invalid amount reverts to the old amount
        self.etable[0].increase = 'foo' # no exception
        self.assertEqual(self.etable[0].increase, '')
        self.assertEqual(self.etable[0].decrease, '42.00')
        self.etable[0].decrease = 'foo' # no exception
        self.assertEqual(self.etable[0].increase, '')
        self.assertEqual(self.etable[0].decrease, '42.00')

class EURAccountEUREntries(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account(currency=EUR)
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
        self.add_account()
        self.add_entry('11/07/2008', 'first', increase='42')
        self.add_entry('12/07/2008', 'second', decrease='12')
    
    def test_selection(self):
        """EntryTable stays in sync with TransactionTable"""
        self.document.select_transaction_table()
        self.ttable.select([0])
        self.clear_gui_calls()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable.selected_indexes, [0])
        self.check_gui_calls(self.etable_gui, refresh=1, show_selected_row=1)
    
    def test_totals(self):
        # the totals line shows the total amount of increases and decreases
        expected = "Showing 2 out of 2. Total increase: 42.00 Total decrease: 12.00"
        self.assertEqual(self.etable.totals, expected)
    
    def test_totals_with_filter(self):
        # when a filter is applied, the number of transaction shown is smaller than the total amount
        self.efbar.filter_type = FILTER_RECONCILED
        expected = "Showing 0 out of 2. Total increase: 0.00 Total decrease: 0.00"
        self.assertEqual(self.etable.totals, expected)
    
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
        self.add_account()
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
        self.add_account()
        self.add_entry('11/07/2008', 'first')
        self.add_account()
        self.add_entry('12/07/2008', 'second')
    
    def test_selection_after_connect(self):
        """The selection in the document is correctly updated when the selected account changes"""
        # The tpanel loads the document selection, so this is why we test through it.
        self.document.select_transaction_table()
        self.ttable.select([0]) # first
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.tpanel.load()
        self.assertEqual(self.tpanel.description, 'second')
    
class TwoEntriesInReconciliationMode(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry(increase='1')
        self.add_entry(increase='2')
        self.document.toggle_reconciliation_mode()
        self.clear_gui_calls()
        self.etable[0].toggle_reconciled()
        
    def test_gui_calls(self):
        """No split was unreconciled, so no confirmation should be asked"""
        self.check_gui_calls(self.document_gui)
    
    def test_reconciled(self):
        """An entry is not reconciled until reonciliation mode goes off"""
        self.assertFalse(self.etable[0].reconciled)
        self.document.toggle_reconciliation_mode()
        self.assertTrue(self.etable[0].reconciled)
    

class TwoEntriesInReconciliationModeOneReconciled(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
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
        self.assertFalse(self.etable[0].reconciled)
        self.assertFalse(self.etable[0].reconciliation_pending)
        self.assertFalse(self.etable[1].reconciliation_pending)
    

class ThreeEntriesInReconciliationModeTwoReconciled(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry('19/07/2008', increase='1')
        self.add_entry('20/07/2008', increase='2')
        self.add_entry('20/07/2008', increase='3')
        self.document.toggle_reconciliation_mode()
        self.etable[1].toggle_reconciled()
        self.etable[2].toggle_reconciled()
        self.document.toggle_reconciliation_mode() # commit reconciliation
        self.document.toggle_reconciliation_mode()
    
    def test_toggle_first(self):
        """As soon as an entry is toggled, all entries following it are unreconciled"""
        self.etable[0].toggle_reconciled()
        self.assertFalse(self.etable[1].reconciled)
        self.assertFalse(self.etable[2].reconciled)
    
    
class ThreeEntriesInReconciliationModeAllReconciled(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('first')
        self.add_account('second')
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.add_entry('19/07/2008', increase='1')
        self.add_entry('20/07/2008', transfer='second', increase='2')
        self.add_entry('20/07/2008', increase='3')
        self.document.toggle_reconciliation_mode()
        self.etable[0].toggle_reconciled()
        self.etable[1].toggle_reconciled()
        self.etable[2].toggle_reconciled()
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.etable[0].toggle_reconciled() # we also reconcile the other side of the 2nd entry
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.document.toggle_reconciliation_mode() # commit reconciliation
        self.document.toggle_reconciliation_mode()
    
    def test_cancel_reconcile(self):
        """It's possible to cancel the reconciliation"""
        self.document_gui.confirm_unreconciliation_result = UNRECONCILIATION_ABORT
        self.etable[0].toggle_reconciled()
        # The action was cancelled
        self.assertTrue(self.etable[0].reconciled)
        self.assertTrue(self.etable[1].reconciled)
        self.assertTrue(self.etable[2].reconciled)
    
    def test_continue_reconcile_but_dont_unreconcile(self):
        # when unreconciling a split and choosing the "continue but don't unreconcile action", actually
        # unreconcile the selected entries
        self.document_gui.confirm_unreconciliation_result = UNRECONCILIATION_CONTINUE_DONT_UNRECONCILE
        self.etable[0].toggle_reconciled()
        # The action was cancelled
        self.assertFalse(self.etable[0].reconciled)
        self.assertTrue(self.etable[1].reconciled)
        self.assertTrue(self.etable[2].reconciled)
    
    def test_cancel_change(self):
        """It's possible to cancel the entry change"""
        self.document_gui.confirm_unreconciliation_result = UNRECONCILIATION_ABORT
        self.etable.select([1])
        self.etable[1].increase = '12'
        self.etable.save_edits()
        # The action was cancelled
        self.assertEqual(self.etable[1].increase, '2.00')
        self.assertTrue(self.etable[0].reconciled)
        self.assertTrue(self.etable[1].reconciled)
        self.assertTrue(self.etable[2].reconciled)
    
    def test_continue_change_but_dont_unreconcile(self):
        # It's possible to continue the entry change without causing unreconciliation
        self.document_gui.confirm_unreconciliation_result = UNRECONCILIATION_CONTINUE_DONT_UNRECONCILE
        self.etable.select([1])
        self.etable[1].increase = '12'
        self.etable.save_edits()
        # The action continued, but no unreconciliation took place
        self.assertEqual(self.etable[1].increase, '12.00')
        self.assertTrue(self.etable[0].reconciled)
        self.assertTrue(self.etable[1].reconciled)
        self.assertTrue(self.etable[2].reconciled)
    
    def test_change_entry_amount(self):
        """Changing an entry's amount unreconciles it and the following entries"""
        self.etable.select([1])
        self.etable[1].increase = '12'
        self.etable.save_edits()
        self.assertTrue(self.etable[0].reconciled)
        self.assertFalse(self.etable[1].reconciled)
        self.assertFalse(self.etable[2].reconciled)
        # Verify that the correct confirmation has taken place
        self.check_gui_calls(self.document_gui, confirm_unreconciliation=1)
        self.assertEqual(self.document_gui.last_affected_split_count, 3)
    
    def test_change_entry_date(self):
        """Changing an entry's date unreconciles it and the following entries"""
        self.etable.select([1])
        self.etable[1].date = '18/07/2008' # puts the second entry first
        self.etable.save_edits()
        self.assertFalse(self.etable[0].reconciled)
        self.assertTrue(self.etable[1].reconciled) # wasn't touched
        self.assertFalse(self.etable[2].reconciled)
    
    def test_change_other_side_amount(self):
        """Changing an entry's amount for which the 'other side' is reconciled unreconciles it"""
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.etable[0].decrease = '12'
        self.etable.save_edits()
        self.assertFalse(self.etable[0].reconciled)
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertTrue(self.etable[0].reconciled)
        self.assertFalse(self.etable[1].reconciled)
        self.assertFalse(self.etable[2].reconciled)
    
    def test_change_other_side_date(self):
        """Changing an entry's date for which the 'other side' is reconciled unreconciles it"""
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.etable[0].date = '18/07/2008'
        self.etable.save_edits()
        self.assertFalse(self.etable[0].reconciled)
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertFalse(self.etable[0].reconciled)
        self.assertTrue(self.etable[1].reconciled) # wasn't touched
        self.assertFalse(self.etable[2].reconciled)
    
    def test_change_other_side_transfer(self):
        """Changing an entry's transfer for which the 'other side' is reconciled unreconciles it.
        However, it does *not* unreconcile the changed entry.
        """
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.etable[0].transfer = 'foobaz'
        self.etable.save_edits()
        self.assertTrue(self.etable[0].reconciled) # stays reconciled
        self.document.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertTrue(self.etable[0].reconciled)
        self.assertFalse(self.etable[1].reconciled)
        # Verify that the correct confirmation has taken place
        self.check_gui_calls(self.document_gui, confirm_unreconciliation=1)
        self.assertEqual(self.document_gui.last_affected_split_count, 2)
    
    def test_dont_unreconcile_preference(self):
        # with the dont_unreconcile pereference ON, just never unreconcile.
        self.app.dont_unreconcile = True
        self.etable.select([1])
        self.etable[1].increase = '12'
        self.etable.save_edits()
        self.assertTrue(self.etable[0].reconciled)
        self.assertTrue(self.etable[1].reconciled)
        self.assertTrue(self.etable[2].reconciled)
        self.check_gui_calls(self.document_gui) # no confirm_unreconciliation
    
    def test_move_second(self):
        """Moving an entry unreconciles every following entry (and the moved entry)"""
        self.etable.move([1], 3)
        self.assertTrue(self.etable[0].reconciled)
        self.assertFalse(self.etable[1].reconciled)
        self.assertFalse(self.etable[2].reconciled)
    
    def test_toggle_second(self):
        """Unreconciling an entry unreconciles every reconciled entries following it"""
        self.clear_gui_calls()
        self.etable[1].toggle_reconciled()
        self.assertTrue(self.etable[0].reconciled)
        self.assertFalse(self.etable[1].reconciled)
        self.assertFalse(self.etable[2].reconciled)
        # Verify that the correct confirmation has taken place
        self.check_gui_calls(self.document_gui, confirm_unreconciliation=1)
        self.assertEqual(self.document_gui.last_affected_split_count, 2)
    

class TwoEntriesTwoCurrencies(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
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
        self.add_account()
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
        self.add_account('first')
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
    

class WithPreviousEntry(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_one_entry_in_previous_range()
    
    def test_totals(self):
        # the totals line ignores the previous entry line
        expected = "Showing 0 out of 0. Total increase: 0.00 Total decrease: 0.00"
        self.assertEqual(self.etable.totals, expected)
    
