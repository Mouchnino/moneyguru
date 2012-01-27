# Created By: Virgil Dupras
# Created On: 2008-08-02
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.gui.base import GUIObject

from ..document import FilterType

class FilterBar(GUIObject):
    def __init__(self, parent_view):
        GUIObject.__init__(self)
        self.mainwindow = parent_view.mainwindow
        self.document = parent_view.document
    
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
        self._account = account_view.account
    
    #--- Override
    def _view_updated(self):
        if self._account.is_income_statement_account():
            self.view.disable_transfers()
        else:
            self.view.enable_transfers()
    
    def refresh(self):
        FilterBar.refresh(self)
        if self._account.is_income_statement_account() and self.filter_type is FilterType.Transfer:
            self.filter_type = None
    
