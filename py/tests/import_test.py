# Created By: Virgil Dupras
# Created On: 2008-05-29
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date
import os.path as op

from hsutil.currency import PLN, CAD

from .base import ApplicationGUI, TestCase, TestSaveLoadMixin, TestQIFExportImportMixin
from ..app import Application
from ..exception import FileFormatError
from ..model.date import MonthRange, YearRange

class TestCase(TestCase):
    def importall(self, filename):
        self.document.parse_file_for_import(filename)
        while self.iwin.panes:
            self.iwin.import_selected_pane()
    

class Pristine(TestCase):
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
        """Importing a moneyguru file works"""
        self.importall(self.filepath('xml', 'moneyguru.xml'))
        # 2 assets, 1 expense
        self.assertEqual(self.bsheet.assets.children_count, 4)
        self.mainwindow.select_income_statement()
        self.assertEqual(self.istatement.expenses.children_count, 3)
        # No need to test further, we already test moneyguru file loading, which is basically the 
        # same thing.
    
    def test_import_qif_with_bad_amount(self):
        # When moneyGuru can't parse something, it should not continue to try to import the file. If
        # it ignores entries it can't parse, the user has no use for the rest of the entries, the
        # integrity of the file has been breached. log a warning with the error, and raise a
        # FileFormatError telling the user to contact support.
        # (The file also has a bad date)
        filename = op.join(self.filepath('qif', 'bad_amount.qif'))
        self.assertRaises(FileFormatError, self.document.parse_file_for_import, filename)
        self.logged.seek(0)
        self.assertTrue(self.logged.read()) # something (a warning) was logged
    

class LoadPayeeDescription(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 3, 1))
        self.document.load_from_xml(self.filepath('moneyguru', 'payee_description.moneyguru'))
        self.mainwindow.select_transaction_table()
    
    def test_attributes(self):
        """description and payee attributes load correctly, even when some of them are missing"""
        self.assertEqual(self.ttable[0].description, 'description')
        self.assertEqual(self.ttable[0].payee, 'payee')
        self.assertEqual(self.ttable[1].description, 'description')
        self.assertEqual(self.ttable[1].payee, '')
        self.assertEqual(self.ttable[2].description, '')
        self.assertEqual(self.ttable[2].payee, 'payee')
    

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
        self.assertEqual(len(self.etable), 3)
    
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
        self.assertEqual(len(self.etable), 2)
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 1)
    

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
        self.assertEqual(len(self.etable), 3)
    

class DoubleOFXImportWithASplitInTheMiddle(TestCase):
    """Import an OFX, change one entry into a split, and then re-import"""
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.importall(self.filepath('ofx', 'desjardins.ofx'))
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.etable.select([2]) #retrait
        row = self.etable.selected_row
        row.transfer = 'account1'
        self.etable.save_edits()
        self.tpanel.load()
        row = self.stable.selected_row
        row.credit = '42'
        self.stable.save_edits() # This will balance out the rest into Imbalance
        self.tpanel.save()
        self.importall(self.filepath('ofx', 'desjardins.ofx'))
    
    def test_split_wasnt_touched(self):
        """When matching transaction and encountering a case where the old transaction was changed
        into a split, bail out and don't touch the amounts"""
        self.assertEqual(len(self.stable), 3)
        self.assertEqual(self.stable[0].credit, '42.00')
    

class LoadFile(TestCase):
    """Loads 'moneyguru.xml', a file with 2 accounts and 2 entries in each. Select the first entry"""
    def setUp(self):
        self.mock_today(2008, 2, 20) # so that the entries are shown
        self.create_instances()
        self.add_account_legacy() # This is to set the modified flag to true so we can make sure it has been put back to false
        self.document.load_from_xml(self.filepath('xml', 'moneyguru.xml'))
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
    
    def test_add_entry(self):
        """Adding an entry sets the modified flag"""
        self.add_entry()
        self.assertTrue(self.document.is_dirty())
    
    def test_change_account_currency(self):
        """Changing an account currency sets the modified flag"""
        self.apanel.load()
        self.apanel.currency = PLN
        self.apanel.save()
        self.assertTrue(self.document.is_dirty())
    
    def test_delete_account(self):
        """Removing an account sets the modified flag"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.delete()
        self.arpanel.ok() # continue deletion
        self.assertTrue(self.document.is_dirty())
    
    def test_delete_entries(self):
        """Deleting an entry sets the modified flag"""
        self.etable.delete()
        self.assertTrue(self.document.is_dirty())
    
    def test_delete_transactions(self):
        """Deleting a transaction sets the modified flag"""
        self.mainwindow.select_transaction_table()
        self.ttable.select([0]) # will be automatic at some point
        self.ttable.delete()
        self.assertTrue(self.document.is_dirty())
    
    def test_change_split(self):
        """Changing a split in the tpanel doesn't make the app dirty unless it's saved"""
        self.etable.select([1])
        self.tpanel.load()
        self.stable.delete()
        self.assertFalse(self.document.is_dirty())

    def test_edit_entry(self):
        # When about to save the document, if an entry is in edition, the document saves the edits first
        row = self.etable.selected_row
        row.description = 'foo'
        self.document.stop_edition()
        self.assertTrue(self.document.is_dirty()) # We started editing, the flag is on
        self.etable.save_edits()
        self.assertTrue(self.document.is_dirty())
    
    def test_initial_selection(self):
        """Right after load, the last entry is selected"""
        self.assertEqual(self.etable.selected_indexes, [1])
    
    def test_not_modified(self):
        """Loading a file resets the modified flag"""
        self.assertFalse(self.document.is_dirty())
    
    def test_rename_account(self):
        """Renaming an account sets the modified flag"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.selected.name = 'some other name'
        self.bsheet.save_edits()
        self.assertTrue(self.document.is_dirty())
    
    def test_save_edit_without_edit(self):
        """Calling save_entry() without having made changes doesn't set the modified flag"""
        self.etable.save_edits()
        self.assertFalse(self.document.is_dirty())
    

class LoadMultiCurrency(TestCase):
    """Loads 'moneyguru2.xml', a file with 2 accounts and a multi-currency transaction."""
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.document.load_from_xml(self.filepath('xml', 'moneyguru2.xml'))
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.etable.select([0])

    def test_amounts(self):
        """The amounts are correctly loaded and the logical imbalance has been dealt with"""
        self.assertEqual(self.etable[0].increase, '200.00')
        self.tpanel.load()
        self.assertEqual(len(self.stable), 4)
        self.assertEqual(self.stable[0].debit, '200.00')
        self.assertEqual(self.stable[1].debit, 'PLN 123.45')
        expected = set(['200.00', 'PLN 123.45'])
        self.assertTrue(self.stable[2].credit in expected)
        self.assertTrue(self.stable[3].credit in expected)
    

class TwoEntriesInRangeSaveThenLoad(TestCase):
    """Two entries having the same date, in range. The app saves to a file then loads the same file.
    """
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2007, 10, 1))
        self.add_account_legacy()
        self.add_entry('1/10/2007', description='first')
        self.add_entry('1/10/2007', description='second')
        self.filename = op.join(self.tmpdir(), 'foo.xml')
        self.document.save_to_xml(self.filename)
        self.document.load_from_xml(self.filename)
        # have been kicked back to bsheet. Select the account again
        self.bsheet.show_selected_account()
        self.etable.select([0])
    
    def test_editing_an_entry_doesnt_change_the_order(self):
        """Editing the first entry doesn't change its position"""
        row = self.etable.selected_row
        row.increase = '42'
        self.etable.save_edits()
        self.assertEqual(self.etable[0].description, 'first')
    
class TwoAccountTwoEntriesInEachWithNonAsciiStrings(TestCase, TestSaveLoadMixin, TestQIFExportImportMixin):
    """Two accounts, two entries in each. Descriptions, categories and account names contain
    non-latin characters (a polish 'l'). currencies are set to non-default values. first account
    is selected.
    
    Mixin with TestSaveLoadMixin to make sure all those values come back up alright
    Same for TestQIFExportImportMixin
    """
    def setUp(self):
        self.create_instances()
        self.add_account_legacy(u'first_account\u0142', currency=PLN)
        self.add_entry('3/10/2007', u'first\u0142', transfer='other account', increase='1 usd')
        self.add_entry('4/10/2007', u'second\u0142', increase='2 usd') # Imbalance
        self.add_account_legacy(u'second_account\u0142', currency=CAD)
        self.add_entry('5/10/2007', u'third\u0142', transfer=u'first_account\u0142', decrease='1 usd')
        self.add_entry('6/10/2007', u'fourth\u0142', transfer='yet another account', decrease='2 usd')
    

class LoadTwice(TestCase, TestSaveLoadMixin):
    """Loads 'moneyguru.xml' twice. Mixed in with TestSaveLoadMixin to make sure that loading 
    completely wipes out previous transactions (If it doesn't, old transaction end up in the save 
    file, making them being re-added to the account in the next load)."""
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.document.load_from_xml(self.filepath('xml', 'moneyguru.xml'))
        self.document.load_from_xml(self.filepath('xml', 'moneyguru.xml'))
    

class InvalidAccountType(TestCase):
    """Loads 'moneyguru_invalid_account_type.xml' which contains a single account with an invalid type."""
    def setUp(self):
        self.create_instances()
        self.document.load_from_xml(self.filepath('xml', 'moneyguru_invalid_account_type.xml'))
    
    def test_account_type(self):
        """The account with the invalid type is imported as an asset account."""
        self.assertEqual(self.bsheet.assets.children_count, 3)
    

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
    

class LoadImportWithTransactionInTheFuture(TestCase):
    def setUp(self):
        self.mock_today(2008, 2, 1) # before any txn date
        self.create_instances()
        self.document.parse_file_for_import(unicode(self.filepath('xml/moneyguru.xml')))
    
    def test_transactions_show_up(self):
        # even when there are txns in the future, they show up in the import panel
        self.assertEqual(len(self.itable), 2)
    
