# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..trans import tr
from .print_view import PrintView

class TransactionPrintBase(PrintView):
    #--- Virtual
    def _get_splits_at_row(self, row_index):
        return []
    
    #--- Public
    def split_count_at_row(self, row_index):
        return len(self._get_splits_at_row(row_index))
    
    def split_values(self, row_index, split_row_index):
        splits = self._get_splits_at_row(row_index)
        split = splits[split_row_index]
        account_name = split.account.name if split.account is not None else tr('Unassigned')
        return [account_name, split.memo, self.app.format_amount(split.amount)]
    

class TransactionPrint(TransactionPrintBase):
    def _get_splits_at_row(self, row_index):
        row = self.parent.maintable[row_index]
        if hasattr(row, 'transaction'):
            return row.transaction.splits
        else:
            return []
    

class EntryPrint(TransactionPrintBase):
    def _get_splits_at_row(self, row_index):
        try:
            entry = self.parent.maintable[row_index].entry
            return [entry.split] + entry.splits
        except AttributeError: # Previous Balance
            return []
    
