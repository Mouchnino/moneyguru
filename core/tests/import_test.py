# Created By: Virgil Dupras
# Created On: 2008-05-29
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from pytest import raises
from hscommon.testutil import eq_
from hscommon import io as hsio
from hscommon.currency import PLN, CAD

from .base import ApplicationGUI, TestApp, with_app, testdata
from ..app import Application
from ..exception import FileFormatError
from ..model.date import MonthRange, YearRange

def importall(app, filename):
    app.doc.parse_file_for_import(filename)
    while app.iwin.panes:
        app.iwin.import_selected_pane()

#--- Pristine
@with_app(TestApp)
def test_qif_export_import(app):
    # Make sure nothing is wrong when the file is empty
    app.do_test_qif_export_import()

@with_app(TestApp)
def test_import_empty(app):
    # Trying to import an empty file results in a FileFormatError
    filename = testdata.filepath('zerofile')
    with raises(FileFormatError):
        app.doc.parse_file_for_import(filename)

@with_app(TestApp)
def test_import_inexistant(app, tmpdir):
    # Raises a FileFormatError when importing a file that doesn't exist.
    filename = str(tmpdir.join('does_not_exist.qif'))
    with raises(FileFormatError):
        app.doc.parse_file_for_import(filename)

@with_app(TestApp)
def test_import_invalid_qif(app):
    # Raise a FileFormatError if the file does not have the right format (for now, a valid 
    # file is a file that starts with a '!Account' line)
    filename = testdata.filepath('qif', 'invalid.qif')
    with raises(FileFormatError):
        app.doc.parse_file_for_import(filename)

@with_app(TestApp)
def test_import_moneyguru_file(app):
    # Importing a moneyguru file works.
    importall(app, testdata.filepath('moneyguru', 'simple.moneyguru'))
    app.show_nwview()
    # 2 assets, 1 expense
    eq_(app.bsheet.assets.children_count, 4)
    app.show_pview()
    eq_(app.istatement.expenses.children_count, 3)
    # No need to test further, we already test moneyguru file loading, which is basically the 
    # same thing.

@with_app(TestApp)
def test_account_only_qif_is_invalid(app):
    # A QIF file with only accounts is correctly seen as invalid. Previously, such a file, if an
    # account had a valid "D" line, would go through the parsing/loading phase and pop up an empty
    # import window, which would ultimately cause a crash.
    with raises(FileFormatError):
        # Whether the FileFormatError is raised during parsing or loading doesn't matter. Loading
        # is a more appropriate error though because the file is a valid QIF, it just doesn't have
        # any txns in it.
        importall(app, testdata.filepath('qif', 'only_accounts.qif'))

#---
def app_qif_import():
    # One account named 'Account 1' and then an parse_file_for_import() call for the 'checkbook.qif' test file.
    app = TestApp(app=Application(ApplicationGUI(), default_currency=PLN))
    app.doc.date_range = YearRange(date(2007, 1, 1))
    app.add_account('Account 1')
    app.add_account('Account 1 1')
    importall(app, testdata.filepath('qif', 'checkbook.qif'))
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.show_account()
    return app
    
@with_app(app_qif_import)
def test_asset_names_after_qif_import(app):
    # All accounts are added despite name collisions. Name collision for 'Account 1' is 
    # resolved by appending ' 1', and that collision thereafter is resolved by appending ' 2'
    # instead.
    expected = ['Account 1', 'Account 1 1', 'Account 1 2', 'Account 2', 'Interest', 'Salary', 'Cash', 'Utilities']
    actual = app.account_names()
    eq_(actual, expected) 

@with_app(app_qif_import)
def test_default_account_currency_after_qif_import(app):
    # This QIF has no currency. Therefore, the default currency should be used for accounts
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[2]
    app.mainwindow.edit_item()
    eq_(app.apanel.currency, PLN)

@with_app(app_qif_import)
def test_default_entry_currency_after_qif_import(app):
    # Entries default to their account's currency. Therefore, changing the account currency
    # after the import should cause the entries to be cooked as amount with currency
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[2]
    app.mainwindow.edit_item()
    app.apanel.currency = CAD
    app.apanel.save()
    app.show_account()
    eq_(app.etable[0].increase, '42.32')    

@with_app(app_qif_import)
def test_imported_txns_have_mtime(app):
    # Transactions that are created through imports get a mtime
    tview = app.show_tview()
    assert tview.ttable[0].mtime != ''

#---
class TestOFXImport:
    # A pristine app importing an OFX file
    def do_setup(self):
        app = TestApp()
        importall(app, testdata.filepath('ofx', 'desjardins.ofx'))
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        return app
    
    @with_app(do_setup)
    def test_account_names(self, app):
        # Checks that the import was done
        #
        # This test only checks the account names.  More precise tests are in
        # ofx_test.py
        eq_(app.account_names(), ['815-30219-11111-EOP', '815-30219-12345-EOP'])
    
    @with_app(do_setup)
    def test_add_referenceless_entries_to_reference_account(self, app):
        # It's possible to add more than one referenceless entries to a referenced account
        # Previously, TransactionList considered 2 transactions with a None reference as conflictual
        # We start with one entry
        app.add_entry()
        app.add_entry()
        eq_(app.etable_count(), 3)
    
    @with_app(do_setup)
    def test_modified(self, app):
        # The app is marked as modified.
        assert app.doc.is_dirty()
    

class TestDoubleOFXImport:
    # Importing two OFX files that have accounts in common. The edition of an entry that is in both
    # files (the same reference number) occurs between the two imports.
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2008, 2, 1))
        importall(app, testdata.filepath('ofx', 'desjardins.ofx'))
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        # The entry that is in both files in the "retrait" one, which we'll edit
        app.etable.select([2]) # Previous Balance + Depot, then there is the Retrait one
        row = app.etable.selected_row
        row.date = '2/2/2008' # One day after
        row.description = 'Cash pour super party chez untel'
        row.transfer = 'Cash'
        app.etable.save_edits()
        importall(app, testdata.filepath('ofx', 'desjardins2.ofx'))
        return app
    
    @with_app(do_setup)
    def test_account_names(self, app):
        # Non-empty accounts from both files are imported
        expected = ['815-30219-11111-EOP', '815-30219-12345-EOP', 'Cash']
        eq_(app.account_names(), expected)
    
    @with_app(do_setup)
    def test_double_import_attributes(self, app):
        # When importing an entry that is already in moneyguru, only overwrite the date and the amount
        # The re-imported entry in the "retrait" one, on the 4th row
        eq_(app.etable[2].date, '01/02/2008') # overwritten
        eq_(app.etable[2].decrease, '2600.00') # overwritten
        eq_(app.etable[2].description, 'Cash pour super party chez untel') # kept
        eq_(app.etable[2].transfer, 'Cash') # kept
    

class TestDoubleOFXImportAcrossSessions:
    # Importing two OFX files across sessions.
    #
    # Correctly remember the OFX IDs even if the account name changes.
    def do_setup(self, tmpdir):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2008, 2, 1))
        importall(app, testdata.filepath('ofx', 'desjardins.ofx'))
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0] # 815-30219-11111-EOP
        app.bsheet.selected.name = 'Desjardins EOP'
        app.bsheet.save_edits()
        filename = str(tmpdir.join('foo.xml'))
        app.doc.save_to_xml(filename)
        app.doc.load_from_xml(filename)
        importall(app, testdata.filepath('ofx', 'desjardins2.ofx'))
        return app
    
    @with_app(do_setup)
    def test_account_names(self, app):
        # Non-empty accounts from both files are imported
        eq_(app.account_names(), ['815-30219-12345-EOP', 'Desjardins EOP'])
    

class TestAnotherDoubleOFXImport:
    # Importing two OFX files that contain transactions with the same FIT ID, but a different account ID.
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2008, 2, 1))
        importall(app, testdata.filepath('ofx', 'desjardins2.ofx'))
        importall(app, testdata.filepath('ofx', 'desjardins3.ofx'))
        return app
    
    @with_app(do_setup)
    def test_account_names(self, app):
        # All non-empty accounts have been imported.
        eq_(app.account_names(), ['815-30219-11111-EOP', 'NEW_ACCOUNT'])
    
    @with_app(do_setup)
    def test_entries_counts(self, app):
        # All accounts have the appropriate number of entries.
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        eq_(app.etable_count(), 2)
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[1]
        app.show_account()
        eq_(app.etable_count(), 1)
    

class TestTripleOFXImportAcrossSessions:
    # Import the same OFX 3 times
    def do_setup(self, tmpdir):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2008, 2, 1))
        importall(app, testdata.filepath('ofx', 'desjardins.ofx'))
        importall(app, testdata.filepath('ofx', 'desjardins.ofx'))
        filename = str(tmpdir.join('foo.xml'))
        app.doc.save_to_xml(filename)
        app.doc.load_from_xml(filename)
        importall(app, testdata.filepath('ofx', 'desjardins.ofx'))
        return app
    
    @with_app(do_setup)
    def test_entry_count(self, app):
        # The number of entries is the same as if the import was made once
        # Previously, the transaction reference would be lost in a transaction conflict resolution
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        eq_(app.etable_count(), 3)
    

#--- Double OFX import with split in the middle
# Import an OFX, change one entry into a split, and then re-import.
def app_double_ofx_import_with_split_in_the_middle():
    app = TestApp()
    app.doc.date_range = MonthRange(date(2008, 2, 1))
    importall(app, testdata.filepath('ofx', 'desjardins.ofx'))
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.show_account()
    app.etable.select([2]) #retrait
    row = app.etable.selected_row
    row.transfer = 'account1'
    app.etable.save_edits()
    app.tpanel.load()
    app.stable.add()
    app.stable[2].credit = '1'
    app.stable.save_edits()
    app.tpanel.save()
    importall(app, testdata.filepath('ofx', 'desjardins.ofx'))
    return app

def test_split_wasnt_touched():
    # When matching transaction and encountering a case where the old transaction was changed
    # into a split, bail out and don't touch the amounts.
    app = app_double_ofx_import_with_split_in_the_middle()
    eq_(len(app.stable), 4)
    eq_(app.stable[2].credit, '1.00')

class TestImportAccountInGroup:
    def do_setup(self):
        app = TestApp()
        importall(app, testdata.filepath('moneyguru', 'account_in_group.moneyguru'))
        app.show_nwview()
        return app
    
    @with_app(do_setup)
    def test_account_was_imported(self, app):
        # The fact that the account was in a group didn't prevent it from being imported.
        eq_(app.bsheet.assets[0].name, 'Some Asset')
    

class TestTwoEntriesInRangeSaveThenLoad:
    # Two entries having the same date, in range. The app saves to a file then loads the same file.
    def do_setup(self, tmpdir):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        app.add_account()
        app.show_account()
        app.add_entry('1/10/2007', description='first')
        app.add_entry('1/10/2007', description='second')
        filename = str(tmpdir.join('foo.xml'))
        app.doc.save_to_xml(filename)
        app.doc.load_from_xml(filename)
        # have been kicked back to bsheet. Select the account again
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        app.etable.select([0])
        return app
    
    @with_app(do_setup)
    def test_editing_an_entry_doesnt_change_the_order(self, app):
        # Editing the first entry doesn't change its position
        row = app.etable.selected_row
        row.increase = '42'
        app.etable.save_edits()
        eq_(app.etable[0].description, 'first')
    

class TestTransferBetweenTwoReferencedAccounts:
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2008, 2, 1))
        importall(app, testdata.filepath('moneyguru', 'with_references1.moneyguru')) # Contains Account 1
        app.add_account('Account 4') # Add it as an asset
        app.show_nwview()
        app.bsheet.selected = app.bsheet.assets[0]
        app.show_account()
        app.etable.select([0])
        row = app.etable[0]
        row.transfer = 'Account 4'
        app.etable.save_edits()
        app.doc.parse_file_for_import(testdata.filepath('moneyguru', 'with_references3.moneyguru')) # Contains Account 4
        # The entry from Account 4 doesn't match yet because they don't have the same reference, but
        # it will be fixed after the import
        app.iwin.selected_target_account_index = 3 # Account 4
        app.itable.bind(0, 1)
        app.iwin.import_selected_pane()
        # The 2 entries are now linked in the same txn.
        return app
    
    @with_app(do_setup)
    def test_first_side_matches(self, app):
        # When importing entries from Account 1, these entries are matched correctly
        app.doc.parse_file_for_import(testdata.filepath('moneyguru', 'with_references1.moneyguru'))
        # All entries should be matched
        eq_(len(app.itable), 2) # 2 entries means they all match
    
    @with_app(do_setup)
    def test_second_side_matches(self, app):
        # When importing entries from Account 3, these entries are matched correctly
        app.doc.parse_file_for_import(testdata.filepath('moneyguru', 'with_references3.moneyguru'))
        # target account should be correct, and all entries should be matched
        eq_(app.iwin.selected_target_account_index, 3) # Account 4
        eq_(len(app.itable), 1) # 1 entry means they all match
    

class TestImportFileWithMultipleTransferReferences:
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2008, 2, 1))
        importall(app, testdata.filepath('moneyguru', 'multiple_transfer_references.moneyguru'))
        return app
    
    @with_app(do_setup)
    def test_account_names_are_correct(self, app):
        # the account names for the transfers are correctly imported. Previously, new_name() was
        # recursively called on them for each occurence in the split.
        app.show_pview()
        eq_(app.istatement.income[0].name, 'income')
        eq_(app.istatement.expenses[0].name, 'expense')
    


def test_date_format_guessing(tmpdir):
    filepath = str(tmpdir.join('foo.qif'))
    def check(str_date, expected_date):
        # To test the date format guessing part, we create a QIF, which uses date guessing.
        app = TestApp()
        contents = "!Type:Bank\nD{str_date}\nT42.32\n^".format(str_date=str_date)
        hsio.open(filepath, 'wt', encoding='utf-8').write(contents)
        app.doc.parse_file_for_import(filepath)
        eq_(app.itable[0].date_import, expected_date)
    
    check('12/20/2010', '20/12/2010')
    check('28/Jun/2010', '28/06/2010')
    check('12/Jan/10', '12/01/2010')
    # When we have really bogus years like this one below, we assume that this is some kind of typo
    # and we go for the last resort: using the last two digits and adding 2000 to it.
    check('01/01/0211', '01/01/2011')
