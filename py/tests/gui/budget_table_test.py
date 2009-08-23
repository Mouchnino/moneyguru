# coding: utf-8 
# Created By: Virgil Dupras
# Created On: 2009-08-22
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ..base import TestCase, CommonSetup

class OneExpenseWithBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget()
        self.mainwindow.select_budget_table()
    
    def test_attrs(self):
        eq_(len(self.btable), 1)
        row = self.btable[0]
        eq_(row.start_date, '01/01/2008')
        eq_(row.stop_date, '')
        eq_(row.repeat_type, 'Monthly')
        eq_(row.interval, '1')
        eq_(row.account, 'Some Expense')
        eq_(row.target, '')
        eq_(row.amount, '100.00')
    
    def test_delete(self):
        # calling delete() deletes the selected rows
        self.btable.select([0])
        self.mainwindow.delete_item()
        eq_(len(self.btable), 0)
        # And the spawns aren't there anymore in the ttable
        self.mainwindow.select_transaction_table()
        eq_(len(self.ttable), 0)
    
