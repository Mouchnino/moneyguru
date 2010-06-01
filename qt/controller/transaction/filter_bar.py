# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-27
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.document import FilterType
from core.gui.filter_bar import TransactionFilterBar as TransactionFilterBarModel

from ..filter_bar import FilterBar

class TransactionFilterBar(FilterBar):
    BUTTONS = [
        ("All", None),
        ("Income", FilterType.Income),
        ("Expenses", FilterType.Expense),
        ("Transfers", FilterType.Transfer),
        ("Unassigned", FilterType.Unassigned),
        ("Reconciled", FilterType.Reconciled),
        ("Not Reconciled", FilterType.NotReconciled),
    ]
    
    def __init__(self, transaction_view, view):
        model = TransactionFilterBarModel(transaction_view=transaction_view.model, view=self)
        FilterBar.__init__(self, model, view)
    
