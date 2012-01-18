# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtGui

from ...support.item_view import TableView
from ..base_view import BaseView
from .table import ScheduleTable

class ScheduleView(BaseView):
    def __init__(self, model):
        BaseView.__init__(self, model)
        self._setupUi()
        self.sctable = ScheduleTable(model=self.model.table, view=self.tableView)
        self._setupColumns() # Can only be done after the model has been connected
    
    def _setupUi(self):
        self.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setMargin(0)
        self.tableView = TableView(self)
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setMinimumSectionSize(18)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(18)
        self.verticalLayout.addWidget(self.tableView)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
    
    #--- QWidget override
    def setFocus(self):
        self.sctable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.sctable)
    
