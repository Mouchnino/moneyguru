# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-03-15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.date_range_selector import DateRangeSelector as DateRangeSelectorModel

# XXX This class doesn't have its own widget and refers to MainWindow's widgets directly. This is
# because actions are shared between the widget and the main menu and it would be too complicated,
# for now, to correctly put actions where they belong. It's hacky, but temporary.

class DateRangeSelector(object):
    def __init__(self, mainwindow):
        self.mainwindow = mainwindow
        self.model = DateRangeSelectorModel(self, mainwindow.model)
    
    def refresh(self):
        mw = self.mainwindow
        mw.dateRangeButton.setText(self.model.display)
        # XXX push down can_navigate to DateRangeSelectorModel!
        canNavigateDateRange = self.model.document.date_range.can_navigate
        mw.actionNextDateRange.setEnabled(canNavigateDateRange)
        mw.actionPreviousDateRange.setEnabled(canNavigateDateRange)
        mw.actionTodayDateRange.setEnabled(canNavigateDateRange)
    
