# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.profit_view import ProfitView as ProfitViewModel

from ..base_view import BaseView
from .sheet import ProfitSheet
from .graph import ProfitGraph
from .income_pie_chart import IncomePieChart
from .expense_pie_chart import ExpensePieChart
from ui.profit_view_ui import Ui_ProfitView

class ProfitView(BaseView, Ui_ProfitView):
    PRINT_TITLE_FORMAT = "Profit and loss from {startDate} to {endDate}"
    
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.psheet = ProfitSheet(doc=doc, view=self.treeView)
        self.pgraph = ProfitGraph(doc=doc, view=self.graphView)
        self.ipiechart = IncomePieChart(doc=doc, view=self.incomePieChart)
        self.epiechart = ExpensePieChart(doc=doc, view=self.expensePieChart)
        children = [self.psheet.model, self.pgraph.model, self.ipiechart.model, self.epiechart.model]
        self.model = ProfitViewModel(view=self, document=doc.model, children=children)
        self._setupColumns() # Can only be done after the model has been connected
        
        self.doc.app.willSavePrefs.connect(self._savePrefs)
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        self.psheet.setColumnsWidth(self.doc.app.prefs.profitColumnWidths)
        self.psheet.setColumnsOrder(self.doc.app.prefs.profitColumnOrder)
    
    def _savePrefs(self):
        h = self.treeView.header()
        widths = [h.sectionSize(index) for index in xrange(len(self.psheet.COLUMNS))]
        self.doc.app.prefs.profitColumnWidths = widths
        order = [h.logicalIndex(index) for index in xrange(len(self.psheet.COLUMNS))]
        self.doc.app.prefs.profitColumnOrder = order
    
    # Temporary
    def connect(self):
        self.model.connect()
    
    def disconnect(self):
        self.model.disconnect()
    
    #--- QWidget override
    def setFocus(self):
        self.psheet.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTree(self.psheet)
        viewPrinter.fit(self.ipiechart.view, 150, 150, expandH=True)
        viewPrinter.fit(self.epiechart.view, 150, 150, expandH=True)
        viewPrinter.fit(self.pgraph.view, 300, 150, expandH=True, expandV=True)
    
    def updateOptionalWidgetsVisibility(self):
        prefs = self.doc.app.prefs
        self.psheet.setHiddenColumns(prefs.profitHiddenColumns)
        self.graphView.setHidden(not prefs.profitGraphVisible)
        self.incomePieChart.setHidden(not prefs.profitPieChartsVisible)
        self.expensePieChart.setHidden(not prefs.profitPieChartsVisible)
    
