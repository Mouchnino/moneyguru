# Created By: Virgil Dupras
# Created On: 2008-08-02
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base import ViewChild

class FilterBar(ViewChild):
    INVALIDATING_MESSAGES = set(['filter_applied'])
    
    def __init__(self, view, parent_view):
        ViewChild.__init__(self, view, parent_view)
    
    #--- Override
    # XXX should be done on _revalidate. is view.refresh really always needed?
    def show(self):
        ViewChild.show(self)
        self.view.refresh()
    
    #--- Properties
    @property
    def filter_type(self):
        return self.document.filter_type
    
    @filter_type.setter
    def filter_type(self, value):
        self.document.filter_type = value
    

class TransactionFilterBar(FilterBar):
    def __init__(self, view, transaction_view):
        FilterBar.__init__(self, view, transaction_view)
    

class EntryFilterBar(FilterBar): # disables buttons
    def __init__(self, view, account_view):
        FilterBar.__init__(self, view, account_view)
        self._disabled_buttons = False
    
    #--- Override
    def show(self):
        FilterBar.show(self)
        account = self.mainwindow.shown_account
        if account is not None and account.is_income_statement_account():
            self.document.filter_type = None
            if not self._disabled_buttons:
                self.view.disable_transfers()
                self._disabled_buttons = True
        else:
            if self._disabled_buttons:
                self.view.enable_transfers()
                self._disabled_buttons = False
    
