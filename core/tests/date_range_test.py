# Created By: Virgil Dupras
# Created On: 2010-01-03
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.testutil import eq_, patch_today

from ..const import PaneType
from ..model.account import AccountType
from ..model.date import MonthRange, QuarterRange, YearRange, YearToDateRange
from .base import TestCase, TestApp, with_app, testdata

#--- Pristine
@with_app(TestApp)
def test_date_range(app):
    # By default, the date range is a yearly range for today.
    eq_(app.doc.date_range, YearRange(date.today()))

@with_app(TestApp)
def test_load_while_on_ytd_range(app):
    # Previously, the document would try to call around() on the current date range, even if not
    # navigable, causing a crash.
    app.drsel.select_year_to_date_range()
    filename = testdata.filepath('moneyguru/payee_description.moneyguru')
    app.doc.load_from_xml(filename) # no crash

@with_app(TestApp)
def test_all_transactions_range(app):
    # Selecting the All Transactions range when there's no transaction doesn't do anything.
    app.drsel.select_all_transactions_range() # no crash

@with_app(TestApp)
def test_set_ahead_months(app):
    # setting the ahead_months preference doesn't change the current date range type
    app.app.ahead_months = 5
    assert isinstance(app.doc.date_range, YearRange)

@with_app(TestApp)
def test_year_start_month_same_as_ahead_month(app):
    # There was a stupid bug where setting year_start_month to the same value as ahead_months
    # wouldn't work.
    app.app.year_start_month = 11 # I don't thin ahead_month's default is every gonna be 11.
    app.app.year_start_month = app.app.ahead_months
    eq_(app.app.year_start_month, app.app.ahead_months)

class RangeOnOctober2007(TestCase):
    def setUp(self):
        self.mock_today(2007, 10, 1)
        self.create_instances()
        self.drsel.select_month_range()
        self.clear_gui_calls()
    
    def test_close_and_load(self):
        # the date range start is remembered in preference
        self.close_and_load()
        eq_(self.document.date_range, MonthRange(date(2007, 10, 1)))
    
    def test_modified_flag(self):
        # Changing the date range does not change the modified flag.
        assert not self.document.is_dirty()
    
    def test_quarter_range(self):
        # When there is no selected entry, the selected range is based on the current date range.
        self.drsel.select_quarter_range()
        eq_(self.document.date_range, QuarterRange(date(2007, 10, 1)))
    
    def test_select_custom_date_range(self):
        self.drsel.select_custom_date_range()
        self.cdrpanel.start_date = '09/12/2008'
        self.cdrpanel.end_date = '18/02/2009'
        self.cdrpanel.save() # changes the date range
        eq_(self.document.date_range.start, date(2008, 12, 9))
        eq_(self.document.date_range.end, date(2009, 2, 18))
        eq_(self.document.date_range.display, '09/12/2008 - 18/02/2009')
        assert not self.document.date_range.can_navigate
    
    def test_select_custom_date_range_without_changing_the_dates(self):
        # When selecting a custom date range that has the same start/end as the previous one, it
        # still causes the change notification (so the DR display changes.
        self.drsel.select_custom_date_range()
        self.cdrpanel.save()
        eq_(self.document.date_range.display, '01/10/2007 - 31/10/2007')
    
    def test_select_prev_date_range(self):
        # If no account is selected, the range is not limited.
        try:
            self.drsel.select_prev_date_range()
        except Exception:
            raise AssertionError()
        eq_(self.document.date_range, MonthRange(date(2007, 9, 1)))
    
    def test_select_today_date_range(self):
        # the document's date range wraps around today's date
        self.drsel.select_today_date_range()
        dr = self.document.date_range
        assert dr.start <= date.today() <= dr.end
    
    def test_select_year_range(self):
        # Verify that the range changes.
        self.drsel.select_year_range()
        eq_(self.document.date_range, YearRange(date(2007, 1, 1)))
        # We don't ask the GUI to perform any animation
        self.check_gui_calls(self.drsel_gui, ['refresh'])
    
    def test_select_year_to_date_range(self):
        # Year-to-date starts at the first day of this year and ends today.
        self.drsel.select_year_to_date_range()
        eq_(self.document.date_range.start, date(date.today().year, 1, 1))
        eq_(self.document.date_range.end, date.today())
        eq_(self.document.date_range.display, 'Jan 2007 - Now')
    

#--- Range on year 2007
def app_range_on_year2007(monkeypatch):
    patch_today(monkeypatch, 2007, 1, 1)
    app = TestApp()
    return app

@with_app(app_range_on_year2007)
def test_month_range(app):
    # When there is no selected entry, the selected range is based on the current date range.
    app.drsel.select_month_range()
    eq_(app.doc.date_range, MonthRange(date(2007, 1, 1)))

class RangeOnYearStartsOnApril(TestCase):
    def setUp(self):
        self.mock_today(2007, 4, 1)
        self.create_instances()
        self.drsel.select_year_range()
        self.app.year_start_month = 4
    
    def test_add_entry(self):
        # When adding an entry, don't revert to a jan-dec based year range
        self.add_account()
        self.mainwindow.show_account()
        self.add_entry('01/01/2008') # in the same date range
        self.test_date_range() # date range hasn't changed
    
    def test_date_range(self):
        # when setting year_start_month at 4, the year range will start on april 1st
        eq_(self.document.date_range.start, date(2007, 4, 1))
        eq_(self.document.date_range.end, date(2008, 3, 31))
    
    def test_select_next_then_previous(self):
        # when navigating date ranges, preserve the year_start_month
        self.drsel.select_next_date_range()
        eq_(self.document.date_range.start, date(2008, 4, 1))
        self.drsel.select_prev_date_range()
        eq_(self.document.date_range.start, date(2007, 4, 1))
    

#---
def app_range_on_year_to_date(monkeypatch):
    patch_today(monkeypatch, 2008, 11, 12)
    app = TestApp()
    app.drsel.select_year_to_date_range()
    return app

@with_app(app_range_on_year_to_date)
def test_close_and_load(app):
    # The date range preference is correctly restored
    newapp = app.save_and_load()
    eq_(newapp.doc.date_range, YearToDateRange())

@with_app(app_range_on_year_to_date)
def test_select_next_prev_today_range(app):
    # next/prev/today do nothing in YTD
    app.drsel.select_next_date_range()
    eq_(app.doc.date_range.start, date(2008, 1, 1))
    app.drsel.select_prev_date_range()
    eq_(app.doc.date_range.start, date(2008, 1, 1))
    app.drsel.select_today_date_range()
    eq_(app.doc.date_range.start, date(2008, 1, 1))

@with_app(app_range_on_year_to_date)
def test_year_start_month_at_4(app):
    # when setting year_start_month at 4, the year-to-date range will start on april 1st
    app.app.year_start_month = 4
    eq_(app.doc.date_range.start, date(2008, 4, 1))
    eq_(app.doc.date_range.end, date(2008, 11, 12))

@with_app(app_range_on_year_to_date)
def test_year_start_month_at_12(app):
    # when the year_start_month is higher than the current month in YTD, the date range will
    # start in the previous year
    app.app.year_start_month = 12
    eq_(app.doc.date_range.start, date(2007, 12, 1))
    eq_(app.doc.date_range.end, date(2008, 11, 12))

@with_app(app_range_on_year_to_date)
def test_computations_for_prev_range_are_also_for_ytd(app):
    # In account sheets, the "Last" column shows data for last year *to date*, not the whole year.
    app.add_account('foo', account_type=AccountType.Expense)
    app.add_txn('01/01/2007', to='foo', amount='1') # in last-YTD range
    app.add_txn('01/12/2007', to='foo', amount='1') # out of last-YTD range
    app.mw.select_pane_of_type(PaneType.Profit)
    eq_(app.istatement.expenses[0].last_cash_flow, '1.00')

class RangeOnRunningYear(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2009, 1, 25)
        self.drsel.select_running_year_range()
        self.clear_gui_calls()
    
    def test_11_ahead_months(self):
        self.app.ahead_months = 11
        eq_(self.document.date_range.start, date(2009, 1, 1))
        eq_(self.document.date_range.end, date(2009, 12, 31))
    
    def test_add_entry(self):
        # _adjust_date_range() on save_edits() caused a crash
        self.add_account_legacy()
        self.etable.add()
        self.etable.save_edits() # no crash
    
    def test_date_range(self):
        # Running year (with the default 2 ahead months) starts 10 months in the past and ends 2 
        # months in the future, rounding the months. (default ahead_months is 2)
        eq_(self.document.date_range.start, date(2008, 4, 1))
        eq_(self.document.date_range.end, date(2009, 3, 31))
        eq_(self.document.date_range.display, 'Running year (Apr - Mar)')
    
    def test_prev_date_range(self):
        # prev_date_range() does nothing
        self.drsel.select_prev_date_range()
        eq_(self.document.date_range.start, date(2008, 4, 1))
    

class RangeOnRunningYearWithAheadMonths(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2009, 1, 25)
        self.app.ahead_months = 5
        self.drsel.select_running_year_range()
        self.clear_gui_calls()
    
    def test_date_range(self):
        # select_running_year_range() uses the ahead_months preference
        eq_(self.document.date_range.start, date(2008, 7, 1))
    

class CustomDateRange(TestCase):
    def setUp(self):
        self.create_instances()
        self.drsel.select_custom_date_range()
        self.cdrpanel.start_date = '09/12/2008'
        self.cdrpanel.end_date = '18/02/2009'
        self.cdrpanel.save() # changes the date range
    
    def test_close_and_load(self):
        # the custom date range's end date is kept in preferences.
        self.close_and_load()
        eq_(self.document.date_range.display, '09/12/2008 - 18/02/2009')
    

class OneEntryYearRange2007(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.mainwindow.show_account()
        self.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00', checkno='42')
        self.document.date_range = YearRange(date(2007, 1, 1))
    
    def test_select_month_range(self):
        # Make sure that the month range selection will be the first valid (contains at least one 
        # entry) range.
        self.drsel.select_month_range()
        eq_(self.document.date_range, MonthRange(date(2007, 10, 1)))
    
    def test_select_quarter_range(self):
        # Make sure that the quarter range selection will be the first valid (contains at least one 
        # entry) range.
        self.drsel.select_quarter_range()
        eq_(self.document.date_range, QuarterRange(date(2007, 10, 1)))
    
    def test_set_date_in_range(self):
        # Setting the date in range doesn't cause useless notifications.
        row = self.etable.selected_row
        row.dat = '11/10/2007'
        self.clear_gui_calls()
        self.etable.save_edits()
        self.check_gui_calls(self.drsel_gui, [])
    
    def test_set_date_out_of_range(self):
        # Setting the date out of range makes the app's date range change accordingly.
        row = self.etable.selected_row
        row.date = '1/1/2008'
        self.clear_gui_calls()
        self.etable.save_edits()
        eq_(self.document.date_range, YearRange(date(2008, 1, 1)))
        expected = ['animate_forward', 'refresh']
        self.check_gui_calls(self.drsel_gui, expected)
    

class TwoEntriesInDifferentQuartersWithYearRange(TestCase):
    # One account, two entries, one in January 2007, one in April 2007. The latest entry is 
    # selected. The range is Yearly, on 2007.
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.add_account()
        self.mainwindow.show_account()
        self.add_entry('1/1/2007', 'first', increase='1')
        self.add_entry('1/4/2007', 'second', increase='2')
    
    def test_select_quarter_range(self):
        # The selected quarter range is the range containing the selected entry, Q2.
        self.drsel.select_quarter_range()
        eq_(self.document.date_range, QuarterRange(date(2007, 4, 1)))
    
    def test_select_month_range(self):
        # The selected month range is the range containing the selected entry, April.
        self.drsel.select_month_range()
        eq_(self.document.date_range, MonthRange(date(2007, 4, 1)))
    

class TwoEntriesInTwoMonthsRangeOnSecond(TestCase):
    # One account, two entries in different months. The month range is on the second.
    # The selection is on the 2nd item (The first add_entry adds a Previous Balance, the second
    # add_entry adds a second item and selects it.)
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.mainwindow.show_account()
        self.add_entry('3/9/2007', 'first', increase='102.00')
        self.add_entry('10/10/2007', 'second', increase='42.00')
        self.document.date_range = MonthRange(date(2007, 10, 1))
        # When the second entry was added, the date was in the previous date range, making the
        # entry go *before* the Previous Entry, but we want the selection to be on the second item
        self.etable.select([1])
    
    def test_next_date_range(self):
        # drsel.select_next_date_range() makes the date range go one month later.
        self.document.date_range = MonthRange(date(2007, 9, 1))
        self.drsel.select_next_date_range()
        eq_(self.document.date_range, MonthRange(date(2007, 10, 1)))
    
    def test_prev_date_range(self):
        # app.select_prev_date_range() makes the date range go one month earlier.
        self.drsel.select_prev_date_range()
        eq_(self.document.date_range, MonthRange(date(2007, 9, 1)))
    

class AllTransactionsRangeWithOneTransactionFarInThePast(TestCase):
    def setUp(self):
        self.mock_today(2010, 1, 10)
        self.create_instances()
        self.add_txn('01/10/1981', from_='foo', to='bar', amount='42')
        self.add_txn('10/01/2010')
        self.drsel.select_all_transactions_range()
    
    def test_add_earlier_transaction(self):
        # Adding a transactions that's earlier than the current start date adjusts the range.
        self.add_txn('30/09/1981')
        eq_(self.ttable.row_count, 3)
    
    def test_includes_ahead_months(self):
        # All Transactions range end_date is computed using the ahead_months pref
        self.app.ahead_months = 3 # triggers a date range update
        self.add_txn('30/04/2010')
        eq_(self.ttable.row_count, 3)
        # but not further...
        self.add_txn('01/05/2010')
        eq_(self.ttable.row_count, 3)
    
    def test_income_statement_last_column(self):
        # the Last column of the income statement must show 0 (there's nothing before).
        self.mainwindow.select_income_statement()
        eq_(self.istatement.expenses.last_cash_flow, '0.00')
    
    def test_save_and_load(self):
        # When reloading a document, if the all transactions range was selected, it must be brought
        # back *after* transactions have been loaded.
        self.document = self.save_and_load(newapp=False)
        self.create_instances()
        self.mainwindow.select_transaction_table()
        eq_(self.ttable.row_count, 2)
    
    def test_transactions_are_shown(self):
        # When under All Transactions range, the range is big enough to contain all txns.
        eq_(self.ttable.row_count, 2)
    
