# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from nose.tools import eq_

from ...document import FilterType
from ..base import TestCase

class TwoEntries(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.mainwindow.show_account()
        self.add_entry('11/07/2008', 'first', increase='42')
        self.add_entry('12/07/2008', 'second', decrease='12')
    
    def test_totals(self):
        # the totals line shows the total amount of increases and decreases
        expected = "Showing 2 out of 2. Total increase: 42.00 Total decrease: 12.00"
        eq_(self.aview.totals, expected)
    
    def test_totals_with_filter(self):
        # when a filter is applied, the number of transaction shown is smaller than the total amount
        self.efbar.filter_type = FilterType.Reconciled
        expected = "Showing 0 out of 2. Total increase: 0.00 Total decrease: 0.00"
        eq_(self.aview.totals, expected)
    
    def test_totals_with_unicode_amount_format(self):
        # it seems that some people have some weird separator in their settings, and there was a
        # UnicodeEncodeError in the totals formatting.
        self.app._decimal_sep = u'\xa0'
        expected = "Showing 2 out of 2. Total increase: 42\xa000 Total decrease: 12\xa000"
        eq_(self.aview.totals, expected)
    

class WithPreviousEntry(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.select_month_range()
        self.add_account()
        self.mainwindow.show_account()
        self.add_entry('1/1/2008')
        self.document.select_next_date_range()
    
    def test_totals(self):
        # the totals line ignores the previous entry line
        expected = "Showing 0 out of 0. Total increase: 0.00 Total decrease: 0.00"
        eq_(self.aview.totals, expected)
    
