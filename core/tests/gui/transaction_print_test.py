# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..base import TestCase
from ..split_test import _SplitTransaction
from ...gui.transaction_print import TransactionPrint

class SplitTransaction(_SplitTransaction):
    def setUp(self):
        _SplitTransaction.setUp(self)
        self.mainwindow.select_transaction_table()
        self.pv = TransactionPrint(self.ttable)
    
    def test_split_count(self):
        self.assertEqual(self.pv.split_count_at_row(0), 5)
        self.assertEqual(self.pv.split_count_at_row(1), 2)
    
    def test_split_values(self):
        self.assertEqual(self.pv.split_values(0, 2), ['expense2', 'some memo', '10.00'])
        self.assertEqual(self.pv.split_values(0, 4), ['Unassigned', '', '-9.00'])
    
