# Created By: Virgil Dupras
# Created On: 2008-08-08
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from ..base import TestCase, DictLoader
from ...model.date import YearRange

class ImportCheckbookQIF(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.document.parse_file_for_import(self.filepath('qif/checkbook.qif'))
        self.check_gui_calls(self.iwin_gui, refresh_tabs=1, refresh_target_accounts=1, show=1)
    
    def test_account_tabs(self):
        """There is one account tab for each imported account, the first is selected, and each tab
        has a counter indicating the number of entries in each account.
        """
        self.assertEqual(len(self.iwin.panes), 2)
        self.assertEqual(self.iwin.panes[0].name, 'Account 1')
        self.assertEqual(self.iwin.panes[1].name, 'Account 2')
        self.assertEqual(self.iwin.panes[0].count, 5)
        self.assertEqual(self.iwin.panes[1].count, 3)
        self.assertEqual(self.iwin.selected_pane_index, 0)
    
    def test_close_pane(self):
        """It's possible to close any pane"""
        self.iwin.close_pane(1) # It's not the selected pane
        self.assertEqual(len(self.iwin.panes), 1)
        self.assertEqual(self.iwin.panes[0].name, 'Account 1')
        self.assertEqual(self.iwin.panes[0].count, 5)
    
    def test_close_selected_pane(self):
        """When closing the selected pane, everything is correctly refreshed"""
        self.add_account_legacy('bar')
        self.iwin.selected_target_account_index = 1
        self.iwin.close_pane(0)
        self.assertEqual(len(self.iwin.panes), 1)
        self.assertEqual(self.iwin.panes[0].name, 'Account 2')
        self.assertEqual(self.iwin.panes[0].count, 3)
        self.assertEqual(len(self.itable), 3)
    
    def test_close_first_pane_when_selected_is_last(self):
        """When the selected pane index is last, closing it decrements the selected pane index"""
        self.iwin.selected_pane_index = 1
        self.iwin.close_pane(0)
        self.assertEqual(self.iwin.selected_pane_index, 0)
    
    def test_close_selected_pane_when_last(self):
        """When the selected pane index is last, closing it decrements the selected pane index"""
        self.iwin.selected_pane_index = 1
        self.iwin.close_pane(1)
        self.assertEqual(self.iwin.selected_pane_index, 0)
    
    def test_dirty(self):
        """Simply loading a file for import doesn't make the document dirty"""
        self.assertFalse(self.document.is_dirty())
    
    def test_import_selected_pane(self):
        """import_selected_pane() imports the currenctly selected pane and closes it"""
        self.iwin.import_selected_pane()
        # The pane has been closed
        self.assertEqual(len(self.iwin.panes), 1)
        self.assertEqual(self.iwin.panes[0].name, 'Account 2')
        self.check_gui_calls(self.iwin_gui, update_selected_pane=1, close_selected_tab=1)
        # The account & entries has been added
        self.assertEqual(self.bsheet.assets[0].name, 'Account 1')
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 5)
        # When importing the last pane, the window should close
        self.clear_gui_calls()
        self.iwin.import_selected_pane()
        self.check_gui_calls(self.iwin_gui, close_selected_tab=1, close=1)
    
    def test_import_selected_pane_with_some_entries_disabled(self):
        # When the will_import checkbox is unchecked, don't import the entry
        self.itable[0].will_import = False
        self.iwin.import_selected_pane()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 4)
    
    def test_remember_target_account_selection(self):
        """When selecting a target account, it's specific to the ane we're in"""
        self.add_account_legacy('foo')
        self.iwin.selected_target_account_index = 1
        self.clear_gui_calls()
        self.iwin.selected_pane_index = 1
        self.check_gui_calls(self.iwin_gui, update_selected_pane=1)
        self.assertEqual(self.iwin.selected_target_account_index, 0)
        self.iwin.selected_target_account_index = 1
        self.iwin.selected_pane_index = 0
        self.assertEqual(self.iwin.selected_target_account_index, 1)
        # target account selection is instance based, not index based
        self.add_account_legacy('bar')
        self.assertEqual(self.iwin.selected_target_account_index, 2)
        self.iwin.selected_pane_index = 1
        self.assertEqual(self.iwin.selected_target_account_index, 2)
    
    def test_select_out_of_range_tab_index(self):
        # ignore index set that are out of range
        self.iwin.selected_pane_index = 2
        self.assertEqual(self.iwin.selected_pane_index, 0)
    
    def test_switch_description_payee(self):
        self.iwin.switch_description_payee()
        # the 4th entry is the Hydro Quebec entry
        self.assertEqual(self.itable[3].description_import, 'Hydro-Quebec')
        self.assertEqual(self.itable[3].payee_import, 'Power Bill')
    
    def test_target_accounts(self):
        """Target accounts are updated when accounts are added/removed"""
        self.assertEqual(self.iwin.target_account_names, ['< New Account >'])
        self.add_account_legacy('Foo')
        self.add_account_legacy('bar')
        self.check_gui_calls(self.iwin_gui, refresh_target_accounts=4) # one for add, one for change
        self.assertEqual(self.iwin.target_account_names, ['< New Account >', 'bar', 'Foo'])
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0] # bar
        self.bsheet.delete()
        self.check_gui_calls(self.iwin_gui, refresh_target_accounts=1)
        self.assertEqual(self.iwin.target_account_names, ['< New Account >', 'Foo'])
        self.add_account_legacy()
        self.check_gui_calls(self.iwin_gui, refresh_target_accounts=1)
        self.assertEqual(self.iwin.target_account_names, ['< New Account >', 'Foo', 'New account'])
    

class ImportCheckbookQIFTwice(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.document.parse_file_for_import(self.filepath('qif/checkbook.qif'))
        self.document.parse_file_for_import(self.filepath('qif/checkbook.qif'))
    
    def test_import_again(self):
        #Importing when there are already open tabs adds the new tabs to the iwin
        self.assertEqual(len(self.iwin.panes), 4)
    
    def test_switch_description_payee_apply_to_all(self):
        self.iwin.switch_description_payee(apply_to_all=True)
        # the 4th entry is the Hydro Quebec entry
        self.iwin.selected_pane_index = 2
        self.assertEqual(self.itable[3].description_import, 'Hydro-Quebec')
        self.assertEqual(self.itable[3].payee_import, 'Power Bill')
    

class ImportCheckbookQIFWithSomeExistingTransactions(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('foo')
        self.add_entry(date='01/01/2007', description='first entry', increase='1')
        self.document.toggle_reconciliation_mode()
        self.etable.toggle_reconciled()
        self.document.toggle_reconciliation_mode() # commit
        self.add_entry(date='02/01/2007', description='second entry', increase='2')
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.document.parse_file_for_import(self.filepath('qif/checkbook.qif'))
        self.clear_gui_calls()
        self.iwin.selected_target_account_index = 1 # foo
        self.check_gui_calls(self.itable_gui, refresh=1)
    
    def test_import(self):
        """Import happens in the selected target account"""
        self.iwin.import_selected_pane()
        self.assertEqual(self.bsheet.assets.children_count, 3) # did not add a new account
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 7) # The entries have been added
    
    def test_match_then_import(self):
        """The entry matching has the correct effect on the import"""
        self.itable.bind(2, 5) # second entry --> 04/02/2007 Transfer 80.00
        self.iwin.import_selected_pane()
        # The merged entry is supposed to be the last because it changed its date
        self.assertEqual(len(self.etable), 6)
        row = self.etable[5]
        self.assertEqual(row.date, '04/02/2007')
        self.assertEqual(row.description, 'second entry')
        self.assertEqual(row.increase, '80.00')
    

class LoadWithReference(TestCase):
    def setUp(self):
        self.create_instances()
        self.TXNS = [
            {'date': '20/07/2009', 'amount': '1', 'reference': 'txn1'},
            {'date': '20/07/2009', 'amount': '1', 'reference': 'txn1'},
        ]
        self.fake_import('foo', self.TXNS)
        self.iwin.import_selected_pane()
    
    def test_import_with_same_reference_twice(self):
        # When 2 txns have the same ref in an account, importing a file with the same ref would
        # cause a crash.
        self.fake_import('foo', self.TXNS)
        self.iwin.selected_target_account_index = 1 # no crash
    

class LoadThemImportWithReference(TestCase):
    def setUp(self):
        self.mock_today(2008, 1, 1)
        self.create_instances()
        self.document.load_from_xml(self.filepath('moneyguru/with_references1.moneyguru'))
        self.document.parse_file_for_import(self.filepath('moneyguru/with_references2.moneyguru'))
        self.clear_gui_calls()
    
    def test_selected_target_account(self):
        """If a target account's reference matched the imported account, select it"""
        self.assertEqual(self.iwin.selected_target_account_index, 1)
    

class ImportMoneyguruFileWithExpenseAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2008, 1, 1))
        self.document.parse_file_for_import(self.filepath('xml/moneyguru.xml'))
    
    def test_account_panes(self):
        # There are only 2 account panes (one for each asset account). the expense account is not there
        self.assertEqual(len(self.iwin.panes), 2)
        self.assertEqual(self.iwin.panes[0].name, 'Account 1')
        self.assertEqual(self.iwin.panes[1].name, 'Account 2')
    

class ImportAccountlessQIF(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.document.parse_file_for_import(self.filepath('qif/accountless.qif'))
    
    def test_account_tabs(self):
        # The account is just imported as 'Account'
        self.assertEqual(len(self.iwin.panes), 1)
        self.assertEqual(self.iwin.panes[0].name, 'Account')
        self.assertEqual(self.iwin.panes[0].count, 5)
    

class ImportAccountlessWithSplitsQIF(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2008, 1, 1))
        self.document.parse_file_for_import(self.filepath('qif/accountless_with_splits.qif'))
    
    def test_account_tabs(self):
        # Previously, splits referring to account not present in the QIF has a None account
        self.assertEqual(len(self.iwin.panes), 1)
        self.assertEqual(self.iwin.panes[0].name, 'Account')
        self.assertEqual(self.iwin.panes[0].count, 2)
    
    def test_transfers(self):
        # The transfer splits' account were correctly set
        self.assertEqual(len(self.itable), 2)
        self.assertEqual(self.itable[0].transfer_import, 'Payment Sent, Fee')
        self.assertEqual(self.itable[0].amount_import, '-1000.00')
        self.assertEqual(self.itable[1].transfer_import, 'Web Accept Payment Received, Fee')
        self.assertEqual(self.itable[1].amount_import, '18.95')
    

class ImportQIFWithEmptyAccount(TestCase): # like checkbook.qif, but with 2 extra empty accounts
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.document.parse_file_for_import(self.filepath('qif/empty_accounts.qif'))
    
    def test_account_tabs(self):
        # The account is just imported as 'Account'
        self.assertEqual(len(self.iwin.panes), 2)
        self.assertEqual(self.iwin.panes[0].name, 'Account 1')
        self.assertEqual(self.iwin.panes[1].name, 'Account 2')
    

LOW_DATE_FIELDS = [
    {'date': '5/11/2008', 'amount': '1'},
    {'date': '12/01/2009', 'amount': '1'},
    {'date': '01/02/2009', 'amount': '1'},
]

HIGH_DAY_FIELDS = [
    {'date': '02/01/2009', 'amount': '1'},
    {'date': '13/01/2009', 'amount': '1'},
]

HIGH_YEAR_FIELDS = [
    {'date': '02/01/1999', 'amount': '1'},
    {'date': '13/01/1999', 'amount': '1'},
]

class ImportTransactionsWithLowDateFields(TestCase):
    def setUp(self):
        self.create_instances()
        self.fake_import('foo', LOW_DATE_FIELDS)
    
    def test_can_switch_fields(self):
        # all fields can be switched
        self.assertTrue(self.iwin.can_switch_date_fields('day', 'month'))
        self.assertTrue(self.iwin.can_switch_date_fields('day', 'year'))
        self.assertTrue(self.iwin.can_switch_date_fields('year', 'month'))
    
    def test_switch_day_month(self):
        self.iwin.switch_date_fields('day', 'month')
        self.assertEqual(self.itable[0].date_import, '11/05/2008')
        self.assertEqual(self.itable[1].date_import, '01/12/2009')
        self.assertEqual(self.itable[2].date_import, '02/01/2009')
    
    def test_switch_day_year(self):
        self.iwin.switch_date_fields('day', 'year')
        self.assertEqual(self.itable[0].date_import, '08/11/2005')
        self.assertEqual(self.itable[1].date_import, '09/01/2012')
        self.assertEqual(self.itable[2].date_import, '09/02/2001')
    

class ImportTransactionsWithHighDayField(TestCase):
    def setUp(self):
        self.create_instances()
        self.fake_import('foo', HIGH_DAY_FIELDS)
    
    def test_can_switch_fields(self):
        # the day can't be switched with month
        self.assertFalse(self.iwin.can_switch_date_fields('day', 'month'))
        self.assertTrue(self.iwin.can_switch_date_fields('day', 'year'))
        self.assertTrue(self.iwin.can_switch_date_fields('year', 'month'))
    

class ImportTransactionsWithHighYearField(TestCase):
    def setUp(self):
        self.create_instances()
        self.fake_import('foo', HIGH_YEAR_FIELDS)
    
    def test_can_switch_fields(self):
        # the year can't be switched because 99 is too high
        self.assertFalse(self.iwin.can_switch_date_fields('day', 'month'))
        self.assertFalse(self.iwin.can_switch_date_fields('day', 'year'))
        self.assertFalse(self.iwin.can_switch_date_fields('year', 'month'))
    

class ImportTransactionWithDayOn31stAndYearCorrespondingToLowMonth(TestCase):
    # The date 31/07/2009 has a high day, and if we were to swap year and month, we'd be ending up
    # with an invalid date (31/09/2007).
    def setUp(self):
        self.create_instances()
        self.fake_import('foo', [{'date': '31/07/2009', 'amount': '1'}])
    
    def test_can_switch_fields(self):
        # September has 30 days, so it's impossible to swap the month and the year.
        assert not self.iwin.can_switch_date_fields('year', 'month')

class ThreeImportsTwoOfThemWithLowDateFields(TestCase):
    def setUp(self):
        self.create_instances()
        self.fake_import('foo1', LOW_DATE_FIELDS)
        self.fake_import('foo2', LOW_DATE_FIELDS)
        self.fake_import('foo3', HIGH_DAY_FIELDS)
    
    def test_switch_apply_to_all(self):
        # when the 'apply_to_all' argument is passed, the swucth happens in all applicable accounts
        self.iwin.switch_date_fields('day', 'month', apply_to_all=True)
        self.iwin.selected_pane_index = 1
        self.assertEqual(self.itable[0].date_import, '11/05/2008') # switched
        self.iwin.selected_pane_index = 2
        self.assertEqual(self.itable[0].date_import, '02/01/2009') # not switched
    

class TwoAccountsWithCommonTransaction(TestCase):
    def setUp(self):
        self.create_instances()
        txns = [
            {
                'date': '5/11/2008',
                'transfer': 'second',
                'description':'foo',
                'payee': 'bar',
                'amount': '1',
            },
        ]
        loader = DictLoader(self.app.default_currency, 'first', txns)
        loader.start_account()
        loader.account_info.name = 'second'
        loader.flush_account()
        loader.load()
        self.document.loader = loader
        self.document.notify('file_loaded_for_import')
    
    def test_switch_date(self):
        # the transaction in the 2 accounts is the same. *don't* switch it twice!
        self.iwin.switch_date_fields('day', 'month', apply_to_all=True)
        self.assertEqual(self.itable[0].date_import, '11/05/2008')
    
    def test_switch_description_payee(self):
        # same as with dates: don't switch twice
        self.iwin.switch_description_payee()
        self.assertEqual(self.itable[0].description_import, 'bar')
        self.assertEqual(self.itable[0].payee_import, 'foo')
    
