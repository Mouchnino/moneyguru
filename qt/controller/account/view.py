# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtCore, QtGui

from core.const import PaneArea
from core.gui.account_view import AccountView as AccountViewModel

from hscommon.trans import trget

from qtlib.radio_box import RadioBox
from ...support.item_view import TableView
from ...support.line_graph_view import LineGraphView
from ...support.bar_graph_view import BarGraphView
from ..base_view import BaseView
from ..chart import Chart
from .filter_bar import EntryFilterBar
from .table import EntryTable

tr = trget('ui')

class EntryView(BaseView):
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self.mainwindow = mainwindow
        self.doc = mainwindow.doc
        self._setupUi()
        self.model = AccountViewModel(view=self, mainwindow=mainwindow.model)
        self.etable = EntryTable(self.model.etable, view=self.tableView)
        self.efbar = EntryFilterBar(model=self.model.filter_bar, view=self.filterBar)
        self.bgraph = Chart(self.model.bargraph, view=self.barGraphView)
        self.lgraph = Chart(self.model.balgraph, view=self.lineGraphView)
        self._setupColumns() # Can only be done after the model has been connected
        
        self.reconciliationButton.clicked.connect(self.model.toggle_reconciliation_mode)
    
    def _setupUi(self):
        self.resize(483, 423)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.filterBar = RadioBox(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filterBar.sizePolicy().hasHeightForWidth())
        self.filterBar.setSizePolicy(sizePolicy)
        self.horizontalLayout.addWidget(self.filterBar)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.reconciliationButton = QtGui.QPushButton(tr("Reconciliation"))
        self.reconciliationButton.setCheckable(True)
        self.horizontalLayout.addWidget(self.reconciliationButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableView = TableView(self)
        self.tableView.setAcceptDrops(True)
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed)
        self.tableView.setDragEnabled(True)
        self.tableView.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setMinimumSectionSize(18)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(18)
        self.verticalLayout.addWidget(self.tableView)
        self.graphView = QtGui.QStackedWidget(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphView.sizePolicy().hasHeightForWidth())
        self.graphView.setSizePolicy(sizePolicy)
        self.graphView.setMinimumSize(QtCore.QSize(0, 200))
        self.lineGraphView = LineGraphView()
        self.graphView.addWidget(self.lineGraphView)
        self.barGraphView = BarGraphView()
        self.graphView.addWidget(self.barGraphView)
        self.verticalLayout.addWidget(self.graphView)
        self.graphView.setCurrentIndex(1)
    
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
    
