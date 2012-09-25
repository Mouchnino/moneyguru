# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import tr
from ..const import PaneType
from .account_sheet_view import AccountSheetView
from .income_statement import IncomeStatement
from .profit_graph import ProfitGraph
from .account_pie_chart import CashFlowPieChart

class ProfitView(AccountSheetView):
    SAVENAME = 'ProfitView'
    VIEW_TYPE = PaneType.Profit
    PRINT_TITLE_FORMAT = tr('Profit and Loss from {start_date} to {end_date}')
    
    def __init__(self, mainwindow):
        AccountSheetView.__init__(self, mainwindow)
        self.sheet = self.istatement = IncomeStatement(self)
        self.columns = self.istatement.columns
        self.graph = self.pgraph = ProfitGraph(self)
        self.pie = CashFlowPieChart(self)
        self.set_children([self.istatement, self.pgraph, self.pie])
    
