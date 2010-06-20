# Created By: Virgil Dupras
# Created On: 2008-05-29
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date
import os.path as op

from nose.tools import eq_

from hsutil.currency import PLN, CAD

from .base import ApplicationGUI, TestCase as TestCaseBase, TestQIFExportImportMixin, TestApp
from ..app import Application
from ..exception import FileFormatError
from ..model.date import MonthRange, YearRange

def importall(app, filename):
    app.doc.parse_file_for_import(filename)
    while app.iwin.panes:
        app.iwin.import_selected_pane()

class TestCase(TestCaseBase):
    def importall(self, filename):
        importall(self.ta, filename)
    

class Pristine(TestCase, TestQIFExportImportMixin):
    # TestQIFExportImportMixin: Make sure nothing is wrong when the file is empty
    def setUp(self):
        self.create_instances()
    
    def test_import_empty(self):
        # Trying to import an empty file results in a FileFormatError
        filename = self.filepath('zerofile')
        self.assertRaises(FileFormatError, self.document.parse_file_for_import, filename)
    
    def test_import_inexistant(self):
        """Raises a FileFormatError when importing a file that doesn't exist"""
        filename = op.join(self.tmpdir(), 'does_not_exist.qif')
        self.assertRaises(FileFormatError, self.document.parse_file_for_import, filename)
    
    def test_import_invalid_qif(self):
        """Raise a FileFormatError if the file does not have the right format (for now, a valid 
        file is a file that starts with a '!Account' line)
        """
        filename = self.filepath('qif', 'invalid.qif')
        self.assertRaises(FileFormatError, self.document.parse_file_for_import, filename)
    
    def test_import_moneyguru_file(self):
        # Importing a moneyguru file works.
        self.importall(self.filepath('moneyguru', 'simple.moneyguru'))
        # 2 assets, 1 expense
        self.assertEqual(self.bsheet.assets.children_count, 4)
        self.mainwindow.select_income_statement()
        self.assertEqual(self.istatement.expenses.children_count, 3)
        # No need to test further, we already test moneyguru file loading, which is basically the 
        # same thing.
    

class QIFImport(TestCase):
    """One account named 'Account 1' and then an parse_file_for_import() call for the 'checkbook.qif' test file
    """
    def setUp(self):
        self.app = Application(ApplicationGUI(), default_currency=PLN)
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.add_account_legacy('Account 1')
        self.add_account_legacy('Account 1 1')
        self.importall(self.filepath('qif', 'checkbook.qif'))
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
    
    def test_asset_names(self):
        """All accounts are added despite name collisions. Name collision for 'Account 1' is 
        resolved by appending ' 1', and that collision thereafter is resolved by appending ' 2'
        instead.
        """
        expected = ['Account 1', 'Account 1 1', 'Account 1 2', 'Account 2', 'Interest', 'Salary', 'Cash', 'Utilities']
        actual = self.account_names()
        self.assertEqual(actual, expected) 
    
    def test_default_account_currency(self):
        """This QIF has no currency. Therefore, the default currency should be used for accounts"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2]
        self.apanel.load()
        self.assertEqual(self.apanel.currency, PLN)
    
    def test_default_entry_currency(self):
        """Entries default to their account's currency. Therefore, changing the account currency
        after the import should cause the entries to be cooked as amount with currency
        """
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2]
        self.apanel.load()
        self.apanel.currency = CAD
        self.apanel.save()
        self.bsheet.show_selected_account()
        self.assertEqual(self.etable[0].increase, '42.32')
    

class OFXImport(TestCase):
    """A pristine app importing an OFX file"""
    def setUp(self):
        self.create_instances()
        self.importall(self.filepath('ofx', 'desjardins.ofx'))
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()

    def test_account_names(self):
        """Checks that the import was done
        
        This test only checks the account names.  More precise tests are in
        ofx_test.py"""
        self.assertEqual(self.account_names(), ['815-30219-11111-EOP', '815-30219-12345-EOP'])
    
    def test_add_referenceless_entries_to_reference_account(self):
        """It's possible to add more than one referenceless entries to a referenced account"""
        # Previously, TransactionList considered 2 transactions with a None reference as conflictual
        # We start with one entry
        self.add_entry()
        self.add_entry()
        self.assertEqual(self.ta.etable_count(), 3)
    
    def test_modified(self):
        """The app is marked as modified."""
        self.assert_(self.document.is_dirty())
    

class DoubleOFXImport(TestCase):
    """Importing two OFX files that have accounts in common. The edition of an entry that is in both
    files (the same reference number) occurs between the two imports."""
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.importall(self.filepath('ofx', 'desjardins.ofx'))
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        # The entry that is in both files in the "retrait" one, which we'll edit
        self.etable.select([2]) # Previous Balance + Depot, then there is the Retrait one
        row = self.etable.selected_row
        row.date = '2/2/2008' # One day after
        row.description = 'Cash pour super party chez untel'
        row.transfer = 'Cash'
        self.etable.save_edits()
        self.importall(self.filepath('ofx', 'desjardins2.ofx'))

    def test_account_names(self):
        """Non-empty accounts from both files are imported"""
        expected = ['815-30219-11111-EOP', '815-30219-12345-EOP', 'Cash']
        self.assertEqual(self.account_names(), expected)
    
    def test_double_import_attributes(self):
        """When importing an entry that is already in moneyguru, only overwrite the date and the amount"""
        # The re-imported entry in the "retrait" one, on the 4th row
        self.assertEqual(self.etable[2].date, '01/02/2008') # overwritten
        self.assertEqual(self.etable[2].decrease, '2600.00') # overwritten
        self.assertEqual(self.etable[2].description, 'Cash pour super party chez untel') # kept
        self.assertEqual(self.etable[2].transfer, 'Cash') # kept
    

class DoubleOFXImportAcrossSessions(TestCase):
    """Importing two OFX files across sessions.
    
    Correctly remember the OFX IDs even if the account name changes."""
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.importall(self.filepath('ofx', 'desjardins.ofx'))
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0] # 815-30219-11111-EOP
        self.bsheet.selected.name = 'Desjardins EOP'
        self.bsheet.save_edits()
        filename = op.join(self.tmpdir(), 'foo.xml')
        self.document.save_to_xml(filename)
        self.document.load_from_xml(filename)
        self.importall(self.filepath('ofx', 'desjardins2.ofx'))

    def test_account_names(self):
        """Non-empty accounts from both files are imported"""
        self.assertEqual(self.account_names(), ['815-30219-12345-EOP', 'Desjardins EOP'])
    

class AnotherDoubleOFXImport(TestCase):
    """Importing two OFX files that contain transactions with the same FIT ID, but a different account ID."""
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.importall(self.filepath('ofx', 'desjardins2.ofx'))
        self.importall(self.filepath('ofx', 'desjardins3.ofx'))

    def test_account_names(self):
        """All non-empty accounts have been imported."""
        self.assertEqual(self.account_names(), ['815-30219-11111-EOP', 'NEW_ACCOUNT'])

    def test_entries_counts(self):
        """All accounts have the appropriate number of entries."""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 2)
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 1)
    

class TripleOFXImportAcrossSessions(TestCase):
    """Import the same OFX 3 times"""
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.importall(self.filepath('ofx', 'desjardins.ofx'))
        self.importall(self.filepath('ofx', 'desjardins.ofx'))
        filename = op.join(self.tmpdir(), 'foo.xml')
        self.document.save_to_xml(filename)
        self.document.load_from_xml(filename)
        self.importall(self.filepath('ofx', 'desjardins.ofx'))
    
    def test_entry_count(self):
        """The number of entries is the same as if the import was made once"""
        # Previously, the transaction reference would be lost in a transaction conflict resolution
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(self.ta.etable_count(), 3)
    

#--- Double OFX import with split in the middle
# Import an OFX, change one entry into a split, and then re-import.
def app_double_ofx_import_with_split_in_the_middle():
    app = TestApp()
    app.doc.date_range = MonthRange(date(2008, 2, 1))
    importall(app, TestCase.filepath('ofx', 'desjardins.ofx'))
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.show_selected_account()
    app.etable.select([2]) #retrait
    row = app.etable.selected_row
    row.transfer = 'account1'
    app.etable.save_edits()
    app.tpanel.load()
    app.stable.add()
    app.stable[2].credit = '1'
    app.stable.save_edits()
    app.tpanel.save()
    importall(app, TestCase.filepath('ofx', 'desjardins.ofx'))
    return app

def test_split_wasnt_touched():
    # When matching transaction and encountering a case where the old transaction was changed
    # into a split, bail out and don't touch the amounts.
    app = app_double_ofx_import_with_split_in_the_middle()
    eq_(len(app.stable), 4)
    eq_(app.stable[2].credit, '1.00')

class ImportAccountInGroup(TestCase):
    def setUp(self):
        self.create_instances()
        self.importall(self.filepath('moneyguru', 'account_in_group.moneyguru'))
        self.mainwindow.select_balance_sheet()
    
    def test_account_was_imported(self):
        # The fact that the account was in a group didn't prevent it from being imported.
        eq_(self.bsheet.assets[0].name, 'Some Asset')
    

class TwoEntriesInRangeSaveThenLoad(TestCase):
    """Two entries having the same date, in range. The app saves to a file then loads the same file.
    """
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_account()
        self.mainwindow.show_account()
        self.add_entry('1/10/2007', description='first')
        self.add_entry('1/10/2007', description='second')
        self.filename = op.join(self.tmpdir(), 'foo.xml')
        self.document.save_to_xml(self.filename)
        self.document.load_from_xml(self.filename)
        # have been kicked back to bsheet. Select the account again
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.etable.select([0])
    
    def test_editing_an_entry_doesnt_change_the_order(self):
        """Editing the first entry doesn't change its position"""
        row = self.etable.selected_row
        row.increase = '42'
        self.etable.save_edits()
        self.assertEqual(self.etable[0].description, 'first')
    

class TransferBetweenTwoReferencedAccounts(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.importall(self.filepath('moneyguru', 'with_references1.moneyguru')) # Contains Account 1
        self.add_account_legacy('Account 4') # Add it as an asset
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.etable.select([0])
        row = self.etable[0]
        row.transfer = 'Account 4'
        self.etable.save_edits()
        self.document.parse_file_for_import(self.filepath('moneyguru', 'with_references3.moneyguru')) # Contains Account 4
        # The entry from Account 4 doesn't match yet because they don't have the same reference, but
        # it will be fixed after the import
        self.iwin.selected_target_account_index = 3 # Account 4
        self.itable.bind(0, 1)
        self.iwin.import_selected_pane()
        # The 2 entries are now linked in the same txn.
    
    def test_first_side_matches(self):
        """When importing entries from Account 1, these entries are matched correctly"""
        self.document.parse_file_for_import(self.filepath('moneyguru', 'with_references1.moneyguru'))
        # All entries should be matched
        self.assertEqual(len(self.itable), 2) # 2 entries means they all match
    
    def test_second_side_matches(self):
        """When importing entries from Account 3, these entries are matched correctly"""
        self.document.parse_file_for_import(self.filepath('moneyguru', 'with_references3.moneyguru'))
        # target account should be correct, and all entries should be matched
        self.assertEqual(self.iwin.selected_target_account_index, 3) # Account 4
        self.assertEqual(len(self.itable), 1) # 1 entry means they all match
    

class ImportFileWithMultipleTransferReferences(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.importall(self.filepath('moneyguru', 'multiple_transfer_references.moneyguru'))
    
    def test_account_names_are_correct(self):
        # the account names for the transfers are correctly imported. Previously, new_name() was
        # recursively called on them for each occurence in the split.
        self.mainwindow.select_income_statement()
        self.assertEqual(self.istatement.income[0].name, 'income')
        self.assertEqual(self.istatement.expenses[0].name, 'expense')
    
