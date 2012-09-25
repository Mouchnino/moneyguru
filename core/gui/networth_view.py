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
from .balance_sheet import BalanceSheet
from .net_worth_graph import NetWorthGraph
from .account_pie_chart import BalancePieChart

class NetWorthView(AccountSheetView):
    SAVENAME = 'NetWorthView'
    VIEW_TYPE = PaneType.NetWorth
    PRINT_TITLE_FORMAT = tr("Net Worth at {end_date}, starting from {start_date}")
    
    def __init__(self, mainwindow):
        AccountSheetView.__init__(self, mainwindow)
        self.sheet = self.bsheet = BalanceSheet(self)
        self.columns = self.bsheet.columns
        self.graph = self.nwgraph = NetWorthGraph(self)
        self.pie = BalancePieChart(self)
        self.set_children([self.bsheet, self.nwgraph, self.pie])
    
