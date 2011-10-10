# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import QSize
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QFrame, QAbstractItemView

from core.gui.networth_view import NetWorthView as NetWorthViewModel

from ...support.item_view import TreeView
from ...support.pie_chart_view import PieChartView
from ...support.line_graph_view import LineGraphView
from ..base_view import BaseView
from .sheet import NetWorthSheet
from .graph import NetWorthGraph
from .asset_pie_chart import AssetPieChart
from .liability_pie_chart import LiabilityPieChart

class NetWorthView(BaseView):
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
        self.resize(558, 447)
        self.verticalLayout_2 = QVBoxLayout(self)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setMargin(0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.treeView = TreeView(self)
        self.treeView.setAcceptDrops(True)
        self.treeView.setFrameShape(QFrame.NoFrame)
        self.treeView.setFrameShadow(QFrame.Plain)
        self.treeView.setEditTriggers(QAbstractItemView.EditKeyPressed|QAbstractItemView.SelectedClicked)
        self.treeView.setDragEnabled(True)
        self.treeView.setDragDropMode(QAbstractItemView.InternalMove)
        self.treeView.setUniformRowHeights(True)
        self.treeView.setAllColumnsShowFocus(True)
        self.treeView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.treeView.header().setStretchLastSection(False)
        self.horizontalLayout.addWidget(self.treeView)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.assetPieChart = PieChartView(self)
        self.assetPieChart.setMinimumSize(QSize(250, 0))
        self.verticalLayout.addWidget(self.assetPieChart)
        self.liabilityPieChart = PieChartView(self)
        self.verticalLayout.addWidget(self.liabilityPieChart)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.graphView = LineGraphView(self)
        self.graphView.setMinimumSize(QSize(0, 200))
        self.verticalLayout_2.addWidget(self.graphView)
    
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
    
