# Created By: Virgil Dupras
# Created On: 2008-08-08
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from ..base import TestCase
from ...model.date import YearRange

class ImportCheckbookQIF(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.itable.disconnect() # The cocoa side does some disconnect/connect stuff. We have to refresh the table on connect()
        self.document.parse_file_for_import(self.filepath('qif', 'checkbook.qif'))
        self.itable.connect()
        self.clear_gui_calls()
    
    def test_delete(self):
        # calling delete() (the std API for all tables), set "will_import" to False
        self.itable.select([3, 4])
        self.itable.delete()
        self.assertFalse(self.itable[3].will_import)
        self.assertFalse(self.itable[4].will_import)
    
    def test_is_two_sided(self):
        # There is no target account, we only have one side
        assert not self.itable.is_two_sided
    
    def test_rows(self):
        """The shown rows are the imported txns from the first account. The target account is a new 
        file, so we don't have any 'left side' entries.
        """
        self.assertEqual(len(self.itable), 5)
        self.assertEqual(self.itable[0].date, '')
        self.assertEqual(self.itable[0].description, '')
        self.assertEqual(self.itable[0].amount, '')
        self.assertEqual(self.itable[0].date_import, '01/01/2007')
        self.assertEqual(self.itable[0].description_import, 'Starting Balance')
        self.assertEqual(self.itable[0].amount_import, '42.32')
        self.assertEqual(self.itable[0].bound, False)
        self.assertTrue(self.itable[0].will_import)
        self.assertTrue(self.itable[0].can_edit_will_import)
        self.assertEqual(self.itable[1].transfer_import, 'Salary') # not all entries have a transfer
        self.assertEqual(self.itable[3].checkno_import, '36') # not all entries have a checkno
        self.assertEqual(self.itable[4].date, '')
        self.assertEqual(self.itable[4].description, '')
        self.assertEqual(self.itable[4].amount, '')
        self.assertEqual(self.itable[4].date_import, '04/02/2007')
        self.assertEqual(self.itable[4].description_import, 'Transfer')
        self.assertEqual(self.itable[4].payee_import, 'Account 2')
        self.assertEqual(self.itable[4].amount_import, '80.00')
        self.assertEqual(self.itable[4].bound, False)
        self.assertTrue(self.itable[4].will_import)
        self.assertTrue(self.itable[4].can_edit_will_import)
    
    def test_select_account(self):
        """Selecting another accounts updates the table"""
        self.iwin.selected_pane_index = 1
        self.check_gui_calls(self.itable_gui, ['refresh'])
        self.assertEqual(len(self.itable), 3)
        self.assertEqual(self.itable[1].date, '')
        self.assertEqual(self.itable[1].description, '')
        self.assertEqual(self.itable[1].amount, '')
        self.assertEqual(self.itable[1].date_import, '05/01/2007')
        self.assertEqual(self.itable[1].description_import, 'Interest')
        self.assertEqual(self.itable[1].amount_import, '8.92')
        self.assertEqual(self.itable[1].bound, False)
    
    def test_will_import_value_is_kept(self):
        # When changing the selected pane around, the will_import values are kept
        self.itable[4].will_import = False
        self.iwin.selected_pane_index = 1
        self.iwin.selected_pane_index = 0
        self.assertFalse(self.itable[4].will_import)
    

class ImportCheckbookQIFWithSomeExistingTransactions(TestCase):
    # The end result of this setup is that only the 2nd existing entry end up in the table 
    # (the first is reconciled)
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('foo')
        self.add_entry(date='01/01/2007', description='first entry', increase='1')
        self.document.toggle_reconciliation_mode()
        self.etable.toggle_reconciled()
        self.document.toggle_reconciliation_mode() # commit
        self.add_entry(date='02/01/2007', description='second entry', increase='2')
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.document.parse_file_for_import(self.filepath('qif', 'checkbook.qif'))
        self.clear_gui_calls()
        self.iwin.selected_target_account_index = 1 # foo
        self.check_gui_calls(self.itable_gui, ['refresh'])
    
    def test_bind(self):
        """Binding 2 entries removes the imported entry and places it at the existing's row"""
        self.itable.bind(2, 4) # now, we shouldn't put the 3rd entry after the 5th in the sort order
        self.assertEqual(len(self.itable), 5)
        self.assertEqual(self.itable[2].date, '02/01/2007')
        self.assertEqual(self.itable[2].description, 'second entry')
        self.assertEqual(self.itable[2].amount, '2.00')
        self.assertEqual(self.itable[2].date_import, '02/01/2007')
        self.assertEqual(self.itable[2].description_import, 'Power Bill')
        self.assertEqual(self.itable[2].amount_import, '-57.12')
        self.check_gui_calls(self.itable_gui, ['refresh'])
    
    def test_can_bind(self):
        """can_bind() returns True only when trying to bind 2 rows with opposite missing elements"""
        self.assertTrue(self.itable.can_bind(2, 3)) # existing --> import
        self.assertTrue(self.itable.can_bind(3, 2)) # import --> existing
        self.assertFalse(self.itable.can_bind(1, 3)) # import --> import
    
    def test_is_two_sided(self):
        # We have a target account, and some transactions can be bound in it. The table is 
        # two-sided.
        assert self.itable.is_two_sided
    
    def test_rows(self):
        """Imported rows are mixed with existing rows"""
        self.assertEqual(len(self.itable), 6) # only unreconciled entries
        # The 1st and 2nd imported entries are on 01/01 and the 3rd is on 02/01. Existing entries
        # come before in the sort order, so the existing entry is placed 3rd.
        self.assertEqual(self.itable[2].date, '02/01/2007')
        self.assertEqual(self.itable[2].description, 'second entry')
        self.assertEqual(self.itable[2].amount, '2.00')
        self.assertEqual(self.itable[2].date_import, '')
        self.assertEqual(self.itable[2].description_import, '')
        self.assertEqual(self.itable[2].amount_import, '')
        # will_import is False and can't be set
        self.assertFalse(self.itable[2].can_edit_will_import)
        self.assertFalse(self.itable[2].will_import)
        self.itable[2].will_import = True
        self.assertFalse(self.itable[2].will_import)
    

class ImportWithEmptyTargetAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('foo')
        self.document.parse_file_for_import(self.filepath('qif', 'checkbook.qif'))
        self.iwin.selected_target_account_index = 1 # foo
    
    def test_is_two_sided(self):
        # We have a target account, but no bindable txns to show. The table is one-sided.
        assert not self.itable.is_two_sided
    

class LoadThenImportWithReference(TestCase):
    # with_reference1 and 2 have references that overlap. This is supposed to cause matching in the
    # import dialog.
    def setUp(self):
        self.create_instances()
        self.document.load_from_xml(self.filepath('moneyguru', 'with_references1.moneyguru'))
        self.document.date_range = YearRange(date(2008, 1, 1))
        self.document.parse_file_for_import(self.filepath('moneyguru', 'with_references2.moneyguru'))
        self.clear_gui_calls()
    
    def test_can_bind(self):
        """can_bind() returns False when a bound entry is involved"""
        self.assertFalse(self.itable.can_bind(0, 1)) # existing --> bound
        self.assertFalse(self.itable.can_bind(1, 0)) # bound --> existing
        self.assertFalse(self.itable.can_bind(1, 2)) # bound --> imported
        self.assertFalse(self.itable.can_bind(2, 1)) # imported --> bound
    
    def test_reconciled_entry_match(self):
        # When an entry with reference is reconciled, the match is added, but will_import defaults
        # to False
        self.assertFalse(self.itable[1].will_import)
    
    def test_rows(self):
        """There are 4 txns in both of the files. However, 2 of them have the same reference, so
        we end up with 3 entries."""
        self.assertEqual(len(self.itable), 3)
        self.assertEqual(self.itable[0].date, '15/02/2008')
        self.assertEqual(self.itable[0].description, 'txn1')
        self.assertEqual(self.itable[0].amount, 'CAD 42.00')
        self.assertEqual(self.itable[0].date_import, '')
        self.assertEqual(self.itable[0].description_import, '')
        self.assertEqual(self.itable[0].amount_import, '')
        self.assertFalse(self.itable[0].bound)
        self.assertEqual(self.itable[1].date, '16/02/2008')
        self.assertEqual(self.itable[1].description, 'txn2')
        self.assertEqual(self.itable[1].amount, 'CAD -14.00')
        self.assertEqual(self.itable[1].date_import, '16/02/2008')
        self.assertEqual(self.itable[1].description_import, 'txn2')
        self.assertEqual(self.itable[1].amount_import, 'CAD -14.00')
        self.assertTrue(self.itable[1].bound)
        self.assertEqual(self.itable[2].date, '')
        self.assertEqual(self.itable[2].description, '')
        self.assertEqual(self.itable[2].amount, '')
        self.assertEqual(self.itable[2].date_import, '20/02/2008')
        self.assertEqual(self.itable[2].description_import, 'txn5')
        self.assertEqual(self.itable[2].amount_import, 'CAD 50.00')
        self.assertFalse(self.itable[2].bound)
    
    def test_unbind(self):
        """unbind_selected() unbinds the selected match"""
        self.itable.unbind(1)
        self.assertEqual(len(self.itable), 4)
        self.assertEqual(self.itable[1].date, '16/02/2008')
        self.assertEqual(self.itable[1].description, 'txn2')
        self.assertEqual(self.itable[1].amount, 'CAD -14.00')
        self.assertEqual(self.itable[1].date_import, '')
        self.assertEqual(self.itable[1].description_import, '')
        self.assertEqual(self.itable[1].amount_import, '')
        self.assertEqual(self.itable[2].date, '')
        self.assertEqual(self.itable[2].description, '')
        self.assertEqual(self.itable[2].amount, '')
        self.assertEqual(self.itable[2].date_import, '16/02/2008')
        self.assertEqual(self.itable[2].description_import, 'txn2')
        self.assertEqual(self.itable[2].amount_import, 'CAD -14.00')
        self.check_gui_calls(self.itable_gui, ['refresh'])
    
    def test_unbind_unbound(self):
        """Trying to unbind an unbound match has no effect"""
        self.itable.unbind(0)
        self.assertEqual(len(self.itable), 3)
        self.itable.unbind(2)
        self.assertEqual(len(self.itable), 3)
    
