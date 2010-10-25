# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.gui.networth_view import NetWorthView as NetWorthViewModel

from ..base_view import BaseView
from .sheet import NetWorthSheet
from .graph import NetWorthGraph
from .asset_pie_chart import AssetPieChart
from .liability_pie_chart import LiabilityPieChart
from ...ui.networth_view_ui import Ui_NetWorthView

class NetWorthView(BaseView, Ui_NetWorthView):
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self.doc = mainwindow.doc
        self._setupUi()
        self.model = NetWorthViewModel(view=self, mainwindow=mainwindow.model)
        self.nwsheet = NetWorthSheet(self, view=self.treeView)
        self.nwgraph = NetWorthGraph(self, view=self.graphView)
        self.apiechart = AssetPieChart(self, view=self.assetPieChart)
        self.lpiechart = LiabilityPieChart(self, view=self.liabilityPieChart)
        children = [self.nwsheet.model, self.nwgraph.model, self.apiechart.model, self.lpiechart.model]
        self.model.set_children(children)
        self._setupColumns() # Can only be done after the model has been connected
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        self.nwsheet.restore_columns()
    
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
        self.graphView.setHidden(not prefs.networthGraphVisible)
        self.assetPieChart.setHidden(not prefs.networthPieChartsVisible)
        self.liabilityPieChart.setHidden(not prefs.networthPieChartsVisible)
    
