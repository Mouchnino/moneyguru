# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..trans import tr
from .print_view import PrintView

# the parent of this view must be a EntryTable
class EntryPrint(PrintView):
    def split_count_at_row(self, row_index):
        try:
            entry = self.parent.etable[row_index].entry
            return len(entry.splits)
        except AttributeError: # Previous Balance
            return 0
    
    def split_values(self, row_index, split_row_index):
        entry = self.parent.etable[row_index].entry
        split = entry.splits[split_row_index]
        account_name = split.account.name if split.account is not None else tr('Unassigned')
        return [account_name, split.memo, self.app.format_amount(split.amount)]
    
