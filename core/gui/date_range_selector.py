# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-03-15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import datetime

from .base import DocumentGUIObject

class DateRangeSelector(DocumentGUIObject):
    def __init__(self, view, mainwindow):
        DocumentGUIObject.__init__(self, view, mainwindow.document)
        self.mainwindow = mainwindow
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.view.refresh_custom_ranges()
        self.view.refresh()
    
    #--- Private
    def _date_range_starting_point(self):
        if self.mainwindow.selected_transactions:
            return self.mainwindow.selected_transactions[0].date
        elif datetime.date.today() in self.document.date_range:
            return datetime.date.today()
        else:
            return self.document.date_range
    
    #--- Public
    def select_month_range(self):
        self.document.select_month_range(starting_point=self._date_range_starting_point())
    
    def select_quarter_range(self):
        self.document.select_quarter_range(starting_point=self._date_range_starting_point())
    
    def select_year_range(self):
        self.document.select_year_range(starting_point=self._date_range_starting_point())
    
    def select_year_to_date_range(self):
        self.document.select_year_to_date_range()
    
    def select_running_year_range(self):
        self.document.select_running_year_range()
    
    def select_all_transactions_range(self):
        self.document.select_all_transactions_range()
    
    def select_custom_date_range(self):
        self.document.select_custom_date_range()
    
    def select_prev_date_range(self):
        self.document.select_prev_date_range()
    
    def select_next_date_range(self):
        self.document.select_next_date_range()
    
    def select_today_date_range(self):
        self.document.select_today_date_range()
    
    def select_saved_range(self, slot):
        saved_range = self.app.saved_custom_ranges[slot]
        if saved_range:
            self.document.select_custom_date_range(saved_range.start, saved_range.end)
    
    #--- Properties
    @property
    def can_navigate(self):
        return self.document.date_range.can_navigate
    
    @property
    def custom_range_names(self):
        return [(r.name if r else None) for r in self.app.saved_custom_ranges]
    
    @property
    def display(self):
        return self.document.date_range.display
    
    #--- Event Handlers
    def date_range_will_change(self):
        self._old_date_range = self.document.date_range
    
    def date_range_changed(self):
        self.view.refresh()
        old = self._old_date_range
        new = self.document.date_range
        if type(new) == type(old):
            if new.start > old.start:
                self.view.animate_forward()
            else:
                self.view.animate_backward()
    
    def saved_custom_ranges_changed(self):
        self.view.refresh_custom_ranges()
    
