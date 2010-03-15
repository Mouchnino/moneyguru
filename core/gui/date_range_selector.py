# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-03-15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base import DocumentGUIObject

class DateRangeSelector(DocumentGUIObject):
    def __init__(self, view, mainwindow):
        DocumentGUIObject.__init__(self, view, mainwindow.document)
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.view.refresh()
    
    #--- Public
    def select_month_range(self):
        self.document.select_month_range()
    
    def select_quarter_range(self):
        self.document.select_quarter_range()
    
    def select_year_range(self):
        self.document.select_year_range()
    
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
    
    #--- Properties
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
    
