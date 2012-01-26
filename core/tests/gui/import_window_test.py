# Created By: Virgil Dupras
# Created On: 2008-08-08
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.testutil import eq_

from ..base import TestApp, with_app, DictLoader, testdata
from ...model.date import YearRange
from ...gui.import_window import SwapType

class TestImportCheckbookQIF:
    def do_setup(self):
        app = TestApp()
        app.clear_gui_calls()
        app.doc.date_range = YearRange(date(2007, 1, 1))
        app.doc.parse_file_for_import(testdata.filepath('qif/checkbook.qif'))
        app.check_gui_calls(app.iwin_gui, ['refresh_tabs', 'refresh_target_accounts', 'show'])
        return app
    
    @with_app(do_setup)
    def test_account_tabs(self, app):
        # There is one account tab for each imported account, the first is selected, and each tab
        # has a counter indicating the number of entries in each account.
        eq_(len(app.iwin.panes), 2)
        eq_(app.iwin.panes[0].name, 'Account 1')
        eq_(app.iwin.panes[1].name, 'Account 2')
        eq_(app.iwin.panes[0].count, 5)
        eq_(app.iwin.panes[1].count, 3)
        eq_(app.iwin.selected_pane_index, 0)
    
    @with_app(do_setup)
    def test_close_pane(self, app):
        # It's possible to close any pane
        app.iwin.close_pane(1) # It's not the selected pane
        eq_(len(app.iwin.panes), 1)
        eq_(app.iwin.panes[0].name, 'Account 1')
        eq_(app.iwin.panes[0].count, 5)
    
    @with_app(do_setup)
    def test_close_selected_pane(self, app):
        # When closing the selected pane, everything is correctly refreshed
        app.add_account('bar')
        app.iwin.selected_target_account_index = 1
        app.iwin.close_pane(0)
        eq_(len(app.iwin.panes), 1)
        eq_(app.iwin.panes[0].name, 'Account 2')
        eq_(app.iwin.panes[0].count, 3)
        eq_(len(app.itable), 3)
    
    @with_app(do_setup)
    def test_close_first_pane_when_selected_is_last(self, app):
        # When the selected pane index is last, closing it decrements the selected pane index
        app.iwin.selected_pane_index = 1
        app.iwin.close_pane(0)
        eq_(app.iwin.selected_pane_index, 0)
    
    @with_app(do_setup)
    def test_close_selected_pane_when_last(self, app):
        # When the selected pane index is last, closing it decrements the selected pane index
        app.iwin.selected_pane_index = 1
        app.iwin.close_pane(1)
        eq_(app.iwin.selected_pane_index, 0)
    
    @with_app(do_setup)
    def test_dirty(self, app):
        # Simply loading a file for import doesn't make the document dirty
        assert not app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_import_selected_pane(self, app):
        # import_selected_pane() imports the currenctly selected pane and closes it
        app.iwin.import_selected_pane()
        # The pane has been closed
        eq_(len(app.iwin.panes), 1)
        eq_(app.iwin.panes[0].name, 'Account 2')
        app.check_gui_calls(app.iwin_gui, ['update_selected_pane', 'close_selected_tab'])
        # The account & entries has been added
        eq_(app.bsheet.assets[0].name, 'Account 1')
        app.bsheet.selected = app.bsheet.assets[0]
        app.bsheet.show_selected_account()
        eq_(app.etable_count(), 5)
        # When importing the last pane, the window should close
        app.clear_gui_calls()
        app.iwin.import_selected_pane()
        app.check_gui_calls(app.iwin_gui, ['close_selected_tab', 'close'])
    
    @with_app(do_setup)
    def test_import_selected_pane_with_some_entries_disabled(self, app):
        # When the will_import checkbox is unchecked, don't import the entry
        app.itable[0].will_import = False
        app.iwin.import_selected_pane()
        app.bsheet.selected = app.bsheet.assets[0]
        app.bsheet.show_selected_account()
        eq_(app.etable_count(), 4)
    
    @with_app(do_setup)
    def test_invert_amounts(self, app):
        app.iwin.swap_type_index = SwapType.InvertAmount
        app.iwin.perform_swap()
        eq_(app.itable[0].amount_import, '-42.32')
        eq_(app.itable[1].amount_import, '-100.00')
        eq_(app.itable[2].amount_import, '60.00')
    
    @with_app(do_setup)
    def test_remember_target_account_selection(self, app):
        # When selecting a target account, it's specific to the ane we're in
        app.add_account('foo')
        app.iwin.selected_target_account_index = 1
        app.clear_gui_calls()
        app.iwin.selected_pane_index = 1
        app.check_gui_calls(app.iwin_gui, ['update_selected_pane'])
        eq_(app.iwin.selected_target_account_index, 0)
        app.iwin.selected_target_account_index = 1
        app.iwin.selected_pane_index = 0
        eq_(app.iwin.selected_target_account_index, 1)
        # target account selection is instance based, not index based
        app.add_account('bar')
        eq_(app.iwin.selected_target_account_index, 2)
        app.iwin.selected_pane_index = 1
        eq_(app.iwin.selected_target_account_index, 2)
    
    @with_app(do_setup)
    def test_select_out_of_range_tab_index(self, app):
        # ignore index set that are out of range
        app.iwin.selected_pane_index = 2
        eq_(app.iwin.selected_pane_index, 0)
    
    @with_app(do_setup)
    def test_switch_description_payee(self, app):
        app.iwin.swap_type_index = SwapType.DescriptionPayee
        app.iwin.perform_swap()
        # the 4th entry is the Hydro Quebec entry
        eq_(app.itable[3].description_import, 'Hydro-Quebec')
        eq_(app.itable[3].payee_import, 'Power Bill')
    
    @with_app(do_setup)
    def test_target_accounts(self, app):
        # Target accounts are updated when accounts are added/removed
        eq_(app.iwin.target_account_names, ['< New Account >'])
        app.add_account('Foo')
        app.check_gui_calls(app.iwin_gui, ['refresh_target_accounts'])
        app.add_account('bar')
        app.check_gui_calls(app.iwin_gui, ['refresh_target_accounts'])
        eq_(app.iwin.target_account_names, ['< New Account >', 'bar', 'Foo'])
        app.mainwindow.select_balance_sheet()
        app.bsheet.selected = app.bsheet.assets[0] # bar
        app.bsheet.delete()
        app.check_gui_calls(app.iwin_gui, ['refresh_target_accounts'])
        eq_(app.iwin.target_account_names, ['< New Account >', 'Foo'])
        app.add_account()
        app.check_gui_calls(app.iwin_gui, ['refresh_target_accounts'])
        eq_(app.iwin.target_account_names, ['< New Account >', 'Foo', 'New account'])
    

class TestImportCheckbookQIFTwice:
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = YearRange(date(2007, 1, 1))
        app.doc.parse_file_for_import(testdata.filepath('qif/checkbook.qif'))
        app.doc.parse_file_for_import(testdata.filepath('qif/checkbook.qif'))
        return app
    
    @with_app(do_setup)
    def test_import_again(self, app):
        #Importing when there are already open tabs adds the new tabs to the iwin
        eq_(len(app.iwin.panes), 4)
    
    @with_app(do_setup)
    def test_switch_description_payee_apply_to_all(self, app):
        app.iwin.swap_type_index = SwapType.DescriptionPayee
        app.iwin.perform_swap(apply_to_all=True)
        # the 4th entry is the Hydro Quebec entry
        app.iwin.selected_pane_index = 2
        eq_(app.itable[3].description_import, 'Hydro-Quebec')
        eq_(app.itable[3].payee_import, 'Power Bill')
    

class TestImportCheckbookQIFWithSomeExistingTransactions:
    def do_setup(self):
        app = TestApp()
        app.add_account('foo')
        app.mw.show_account()
        app.add_entry(date='01/01/2007', description='first entry', increase='1')
        app.aview.toggle_reconciliation_mode()
        app.etable.toggle_reconciled()
        app.aview.toggle_reconciliation_mode() # commit
        app.add_entry(date='02/01/2007', description='second entry', increase='2')
        app.doc.date_range = YearRange(date(2007, 1, 1))
        app.doc.parse_file_for_import(testdata.filepath('qif/checkbook.qif'))
        app.clear_gui_calls()
        app.iwin.selected_target_account_index = 1 # foo
        app.itable.view.check_gui_calls(['refresh'])
        return app
    
    @with_app(do_setup)
    def test_import(self, app):
        # Import happens in the selected target account
        app.iwin.import_selected_pane()
        eq_(app.bsheet.assets.children_count, 3) # did not add a new account
        app.bsheet.selected = app.bsheet.assets[0]
        app.bsheet.show_selected_account()
        eq_(app.etable_count(), 7) # The entries have been added
    
    @with_app(do_setup)
    def test_match_then_import(self, app):
        # The entry matching has the correct effect on the import
        app.itable.bind(2, 5) # second entry --> 04/02/2007 Transfer 80.00
        app.iwin.import_selected_pane()
        # The merged entry is supposed to be the last because it changed its date
        eq_(app.etable_count(), 6)
        row = app.etable[5]
        eq_(row.date, '04/02/2007')
        eq_(row.description, 'second entry')
        eq_(row.increase, '80.00')
    

class TestLoadWithReference:
    def do_setup(self):
        app = TestApp()
        self.TXNS = [
            {'date': '20/07/2009', 'amount': '1', 'reference': 'txn1'},
            {'date': '20/07/2009', 'amount': '1', 'reference': 'txn1'},
        ]
        app.fake_import('foo', self.TXNS)
        app.iwin.import_selected_pane()
        return app
    
    @with_app(do_setup)
    def test_import_with_same_reference_twice(self, app):
        # When 2 txns have the same ref in an account, importing a file with the same ref would
        # cause a crash.
        app.fake_import('foo', self.TXNS)
        app.iwin.selected_target_account_index = 1 # no crash
    

class TestLoadThemImportWithReference:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2008, 1, 1)
        app = TestApp()
        app.doc.load_from_xml(testdata.filepath('moneyguru/with_references1.moneyguru'))
        app.doc.parse_file_for_import(testdata.filepath('moneyguru/with_references2.moneyguru'))
        return app
    
    @with_app(do_setup)
    def test_selected_target_account(self, app):
        # If a target account's reference matched the imported account, select it
        eq_(app.iwin.selected_target_account_index, 1)
    

class TestImportMoneyguruFileWithExpenseAccount:
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = YearRange(date(2008, 1, 1))
        app.doc.parse_file_for_import(testdata.filepath('moneyguru', 'simple.moneyguru'))
        return app
    
    @with_app(do_setup)
    def test_account_panes(self, app):
        # There are only 2 account panes (one for each asset account). the expense account is not there
        eq_(len(app.iwin.panes), 2)
        eq_(app.iwin.panes[0].name, 'Account 1')
        eq_(app.iwin.panes[1].name, 'Account 2')
    

class TestImportAccountlessQIF:
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = YearRange(date(2007, 1, 1))
        app.doc.parse_file_for_import(testdata.filepath('qif/accountless.qif'))
        return app
    
    @with_app(do_setup)
    def test_account_tabs(self, app):
        # The account is just imported as 'Account'
        eq_(len(app.iwin.panes), 1)
        eq_(app.iwin.panes[0].name, 'Account')
        eq_(app.iwin.panes[0].count, 5)
    

class TestImportAccountlessWithSplitsQIF:
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = YearRange(date(2008, 1, 1))
        app.doc.parse_file_for_import(testdata.filepath('qif/accountless_with_splits.qif'))
        return app
    
    @with_app(do_setup)
    def test_account_tabs(self, app):
        # Previously, splits referring to account not present in the QIF has a None account
        eq_(len(app.iwin.panes), 1)
        eq_(app.iwin.panes[0].name, 'Account')
        eq_(app.iwin.panes[0].count, 2)
    
    @with_app(do_setup)
    def test_transfers(self, app):
        # The transfer splits' account were correctly set
        eq_(len(app.itable), 2)
        eq_(app.itable[0].transfer_import, 'Payment Sent, Fee')
        eq_(app.itable[0].amount_import, '-1000.00')
        eq_(app.itable[1].transfer_import, 'Web Accept Payment Received, Fee')
        eq_(app.itable[1].amount_import, '18.95')
    

class TestImportQIFWithEmptyAccount: # like checkbook.qif, but with 2 extra empty accounts
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = YearRange(date(2007, 1, 1))
        app.doc.parse_file_for_import(testdata.filepath('qif/empty_accounts.qif'))
        return app
    
    @with_app(do_setup)
    def test_account_tabs(self, app):
        # The account is just imported as 'Account'
        eq_(len(app.iwin.panes), 2)
        eq_(app.iwin.panes[0].name, 'Account 1')
        eq_(app.iwin.panes[1].name, 'Account 2')
    

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

class TestImportTransactionsWithLowDateFields:
    def do_setup(self):
        app = TestApp()
        app.fake_import('foo', LOW_DATE_FIELDS)
        return app
    
    @with_app(do_setup)
    def test_can_switch_fields(self, app):
        # all fields can be switched
        app.iwin.swap_type_index = SwapType.DayMonth
        assert app.iwin.can_perform_swap()
        app.iwin.swap_type_index = SwapType.DayYear
        assert app.iwin.can_perform_swap()
        app.iwin.swap_type_index = SwapType.MonthYear
        assert app.iwin.can_perform_swap()
    
    @with_app(do_setup)
    def test_switch_day_month(self, app):
        app.iwin.swap_type_index = SwapType.DayMonth
        app.iwin.perform_swap()
        eq_(app.itable[0].date_import, '11/05/2008')
        eq_(app.itable[1].date_import, '01/12/2009')
        eq_(app.itable[2].date_import, '02/01/2009')
    
    @with_app(do_setup)
    def test_switch_day_year(self, app):
        app.iwin.swap_type_index = SwapType.DayYear
        app.iwin.perform_swap()
        eq_(app.itable[0].date_import, '08/11/2005')
        eq_(app.itable[1].date_import, '09/01/2012')
        eq_(app.itable[2].date_import, '09/02/2001')
    

class TestImportTransactionsWithHighDayField:
    def do_setup(self):
        app = TestApp()
        app.fake_import('foo', HIGH_DAY_FIELDS)
        return app
    
    @with_app(do_setup)
    def test_can_switch_fields(self, app):
        # the day can't be switched with month
        app.iwin.swap_type_index = SwapType.DayMonth
        assert not app.iwin.can_perform_swap()
        app.iwin.swap_type_index = SwapType.DayYear
        assert app.iwin.can_perform_swap()
        app.iwin.swap_type_index = SwapType.MonthYear
        assert app.iwin.can_perform_swap()
    

class TestImportTransactionsWithHighYearField:
    def do_setup(self):
        app = TestApp()
        app.fake_import('foo', HIGH_YEAR_FIELDS)
        return app
    
    @with_app(do_setup)
    def test_can_switch_fields(self, app):
        # the year can't be switched because 99 is too high
        app.iwin.swap_type_index = SwapType.DayMonth
        assert not app.iwin.can_perform_swap()
        app.iwin.swap_type_index = SwapType.DayYear
        assert not app.iwin.can_perform_swap()
        app.iwin.swap_type_index = SwapType.MonthYear
        assert not app.iwin.can_perform_swap()
    

class TestImportTransactionWithDayOn31stAndYearCorrespondingToLowMonth:
    # The date 31/07/2009 has a high day, and if we were to swap year and month, we'd be ending up
    # with an invalid date (31/09/2007).
    def do_setup(self):
        app = TestApp()
        app.fake_import('foo', [{'date': '31/07/2009', 'amount': '1'}])
        return app
    
    @with_app(do_setup)
    def test_can_switch_fields(self, app):
        # September has 30 days, so it's impossible to swap the month and the year.
        app.iwin.swap_type_index = SwapType.MonthYear
        assert not app.iwin.can_perform_swap()

class TestThreeImportsTwoOfThemWithLowDateFields:
    def do_setup(self):
        app = TestApp()
        app.fake_import('foo1', LOW_DATE_FIELDS)
        app.fake_import('foo2', LOW_DATE_FIELDS)
        app.fake_import('foo3', HIGH_DAY_FIELDS)
        return app
    
    @with_app(do_setup)
    def test_switch_apply_to_all(self, app):
        # when the 'apply_to_all' argument is passed, the swucth happens in all applicable accounts
        app.iwin.swap_type_index = SwapType.DayMonth
        app.iwin.perform_swap(apply_to_all=True)
        app.iwin.selected_pane_index = 1
        eq_(app.itable[0].date_import, '11/05/2008') # switched
        app.iwin.selected_pane_index = 2
        eq_(app.itable[0].date_import, '02/01/2009') # not switched
    

class TestTwoAccountsWithCommonTransaction:
    def do_setup(self):
        app = TestApp()
        txns = [
            {
                'date': '5/11/2008',
                'transfer': 'second',
                'description':'foo',
                'payee': 'bar',
                'amount': '1',
            },
        ]
        loader = DictLoader(app.doc.default_currency, 'first', txns)
        loader.start_account()
        loader.account_info.name = 'second'
        loader.flush_account()
        loader.load()
        app.doc.loader = loader
        app.doc.notify('file_loaded_for_import')
        return app
    
    @with_app(do_setup)
    def test_switch_date(self, app):
        # the transaction in the 2 accounts is the same. *don't* switch it twice!
        app.iwin.swap_type_index = SwapType.DayMonth
        app.iwin.perform_swap(apply_to_all=True)
        eq_(app.itable[0].date_import, '11/05/2008')
    
    @with_app(do_setup)
    def test_switch_description_payee(self, app):
        # same as with dates: don't switch twice
        app.iwin.swap_type_index = SwapType.DescriptionPayee
        app.iwin.perform_swap(apply_to_all=True)
        eq_(app.itable[0].description_import, 'bar')
        eq_(app.itable[0].payee_import, 'foo')
    
