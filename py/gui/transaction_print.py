# Unit Name: moneyguru.gui.transaction_print
# Created By: Virgil Dupras
# Created On: 2009-04-05
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from .print_view import PrintView

# the parent of this view must be a TransactionTable
class TransactionPrint(PrintView):
    def split_count_at_row(self, row_index):
        txn = self.parent[row_index].transaction
        return len(txn.splits)
    
    def split_values(self, row_index, split_row_index):
        txn = self.parent[row_index].transaction
        split = txn.splits[split_row_index]
        account_name = split.account.name if split.account is not None else 'Unassigned'
        return [account_name, split.memo, self.app.format_amount(split.amount)]
    
