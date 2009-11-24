# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base_view import BaseView
from .profit_sheet import ProfitSheet
from .profit_graph import ProfitGraph
from .income_pie_chart import IncomePieChart
from .expense_pie_chart import ExpensePieChart
from ui.profit_view_ui import Ui_ProfitView

class ProfitView(BaseView, Ui_ProfitView):
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.psheet = ProfitSheet(doc=doc, view=self.treeView)
        self.pgraph = ProfitGraph(doc=doc, view=self.graphView)
        self.ipiechart = IncomePieChart(doc=doc, view=self.incomePieChart)
        self.epiechart = ExpensePieChart(doc=doc, view=self.expensePieChart)
        self.children = [self.psheet, self.pgraph, self.ipiechart, self.epiechart]
    
    def _setupUi(self):
        self.setupUi(self)
    
    #--- Public
    def updateOptionalWidgetsVisibility(self):
        prefs = self.doc.app.prefs
        h = self.treeView.header()
        PREF2COLNAME = {
            'profitSheetChangeColumnVisible': 'delta',
            'profitSheetChangePercColumnVisible': 'delta_perc',
            'profitSheetLastColumnVisible': 'last_cash_flow',
            'profitSheetBudgetedColumnVisible': 'budgeted',
        }
        for prefName, colName in PREF2COLNAME.items():
            sectionIndex = self.psheet.ROWATTRS.index(colName)
            isVisible = getattr(prefs, prefName)
            h.setSectionHidden(sectionIndex, not isVisible)
        self.graphView.setHidden(not prefs.profitSheetGraphVisible)
        self.incomePieChart.setHidden(not prefs.profitSheetPieChartsVisible)
        self.expensePieChart.setHidden(not prefs.profitSheetPieChartsVisible)
    
