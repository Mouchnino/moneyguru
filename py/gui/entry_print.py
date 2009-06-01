# Unit Name: moneyguru.gui.entry_print
# Created By: Virgil Dupras
# Created On: 2009-04-05
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from .print_view import PrintView

# the parent of this view must be a EntryTable
class EntryPrint(PrintView):
    def split_count_at_row(self, row_index):
        try:
            entry = self.parent[row_index].entry
            return len(entry.splits)
        except AttributeError: # Previous Balance
            return 0
    
    def split_values(self, row_index, split_row_index):
        entry = self.parent[row_index].entry
        split = entry.splits[split_row_index]
        account_name = split.account.name if split.account is not None else 'Unassigned'
        return [account_name, split.memo, self.app.format_amount(split.amount)]
    
