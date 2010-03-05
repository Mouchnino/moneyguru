# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..base import TestCase
from ..split_test import _SplitTransaction
from ...gui.entry_print import EntryPrint

class SplitTransaction(_SplitTransaction):
    def setUp(self):
        _SplitTransaction.setUp(self)
        self.pv = EntryPrint(self.etable)
    
    def test_split_count(self):
        self.assertEqual(self.pv.split_count_at_row(0), 4)
        self.assertEqual(self.pv.split_count_at_row(1), 1)
    
    def test_split_values(self):
        self.assertEqual(self.pv.split_values(0, 1), ['expense2', 'some memo', '10.00'])
        self.assertEqual(self.pv.split_values(0, 3), ['Unassigned', '', '-9.00'])
    

class OneEntryInPreviousRange(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.select_month_range()
        self.add_account()
        self.mainwindow.show_account()
        self.add_entry('1/1/2008')
        self.document.select_next_date_range()
        self.pv = EntryPrint(self.etable)
    
    def test_split_count(self):
        # For the "Previous Balance" entry, return 0, don't crash
        self.assertEqual(self.pv.split_count_at_row(0), 0)
    
