# Created By: Virgil Dupras
# Created On: 2009-04-12
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..base import TestCase, CommonSetup

class DeletingSecondAccount(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_three_accounts_one_entry()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # account 'two', the one with the entry
        self.bsheet.delete() # the panel shows up
    
    def test_available_accounts(self):
        # the available accounts in arpanel are No Account, one and three
        expected = ['No Account', 'one', 'three']
        self.assertEqual(self.arpanel.available_accounts, expected)
    
    def test_no_delete_took_place(self):
        # the panel shows up, but no deletion takes place yet.
        self.assertEqual(len(self.bsheet.assets), 4) # 2 + total lines.
    
    def test_reassign_to_one(self):
        # choosing 'one' and continuing reassigns two's entry to one.
        self.arpanel.account_index = 1 # one
        self.arpanel.ok()
        self.assertEqual(len(self.bsheet.assets), 3) # now, it's deleted
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 1)
        self.assertEqual(self.etable[0].transfer, 'three')
        self.assertEqual(self.etable[0].increase, '42.00') # got the right side of the txn
    
