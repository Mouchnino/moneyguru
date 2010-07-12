# coding: utf-8 
# Created By: Virgil Dupras
# Created On: 2009-08-22
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.testutil import eq_

from ..base import TestCase, CommonSetup

class OneExpenseWithBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget()
        self.mainwindow.select_budget_table()
        self.clear_gui_calls()
    
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
        eq_(self.ttable.row_count, 0)
    
    def test_edition_must_stop(self):
        # When the edition_must_stop event is broadcasted, btable must ignore it because the objc
        # side doesn't have a stop_editing method.
        self.document.stop_edition()
        self.check_gui_calls_partial(self.btable_gui, not_expected=['stop_editing'])
    
