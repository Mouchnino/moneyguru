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
    
    #--- model --> view
    def animate_backward(self):
        # I didn't find a way to have a nice fading effect like we do on the Cocoa side in Qt.
        # The animation framework seems to be mainly for the QGraphicsScene framework. Since QWidget
        # doesn't have an opacity property, we're kind of screwed. However, since the date range
        # widget now displays the dates of the current range, this animation is less important than
        # it used to be.
        pass
    
    def animate_forward(self):
        pass
    
    def refresh(self):
        mw = self.mainwindow
        mw.dateRangeButton.setText(self.model.display)
        canNavigateDateRange = self.model.can_navigate
        mw.actionNextDateRange.setEnabled(canNavigateDateRange)
        mw.actionPreviousDateRange.setEnabled(canNavigateDateRange)
        mw.actionTodayDateRange.setEnabled(canNavigateDateRange)
    
