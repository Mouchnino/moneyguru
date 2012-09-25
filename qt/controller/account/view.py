# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QSizePolicy, QPushButton, QAbstractItemView,
    QStackedWidget, QSplitter)

from core.const import PaneArea

from hscommon.trans import trget
from qtlib.radio_box import RadioBox
from qtlib.util import horizontalSpacer

from ...support.item_view import TableView
from ...support.line_graph_view import LineGraphView
from ...support.bar_graph_view import BarGraphView
from ..base_view import BaseView
from ..chart import Chart
from .filter_bar import EntryFilterBar
from .table import EntryTable

tr = trget('ui')

class EntryView(BaseView):
    def _setup(self):
        self._setupUi()
        self.etable = EntryTable(self.model.etable, view=self.tableView)
        self.efbar = EntryFilterBar(model=self.model.filter_bar, view=self.filterBar)
        self.bgraph = Chart(self.model.bargraph, view=self.barGraphView)
        self.lgraph = Chart(self.model.balgraph, view=self.lineGraphView)
        self._setupColumns() # Can only be done after the model has been connected
        
        self.reconciliationButton.clicked.connect(self.model.toggle_reconciliation_mode)
    
    def _setupUi(self):
        self.resize(483, 423)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.filterBar = RadioBox(self)
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filterBar.sizePolicy().hasHeightForWidth())
        self.filterBar.setSizePolicy(sizePolicy)
        self.horizontalLayout.addWidget(self.filterBar)
        self.horizontalLayout.addItem(horizontalSpacer())
        self.reconciliationButton = QPushButton(tr("Reconciliation"))
        self.reconciliationButton.setCheckable(True)
        self.horizontalLayout.addWidget(self.reconciliationButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.splitterView = QSplitter()
        self.splitterView.setOrientation(Qt.Vertical)
        self.splitterView.setChildrenCollapsible(False)
        self.tableView = TableView(self)
        self.tableView.setAcceptDrops(True)
        self.tableView.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.tableView.setDragEnabled(True)
        self.tableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setMinimumSectionSize(18)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(18)
        self.splitterView.addWidget(self.tableView)
        self.graphView = QStackedWidget(self)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphView.sizePolicy().hasHeightForWidth())
        self.graphView.setSizePolicy(sizePolicy)
        self.graphView.setMinimumSize(0, 200)
        self.lineGraphView = LineGraphView()
        self.graphView.addWidget(self.lineGraphView)
        self.barGraphView = BarGraphView()
        self.graphView.addWidget(self.barGraphView)
        self.splitterView.addWidget(self.graphView)
        self.graphView.setCurrentIndex(1)
        self.splitterView.setStretchFactor(0, 1)
        self.splitterView.setStretchFactor(1, 0)
        self.verticalLayout.addWidget(self.splitterView)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
    
    #--- QWidget override
    def setFocus(self):
        self.etable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        hidden = self.model.mainwindow.hidden_areas
        viewPrinter.fitTable(self.etable)
        if PaneArea.BottomGraph not in hidden:
            viewPrinter.fit(self.graphView.currentWidget(), 300, 150, expandH=True, expandV=True)
    
    def restoreSubviewsSize(self):
        graphHeight = self.model.graph_height_to_restore
        if graphHeight:
            splitterHeight = self.splitterView.height()
            sizes = [splitterHeight-graphHeight, graphHeight]
            self.splitterView.setSizes(sizes)
    
    #--- model --> view
    def refresh_reconciliation_button(self):
        if self.model.can_toggle_reconciliation_mode:
            self.reconciliationButton.setEnabled(True)
            self.reconciliationButton.setChecked(self.model.reconciliation_mode)
        else:
            self.reconciliationButton.setEnabled(False)
            self.reconciliationButton.setChecked(False)
    
    def show_bar_graph(self):
        self.graphView.setCurrentIndex(1)
    
    def show_line_graph(self):
        self.graphView.setCurrentIndex(0)
    
    def update_visibility(self):
        hidden = self.model.mainwindow.hidden_areas
        self.graphView.setHidden(PaneArea.BottomGraph in hidden)
    
