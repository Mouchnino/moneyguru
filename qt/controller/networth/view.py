# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..base_view import BaseView
from .sheet import NetWorthSheet
from .graph import NetWorthGraph
from .asset_pie_chart import AssetPieChart
from .liability_pie_chart import LiabilityPieChart
from ui.networth_view_ui import Ui_NetWorthView

class NetWorthView(BaseView, Ui_NetWorthView):
    PRINT_TITLE_FORMAT = "Net Worth at {endDate}, starting from {startDate}"
    
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.nwsheet = NetWorthSheet(doc=doc, view=self.treeView)
        self.nwgraph = NetWorthGraph(doc=doc, view=self.graphView)
        self.apiechart = AssetPieChart(doc=doc, view=self.assetPieChart)
        self.lpiechart = LiabilityPieChart(doc=doc, view=self.liabilityPieChart)
        self.children = [self.nwsheet, self.nwgraph, self.apiechart, self.lpiechart]
        self._setupColumns() # Can only be done after the model has been connected
        
        self.doc.app.willSavePrefs.connect(self._savePrefs)
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        self.nwsheet.setColumnsWidth(self.doc.app.prefs.networthColumnWidths)
    
    def _savePrefs(self):
        h = self.treeView.header()
        widths = [h.sectionSize(index) for index in xrange(len(self.nwsheet.COLUMNS))]
        self.doc.app.prefs.networthColumnWidths = widths
    
    #--- QWidget override
    def setFocus(self):
        self.nwsheet.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTree(self.nwsheet)
        viewPrinter.fit(self.apiechart.view, 150, 150, expandH=True)
        viewPrinter.fit(self.lpiechart.view, 150, 150, expandH=True)
        viewPrinter.fit(self.nwgraph.view, 300, 150, expandH=True, expandV=True)
    
    def updateOptionalWidgetsVisibility(self):
        prefs = self.doc.app.prefs
        self.nwsheet.setHiddenColumns(prefs.networthHiddenColumns)
        self.graphView.setHidden(not prefs.networthGraphVisible)
        self.assetPieChart.setHidden(not prefs.networthPieChartsVisible)
        self.liabilityPieChart.setHidden(not prefs.networthPieChartsVisible)
    
