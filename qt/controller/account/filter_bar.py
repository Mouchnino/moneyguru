# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-27
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.document import FilterType
from core.gui.filter_bar import EntryFilterBar as EntryFilterBarModel

from ..filter_bar import FilterBar

class EntryFilterBar(FilterBar):
    BUTTONS = [
        ("All", None),
        ("Increase", FilterType.Income),
        ("Decrease", FilterType.Expense),
        ("Transfers", FilterType.Transfer),
        ("Unassigned", FilterType.Unassigned),
        ("Reconciled", FilterType.Reconciled),
        ("Not Reconciled", FilterType.NotReconciled),
    ]
    
    def __init__(self, doc, view):
        model = EntryFilterBarModel(document=doc.model, view=self)
        FilterBar.__init__(self, model, view)
    
    #--- model --> view
    def disable_transfers(self):
        self.view.setTabEnabled(3, False)
    
    def enable_transfers(self):
        self.view.setTabEnabled(3, True)
    
