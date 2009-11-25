# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-21
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from .base_view import BaseView
from .schedule_table import ScheduleTable
from ui.schedule_view_ui import Ui_ScheduleView

class ScheduleView(BaseView, Ui_ScheduleView):
    def __init__(self, doc):
        BaseView.__init__(self)
        self.doc = doc
        self._setupUi()
        self.sctable = ScheduleTable(doc=doc, view=self.tableView)
        self.children = [self.sctable]
        self._setupColumns() # Can only be done after the model has been connected
    
    def _setupUi(self):
        self.setupUi(self)
    
    def _setupColumns(self):
        h = self.tableView.horizontalHeader()
        h.setHighlightSections(False)
        self.sctable.resizeColumns()
    
    #--- Public
    def updateOptionalWidgetsVisibility(self):
        prefs = self.doc.app.prefs
        h = self.tableView.horizontalHeader()
        PREF2COLNAME = {
            'scheduleTableDescriptionColumnVisible': 'description',
            'scheduleTablePayeeColumnVisible': 'payee',
            'scheduleTableChecknoColumnVisible': 'checkno',
        }
        for prefName, colName in PREF2COLNAME.items():
            sectionIndex = self.sctable.ATTR2COLUMN[colName].index
            isVisible = getattr(prefs, prefName)
            h.setSectionHidden(sectionIndex, not isVisible)
    
