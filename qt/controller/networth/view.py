# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import QSize
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QFrame, QAbstractItemView

from core.const import PaneArea

from ...support.item_view import TreeView
from ...support.pie_chart_view import PieChartView
from ...support.line_graph_view import LineGraphView
from ..base_view import BaseView
from ..chart import Chart
from .sheet import NetWorthSheet

class NetWorthView(BaseView):
    def __init__(self, model):
        BaseView.__init__(self, model)
        self._setupUi()
        self.nwsheet = NetWorthSheet(self.model.bsheet, view=self.treeView)
        self.nwgraph = Chart(self.model.nwgraph, view=self.graphView)
        self.apiechart = Chart(self.model.apie, view=self.assetPieChart)
        self.lpiechart = Chart(self.model.lpie, view=self.liabilityPieChart)
    
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
    
    #--- QWidget override
    def setFocus(self):
        self.nwsheet.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        hidden = self.model.mainwindow.hidden_areas
        viewPrinter.fitTree(self.nwsheet)
        if PaneArea.RightChart not in hidden:
            viewPrinter.fit(self.apiechart.view, 150, 150, expandH=True)
            viewPrinter.fit(self.lpiechart.view, 150, 150, expandH=True)
        if PaneArea.BottomGraph not in hidden:
            viewPrinter.fit(self.nwgraph.view, 300, 150, expandH=True, expandV=True)
    
    #--- model --> view
    def update_visibility(self):
        hidden = self.model.mainwindow.hidden_areas
        self.graphView.setHidden(PaneArea.BottomGraph in hidden)
        self.assetPieChart.setHidden(PaneArea.RightChart in hidden)
        self.liabilityPieChart.setHidden(PaneArea.RightChart in hidden)
    
