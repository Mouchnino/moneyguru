# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-03
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_

from ..model.date import MonthRange, QuarterRange, YearRange, YearToDateRange
from .base import TestCase

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
    
    def test_date_range(self):
        # By default, the date range is a yearly range for today.
        eq_(self.document.date_range, YearRange(date.today()))
    
    def test_load_while_on_ytd_range(self):
        # Previously, the document would try to call around() on the current date range, even if not
        # navigable, causing a crash.
        self.document.select_year_to_date_range()
        filename = self.filepath('moneyguru/payee_description.moneyguru')
        self.document.load_from_xml(filename) # no crash
    
    def test_set_ahead_months(self):
        # setting the ahead_months preference doesn't change the current date range type
        self.app.ahead_months = 5
        assert isinstance(self.document.date_range, YearRange)
    

class RangeOnOctober2007(TestCase):
    def setUp(self):
        self.mock_today(2007, 10, 1)
        self.create_instances()
        self.document.select_month_range()
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
        self.document.select_quarter_range()
        eq_(self.document.date_range, QuarterRange(date(2007, 10, 1)))
    
    def test_select_custom_date_range(self):
        self.document.select_custom_date_range()
        self.check_gui_calls(self.mainwindow_gui, ['show_custom_date_range_panel'])
        self.cdrpanel.start_date = '09/12/2008'
        self.cdrpanel.end_date = '18/02/2009'
        self.cdrpanel.ok() # changes the date range
        eq_(self.document.date_range.start, date(2008, 12, 9))
        eq_(self.document.date_range.end, date(2009, 2, 18))
        eq_(self.document.date_range.display, '09/12/2008 - 18/02/2009')
        assert not self.document.date_range.can_navigate
    
    def test_select_custom_date_range_without_changing_the_dates(self):
        # When selecting a custom date range that has the same start/end as the previous one, it
        # still causes the change notification (so the DR display changes.
        self.document.select_custom_date_range()
        self.cdrpanel.ok()
        eq_(self.document.date_range.display, '01/10/2007 - 31/10/2007')
    
    def test_select_prev_date_range(self):
        # If no account is selected, the range is not limited.
        try:
            self.document.select_prev_date_range()
        except Exception:
            raise AssertionError()
        eq_(self.document.date_range, MonthRange(date(2007, 9, 1)))
    
    def test_select_today_date_range(self):
        # the document's date range wraps around today's date
        self.document.select_today_date_range()
        dr = self.document.date_range
        assert dr.start <= date.today() <= dr.end
    
    def test_select_year_range(self):
        # Verify that the range changes.
        self.document.select_year_range()
        eq_(self.document.date_range, YearRange(date(2007, 1, 1)))
        # We don't ask the GUI to perform any animation
        self.check_gui_calls(self.mainwindow_gui, ['refresh_date_range_selector'])
    
    def test_select_year_to_date_range(self):
        # Year-to-date starts at the first day of this year and ends today.
        self.document.select_year_to_date_range()
        eq_(self.document.date_range.start, date(date.today().year, 1, 1))
        eq_(self.document.date_range.end, date.today())
        eq_(self.document.date_range.display, 'Jan 2007 - Now')
    

class RangeOnYear2007(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
    
    def test_month_range(self):
        # When there is no selected entry, the selected range is based on the current date range.
        self.document.select_month_range()
        eq_(self.document.date_range, MonthRange(date(2007, 1, 1)))
    

class RangeOnYearStartsOnApril(TestCase):
    def setUp(self):
        self.mock_today(2007, 4, 1)
        self.create_instances()
        self.document.select_year_range()
        self.app.year_start_month = 4
    
    def test_add_entry(self):
        # When adding an entry, don't revert to a jan-dec based year range
        self.add_account()
        self.document.show_selected_account()
        self.add_entry('01/01/2008') # in the same date range
        self.test_date_range() # date range hasn't changed
    
    def test_date_range(self):
        # when setting year_start_month at 4, the year range will start on april 1st
        eq_(self.document.date_range.start, date(2007, 4, 1))
        eq_(self.document.date_range.end, date(2008, 3, 31))
    
    def test_select_next_then_previous(self):
        # when navigating date ranges, preserve the year_start_month
        self.document.select_next_date_range()
        eq_(self.document.date_range.start, date(2008, 4, 1))
        self.document.select_prev_date_range()
        eq_(self.document.date_range.start, date(2007, 4, 1))
    

class RangeOnYearToDate(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2008, 11, 12)
        self.document.select_year_to_date_range()
    
    def test_close_and_load(self):
        # The date range preference is correctly restored
        self.close_and_load()
        eq_(self.document.date_range, YearToDateRange())
    
    def test_select_next_prev_today_range(self):
        # next/prev/today do nothing in YTD
        self.document.select_next_date_range()
        eq_(self.document.date_range.start, date(2008, 1, 1))
        self.document.select_prev_date_range()
        eq_(self.document.date_range.start, date(2008, 1, 1))
        self.document.select_today_date_range()
        eq_(self.document.date_range.start, date(2008, 1, 1))
    
    def test_year_start_month_at_4(self):
        # when setting year_start_month at 4, the year-to-date range will start on april 1st
        self.app.year_start_month = 4
        eq_(self.document.date_range.start, date(2008, 4, 1))
        eq_(self.document.date_range.end, date(2008, 11, 12))
    
    def test_year_start_month_at_12(self):
        # when the year_start_month is higher than the current month in YTD, the date range will
        # start in the previous year
        self.app.year_start_month = 12
        eq_(self.document.date_range.start, date(2007, 12, 1))
        eq_(self.document.date_range.end, date(2008, 11, 12))
    

class RangeOnRunningYear(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2009, 1, 25)
        self.document.select_running_year_range()
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
        self.document.select_prev_date_range()
        eq_(self.document.date_range.start, date(2008, 4, 1))
    

class RangeOnRunningYearWithAheadMonths(TestCase):
    def setUp(self):
        self.create_instances()
        self.mock_today(2009, 1, 25)
        self.app.ahead_months = 5
        self.document.select_running_year_range()
        self.clear_gui_calls()
    
    def test_date_range(self):
        # select_running_year_range() uses the ahead_months preference
        eq_(self.document.date_range.start, date(2008, 7, 1))
    

class CustomDateRange(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.select_custom_date_range()
        self.cdrpanel.start_date = '09/12/2008'
        self.cdrpanel.end_date = '18/02/2009'
        self.cdrpanel.ok() # changes the date range
    
    def test_close_and_load(self):
        # the custom date range's end date is kept in preferences.
        self.close_and_load()
        eq_(self.document.date_range.display, '09/12/2008 - 18/02/2009')
    

class OneEntryYearRange2007(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.document.show_selected_account()
        self.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00', checkno='42')
        self.document.date_range = YearRange(date(2007, 1, 1))
    
    def test_select_month_range(self):
        # Make sure that the month range selection will be the first valid (contains at least one 
        # entry) range.
        self.document.select_month_range()
        eq_(self.document.date_range, MonthRange(date(2007, 10, 1)))
    
    def test_select_quarter_range(self):
        # Make sure that the quarter range selection will be the first valid (contains at least one 
        # entry) range.
        self.document.select_quarter_range()
        eq_(self.document.date_range, QuarterRange(date(2007, 10, 1)))
    
    def test_set_date_in_range(self):
        # Setting the date in range doesn't cause useless notifications.
        row = self.etable.selected_row
        row.dat = '11/10/2007'
        self.clear_gui_calls()
        self.etable.save_edits()
        not_expected = ['animate_date_range_backward', 'animate_date_range_forward',
            'refresh_date_range_selector']
        self.check_gui_calls_partial(self.mainwindow_gui, not_expected=not_expected)
    
    def test_set_date_out_of_range(self):
        # Setting the date out of range makes the app's date range change accordingly.
        row = self.etable.selected_row
        row.date = '1/1/2008'
        self.clear_gui_calls()
        self.etable.save_edits()
        eq_(self.document.date_range, YearRange(date(2008, 1, 1)))
        expected = ['animate_date_range_forward', 'refresh_date_range_selector']
        self.check_gui_calls_partial(self.mainwindow_gui, expected)
    

class TwoEntriesInDifferentQuartersWithYearRange(TestCase):
    # One account, two entries, one in January 2007, one in April 2007. The latest entry is 
    # selected. The range is Yearly, on 2007.
    def setUp(self):
        self.create_instances()
        self.document.date_range = YearRange(date(2007, 1, 1))
        self.add_account()
        self.document.show_selected_account()
        self.add_entry('1/1/2007', 'first', increase='1')
        self.add_entry('1/4/2007', 'second', increase='2')
    
    def test_select_quarter_range(self):
        # The selected quarter range is the range containing the selected entry, Q2.
        self.document.select_quarter_range()
        eq_(self.document.date_range, QuarterRange(date(2007, 4, 1)))
    
    def test_select_month_range(self):
        # The selected month range is the range containing the selected entry, April.
        self.document.select_month_range()
        eq_(self.document.date_range, MonthRange(date(2007, 4, 1)))
    

class TwoEntriesInTwoMonthsRangeOnSecond(TestCase):
    # One account, two entries in different months. The month range is on the second.
    # The selection is on the 2nd item (The first add_entry adds a Previous Balance, the second
    # add_entry adds a second item and selects it.)
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.document.show_selected_account()
        self.add_entry('3/9/2007', 'first', increase='102.00')
        self.add_entry('10/10/2007', 'second', increase='42.00')
        self.document.date_range = MonthRange(date(2007, 10, 1))
        # When the second entry was added, the date was in the previous date range, making the
        # entry go *before* the Previous Entry, but we want the selection to be on the second item
        self.etable.select([1])
    
    def test_next_date_range(self):
        # document.select_next_date_range() makes the date range go one month later.
        self.document.date_range = MonthRange(date(2007, 9, 1))
        self.document.select_next_date_range()
        eq_(self.document.date_range, MonthRange(date(2007, 10, 1)))
    
    def test_prev_date_range(self):
        # app.select_prev_date_range() makes the date range go one month earlier.
        self.document.select_prev_date_range()
        eq_(self.document.date_range, MonthRange(date(2007, 9, 1)))
    
