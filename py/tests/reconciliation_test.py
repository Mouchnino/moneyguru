# Created By: Virgil Dupras
# Created On: 2008-05-28
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date, timedelta

from .base import TestCase, TestSaveLoadMixin, CommonSetup as CommonSetupBase
from ..model.account import LIABILITY

class CommonSetup(CommonSetupBase):
    def setup_three_entries_reconciliation_mode(self):
        self.add_account()
        self.document.show_selected_account()
        self.add_entry('1/1/2008', 'one')
        self.add_entry('20/1/2008', 'two')
        self.add_entry('31/1/2008', 'three')
        self.document.toggle_reconciliation_mode()
    

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
        self.clear_gui_calls()
    
    def test_reconciliation_mode(self):
        #Toggling reconciliation mode on and off
        self.assertFalse(self.document.in_reconciliation_mode())
        self.document.toggle_reconciliation_mode()
        self.check_gui_calls(self.mainwindow_gui, refresh_reconciliation_button=1)
        self.assertTrue(self.document.in_reconciliation_mode())
        self.document.toggle_reconciliation_mode()
        self.assertFalse(self.document.in_reconciliation_mode())
    

class OneEntry(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_one_entry()
    
    def test_toggle_entries_reconciled(self):
        # When reconciliation mode is off, doesn't do anything.
        self.etable.toggle_reconciled()
        self.assertFalse(self.etable[0].reconciliation_pending)
        self.assertFalse(self.etable[0].reconciled)
    

class OneEntryWithAmountInReconciliationMode(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.setup_one_entry()
        self.document.toggle_reconciliation_mode()
    
    def test_can_reconcile_entry(self):
        """An entry today is reconciliable"""
        self.assertTrue(self.etable[0].can_reconcile())
    
    def test_can_reconcile_previous_entry(self):
        """It's not possible to reconcile a previous entry"""
        self.document.select_next_date_range()
        self.assertFalse(self.etable[0].can_reconcile())
    
    def test_reconcile(self):
        """The entry's reconciled state can be written and read"""
        self.assertFalse(self.etable[0].reconciled)
        row = self.etable.selected_row
        row.toggle_reconciled()
        self.assertTrue(self.etable[0].reconciliation_pending)
    
    def test_reconciling_sets_dirty_flag(self):
        """Reconciling an entry sets the dirty flag"""
        self.save_file()
        row = self.etable.selected_row
        row.toggle_reconciled()
        self.assertTrue(self.document.is_dirty())
    
    def test_reconciliation_balance(self):
        """Unreconcilied entries return a None balance, and reconciled entries return a 
        reconciliation balance"""
        self.assertEqual(self.etable[0].balance, '')
        row = self.etable.selected_row
        row.toggle_reconciled()
        self.assertEqual(self.etable[0].balance, '-42.00')
    
    def test_toggle_entries_reconciled_balance(self):
        """Balance is cooked when toggling reconciliation"""
        self.etable.toggle_reconciled()
        self.assertEqual(self.etable[0].balance, '-42.00')
    
    def test_toggle_entries_reconciled_sets_dirty_flag(self):
        """Toggling reconciliation sets the dirty flag"""
        self.save_file()
        self.etable.toggle_reconciled()
        self.assertTrue(self.document.is_dirty())
    

class OneEntryInTheFuture(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        str_date = (date.today() + timedelta(days=1)).strftime('%d/%m/%Y')
        self.add_entry(str_date, increase='42')
        self.document.toggle_reconciliation_mode()
    
    def test_can_reconcile_entry(self):
        """It's not possible to reconcile an entry in the future"""
        self.assertFalse(self.etable[0].can_reconcile())
    
    def test_can_set_entry_balance(self):
        """It's not possible to set an entry's reconciliation balance"""
        assert not self.etable.can_edit_cell('balance', 0)
    

class OneEntryInLiability(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy(account_type=LIABILITY)
        self.add_entry(increase='42')
        self.document.toggle_reconciliation_mode()
    
    def test_entry_balance(self):
        """The balance of the entry is None"""
        # Previously, it would crash because it would try to negate None
        self.assertEqual(self.etable[0].balance, '')
    

class TwoEntries(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_entry(increase='42')
        self.add_entry(increase='21')
        self.document.toggle_reconciliation_mode()
    
    def test_reconcile_not_selected(self):
        """Reconciling also selects the entry."""
        self.assertEqual(self.etable.selected_index, 1)
        self.etable[0].toggle_reconciled()
        self.assertEqual(self.etable.selected_index, 0)

    def test_reconcile_second_before_first(self):
        """reconcile_balance is set in stone when an entry is reconciled, meaning that the reconcile
        balance for the 2nd entry will stay at 21 even when the 1st entry is reconciled
        """
        self.etable.select([1])
        row = self.etable.selected_row
        row.toggle_reconciled()
        self.etable.select([0])
        row = self.etable.selected_row
        row.toggle_reconciled()
    

class ThreeEntries(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_three_entries_reconciliation_mode()
    
    def test_toggle_reconcile_then_save(self):
        # saving the file commits reconciliation
        self.etable[1].toggle_reconciled()
        self.save_file()
        self.assertTrue(self.etable[1].reconciled)
    
    def test_toggle_reconciliation_with_selection_disordered(self):
        """When toggling reconciliation with mutiple selection, make sure that the order in which
        the entries are toggled doesn't cause adjustments"""
        self.etable.select([2, 1, 0])
        self.etable.toggle_reconciled()
        self.assertEqual(len(self.etable), 3) # no adjustment created
    

class ThreeEntriesOneReconciled(TestCase, CommonSetup, TestSaveLoadMixin):
    def setUp(self):
        self.create_instances()
        self.setup_three_entries_reconciliation_mode()
        self.etable.select([1])
        row = self.etable.selected_row
        row.toggle_reconciled()
    
    def test_toggle_entries_reconciled_with_non_reconciled(self):
        """When none of the selected entries are reconciled, all selected entries get reconciled"""
        self.etable.select([0, 2])
        self.etable.toggle_reconciled()
        self.assertTrue(self.etable[0].reconciliation_pending)
        self.assertTrue(self.etable[2].reconciliation_pending)
    
    def test_toggle_entries_reconciled_with_all_reconciled(self):
        """When all of the selected entries are reconciled, all selected entries get un-reconciled"""
        self.etable.select([0, 2])
        self.etable.toggle_reconciled() # Both reconciled now
        self.etable.toggle_reconciled()
        self.assertFalse(self.etable[0].reconciled)
        self.assertFalse(self.etable[2].reconciled)
    
    def test_toggle_entries_reconciled_with_some_reconciled(self):
        """When some of the selected entries are reconciled, all selected entries get reconciled"""
        self.etable.select([2])
        row = self.etable.selected_row
        row.toggle_reconciled()
        self.etable.select([0, 2])
        self.etable.toggle_reconciled()
        self.assertTrue(self.etable[0].reconciliation_pending)
        self.assertTrue(self.etable[2].reconciliation_pending)
    
