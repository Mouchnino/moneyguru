# Created By: Virgil Dupras
# Created On: 2008-06-18
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import re
from calendar import monthrange
from datetime import date, timedelta

from ..model.date import format_year_month_day

DAY = 'day'
MONTH = 'month'
YEAR = 'year'

re_sep = re.compile(r'(/|-|\.)')

FMT_ELEM = {
    'dd': DAY,
    'd': DAY,
    'MM': MONTH,
    'M': MONTH,
    'yyyy': YEAR,
    'yy': YEAR,
}

class DateWidget(object):
    def __init__(self, format):
        # format is a Unicode format. The format has to be cleaned first. This class don't have 
        # tolerance for garbage in the format
        self._format = format
        self._sep = re_sep.search(format).groups()[0]
        fmt_elems = format.split(self._sep)
        self._order = [FMT_ELEM[elem] for elem in fmt_elems]
        self._elem2fmt = dict(zip(self._order, fmt_elems))
        self._selected = DAY
        self._buffer = ''
        self._day = 0
        self._month = 0
        self._year = 0
        self.date = date.today()
    
    def _next(self):
        if self._selected == DAY:
            self._selected = MONTH
        elif self._selected == MONTH:
            self._selected = YEAR
    
    def _flush_buffer(self, move=True):
        if not self._buffer:
            return
        value = int(self._buffer)
        if self._selected == DAY:
            if not (1 <= value <= 31):
                raise ValueError()
            self._day = value
        elif self._selected == MONTH:
            if not (1 <= value <= 12):
                raise ValueError()
            self._month = value
        else:
            if value < 100:
                value += 2000 if value < 69 else 1900
            self._year = value
        self._buffer = ''
        if move:
            self._next()
    
    def backspace(self):
        self._buffer = self._buffer[:-1]
    
    def decrease(self):
        self._flush_buffer(move=False)
        if self._selected == DAY:
            self.date -= timedelta(days=1)
        elif self._selected == MONTH:
            if self.date.month == 1:
                self.date = self.date.replace(month=12, year=self.date.year - 1)
            else:
                month = self.date.month - 1
                days_in_month = monthrange(self.date.year, month)[1]
                day = min(self.date.day, days_in_month)
                self.date = self.date.replace(month=month, day=day)
        else:
            self.date = self.date.replace(year=self.date.year - 1)
    
    def exit(self):
        self._flush_buffer(move=False)
        self.date # will correct the date
        self._selected = DAY
    
    def increase(self):
        self._flush_buffer(move=False)
        if self._selected == DAY:
            self.date += timedelta(days=1)
        elif self._selected == MONTH:
            if self.date.month == 12:
                self.date = self.date.replace(month=1, year=self.date.year + 1)
            else:
                month = self.date.month + 1
                days_in_month = monthrange(self.date.year, month)[1]
                day = min(self.date.day, days_in_month)
                self.date = self.date.replace(month=month, day=day)
        else:
            self.date = self.date.replace(year=self.date.year + 1)
    
    def left(self):
        self._flush_buffer(move=False)
        index = (self._order.index(self._selected) - 1)
        self._selected = self._order[index]
    
    def right(self):
        self._flush_buffer(move=False)
        index = (self._order.index(self._selected) + 1) % 3
        self._selected = self._order[index]
    
    def type(self, stuff):
        if stuff == self._sep:
            self._flush_buffer()
            return
        if not stuff.isdigit(): # invalid
            return
        self._buffer += stuff
        sel = self.selection
        sel_len = sel[1] - sel[0] + 1
        if len(self._buffer) == max(sel_len, 2): # We must at least buffer one char at all time
            try:
                self._flush_buffer()
            except ValueError:
                self._buffer = self._buffer[:-1]
    
    @property
    def date(self):
        while True:
            try:
                return date(self._year, self._month, self._day)
            except ValueError:
                assert self._day in [29, 30, 31]
                self._day -= 1
    
    @date.setter
    def date(self, value):
        self._year = value.year
        self._month = value.month
        self._day = value.day
        fmt_elems = self._format.split(self._sep)
        pos = 0
        self._elem_pos = {}
        for fmt_elem in fmt_elems:
            elem_len = len(fmt_elem)
            elem = FMT_ELEM[fmt_elem]
            if elem_len == 1:
                if ((elem == DAY) and (value.day >= 10)) or ((elem == MONTH) and (value.month >= 10)):
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
        if self._buffer:
            elem2fmt = self._elem2fmt.copy()
            elem2fmt[self._selected] = self._buffer.ljust(max(2, len(elem2fmt[self._selected])))
            format = self._sep.join([elem2fmt[elem] for elem in self._order])
        else:
            format = self._format
        return format_year_month_day(self._year, self._month, self._day, format)
    
