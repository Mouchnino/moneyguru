# Created By: Virgil Dupras
# Created On: 2008-07-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.currency import CAD, EUR

from ..base import TestCase, TestSaveLoadMixin, TestQIFExportImportMixin

class OneEntry(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('first', currency=CAD)
        self.add_entry(transfer='second', increase='42')
    
    def test_add_gui_calls(self):
        # refresh() and start_editing() are called after a add()
        self.tpanel.load()
        self.clear_gui_calls()
        self.stable.add()
        self.check_gui_calls(self.stable_gui, ['refresh', 'start_editing', 'stop_editing'])
    
    def test_cancel_edits(self):
        # cancel_edits() sets edited to None and makes the right gui calls
        self.tpanel.load()
        self.stable[0].account = 'foo'
        self.clear_gui_calls()
        self.stable.cancel_edits()
        assert self.stable.edited is None
        self.check_gui_calls(self.stable_gui, ['refresh', 'stop_editing'])
    
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
        self.add_account_legacy('first', EUR)
        self.add_account_legacy('second', EUR)
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
        self.add_account_legacy('first')
        self.add_account_legacy('second')
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
        self.add_account_legacy('first')
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
    
