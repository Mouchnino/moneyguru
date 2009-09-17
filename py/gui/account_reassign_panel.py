# Created By: Virgil Dupras
# Created On: 2009-04-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..model.account import sort_accounts
from .base import DocumentGUIObject

class AccountReassignPanel(DocumentGUIObject):
    def load(self):
        self.account = self.document.selected_account
        accounts = self.document.accounts[:]
        accounts.remove(self.account)
        sort_accounts(accounts)
        self.available_accounts = [a.name for a in accounts]
        self.available_accounts.insert(0, 'No Account')
        self._accounts = accounts
        self._accounts.insert(0, None)
        self.account_index = 0
    
    def ok(self):
        assert self.account is self.document.selected_account
        reassign_to = self._accounts[self.account_index]
        self.document.reassign_and_delete_selected_account(reassign_to)
    
