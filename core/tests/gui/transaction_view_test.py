# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ...document import FilterType
from ..base import TestCase

class OneTransaction(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_txn()
    
    def test_totals(self):
        # The totals line is correctly pluralized
        expected = "Showing 1 out of 1." # no "s"
        eq_(self.tview.totals, expected)
    

class TwoTransactionsOneOutOfRange(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.select_month_range()
        self.add_txn('11/06/2008')
        self.add_txn('11/07/2008') # The month range has now changed to July 2008
    
    def test_totals(self):
        # The total number of txns don't include out of range transactions
        expected = "Showing 1 out of 1."
        eq_(self.tview.totals, expected)
    

class ThreeTransactionsInRange(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_txn()
        self.add_txn()
        self.add_txn() 
    
    def test_totals(self):
        # the totals line shows the number of shown transactions
        expected = "Showing 3 out of 3."
        eq_(self.tview.totals, expected)
    
    def test_totals_with_filter(self):
        # when a filter is applied, the number of transaction shown is smaller than the total amount
        self.tfbar.filter_type = FilterType.Reconciled
        expected = "Showing 0 out of 3."
        eq_(self.tview.totals, expected)
    
