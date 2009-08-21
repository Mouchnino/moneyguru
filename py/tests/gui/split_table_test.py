# Created By: Virgil Dupras
# Created On: 2008-07-05
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.currency import CAD, EUR

from ..base import TestCase, TestSaveLoadMixin, TestQIFExportImportMixin

class OneEntry(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('first', currency=CAD)
        self.add_entry(transfer='second', increase='42')
    
    def test_add_gui_calls(self):
        """refresh() and start_editing() are called after a add()"""
        self.tpanel.load()
        self.clear_gui_calls()
        self.stable.add()
        self.check_gui_calls(self.stable_gui, refresh=1, start_editing=1, stop_editing=1)
    
    def test_cancel_edits(self):
        # cancel_edits() sets edited to None and makes the right gui calls
        self.tpanel.load()
        self.stable[0].account = 'foo'
        self.clear_gui_calls()
        self.stable.cancel_edits()
        self.assertTrue(self.stable.edited is None)
        self.check_gui_calls(self.stable_gui, refresh=1, stop_editing=1)
    
    def test_changes_split_buffer_only(self):
        """Changes made to the split table don't directly get to the model until tpanel.save()"""
        self.tpanel.load()
        row = self.stable.selected_row
        row.debit = '40'
        self.stable.save_edits()
        # Now, let's force a refresh of etable
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable[0].increase, 'CAD 42.00')
    
    def test_completion(self):
        """Just make sure it works. That is enough to know SplitTable is of the right subclass"""
        self.assertEqual(self.stable.complete('s', 'account'), 'second')
    
    def test_completion_new_txn(self):
        # When completing an account from a new txn, the completion wouldn't work at all
        self.mainwindow.select_transaction_table()
        self.ttable.add()
        self.tpanel.load()
        self.assertEqual(self.stable.complete('f', 'account'), 'first')
    
    def test_load_tpanel_from_ttable(self):
        """When the tpanel is loaded form the ttable, the system currency is used"""
        self.mainwindow.select_transaction_table()
        self.tpanel.load() # no crash
        self.assertEqual(self.stable[0].debit, 'CAD 42.00')
    
    def test_memo(self):
        """It's possible to set a different memo for each split"""
        self.tpanel.load()
        row = self.stable.selected_row
        row.memo = 'memo1'
        self.stable.save_edits()
        self.stable.select([1])
        row = self.stable.selected_row
        row.memo = 'memo2'
        self.stable.save_edits()
        self.tpanel.save()
        self.tpanel.load()
        self.assertEqual(self.stable[0].memo, 'memo1')
        self.assertEqual(self.stable[1].memo, 'memo2')
    
    def test_set_wrong_values_for_attributes(self):
        """set_attribute_avlue catches ValueError"""
        self.tpanel.load()
        row = self.stable.selected_row
        row.debit = 'invalid'
        row.credit = 'invalid'
        # no crash occured
    

class OneTransactionBeingAdded(TestCase):
    def setUp(self):
        self.create_instances()
        self.mainwindow.select_transaction_table()
        self.ttable.add()
    
    def test_change_splits(self):
        """It's possible to change the splits of a newly created transaction"""
        # Previously, it would crash because of the 0 amounts.
        # At this moment, we have a transaction with 2 empty splits
        self.tpanel.load()
        self.stable[0].account = 'first'
        self.stable[0].credit = '42'
        self.stable.save_edits()
        self.stable.select([1])
        self.stable[1].account = 'second'
        self.stable.save_edits()
        self.tpanel.save()
        row = self.ttable[0]
        self.assertEqual(row.from_, 'first')
        self.assertEqual(row.to, 'second')
        self.assertEqual(row.amount, '42.00')
    
    def test_delete_split_with_none_selected(self):
        # don't crash when stable.delete() is called enough times to leave the table empty
        self.tpanel.load()
        self.stable.delete() # Unassigned 1
        self.stable.delete() # Unassigned 2
        try:
            self.stable.delete()
        except AttributeError:
            self.fail("When the table is empty, don't try to delete")
    

class EURAccountsEURTransfer(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('first', EUR)
        self.add_account('second', EUR)
        self.add_entry(transfer='first', increase='42') # EUR
        self.tpanel.load()
    
    def test_amounts_display(self):
        """The amounts' currency are explicitly displayed"""
        self.assertEqual(self.stable[0].debit, 'EUR 42.00')
        self.assertEqual(self.stable[1].credit, 'EUR 42.00')
    
class OneTransactionWithMemos(TestCase, TestSaveLoadMixin, TestQIFExportImportMixin):
    # TestSaveLoadMixin: Make sure memos are loaded/saved
    # same for TestQIFExportImportMixin
    def setUp(self):
        self.create_instances()
        self.add_account('first')
        self.add_account('second')
        self.mainwindow.select_transaction_table()
        self.ttable.add()
        self.tpanel.load()
        self.stable[0].account = 'first'
        self.stable[0].memo = 'memo1'
        self.stable[0].credit = '42'
        self.stable.save_edits()
        self.stable.select([1])
        self.stable[1].account = 'second'
        self.stable[1].memo = 'memo2'
        self.stable.save_edits()
        self.tpanel.save()
    

class OneTransactionWithUnassignedSplit(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('first')
        self.add_entry(transfer='second', increase='42')
        self.tpanel.load()
        self.stable.select([1])
        self.stable[1].credit = '22'
        self.stable.save_edits()
        # An unassigned split is created for 20
        self.tpanel.save()
    
    def test_balance_first_split(self):
        """Changing the amount of the first split so it balances the second will remove the
        unassigned split.
        """
        self.tpanel.load()
        self.stable[0].debit = '22'
        self.stable.save_edits()
        # An unassigned split is created for 20
        self.tpanel.save()
        self.assertEqual(len(self.stable), 2)
    

class ThreeWaySplitAllReconciledPlusOneSimpleEntryReconciled(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('first')
        self.add_account('second')
        self.add_account('third')
        self.mainwindow.select_transaction_table()
        self.ttable.add()
        self.ttable.edited.description = 'foo'
        self.tpanel.load()
        self.stable[0].account = 'first'
        self.stable[0].credit = '42'
        self.stable.save_edits()
        self.stable.select([1])
        self.stable[1].account = 'second'
        self.stable[1].debit = '20'
        self.stable.save_edits()
        self.stable.select([2])
        self.stable[2].account = 'third'
        self.stable[2].debit = '22'
        self.stable.save_edits()
        self.tpanel.save()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.add_entry(description='bar')
        self.document.toggle_reconciliation_mode()
        self.etable[0].toggle_reconciled()
        self.etable[1].toggle_reconciled()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.etable[0].toggle_reconciled()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2]
        self.bsheet.show_selected_account()
        self.etable[0].toggle_reconciled()
        self.document.toggle_reconciliation_mode() # commit
        self.tpanel.load()
        self.clear_gui_calls()
    
    def test_change_memo(self):
        """Changing the memo of a split doesn't affect reconciliation"""
        self.stable[0].memo = 'foobar'
        self.stable.save_edits()
        self.tpanel.save()
        self.assertTrue(self.etable[0].reconciled)
        self.check_gui_calls(self.document_gui) # no confirmation
    
    def test_change_first_split_amount(self):
        """Changing the amount of a split only unreconcile this split (and the splits following it
        in the same account, of course)
        """
        self.stable[0].credit = '43'
        self.stable.save_edits()
        self.tpanel.save()
        self.assertTrue(self.etable[0].reconciled) # 3rd split untouched
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertTrue(self.etable[0].reconciled) # 2nd split untouched
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertFalse(self.etable[0].reconciled) # 1st split unreconciled
        self.assertFalse(self.etable[1].reconciled) # as well as the one following it.
        # Verify that the correct confirmation has taken place
        self.check_gui_calls(self.document_gui, confirm_unreconciliation=1)
        self.assertEqual(self.document_gui.last_affected_split_count, 2)
        # changing a split refreshes the mct button
        self.check_gui_calls_partial(self.tpanel_gui, refresh_mct_button=1)
    
    def test_change_first_split_account(self):
        """Changing the account of a split only unreconcile this split (and the splits following it
        in the same account, of course)
        """
        self.stable[0].account = 'zzz' # the new asset will be created last
        self.stable.save_edits()
        self.tpanel.save()
        self.assertTrue(self.etable[0].reconciled) # 3rd split untouched
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertTrue(self.etable[0].reconciled) # 2nd split untouched
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertFalse(self.etable[0].reconciled) # split following the split has been unreconciled
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[3] # zzz
        self.bsheet.show_selected_account()
        self.assertFalse(self.etable[0].reconciled) # 1st split unreconciled
    
    def test_delete_split(self):
        """Deleting a split unreconciles every split following it"""
        self.stable.delete() # the first split
        self.tpanel.save()
        self.assertTrue(self.etable[0].reconciled) # 3rd split untouched
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertTrue(self.etable[0].reconciled) # 2nd split untouched
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertFalse(self.etable[0].reconciled) # split following the split has been unreconciled
        # deleting a split refreshes the mct button
        self.check_gui_calls_partial(self.tpanel_gui, refresh_mct_button=1)
    
