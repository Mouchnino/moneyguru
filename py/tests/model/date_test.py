# Created By: Eric Mc Sween
# Created On: 2007-12-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import unittest
from datetime import date

from hsutil.testcase import TestCase

from ...model.date import (parse_date, format_date, clean_format, DateRange, MonthRange,
    QuarterRange, YearRange, RunningYearRange)

class DateStuff(TestCase):
    def test_clean_format(self):
        self.assertEqual(clean_format('foobar'), 'dd/MM/yyyy') # fallback
        self.assertEqual(clean_format('yyyy-MM-ddfoobar'), 'yyyy-MM-dd') # just remove the garbage
        self.assertEqual(clean_format('yyyy.MM.ddfoobar'), 'yyyy.MM.dd') # keep the dot in
        self.assertEqual(clean_format('yy.M.d'), 'yy.M.d') # short versions are accepted
        # We don't end up with a format starting with '/'
        self.assertEqual(clean_format('EEEE/MMMM/dd/yyyy'), 'MM/dd/yyyy')
    
    def test_parse_date(self):
        self.assertEqual(parse_date('11/10/2007', 'dd/MM/yyyy'), date(2007, 10, 11))
        self.assertEqual(parse_date('02/01/2007', 'dd/MM/yyyy'), date(2007, 1, 2))
        self.assertEqual(parse_date('2007-01-02', 'yyyy-MM-dd'), date(2007, 1, 2))
        self.assertEqual(parse_date('07-01-02', 'yy-MM-dd'), date(2007, 1, 2))
        self.assertEqual(parse_date('07-1-2', 'yy-M-d'), date(2007, 1, 2))
    
    def test_format_date(self):
        self.assertEqual(format_date(date(2007, 10, 11), 'dd/MM/yyyy'), '11/10/2007')
        self.assertEqual(format_date(date(2007, 1, 2), 'dd/MM/yyyy'), '02/01/2007')
        self.assertEqual(format_date(date(2007, 1, 2), 'yyyy-MM-dd'), '2007-01-02')
        self.assertEqual(format_date(date(2007, 1, 2), 'yy-MM-dd'), '07-01-02')
        self.assertEqual(format_date(date(2007, 1, 2), 'yy-M-d'), '07-1-2')
    

class Ranges(TestCase):
    def setUp(self):
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
        self.assertEqual(self.january.start, date(2008, 1, 1))
        self.assertEqual(self.q1.start, date(2008, 1, 1))
        self.assertEqual(self.q2.start, date(2008, 4, 1))
        self.assertEqual(self.year2008.start, date(2008, 1, 1))

    def test_end(self):
        self.assertEqual(self.january.end, date(2008, 1, 31))
        self.assertEqual(self.february.end, date(2008, 2, 29))
        self.assertEqual(self.q1.end, date(2008, 3, 31))
        self.assertEqual(self.q2.end, date(2008, 6, 30))
        self.assertEqual(self.year2008.end, date(2008, 12, 31))

    def test_seed_with_range(self):
        self.assertEqual(QuarterRange(self.january), self.q1)
        self.assertEqual(YearRange(self.february), self.year2008)
        self.assertEqual(MonthRange(self.year2008), self.january)

    def test_eq_ne(self):
        self.assertEqual(MonthRange(date(2008, 1, 10)), self.january)
        self.assert_(MonthRange(date(2008, 2, 10)) != self.january) # assertNotEqual() doesn't seem to call __ne__

    def test_eq_with_other_types(self):
        self.assertRaises(TypeError, self.january.__eq__, "foo")
        self.assertRaises(TypeError, self.january.__ne__, "foo")

    def test_repr(self):
        self.assertEqual(repr(self.january), '<MonthRange 2008/01/01 - 2008/01/31>')

    def test_next(self):
        self.assertEqual(self.january.next(), self.february)
        self.assertEqual(self.december.next(), self.january2009)
        self.assertEqual(self.q1.next(), self.q2)
        self.assertEqual(self.q4.next(), self.q12009)
        self.assertEqual(self.year2008.next(), self.year2009)

    def test_prev(self):
        self.assertEqual(self.february.prev(), self.january)
        self.assertEqual(self.january2009.prev(), self.december)
        self.assertEqual(self.q2.prev(), self.q1)
        self.assertEqual(self.q12009.prev(), self.q4)
        self.assertEqual(self.year2009.prev(), self.year2008)

    def test_around(self):
        self.assertEqual(self.january.around(date(2008, 12, 2)), self.december)

    def test_contains(self):
        self.assertTrue(date(2008, 2, 2) in self.february)
        self.assertFalse(date(2008, 2, 2) in self.q2)

    def test_display(self):
        self.assertEqual(self.january.display, 'January 2008')
        self.assertEqual(self.february.display, 'February 2008')
        self.assertEqual(self.december.display, 'December 2008')
        self.assertEqual(self.january2009.display, 'January 2009')
        self.assertEqual(self.q1.display, 'Q1 2008')
        self.assertEqual(self.q2.display, 'Q2 2008')
        self.assertEqual(self.q12009.display, 'Q1 2009')
        self.assertEqual(self.q4.display, 'Q4 2008')
        self.assertEqual(self.year2008.display, '2008')
        self.assertEqual(self.year2009.display, '2009')
    
    def test_iter(self):
        # iter(date_ranges) iterates through every date present in the range
        result = list(self.january)
        self.assertEqual(len(result), 31)
        self.assertEqual(result[0], date(2008, 1, 1))
        self.assertEqual(result[-1], date(2008, 1, 31))
    

class RangesNoSetup(TestCase):
    def test_hash(self):
        # date ranges are hashable
        date_range1 = MonthRange(date(2008, 9, 1))
        date_range2 = MonthRange(date(2008, 9, 1))
        date_range3 = MonthRange(date(2008, 8, 1))
        self.assertTrue(date_range2 in set([date_range1]))
        self.assertFalse(date_range3 in set([date_range1]))
    
    def test_intersection(self):
        # dr1 & dr2 return a date range that is common to both or a NULL_DATE_RANGE
        dr1 = MonthRange(date(2008, 9, 1))
        dr2 = DateRange(date(2008, 8, 12), date(2008, 9, 8))
        dr3 = DateRange(date(2008, 9, 11), date(2008, 10, 13))
        dr4 = DateRange(date(2008, 9, 11), date(2008, 9, 13))
        self.assertEqual(dr1 & dr2, DateRange(date(2008, 9, 1), date(2008, 9, 8)))
        self.assertEqual(dr1 & dr3, DateRange(date(2008, 9, 11), date(2008, 9, 30)))
        self.assertEqual(dr1 & dr4, DateRange(date(2008, 9, 11), date(2008, 9, 13)))
        self.assertFalse(dr2 & dr3)
    
    def test_nonzero(self):
        # Only valid date ranges are non-zero
        self.assertTrue(MonthRange(date(2008, 9, 1)))
        self.assertFalse(DateRange(date(2008, 9, 2), date(2008, 9, 1)))
    
    def test_running_year(self):
        # The running year ends at the end of the current month and adds 'ahead_months' to it. the
        # start date is then one year earlier.
        self.mock_today(2009, 1, 25)
        dr = RunningYearRange(ahead_months=2)
        self.assertEqual(dr.end, date(2009, 3, 31))
        self.assertEqual(dr.start, date(2008, 4, 1))
        self.assertEqual(dr.display, 'Running year')
    

if __name__ == '__main__':
    unittest.main()
