# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.schedule_view import ScheduleView as ScheduleViewModel

from ..base_view import BaseView
from .table import ScheduleTable
from ui.schedule_view_ui import Ui_ScheduleView

class ScheduleView(BaseView, Ui_ScheduleView):
    def __init__(self, mainwindow):
        BaseView.__init__(self)
        self.doc = mainwindow.doc
        self._setupUi()
        self.model = ScheduleViewModel(view=self, mainwindow=mainwindow.model)
        self.sctable = ScheduleTable(self, view=self.tableView)
        children = [self.sctable.model]
        self.model.set_children(children)
        self._setupColumns() # Can only be done after the model has been connected
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.sctable.restoreColumns()
    
    #--- QWidget override
    def setFocus(self):
        self.sctable.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        viewPrinter.fitTable(self.sctable)
    
