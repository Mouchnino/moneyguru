# Created By: Virgil Dupras
# Created On: 2009-04-05
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..trans import tr
from .print_view import PrintView

# the parent of this view must be a TransactionTable
class TransactionPrint(PrintView):
    def split_count_at_row(self, row_index):
        row = self.parent.ttable[row_index]
        if hasattr(row, 'transaction'):
            return len(row.transaction.splits)
        else:
            return 0
    
    def split_values(self, row_index, split_row_index):
        txn = self.parent.ttable[row_index].transaction
        split = txn.splits[split_row_index]
        account_name = split.account.name if split.account is not None else tr('Unassigned')
        return [account_name, split.memo, self.app.format_amount(split.amount)]
    
