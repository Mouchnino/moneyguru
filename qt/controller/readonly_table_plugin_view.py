# Created On: 2012-02-03
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtGui import (QVBoxLayout, QAbstractItemView)

from ..support.item_view import TableView
from .base_view import BaseView
from .table import Table

class ReadOnlyTablePluginView(BaseView):
    def _setup(self):
        self._setupUi()
        self.table = Table(model=self.model.table, view=self.tableView)
    
    def _setupUi(self):
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setMargin(0)
        self.tableView = TableView(self)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setMinimumSectionSize(18)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(18)
        self.verticalLayout.addWidget(self.tableView)
    
    #--- QWidget override
    def setFocus(self):
        self.table.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.table)
    
