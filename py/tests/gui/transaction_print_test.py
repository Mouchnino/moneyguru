# Unit Name: moneyguru.gui.transaction_print_test
# Created By: Virgil Dupras
# Created On: 2009-04-05
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from ..base import TestCase
from ..split_test import _SplitTransaction
from ...gui.transaction_print import TransactionPrint

class SplitTransaction(_SplitTransaction):
    def setUp(self):
        _SplitTransaction.setUp(self)
        self.document.select_transaction_table()
        self.pv = TransactionPrint(self.ttable)
    
    def test_split_count(self):
        self.assertEqual(self.pv.split_count_at_row(0), 5)
        self.assertEqual(self.pv.split_count_at_row(1), 2)
    
    def test_split_values(self):
        self.assertEqual(self.pv.split_values(0, 2), ['expense2', 'some memo', '10.00'])
        self.assertEqual(self.pv.split_values(0, 4), ['Unassigned', '', '-9.00'])
    
