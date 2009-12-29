# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-27
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.document import (FILTER_UNASSIGNED, FILTER_INCOME, FILTER_EXPENSE, FILTER_TRANSFER,
    FILTER_RECONCILED, FILTER_NOTRECONCILED)
from core.gui.filter_bar import FilterBar as FilterBarModel

from ..filter_bar import FilterBar

class TransactionFilterBar(FilterBar):
    BUTTONS = [
        ("All", None),
        ("Income", FILTER_INCOME),
        ("Expenses", FILTER_EXPENSE),
        ("Transfers", FILTER_TRANSFER),
        ("Unassigned", FILTER_UNASSIGNED),
        ("Reconciled", FILTER_RECONCILED),
        ("Not Reconciled", FILTER_NOTRECONCILED),
    ]
    
    def __init__(self, doc, view):
        model = FilterBarModel(document=doc.model, view=self)
        FilterBar.__init__(self, model, view)
    
