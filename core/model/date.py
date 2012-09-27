# Created By: Eric Mc Sween
# Created On: 2007-12-12
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import re
from calendar import monthrange
from datetime import date, datetime, timedelta

from hscommon.trans import tr

ONE_DAY = timedelta(1)

#--- Date Ranges

class DateRange:
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __repr__(self):
        start_date_str = self.start.strftime('%Y/%m/%d') if self.start.year > 1900 else 'MINDATE'
        return '<%s %s - %s>' % (type(self).__name__, start_date_str, self.end.strftime('%Y/%m/%d'))
    
    def __bool__(self):
        return self.start <= self.end
    
    def __and__(self, other):
        maxstart = max(self.start, other.start)
        minend = min(self.end, other.end)
        return DateRange(maxstart, minend)
    
    def __eq__(self, other):
        if not isinstance(other, DateRange):
            raise TypeError()
        return type(self) == type(other) and self.start == other.start and self.end == other.end
    
    def __ne__(self, other):
        return not self == other
    
    def __contains__(self, date):
        return self.start <= date <= self.end
    
    def __iter__(self):
        date = self.start
        end = self.end
        while date <= end:
            yield date
            date += ONE_DAY
    
    def __hash__(self):
        return hash((self.start, self.end))
    
    def adjusted(self, new_date):
        # Some date ranges change when new transactions are beind added or changed. This is where
        # it happens. Returns a new adjusted date range or None.
        return None
    
    def around(self, date):
        return self

    def next(self):
        return self

    def prev(self):
        return self
    
    @property
    def can_navigate(self): # if it's possible to use prev/next to navigate in date ranges
        return False
    
    @property
    def days(self):
        """The number of days in the date range.
        """
        return (self.end - self.start).days + 1
    
    @property
    def future(self):
        """The future part of the date range.
        """
        today = date.today()
        if self.start > today:
            return self
        else:
            return DateRange(today + ONE_DAY, self.end)
    
    @property
    def past(self):
        """The past part of the date range.
        """
        today = date.today()
        if self.end < today:
            return self
        else:
            return DateRange(self.start, today)
    

class NavigableDateRange(DateRange):
    def adjusted(self, new_date):
        result = self.around(new_date)
        if result == self:
            result = None
        return result
    
    def around(self, date):
        return type(self)(date)
    
    def next(self):
        return self.around(self.end + ONE_DAY)
    
    def prev(self):
        return self.around(self.start - ONE_DAY)
    
    @property
    def can_navigate(self): # if it's possible to use prev/next to navigate in date ranges
        return True
    

class MonthRange(NavigableDateRange):
    def __init__(self, seed):
        if isinstance(seed, DateRange):
            seed = seed.start
        month = seed.month
        year = seed.year
        days_in_month = monthrange(year, month)[1]
        start = date(year, month, 1)
        end = date(year, month, days_in_month)
        DateRange.__init__(self, start, end)
    
    @property
    def display(self):
        return self.start.strftime('%B %Y')
    

class QuarterRange(NavigableDateRange):
    def __init__(self, seed):
        if isinstance(seed, DateRange):
            seed = seed.start
        month = seed.month
        year = seed.year
        first_month = (month - 1) // 3 * 3 + 1
        last_month = first_month + 2
        days_in_last_month = monthrange(year, last_month)[1]
        start = date(year, first_month, 1)
        end = date(year, last_month, days_in_last_month)
        DateRange.__init__(self, start, end)
    
    @property
    def display(self):
        return tr('Q{0} {1}').format(self.start.month // 3 + 1, self.start.year)
    

class YearRange(NavigableDateRange):
    def __init__(self, seed, year_start_month=1):
        assert 1 <= year_start_month <= 12
        if isinstance(seed, DateRange):
            seed = seed.start
        year = seed.year
        if seed.month < year_start_month:
            year -= 1
        start = date(year, year_start_month, 1)
        end = inc_year(start, 1) - ONE_DAY
        DateRange.__init__(self, start, end)
    
    def around(self, date):
        return type(self)(date, year_start_month=self.start.month)
    
    def next(self):
        return YearRange(inc_year(self.start, 1), year_start_month=self.start.month)
    
    def prev(self):
        return YearRange(inc_year(self.start, -1), year_start_month=self.start.month)
    
    @property
    def display(self):
        return '{0} - {1}'.format(self.start.strftime('%b %Y'), self.end.strftime('%b %Y'))
    

class YearToDateRange(DateRange):
    def __init__(self, year_start_month=1):
        start_year = date.today().year
        if date.today().month < year_start_month:
            start_year -= 1
        start = date(start_year, year_start_month, 1)
        end = date.today()
        DateRange.__init__(self, start, end)
    
    def prev(self): # for income statement's Last column
        start = inc_year(self.start, -1)
        end = inc_year(self.end, -1)
        return DateRange(start, end)
    
    @property
    def display(self):
        return tr('{0} - Now').format(self.start.strftime('%b %Y'))
    

def compute_ahead_months(ahead_months):
    assert ahead_months < 12
    if ahead_months == 0:
        return date.today()
    month_range = MonthRange(date.today())
    for _ in range(ahead_months-1):
        month_range = month_range.next()
    return month_range.end

class RunningYearRange(DateRange):
    def __init__(self, ahead_months):
        end = compute_ahead_months(ahead_months)
        end_plus_one = end + ONE_DAY
        start = end_plus_one.replace(year=end_plus_one.year-1)
        if start.day != 1:
            start = inc_month(start, 1).replace(day=1)
        DateRange.__init__(self, start, end)
    
    def prev(self): # for income statement's Last column
        start = self.start.replace(year=self.start.year - 1)
        end = self.start - ONE_DAY
        return DateRange(start, end)
    
    @property
    def display(self):
        return tr('Running year ({0} - {1})').format(self.start.strftime('%b'), self.end.strftime('%b'))
    

class AllTransactionsRange(DateRange):
    def __init__(self, first_date, last_date, ahead_months):
        start = first_date
        end = max(last_date, compute_ahead_months(ahead_months))
        DateRange.__init__(self, start, end)
        self.ahead_months = ahead_months
    
    def adjusted(self, new_date):
        first_date = min(self.start, new_date)
        last_date = max(self.end, new_date)
        result = AllTransactionsRange(first_date=first_date, last_date=last_date,
            ahead_months=self.ahead_months)
        if result == self:
            result = None
        return result
    
    def prev(self): # for income statement's Last column
        start = self.start - ONE_DAY
        return DateRange(start, start) # whatever, as long as there's nothing in it
    
    @property
    def display(self):
        return tr("All Transactions")
    

class CustomDateRange(DateRange):
    def __init__(self, start, end, format_func):
        DateRange.__init__(self, start, end)
        self._format_func = format_func
    
    def prev(self): # for income statement's Last column
        end = self.start - ONE_DAY
        start = end - (self.end - self.start)
        return CustomDateRange(start, end, self._format_func)
    
    @property
    def display(self):
        return '{0} - {1}'.format(self._format_func(self.start), self._format_func(self.end))

#--- Date Incrementing

def inc_day(date, count):
    return date + timedelta(count)

def inc_week(date, count):
    return inc_day(date, count * 7)

def inc_month(date, count):
    y, m, d = date.year, date.month, date.day
    m += count
    y += (m - 1) // 12
    m = ((m - 1) % 12) + 1
    days_in_month = monthrange(y, m)[1]
    d = min(d, days_in_month)
    return date.replace(year=y, month=m, day=d)

def inc_year(date, count):
    return inc_month(date, count * 12)

def inc_weekday_in_month(date, count):
    weekday = date.weekday()
    weekno = (date.day - 1) // 7
    new_month = inc_month(date, count)
    first_weekday = new_month.replace(day=1).weekday()
    diff = weekday - first_weekday
    if diff < 0:
        diff += 7
    try:
        return new_month.replace(day=weekno * 7 + diff + 1)
    except ValueError:
        return None

def inc_last_weekday_in_month(date, count):
    weekday = date.weekday()
    new_month = inc_month(date, count)
    days_in_month = monthrange(new_month.year, new_month.month)[1]
    last_weekday = new_month.replace(day=days_in_month).weekday()
    diff = last_weekday - weekday
    if diff < 0:
        diff += 7
    return new_month.replace(day=days_in_month - diff)

#--- Date Formatting
# For the functions below, the format used is a subset of the Unicode format type
# http://unicode.org/reports/tr35/tr35-6.html#Date_Format_Patterns
# Only the basics are supported: /-. yyyy yy MM M dd d
# anything else in the format should be cleaned out *before* using parse and format

# Why not just convert the Unicode format to strftime's format? Because the strftime formatting
# does not support padding-less month and day.

re_separators = re.compile(r'/|-|\.| ')

def clean_format(format):
    """Removes any format element that is not supported. If the result is an invalid format, return
    a fallback format
    """
    format = DateFormat(format)
    format.make_numerical()
    return format.iso_format

def parse_date(string, format):
    return DateFormat(format).parse_date(string)

def format_date(date, format):
    return format_year_month_day(date.year, date.month, date.day, format)

def format_year_month_day(year, month, day, format):
    result = format.replace('yyyy', str(year))
    result = result.replace('yy', str(year)[-2:])
    result = result.replace('MM', '%02d' % month)
    result = result.replace('M', '%d' % month)
    result = result.replace('dd', '%02d' % day)
    result = result.replace('d', '%d' % day)
    return result

class DateFormat:
    ISO2SYS = {'yyyy': '%Y', 'yy': '%y', 'MMM': '%b', 'MM': '%m', 'M': '%m', 'dd': '%d', 'd': '%d'}
    SYS2ISO = {'%Y': 'yyyy', '%y': 'yy', '%m': 'MM', '%b': 'MMM', '%d': 'dd'}
    
    def __init__(self, format):
        if format is None:
            format = ''
        # Default values in case we can't parse
        self.separator = '/'
        self.elements = ['dd', 'MM', 'yyyy']
        m_separators = re_separators.search(format)
        if m_separators:
            self.separator = m_separators.group()
            elements = format.split(self.separator)
            if all(elem in self.ISO2SYS for elem in elements):
                self.elements = elements
    
    @staticmethod
    def from_sysformat(format):
        if format is None:
            format = ''
        for key, value in DateFormat.SYS2ISO.items():
            format = format.replace(key, value)
        return DateFormat(format)
    
    def copy(self):
        return DateFormat(self.iso_format)
    
    def parse_date(self, string):
        return datetime.strptime(string, self.sys_format).date()
    
    def make_numerical(self):
        # If the date format contains a non-numerical month, change it to a numerical one.
        if 'MMM' in self.elements:
            self.elements[self.elements.index('MMM')] = 'MM'
    
    @property
    def iso_format(self):
        return self.separator.join(self.elements)
    
    @property
    def sys_format(self):
        repl_elems = [self.ISO2SYS[elem] for elem in self.elements]
        return self.separator.join(repl_elems)

