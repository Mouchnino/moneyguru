# Unit Name: moneyguru.gui.custom_date_range_panel
# Created By: Virgil Dupras
# Created On: 2009-02-18
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from datetime import date

from ..model.date import CustomDateRange
from .base import DocumentGUIObject

class CustomDateRangePanel(DocumentGUIObject):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        self._start_date = date.today()
        self._end_date = date.today()
    
    def load(self):
        self._start_date = self.document.date_range.start
        self._end_date = self.document.date_range.end
    
    def ok(self):
        start = self._start_date
        end = self._end_date
        self.document.date_range = CustomDateRange(start, end, self.app.format_date)
    
    #--- Properties
    @property
    def start_date(self):
        return self.app.format_date(self._start_date)
    
    @start_date.setter
    def start_date(self, value):
        date = self.app.parse_date(value)
        if date == self._start_date:
            return
        self._start_date = date
        if date > self._end_date:
            self._end_date = date
    
    @property
    def end_date(self):
        return self.app.format_date(self._end_date)
    
    @end_date.setter
    def end_date(self, value):
        date = self.app.parse_date(value)
        if date == self._end_date:
            return
        self._end_date = date
        if date < self._start_date:
            self._start_date = date
    
