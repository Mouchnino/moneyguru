# Created By: Eric Mc Sween
# Created On: 2007-12-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from pytest import raises
from hscommon.testutil import eq_, patch_today

from ...model.date import (parse_date, format_date, clean_format, DateRange, MonthRange,
    QuarterRange, YearRange, RunningYearRange, YearToDateRange)

class TestDateStuff:
    def test_clean_format(self):
        eq_(clean_format('foobar'), 'dd/MM/yyyy') # fallback
        eq_(clean_format('yyyy-MM-ddfoobar'), 'yyyy-MM-dd') # just remove the garbage
        eq_(clean_format('yyyy.MM.ddfoobar'), 'yyyy.MM.dd') # keep the dot in
        eq_(clean_format('yy.M.d'), 'yy.M.d') # short versions are accepted
        # We don't end up with a format starting with '/'
        eq_(clean_format('EEEE/MMMM/dd/yyyy'), 'MM/dd/yyyy')
    
    def test_parse_date(self):
        eq_(parse_date('11/10/2007', 'dd/MM/yyyy'), date(2007, 10, 11))
        eq_(parse_date('02/01/2007', 'dd/MM/yyyy'), date(2007, 1, 2))
        eq_(parse_date('2007-01-02', 'yyyy-MM-dd'), date(2007, 1, 2))
        eq_(parse_date('07-01-02', 'yy-MM-dd'), date(2007, 1, 2))
        eq_(parse_date('07-1-2', 'yy-M-d'), date(2007, 1, 2))
    
    def test_format_date(self):
        eq_(format_date(date(2007, 10, 11), 'dd/MM/yyyy'), '11/10/2007')
        eq_(format_date(date(2007, 1, 2), 'dd/MM/yyyy'), '02/01/2007')
        eq_(format_date(date(2007, 1, 2), 'yyyy-MM-dd'), '2007-01-02')
        eq_(format_date(date(2007, 1, 2), 'yy-MM-dd'), '07-01-02')
        eq_(format_date(date(2007, 1, 2), 'yy-M-d'), '07-1-2')
    

class TestRanges:
    def setup_method(self, method):
        self.january = MonthRange(date(2008, 1, 1))
        self.february = MonthRange(date(2008, 2, 10))
        self.december = MonthRange(date(2008, 12, 12))
        self.january2009 = MonthRange(date(2009, 1, 12))
        self.q1 = QuarterRange(date(2008, 2, 10))
        self.q2 = QuarterRange(date(2008, 6, 11))
        self.q4 = QuarterRange(date(2008, 11, 5))
        self.q12009 = QuarterRange(date(2009, 1, 10))
        self.year2008 = YearRange(date(2008, 3, 21))
        self.year2009 = YearRange(date(2009, 4, 4))

    def test_start(self):
        eq_(self.january.start, date(2008, 1, 1))
        eq_(self.q1.start, date(2008, 1, 1))
        eq_(self.q2.start, date(2008, 4, 1))
        eq_(self.year2008.start, date(2008, 1, 1))

    def test_end(self):
        eq_(self.january.end, date(2008, 1, 31))
        eq_(self.february.end, date(2008, 2, 29))
        eq_(self.q1.end, date(2008, 3, 31))
        eq_(self.q2.end, date(2008, 6, 30))
        eq_(self.year2008.end, date(2008, 12, 31))

    def test_seed_with_range(self):
        eq_(QuarterRange(self.january), self.q1)
        eq_(YearRange(self.february), self.year2008)
        eq_(MonthRange(self.year2008), self.january)

    def test_eq_ne(self):
        eq_(MonthRange(date(2008, 1, 10)), self.january)
        assert MonthRange(date(2008, 2, 10)) != self.january # assertNotEqual() doesn't seem to call __ne__

    def test_eq_with_other_types(self):
        with raises(TypeError):
            self.january == 'foo'
        with raises(TypeError):
            self.january != 'foo'

    def test_repr(self):
        eq_(repr(self.january), '<MonthRange 2008/01/01 - 2008/01/31>')

    def test_next(self):
        eq_(self.january.next(), self.february)
        eq_(self.december.next(), self.january2009)
        eq_(self.q1.next(), self.q2)
        eq_(self.q4.next(), self.q12009)
        eq_(self.year2008.next(), self.year2009)

    def test_prev(self):
        eq_(self.february.prev(), self.january)
        eq_(self.january2009.prev(), self.december)
        eq_(self.q2.prev(), self.q1)
        eq_(self.q12009.prev(), self.q4)
        eq_(self.year2009.prev(), self.year2008)

    def test_around(self):
        eq_(self.january.around(date(2008, 12, 2)), self.december)

    def test_contains(self):
        assert date(2008, 2, 2) in self.february
        assert not date(2008, 2, 2) in self.q2

    def test_display(self):
        eq_(self.january.display, 'January 2008')
        eq_(self.february.display, 'February 2008')
        eq_(self.december.display, 'December 2008')
        eq_(self.january2009.display, 'January 2009')
        eq_(self.q1.display, 'Q1 2008')
        eq_(self.q2.display, 'Q2 2008')
        eq_(self.q12009.display, 'Q1 2009')
        eq_(self.q4.display, 'Q4 2008')
        eq_(self.year2008.display, 'Jan 2008 - Dec 2008')
        eq_(self.year2009.display, 'Jan 2009 - Dec 2009')
    
    def test_iter(self):
        # iter(date_ranges) iterates through every date present in the range
        result = list(self.january)
        eq_(len(result), 31)
        eq_(result[0], date(2008, 1, 1))
        eq_(result[-1], date(2008, 1, 31))
    

class TestRangesNoSetup:
    def test_hash(self):
        # date ranges are hashable
        date_range1 = MonthRange(date(2008, 9, 1))
        date_range2 = MonthRange(date(2008, 9, 1))
        date_range3 = MonthRange(date(2008, 8, 1))
        assert date_range2 in set([date_range1])
        assert not date_range3 in set([date_range1])
    
    def test_intersection(self):
        # dr1 & dr2 return a date range that is common to both or a NULL_DATE_RANGE
        dr1 = MonthRange(date(2008, 9, 1))
        dr2 = DateRange(date(2008, 8, 12), date(2008, 9, 8))
        dr3 = DateRange(date(2008, 9, 11), date(2008, 10, 13))
        dr4 = DateRange(date(2008, 9, 11), date(2008, 9, 13))
        eq_(dr1 & dr2, DateRange(date(2008, 9, 1), date(2008, 9, 8)))
        eq_(dr1 & dr3, DateRange(date(2008, 9, 11), date(2008, 9, 30)))
        eq_(dr1 & dr4, DateRange(date(2008, 9, 11), date(2008, 9, 13)))
        assert not dr2 & dr3
    
    def test_nonzero(self):
        # Only valid date ranges are non-zero
        assert MonthRange(date(2008, 9, 1))
        assert not DateRange(date(2008, 9, 2), date(2008, 9, 1))
    
    def test_running_year(self, monkeypatch):
        # The running year ends at the end of the current month and adds 'ahead_months' to it. the
        # start date is then one year earlier.
        patch_today(monkeypatch, 2009, 1, 25)
        dr = RunningYearRange(ahead_months=2)
        eq_(dr.end, date(2009, 3, 31))
        eq_(dr.start, date(2008, 4, 1))
        eq_(dr.display, 'Running year (Apr - Mar)')
    
    def test_year_to_date(self, monkeypatch):
        patch_today(monkeypatch, 2009, 10, 7)
        dr = YearToDateRange(year_start_month=2)
        eq_(dr.display, 'Feb 2009 - Now')
    
    def test_year_with_start_month(self):
        dr = YearRange(date(2009, 10, 7), year_start_month=5)
        eq_(dr.display, 'May 2009 - Apr 2010')
    
