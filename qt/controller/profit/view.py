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
from core.gui.profit_view import ProfitView as ProfitViewModel

from ...support.item_view import TreeView
from ...support.pie_chart_view import PieChartView
from ...support.bar_graph_view import BarGraphView
from ..base_view import BaseView
from ..chart import Chart
from .sheet import ProfitSheet

class ProfitView(BaseView):
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self.doc = mainwindow.doc
        self._setupUi()
        self.model = ProfitViewModel(view=self, mainwindow=mainwindow.model)
        self.psheet = ProfitSheet(self.doc, self.model.istatement, view=self.treeView)
        self.pgraph = Chart(self.model.pgraph, view=self.graphView)
        self.ipiechart = Chart(self.model.ipie, view=self.incomePieChart)
        self.epiechart = Chart(self.model.epie, view=self.expensePieChart)
    
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
        self.incomePieChart = PieChartView(self)
        self.incomePieChart.setMinimumSize(QSize(250, 0))
        self.verticalLayout.addWidget(self.incomePieChart)
        self.expensePieChart = PieChartView(self)
        self.verticalLayout.addWidget(self.expensePieChart)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.graphView = BarGraphView(self)
        self.graphView.setMinimumSize(QSize(0, 200))
        self.verticalLayout_2.addWidget(self.graphView)
    
    #--- QWidget override
    def setFocus(self):
        self.psheet.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        hidden = self.model.mainwindow.hidden_areas
        viewPrinter.fitTree(self.psheet)
        if PaneArea.RightChart not in hidden:
            viewPrinter.fit(self.ipiechart.view, 150, 150, expandH=True)
            viewPrinter.fit(self.epiechart.view, 150, 150, expandH=True)
        if PaneArea.BottomGraph not in hidden:
            viewPrinter.fit(self.pgraph.view, 300, 150, expandH=True, expandV=True)
    
    #--- model --> view
    def update_visibility(self):
        hidden = self.model.mainwindow.hidden_areas
        self.graphView.setHidden(PaneArea.BottomGraph in hidden)
        self.incomePieChart.setHidden(PaneArea.RightChart in hidden)
        self.expensePieChart.setHidden(PaneArea.RightChart in hidden)
    
    
