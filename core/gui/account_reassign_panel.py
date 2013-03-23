# Created By: Virgil Dupras
# Created On: 2009-04-12
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.gui.selectable_list import GUISelectableList
from hscommon.trans import tr

from ..model.account import sort_accounts
from .base import MainWindowPanel

class AccountReassignPanel(MainWindowPanel):
    def __init__(self, mainwindow):
        MainWindowPanel.__init__(self, mainwindow)
        self.account_list = GUISelectableList()
    
    def _load(self, accounts):
        self.deleted_accounts = set(accounts)
        all_accounts = self.document.accounts[:]
        target_accounts = [a for a in all_accounts if a not in self.deleted_accounts]
        sort_accounts(target_accounts)
        target_account_names = [a.name for a in target_accounts]
        target_account_names.insert(0, tr('No Account'))
        self._target_accounts = target_accounts
        self._target_accounts.insert(0, None)
        self.account_list[:] = target_account_names
        self.account_list.select(0)
    
    def _save(self):
        reassign_to = self._target_accounts[self.account_list.selected_index]
        self.document.delete_accounts(self.deleted_accounts, reassign_to=reassign_to)
    
