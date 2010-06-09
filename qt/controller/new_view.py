# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-06-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QShortcut, QKeySequence

from core.const import PaneType
from core.gui.empty_view import EmptyView as EmptyViewModel

from .base_view import BaseView
from ui.new_view_ui import Ui_NewView

class NewView(BaseView, Ui_NewView):
    PRINT_TITLE_FORMAT = "New Tab"
    
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self._setupUi()
        self.model = EmptyViewModel(view=self, mainwindow=mainwindow.model)
        self.model.set_children([])
        
        self.networthButton.clicked.connect(self.networthButtonClicked)
        self.profitButton.clicked.connect(self.profitButtonClicked)
        self.transactionButton.clicked.connect(self.transactionButtonClicked)
        self.scheduleButton.clicked.connect(self.scheduleButtonClicked)
        self.budgetButton.clicked.connect(self.budgetButtonClicked)
        self.shortcut1.activated.connect(self.networthButtonClicked)
        self.shortcut2.activated.connect(self.profitButtonClicked)
        self.shortcut3.activated.connect(self.transactionButtonClicked)
        self.shortcut4.activated.connect(self.scheduleButtonClicked)
        self.shortcut5.activated.connect(self.budgetButtonClicked)
    
    def _setupUi(self):
        self.setupUi(self)
        self.shortcut1 = QShortcut(QKeySequence('1'), self, None, None, Qt.WidgetShortcut)
        self.shortcut2 = QShortcut(QKeySequence('2'), self, None, None, Qt.WidgetShortcut)
        self.shortcut3 = QShortcut(QKeySequence('3'), self, None, None, Qt.WidgetShortcut)
        self.shortcut4 = QShortcut(QKeySequence('4'), self, None, None, Qt.WidgetShortcut)
        self.shortcut5 = QShortcut(QKeySequence('5'), self, None, None, Qt.WidgetShortcut)
    
    #--- Event Handlers
    def networthButtonClicked(self):
        self.model.select_pane_type(PaneType.NetWorth)
    
    def profitButtonClicked(self):
        self.model.select_pane_type(PaneType.Profit)
    
    def transactionButtonClicked(self):
        self.model.select_pane_type(PaneType.Transaction)
    
    def scheduleButtonClicked(self):
        self.model.select_pane_type(PaneType.Schedule)
    
    def budgetButtonClicked(self):
        self.model.select_pane_type(PaneType.Budget)
    
