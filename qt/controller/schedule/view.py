# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..base_view import BaseView
from .table import ScheduleTable
from ui.schedule_view_ui import Ui_ScheduleView

class ScheduleView(BaseView, Ui_ScheduleView):
    PRINT_TITLE_FORMAT = "Schedules from {startDate} to {endDate}"
    
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.sctable = ScheduleTable(doc=doc, view=self.tableView)
        self.children = [self.sctable]
        self._setupColumns() # Can only be done after the model has been connected
        
        self.doc.app.willSavePrefs.connect(self._savePrefs)
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setMovable(True) # column drag & drop reorder
        self.sctable.setColumnsWidth(self.doc.app.prefs.scheduleColumnWidths)
        self.sctable.setColumnsOrder(self.doc.app.prefs.scheduleColumnOrder)
    
    def _savePrefs(self):
        h = self.tableView.horizontalHeader()
        widths = [h.sectionSize(index) for index in xrange(len(self.sctable.COLUMNS))]
        self.doc.app.prefs.scheduleColumnWidths = widths
        order = [h.logicalIndex(index) for index in xrange(len(self.sctable.COLUMNS))]
        self.doc.app.prefs.scheduleColumnOrder = order
    
    #--- Public
    def updateOptionalWidgetsVisibility(self):
        self.sctable.setHiddenColumns(self.doc.app.prefs.scheduleHiddenColumns)
    
