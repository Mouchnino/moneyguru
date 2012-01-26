# Created By: Virgil Dupras
# Created On: 2010-01-03
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.testutil import eq_

from ..const import PaneType
from ..model.account import AccountType
from ..model.date import MonthRange, QuarterRange, YearRange, YearToDateRange
from .base import TestApp, with_app, testdata

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
    dpview = app.show_dpview()
    dpview.ahead_months_list.select(5)
    assert isinstance(app.doc.date_range, YearRange)

@with_app(TestApp)
def test_year_start_month_same_as_ahead_month(app):
    # There was a stupid bug where setting year_start_month to the same value as ahead_months
    # wouldn't work.
    dpview = app.show_dpview()
    dpview.year_start_month_list.select(11) # I don't think ahead_month's default is every gonna be 11.
    # +1 is because our actual year_start_month is always list-index + 1
    dpview.year_start_month_list.select(dpview.ahead_months_list.selected_index-1)
    eq_(app.doc.year_start_month, app.doc.ahead_months)

#---
class TestRangeOnOctober2007:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2007, 10, 1)
        app = TestApp()
        app.drsel.select_month_range()
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_close_and_load(self, app):
        # the date range start is remembered in preference
        app = app.close_and_load()
        eq_(app.doc.date_range, MonthRange(date(2007, 10, 1)))
    
    @with_app(do_setup)
    def test_modified_flag(self, app):
        # Changing the date range does not change the modified flag.
        assert not app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_quarter_range(self, app):
        # When there is no selected entry, the selected range is based on the current date range.
        app.drsel.select_quarter_range()
        eq_(app.doc.date_range, QuarterRange(date(2007, 10, 1)))
    
    @with_app(do_setup)
    def test_select_custom_date_range(self, app):
        app.drsel.select_custom_date_range()
        app.cdrpanel.start_date = '09/12/2008'
        app.cdrpanel.end_date = '18/02/2009'
        app.cdrpanel.save() # changes the date range
        eq_(app.doc.date_range.start, date(2008, 12, 9))
        eq_(app.doc.date_range.end, date(2009, 2, 18))
        eq_(app.doc.date_range.display, '09/12/2008 - 18/02/2009')
        assert not app.doc.date_range.can_navigate
    
    @with_app(do_setup)
    def test_select_custom_date_range_without_changing_the_dates(self, app):
        # When selecting a custom date range that has the same start/end as the previous one, it
        # still causes the change notification (so the DR display changes.
        app.drsel.select_custom_date_range()
        app.cdrpanel.save()
        eq_(app.doc.date_range.display, '01/10/2007 - 31/10/2007')
    
    @with_app(do_setup)
    def test_select_prev_date_range(self, app):
        # If no account is selected, the range is not limited.
        try:
            app.drsel.select_prev_date_range()
        except Exception:
            raise AssertionError()
        eq_(app.doc.date_range, MonthRange(date(2007, 9, 1)))
    
    @with_app(do_setup)
    def test_select_today_date_range(self, app):
        # the document's date range wraps around today's date
        app.drsel.select_today_date_range()
        dr = app.doc.date_range
        assert dr.start <= date.today() <= dr.end
    
    @with_app(do_setup)
    def test_select_year_range(self, app):
        # Verify that the range changes.
        app.drsel.select_year_range()
        eq_(app.doc.date_range, YearRange(date(2007, 1, 1)))
        # We don't ask the GUI to perform any animation
        app.drsel.view.check_gui_calls(['refresh'])
    
    @with_app(do_setup)
    def test_select_year_to_date_range(self, app):
        # Year-to-date starts at the first day of this year and ends today.
        app.drsel.select_year_to_date_range()
        eq_(app.doc.date_range.start, date(date.today().year, 1, 1))
        eq_(app.doc.date_range.end, date.today())
        eq_(app.doc.date_range.display, 'Jan 2007 - Now')
    

#--- Range on year 2007
def app_range_on_year2007(monkeypatch):
    monkeypatch.patch_today(2007, 1, 1)
    app = TestApp()
    return app

@with_app(app_range_on_year2007)
def test_month_range(app):
    # When there is no selected entry, the selected range is based on the current date range.
    app.drsel.select_month_range()
    eq_(app.doc.date_range, MonthRange(date(2007, 1, 1)))

#---
class TestRangeOnYearStartsOnApril:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2007, 4, 1)
        app = TestApp()
        app.drsel.select_year_range()
        app.dpview = app.show_dpview()
        app.dpview.year_start_month_list.select(3)
        return app
    
    @with_app(do_setup)
    def test_add_entry(self, app):
        # When adding an entry, don't revert to a jan-dec based year range
        app.add_account()
        app.mainwindow.show_account()
        app.add_entry('01/01/2008') # in the same date range
        # date range hasn't changed
        eq_(app.doc.date_range.start, date(2007, 4, 1))
        eq_(app.doc.date_range.end, date(2008, 3, 31))
    
    @with_app(do_setup)
    def test_date_range(self, app):
        # when setting year_start_month at 4, the year range will start on april 1st
        eq_(app.doc.date_range.start, date(2007, 4, 1))
        eq_(app.doc.date_range.end, date(2008, 3, 31))
    
    @with_app(do_setup)
    def test_select_next_then_previous(self, app):
        # when navigating date ranges, preserve the year_start_month
        app.drsel.select_next_date_range()
        eq_(app.doc.date_range.start, date(2008, 4, 1))
        app.drsel.select_prev_date_range()
        eq_(app.doc.date_range.start, date(2007, 4, 1))
    

#---
def app_range_on_year_to_date(monkeypatch):
    monkeypatch.patch_today(2008, 11, 12)
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
    dpview = app.show_dpview()
    dpview.year_start_month_list.select(3)
    eq_(app.doc.date_range.start, date(2008, 4, 1))
    eq_(app.doc.date_range.end, date(2008, 11, 12))

@with_app(app_range_on_year_to_date)
def test_year_start_month_at_12(app):
    # when the year_start_month is higher than the current month in YTD, the date range will
    # start in the previous year
    dpview = app.show_dpview()
    dpview.year_start_month_list.select(11)
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

#---
class TestRangeOnRunningYear:
    def do_setup(self, monkeypatch):
        app = TestApp()
        monkeypatch.patch_today(2009, 1, 25)
        app.drsel.select_running_year_range()
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_11_ahead_months(self, app):
        dpview = app.show_dpview()
        dpview.ahead_months_list.select(11)
        eq_(app.doc.date_range.start, date(2008, 12, 1))
        eq_(app.doc.date_range.end, date(2009, 11, 30))
    
    @with_app(do_setup)
    def test_0_ahead_months(self, app):
        # When ahead month is 0, we end our range today. The start date is the first day of our
        # current month.
        dpview = app.show_dpview()
        dpview.ahead_months_list.select(0)
        eq_(app.doc.date_range.start, date(2008, 2, 1))
        eq_(app.doc.date_range.end, date(2009, 1, 25))
    
    @with_app(do_setup)
    def test_add_entry(self, app):
        # _adjust_date_range() on save_edits() caused a crash
        app.add_account()
        app.mw.show_account()
        app.etable.add()
        app.etable.save_edits() # no crash
    
    @with_app(do_setup)
    def test_date_range(self, app):
        # Running year (with the default 3 ahead months) starts 10 months in the past and ends 2 
        # months in the future, rounding the months. (default ahead_months is 2)
        eq_(app.doc.date_range.start, date(2008, 4, 1))
        eq_(app.doc.date_range.end, date(2009, 3, 31))
        eq_(app.doc.date_range.display, 'Running year (Apr - Mar)')
    
    @with_app(do_setup)
    def test_prev_date_range(self, app):
        # prev_date_range() does nothing
        app.drsel.select_prev_date_range()
        eq_(app.doc.date_range.start, date(2008, 4, 1))
    
#---
class TestRangeOnRunningYearWithAheadMonths:
    def do_setup(self, monkeypatch):
        app = TestApp()
        monkeypatch.patch_today(2009, 1, 25)
        dpview = app.show_dpview()
        dpview.ahead_months_list.select(5)
        app.drsel.select_running_year_range()
        app.clear_gui_calls()
        return app
    
    @with_app(do_setup)
    def test_date_range(self, app):
        # select_running_year_range() uses the ahead_months preference
        eq_(app.doc.date_range.start, date(2008, 6, 1))
    

#---
class TestCustomDateRange:
    def do_setup(self):
        app = TestApp()
        app.drsel.select_custom_date_range()
        app.cdrpanel.start_date = '09/12/2008'
        app.cdrpanel.end_date = '18/02/2009'
        app.cdrpanel.save() # changes the date range
        return app
    
    @with_app(do_setup)
    def test_close_and_load(self, app):
        # the custom date range's end date is kept in preferences.
        app = app.close_and_load()
        eq_(app.doc.date_range.display, '09/12/2008 - 18/02/2009')
    

#---
class TestOneEntryYearRange2007:
    def do_setup(self):
        app = TestApp()
        app.add_account('Checking')
        app.mainwindow.show_account()
        app.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00', checkno='42')
        app.doc.date_range = YearRange(date(2007, 1, 1))
        return app
    
    @with_app(do_setup)
    def test_select_month_range(self, app):
        # Make sure that the month range selection will be the first valid (contains at least one 
        # entry) range.
        app.drsel.select_month_range()
        eq_(app.doc.date_range, MonthRange(date(2007, 10, 1)))
    
    @with_app(do_setup)
    def test_select_quarter_range(self, app):
        # Make sure that the quarter range selection will be the first valid (contains at least one 
        # entry) range.
        app.drsel.select_quarter_range()
        eq_(app.doc.date_range, QuarterRange(date(2007, 10, 1)))
    
    @with_app(do_setup)
    def test_set_date_in_range(self, app):
        # Setting the date in range doesn't cause useless notifications.
        row = app.etable.selected_row
        row.dat = '11/10/2007'
        app.clear_gui_calls()
        app.etable.save_edits()
        app.drsel.view.check_gui_calls([])
    
    @with_app(do_setup)
    def test_set_date_out_of_range(self, app):
        # Setting the date out of range makes the app's date range change accordingly.
        row = app.etable.selected_row
        row.date = '1/1/2008'
        app.clear_gui_calls()
        app.etable.save_edits()
        eq_(app.doc.date_range, YearRange(date(2008, 1, 1)))
        expected = ['animate_forward', 'refresh']
        app.drsel.view.check_gui_calls(expected)
    

#---
class TestTwoEntriesInDifferentQuartersWithYearRange:
    # One account, two entries, one in January 2007, one in April 2007. The latest entry is 
    # selected. The range is Yearly, on 2007.
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = YearRange(date(2007, 1, 1))
        app.add_account()
        app.mainwindow.show_account()
        app.add_entry('1/1/2007', 'first', increase='1')
        app.add_entry('1/4/2007', 'second', increase='2')
        return app
    
    @with_app(do_setup)
    def test_select_quarter_range(self, app):
        # The selected quarter range is the range containing the selected entry, Q2.
        app.drsel.select_quarter_range()
        eq_(app.doc.date_range, QuarterRange(date(2007, 4, 1)))
    
    @with_app(do_setup)
    def test_select_month_range(self, app):
        # The selected month range is the range containing the selected entry, April.
        app.drsel.select_month_range()
        eq_(app.doc.date_range, MonthRange(date(2007, 4, 1)))
    

#---
class TestTwoEntriesInTwoMonthsRangeOnSecond:
    # One account, two entries in different months. The month range is on the second.
    # The selection is on the 2nd item (The first add_entry adds a Previous Balance, the second
    # add_entry adds a second item and selects it.)
    def do_setup(self):
        app = TestApp()
        app.add_account('Checking')
        app.mainwindow.show_account()
        app.add_entry('3/9/2007', 'first', increase='102.00')
        app.add_entry('10/10/2007', 'second', increase='42.00')
        app.doc.date_range = MonthRange(date(2007, 10, 1))
        # When the second entry was added, the date was in the previous date range, making the
        # entry go *before* the Previous Entry, but we want the selection to be on the second item
        app.etable.select([1])
        return app
    
    @with_app(do_setup)
    def test_next_date_range(self, app):
        # drsel.select_next_date_range() makes the date range go one month later.
        app.doc.date_range = MonthRange(date(2007, 9, 1))
        app.drsel.select_next_date_range()
        eq_(app.doc.date_range, MonthRange(date(2007, 10, 1)))
    
    @with_app(do_setup)
    def test_prev_date_range(self, app):
        # app.select_prev_date_range() makes the date range go one month earlier.
        app.drsel.select_prev_date_range()
        eq_(app.doc.date_range, MonthRange(date(2007, 9, 1)))
    

#---
class TestAllTransactionsRangeWithOneTransactionFarInThePast:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2010, 1, 10)
        app = TestApp()
        app.add_txn('01/10/1981', from_='foo', to='bar', amount='42')
        app.add_txn('10/01/2010')
        app.drsel.select_all_transactions_range()
        return app
    
    @with_app(do_setup)
    def test_add_earlier_transaction(self, app):
        # Adding a transactions that's earlier than the current start date adjusts the range.
        app.add_txn('30/09/1981')
        eq_(app.ttable.row_count, 3)
    
    @with_app(do_setup)
    def test_includes_ahead_months(self, app):
        # All Transactions range end_date is computed using the ahead_months pref
        dpview = app.show_dpview()
        dpview.ahead_months_list.select(4) # triggers a date range update
        app.add_txn('30/04/2010')
        eq_(app.ttable.row_count, 3)
        # but not further...
        app.add_txn('01/05/2010')
        eq_(app.ttable.row_count, 3)
    
    @with_app(do_setup)
    def test_income_statement_last_column(self, app):
        # the Last column of the income statement must show 0 (there's nothing before).
        app.show_pview()
        eq_(app.istatement.expenses.last_cash_flow, '0.00')
    
    @with_app(do_setup)
    def test_save_and_load(self, app):
        # When reloading a document, if the all transactions range was selected, it must be brought
        # back *after* transactions have been loaded.
        newapp = app.save_and_load()
        newapp.show_tview()
        eq_(newapp.ttable.row_count, 2)
    
    @with_app(do_setup)
    def test_transactions_are_shown(self, app):
        # When under All Transactions range, the range is big enough to contain all txns.
        eq_(app.ttable.row_count, 2)
    
