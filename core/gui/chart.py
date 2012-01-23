# Created By: Virgil Dupras
# Created On: 2008-09-04
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from .base import ViewChild, MESSAGES_DOCUMENT_CHANGED

class Chart(ViewChild):
    INVALIDATING_MESSAGES = MESSAGES_DOCUMENT_CHANGED | set(['accounts_excluded',
        'date_range_changed'])
    
    #--- Override
    def _revalidate(self):
        self.compute()
        self.view.refresh()
    
    #--- Virtual
    def compute(self):
        raise NotImplementedError()
    
    #--- Event Handlers
    def _data_changed(self):
        self._revalidate()
    
    account_changed = _data_changed
    account_deleted = _data_changed
    date_range_changed = _data_changed
    document_changed = _data_changed
    performed_undo_or_redo = _data_changed
    transaction_changed = _data_changed
    transaction_deleted = _data_changed
    transactions_imported = _data_changed
    
    #--- Properties
    @property
    def data(self):
        return self._data
    
    @property
    def title(self):
        return ''
    
    @property
    def currency(self):
        return self.document.default_currency
    
