# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt

from qtlib.column import Column
from core.gui.balance_sheet import BalanceSheet as BalanceSheetModel
from core.trans import tr
from ..account_sheet import AccountSheet, AccountSheetDelegate

class NetWorthSheet(AccountSheet):
    COLUMNS = [
        Column('name', tr('Account'), 133),
        Column('account_number', tr('Account #'), 80),
        Column('end', tr('End'), 100, alignment=Qt.AlignRight),
        Column('start', tr('Start'), 100, alignment=Qt.AlignRight),
        Column('delta', tr('Change'), 100, alignment=Qt.AlignRight),
        Column('delta_perc', tr('Change %'), 100),
        Column('budgeted', tr('Budgeted'), 100, alignment=Qt.AlignRight),
    ]
    AMOUNT_ATTRS = set(['end', 'start', 'delta', 'delta_perc', 'budgeted'])
    BOLD_ATTRS = set(['end'])
    
    def __init__(self, networth_view, view):
        model = BalanceSheetModel(view=self, networth_view=networth_view.model)
        AccountSheet.__init__(self, networth_view.doc, model, view)
    
