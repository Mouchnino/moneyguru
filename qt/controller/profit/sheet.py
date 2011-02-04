# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt

from qtlib.column import Column
from hscommon.trans import tr
from core.gui.income_statement import IncomeStatement as IncomeStatementModel
from ..account_sheet import AccountSheet, AccountSheetDelegate

class ProfitSheet(AccountSheet):
    COLUMNS = [
        Column('name', tr('Account'), 133),
        Column('account_number', tr('Account #'), 80),
        Column('cash_flow', tr('Current'), 100, alignment=Qt.AlignRight),
        Column('last_cash_flow', tr('Last'), 100, alignment=Qt.AlignRight),
        Column('delta', tr('Change'), 100, alignment=Qt.AlignRight),
        Column('delta_perc', tr('Change %'), 100),
        Column('budgeted', tr('Budgeted'), 100, alignment=Qt.AlignRight),
    ]
    AMOUNT_ATTRS = {'cash_flow', 'last_cash_flow', 'delta', 'delta_perc', 'budgeted'}
    BOLD_ATTRS = {'cash_flow', }
    
    def __init__(self, profit_view, view):
        model = IncomeStatementModel(view=self, profit_view=profit_view.model)
        AccountSheet.__init__(self, profit_view.doc, model, view)
    
