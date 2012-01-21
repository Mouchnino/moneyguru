# Created By: Virgil Dupras
# Created On: 2008-08-02
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.gui.base import NoopGUI

class FilterBar:
    def __init__(self, parent_view):
        self.mainwindow = parent_view.mainwindow
        self.document = parent_view.document
        self.view = NoopGUI()
    
    #--- Public
    def refresh(self):
        self.view.refresh()
    
    #--- Properties
    @property
    def filter_type(self):
        return self.document.filter_type
    
    @filter_type.setter
    def filter_type(self, value):
        self.document.filter_type = value
    

class EntryFilterBar(FilterBar): # disables buttons
    def __init__(self, account_view):
        FilterBar.__init__(self, account_view)
        self._disabled_buttons = False
        self._previous_account = None
    
    #--- Override
    def refresh(self):
        FilterBar.refresh(self)
        account = self.mainwindow.shown_account
        if account is not self._previous_account:
            self._previous_account = account
            if account is not None and account.is_income_statement_account():
                self.document.filter_type = None
                if not self._disabled_buttons:
                    self.view.disable_transfers()
                    self._disabled_buttons = True
            else:
                if self._disabled_buttons:
                    self.view.enable_transfers()
                    self._disabled_buttons = False
    
