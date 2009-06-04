# Unit Name: moneyguru.gui.entry_print_test
# Created By: Virgil Dupras
# Created On: 2009-04-05
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from ..base import TestCase, CommonSetup
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
    

class OneEntryInPreviousRange(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_one_entry_in_previous_range()
        self.pv = EntryPrint(self.etable)
    
    def test_split_count(self):
        # For the "Previous Balance" entry, return 0, don't crash
        self.assertEqual(self.pv.split_count_at_row(0), 0)
    
