# Created By: Eric Mc Sween
# Created On: 2007-12-12
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
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
        start_date_str = strftime('%Y/%m/%d', self.start) if self.start.year > 1900 else 'MINDATE'
        return '<%s %s - %s>' % (type(self).__name__, start_date_str, strftime('%Y/%m/%d', self.end))
    
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
        return strftime('%B %Y', self.start)
    

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
        return 'Q%d %d' % (self.start.month // 3 + 1, self.start.year)
    

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
        return '{0} - {1}'.format(strftime('%b %Y', self.start), strftime('%b %Y', self.end))
    

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
        return tr('{0} - Now').format(strftime('%b %Y', self.start))
    

def compute_ahead_months(ahead_months):
    assert ahead_months < 12
    month_range = MonthRange(date.today())
    for _ in range(ahead_months):
        month_range = month_range.next()
    return month_range.end

class RunningYearRange(DateRange):
    def __init__(self, ahead_months):
        end = compute_ahead_months(ahead_months)
        end_plus_one = end + ONE_DAY
        start = end_plus_one.replace(year=end_plus_one.year-1)
        DateRange.__init__(self, start, end)
    
    def prev(self): # for income statement's Last column
        start = self.start.replace(year=self.start.year - 1)
        end = self.start - ONE_DAY
        return DateRange(start, end)
    
    @property
    def display(self):
        return tr('Running year ({0} - {1})').format(strftime('%b', self.start), strftime('%b', self.end))
    

class AllTransactionsRange(DateRange):
    def __init__(self, start, ahead_months):
        end = compute_ahead_months(ahead_months)
        DateRange.__init__(self, start, end)
    
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

re_separators = re.compile(r'/|-|\.')
re_year = re.compile(r'y{4}|y{2}')
re_month = re.compile(r'M{1,2}')
re_day = re.compile(r'd{1,2}')

def clean_format(format):
    """Removes any format element that is not supported. If the result is an invalid format, return
    a fallback format
    """
    m_separators = re_separators.search(format)
    m_day = re_day.search(format)
    m_month = re_month.search(format)
    m_year = re_year.search(format)
    if any(m is None for m in (m_separators, m_day, m_month, m_year)):
        return 'dd/MM/yyyy'
    separator = m_separators.group()
    matches = [m_day, m_month, m_year]
    matches.sort(key=lambda m: m.start()) # sort matches in order of appearance
    return separator.join(m.group() for m in matches)

def parse_date(string, format):
    format = format.replace('yyyy', '%Y')
    format = format.replace('yy', '%y')
    format = re_month.sub('%m', format)
    format = re_day.sub('%d', format)
    return datetime.strptime(string, format).date()

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

#--- Misc
def strftime(fmt, date):
    # Under Python 2, there used to be problems with unicode/str results and strftime, problems that
    # aren't there under Python3 anymore. Use of this function should be phased out and replaced
    # with a simple date.strftime() call.
    return date.strftime(fmt)
