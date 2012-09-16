# Created By: Virgil Dupras
# Created On: 2008-06-18
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from ..model.date import format_year_month_day, inc_day, inc_month, inc_year, DateFormat

DAY = 'day'
MONTH = 'month'
YEAR = 'year'

FMT_ELEM = {
    'dd': DAY,
    'd': DAY,
    'MM': MONTH,
    'M': MONTH,
    'yyyy': YEAR,
    'yy': YEAR,
}

class DateWidget:
    def __init__(self, format):
        if not isinstance(format, DateFormat):
            format = DateFormat(format)
        self._format = format
        fmt_elems = format.elements
        self._order = [FMT_ELEM[elem] for elem in fmt_elems]
        self._elem2fmt = dict(zip(self._order, fmt_elems))
        self._selected = DAY
        self._buffer = ''
        self._day = 0
        self._month = 0
        self._year = 0
        self.date = date.today()
    
    #--- Private
    def _next(self):
        if self._selected == DAY:
            self._selected = MONTH
        elif self._selected == MONTH:
            self._selected = YEAR
    
    def _flush_buffer(self, force=False):
        # Returns a bool indicating if the buffer was effectively flushed
        if not self._buffer:
            return False
        value = int(self._buffer)
        valid = False
        if self._selected == DAY:
            valid = 1 <= value <= 31
            if valid:
                self._day = value
        elif self._selected == MONTH:
            valid = 1 <= value <= 12
            if valid:
                self._month = value
        else:
            valid = (value < 100) or (value >= 1900)
            if valid:
                if value < 100:
                    value += 2000 if value < 69 else 1900
                self._year = value
        if valid or force:
            self._buffer = ''
        return valid
    
    def _increase_or_decrease(self, increase):
        inc_count = 1 if increase else -1
        if self.date is None:
            return
        self._flush_buffer(force=True)
        olddate = self.date
        if self._selected == DAY:
            self.date = inc_day(olddate, inc_count)
        elif self._selected == MONTH:
            self.date = inc_month(olddate, inc_count)
        else:
            self.date = inc_year(olddate, inc_count)
    
    #--- Public
    def backspace(self):
        self._buffer = self._buffer[:-1]
    
    def decrease(self):
        self._increase_or_decrease(increase=False)
    
    def exit(self):
        self._flush_buffer(force=True)
        self.date # will correct the date
        self._selected = DAY
    
    def increase(self):
        self._increase_or_decrease(increase=True)
    
    def left(self):
        self._flush_buffer(force=True)
        index = (self._order.index(self._selected) - 1)
        self._selected = self._order[index]
    
    def right(self):
        self._flush_buffer(force=True)
        index = (self._order.index(self._selected) + 1) % 3
        self._selected = self._order[index]
    
    def type(self, stuff):
        if stuff == self._format.separator:
            if self._flush_buffer():
                self._next()
            return
        if stuff in {'t', 'T'}:
            self._buffer = ''
            self.date = date.today()
            return
        if not stuff.isdigit(): # invalid
            return
        self._buffer += stuff
        sel = self.selection
        sel_len = sel[1] - sel[0] + 1
        if len(self._buffer) == max(sel_len, 2): # We must at least buffer one char at all time
            if self._flush_buffer():
                self._next()
            else:
                self._buffer = self._buffer[:-1]
    
    @property
    def date(self):
        try:
            return date(self._year, self._month, self._day)
        except ValueError:
            if self._day in [29, 30, 31]: # Might be a "nearly valid" date
                self._day -= 1
                return self.date
            else: # Invalid date
                return None
    
    @date.setter
    def date(self, value):
        # value: None for invalid date
        if value is None:
            self._year = self._month = self._day = 0
        else:
            self._year = value.year
            self._month = value.month
            self._day = value.day
        fmt_elems = self._format.elements
        pos = 0
        self._elem_pos = {}
        for fmt_elem in fmt_elems:
            elem_len = len(fmt_elem)
            elem = FMT_ELEM[fmt_elem]
            if elem_len == 1:
                if ((elem == DAY) and (self._day >= 10)) or ((elem == MONTH) and (self._month >= 10)):
                    elem_len += 1
            self._elem_pos[elem] = (pos, pos + elem_len - 1)
            pos += elem_len + 1 # + 1 is for the separator
    
    @property
    def selection(self):
        sel = self._elem_pos[self._selected]
        if self._buffer and sel[0] == sel[1]: # during buffering, the selection is at least 2 in length
            sel = (sel[0], sel[1] + 1)
        return sel
    
    @property
    def text(self):
        elem2fmt = self._elem2fmt.copy()
        elem2value = {DAY: self._day, MONTH: self._month, YEAR: self._year}
        # Replace fields with invalid values (0) with "-" chars
        for elem, value in elem2value.items():
            if value == 0:
                elem2fmt[elem] = '-' * len(elem2fmt[elem])
        if self._buffer:
            elem2fmt[self._selected] = self._buffer.ljust(max(2, len(elem2fmt[self._selected])))
        format = self._format.separator.join([elem2fmt[elem] for elem in self._order])
        return format_year_month_day(self._year, self._month, self._day, format)
    
    @text.setter
    def text(self, value):
        try:
            self.date = self._format.parse_date(value)
        except ValueError: # invalid date
            self.date = None
    
