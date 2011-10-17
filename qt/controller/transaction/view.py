# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtCore, QtGui

from qtlib.radio_box import RadioBox
from core.gui.transaction_view import TransactionView as TransactionViewModel

from ...support.item_view import TableView
from ..base_view import BaseView
from .filter_bar import TransactionFilterBar
from .table import TransactionTable

class TransactionView(BaseView):
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self.doc = mainwindow.doc
        self._setupUi()
        self.model = TransactionViewModel(view=self, mainwindow=mainwindow.model)
        self.ttable = TransactionTable(self, view=self.tableView)
        self.tfbar = TransactionFilterBar(model=self.model.filter_bar, view=self.filterBar)
        children = [self.ttable.model]
        self.model.set_children(children)
        self._setupColumns() # Can only be done after the model has been connected
    
    def _setupUi(self):
        self.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.filterBar = RadioBox(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filterBar.sizePolicy().hasHeightForWidth())
        self.filterBar.setSizePolicy(sizePolicy)
        self.filterBar.setMinimumSize(QtCore.QSize(0, 20))
        self.verticalLayout.addWidget(self.filterBar)
        self.tableView = TableView(self)
        self.tableView.setAcceptDrops(True)
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed)
        self.tableView.setDragEnabled(True)
        self.tableView.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.setCornerButtonEnabled(False)
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setMinimumSectionSize(18)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(18)
        self.verticalLayout.addWidget(self.tableView)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.ttable.restore_columns()
    
    #--- QWidget override
    def setFocus(self):
        self.ttable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.ttable)
    
