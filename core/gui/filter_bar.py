# Created By: Virgil Dupras
# Created On: 2008-08-02
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base import DocumentGUIObject

class FilterBar(DocumentGUIObject):
    #--- Override
    def connect(self):
        DocumentGUIObject.connect(self)
        self.view.refresh()
    
    #--- Properties
    @property
    def filter_type(self):
        return self.document.filter_type
    
    @filter_type.setter
    def filter_type(self, value):
        self.document.filter_type = value
    

class EntryFilterBar(FilterBar): # disables buttons
    def __init__(self, view, document):
        FilterBar.__init__(self, view, document)
        self._disabled_buttons = False
    
    #--- Override
    def connect(self):
        account = self.document.selected_account
        if account is not None and account.is_income_statement_account():
            self.document.filter_type = None
            if not self._disabled_buttons:
                self.view.disable_transfers()
                self._disabled_buttons = True
        else:
            if self._disabled_buttons:
                self.view.enable_transfers()
                self._disabled_buttons = False
        FilterBar.connect(self)
    
