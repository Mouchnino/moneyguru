# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-08-23
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ...model.account import INCOME, LIABILITY
from ..base import TestCase, CommonSetup

class OneExpenseWithBudget(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_account_with_budget()
        # The accounts' name and order in which they are created is important, as it tests that
        # the budget panel sorts them correctly.
        self.add_account('liability', account_type=LIABILITY)
        self.add_account('asset')
        self.add_account('Some Income', account_type=INCOME)
        self.mainwindow.select_budget_table()
        self.btable.select([0])
        self.mainwindow.edit_item()
    
    def test_attrs(self):
        eq_(self.bpanel.start_date, '01/01/2008')
        eq_(self.bpanel.stop_date, '')
        eq_(self.bpanel.repeat_type_index, 2) # monthly
        eq_(self.bpanel.repeat_every, 1)
        eq_(self.bpanel.account_options, ['Some Income', 'Some Expense'])
        eq_(self.bpanel.account_index, 1)
        eq_(self.bpanel.target_options, ['None', 'asset', 'liability'])
        eq_(self.bpanel.target_index, 0)
        eq_(self.bpanel.amount, '100.00')
    
    def test_edit_then_save(self):
        # Saving edits on the panel actually updates the budget
        self.bpanel.account_index = 0 # Some Income
        self.bpanel.target_index = 2 # liability
        self.bpanel.amount = '42'
        self.bpanel.save()
        row = self.btable[0]
        eq_(row.account, 'Some Income')
        eq_(row.target, 'liability')
        eq_(row.amount, '42.00')
        # To see if the save_edits() worked, we look if the spawns are correct in the ttable
        self.mainwindow.select_transaction_table()
        row = self.ttable[0]
        eq_(row.to, 'liability')
        eq_(row.from_, 'Some Income')
        eq_(row.amount, '42.00')
    
    def test_edit_without_selection(self):
        # Initiating a budget edition while none is selected doesn't crash
        self.btable.select([])
        self.mainwindow.edit_item() # no crash
    
    def test_new_budget(self):
        self.mainwindow.new_item()
        eq_(self.bpanel.start_date, '27/01/2008') # mocked date
        eq_(self.bpanel.repeat_type_index, 2) # monthly
        eq_(self.bpanel.account_index, 0)
        eq_(self.bpanel.target_index, 0)
        self.bpanel.save()
        eq_(len(self.btable), 2) # has been added
    
