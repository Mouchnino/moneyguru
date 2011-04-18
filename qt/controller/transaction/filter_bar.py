# Created By: Virgil Dupras
# Created On: 2009-11-27
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import tr
from core.document import FilterType
from core.gui.filter_bar import TransactionFilterBar as TransactionFilterBarModel

from ..filter_bar import FilterBar

class TransactionFilterBar(FilterBar):
    BUTTONS = [
        (tr("All"), None),
        (tr("Income"), FilterType.Income),
        (tr("Expenses"), FilterType.Expense),
        (tr("Transfers"), FilterType.Transfer),
        (tr("Unassigned"), FilterType.Unassigned),
        (tr("Reconciled"), FilterType.Reconciled),
        (tr("Not Reconciled"), FilterType.NotReconciled),
    ]
    
    def __init__(self, transaction_view, view):
        model = TransactionFilterBarModel(transaction_view=transaction_view.model, view=self)
        FilterBar.__init__(self, model, view)
    
