# Created By: Virgil Dupras
# Created On: 2008-09-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base import DocumentGUIObject

class Chart(DocumentGUIObject):
    #--- Override
    def connect(self):
        DocumentGUIObject.connect(self)
        self.compute()
        self.view.refresh()
    
    #--- Virtual
    def compute(self):
        raise NotImplementedError()
    
    #--- Event Handlers
    def account_changed(self):
        self.compute()
        self.view.refresh()
    
    def account_deleted(self):
        self.compute()
        self.view.refresh()
    
    def date_range_changed(self):
        self.compute()
        self.view.refresh()
    
    def entries_imported(self):
        self.compute()
        self.view.refresh()
    
    def entry_changed(self):
        self.compute()
        self.view.refresh()
    
    def entry_deleted(self):
        self.compute()
        self.view.refresh()
    
    def redone(self):
        self.compute()
        self.view.refresh()
    
    def undone(self):
        self.compute()
        self.view.refresh()
    
    #--- Properties
    @property
    def data(self):
        return self._data
    
    @property
    def title(self):
        return ''
    
    @property
    def currency(self):
        return self.app.default_currency
    
