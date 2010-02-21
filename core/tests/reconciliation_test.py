# Created By: Virgil Dupras
# Created On: 2008-05-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from .base import TestCase, TestSaveLoadMixin, CommonSetup as CommonSetupBase, TestApp
from ..model.account import AccountType

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
        assert not self.document.in_reconciliation_mode()
        self.document.toggle_reconciliation_mode()
        self.check_gui_calls(self.mainwindow_gui, ['refresh_reconciliation_button'])
        assert self.document.in_reconciliation_mode()
        self.document.toggle_reconciliation_mode()
        assert not self.document.in_reconciliation_mode()
    

class OneEntry(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.show_selected_account()
        self.add_entry('11/07/2008', decrease='42')
    
    def test_initial_attrs(self):
        # initially, an entry is not reconciled
        assert not self.etable[0].reconciled
        eq_(self.etable[0].reconciliation_date, '')
    
    def test_set_reconciliation_date(self):
        # It's possible to set any date as a reconciliation date (even when not in reconciliation
        # mode).
        self.etable[0].reconciliation_date = '12/07/2008'
        self.etable.save_edits()
        eq_(self.etable[0].reconciliation_date, '12/07/2008')
    
    def test_toggle_entries_reconciled(self):
        # When reconciliation mode is off, doesn't do anything.
        self.etable.toggle_reconciled()
        assert not self.etable[0].reconciled
    

class OneEntryInReconciliationMode(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.document.show_selected_account()
        self.add_entry('11/07/2008', decrease='42')
        self.document.toggle_reconciliation_mode()
    
    def test_can_reconcile_entry(self):
        # An entry today is reconciliable.
        assert not self.etable[0].reconciled
        assert self.etable[0].can_reconcile()
    
    def test_cant_reconcile_previous_balance_entry(self):
        # It's not possible to reconcile a previous balance entry.
        self.document.select_next_date_range()
        # The first entry is not a "Previous Balance" entry
        assert not self.etable[0].can_reconcile()
    
    def test_commit_reconciliation(self):
        # committing reconciliation sets the entry's reconciliation date to the txn's date
        self.etable.selected_row.toggle_reconciled()
        self.document.toggle_reconciliation_mode()
        assert self.etable[0].reconciled
        eq_(self.etable[0].reconciliation_date, '11/07/2008')
    
    def test_reconciling_sets_dirty_flag(self):
        # Reconciling an entry sets the dirty flag.
        self.save_file()
        self.etable.selected_row.toggle_reconciled()
        assert self.document.is_dirty()
    
    def test_reconciliation_balance(self):
        # Unreconcilied entries return a None balance, and reconciled entries return a 
        # reconciliation balance
        eq_(self.etable[0].balance, '')
        row = self.etable.selected_row
        row.toggle_reconciled()
        eq_(self.etable[0].balance, '-42.00')
    
    def test_toggle_reconciled(self):
        # calling toggle_reconciled() on a row toggles reconciliation and shows a reconciliation
        # balance.
        self.etable.selected_row.toggle_reconciled()
        assert self.etable[0].reconciled
        eq_(self.etable[0].balance, '-42.00')
    
    def test_toggle_entries_reconciled_sets_dirty_flag(self):
        # Toggling reconciliation sets the dirty flag.
        self.save_file()
        self.etable.toggle_reconciled()
        assert self.document.is_dirty()
    

class OneEntryInTheFuture(TestCase):
    def setUp(self):
        self.mock_today(2009, 12, 26)
        self.create_instances()
        self.add_account()
        self.document.show_selected_account()
        self.add_entry('27/12/2009', increase='42')
        self.document.toggle_reconciliation_mode()
    
    def test_can_reconcile_entry(self):
        # It's not possible to reconcile an entry in the future.
        assert not self.etable[0].can_reconcile()
    
    def test_can_set_entry_balance(self):
        # It's not possible to set an entry's reconciliation balance.
        assert not self.etable.can_edit_cell('balance', 0)
    

class OneEntryInLiability(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account(account_type=AccountType.Liability)
        self.document.show_selected_account()
        self.add_entry(increase='42')
        self.document.toggle_reconciliation_mode()
    
    def test_entry_balance(self):
        # The balance of the entry is empty.
        # Previously, it would crash because it would try to negate None
        eq_(self.etable[0].balance, '')
    

#--- Reconciled entry
def app_reconciled_entry():
    app = TestApp()
    app.add_account()
    app.doc.show_selected_account()
    app.add_entry('11/07/2008', transfer='foo', decrease='42')
    app.doc.toggle_reconciliation_mode()
    app.etable.selected_row.toggle_reconciled()
    app.doc.toggle_reconciliation_mode()
    return app

def test_change_amount_currency_dereconciles_entry():
    # Changing an antry's amount to another currency de-reconciles it.
    app = app_reconciled_entry()
    app.etable[0].decrease = '12eur'
    app.etable.save_edits()
    assert not app.etable[0].reconciled

def test_change_amount_currency_from_other_side_dereconciles_entry():
    # Changing an entry's amount from the "other side" also de-reconcile that entry
    app = app_reconciled_entry()
    app.mainwindow.show_account()
    app.etable[0].increase = '12eur'
    app.etable.save_edits()
    app.mainwindow.show_account()
    assert not app.etable[0].reconciled

class OneEntryReconciledDifferentDate(TestCase):
    # 1 entry, reconciled at a different date than its own date
    def setUp(self):
        self.mock_today(2008, 7, 20)
        self.create_instances()
        self.add_account()
        self.document.show_selected_account()
        self.add_entry('11/07/2008', decrease='42')
        self.etable[0].reconciliation_date = '12/07/2008'
        self.etable.save_edits()
    
    def test_save_and_load(self):
        # reconciliation date is correctly saved and loaded
        self.document = self.save_and_load()
        self.create_instances()
        self.bsheet.selected = self.bsheet.assets[0]
        self.document.show_selected_account()
        eq_(self.etable[0].reconciliation_date, '12/07/2008')
    

class ThreeEntries(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_three_entries_reconciliation_mode()
    
    def test_reconcile_not_selected(self):
        # Reconciling also selects the entry.
        # current selection is the last entry.
        self.etable[0].toggle_reconciled()
        eq_(self.etable.selected_index, 0)
    
    def test_toggle_reconcile_then_save(self):
        # saving the file commits reconciliation
        self.etable[1].toggle_reconciled()
        self.save_file()
        assert self.etable[1].reconciled
    

class ThreeEntriesOneReconciled(TestCase, CommonSetup, TestSaveLoadMixin):
    # 3 entries, in reconciliation mode, with the entry at index 1 having its reconciliation pending.
    def setUp(self):
        self.create_instances()
        self.setup_three_entries_reconciliation_mode()
        self.etable.select([1])
        row = self.etable.selected_row
        row.toggle_reconciled()
    
    def test_toggle_entries_reconciled_with_none_reconciled(self):
        # When none of the selected entries are reconciled, all selected entries get reconciled.
        self.etable.select([0, 2])
        self.etable.toggle_reconciled()
        assert self.etable[0].reconciled
        assert self.etable[2].reconciled
    
    def test_toggle_entries_reconciled_with_all_reconciled(self):
        # When all of the selected entries are reconciled, all selected entries get de-reconciled
        self.etable.select([0, 2])
        self.etable.toggle_reconciled() # Both reconciled now
        self.etable.toggle_reconciled()
        assert not self.etable[0].reconciled
        assert not self.etable[2].reconciled
    
    def test_toggle_entries_reconciled_with_some_reconciled(self):
        # When some of the selected entries are reconciled, all selected entries get reconciled
        self.etable.select([0, 1, 2]) # entry at index 1 is pending reconciliation
        self.etable.toggle_reconciled()
        assert self.etable[0].reconciled
        assert self.etable[1].reconciled
        assert self.etable[2].reconciled
    
