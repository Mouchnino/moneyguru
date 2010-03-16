# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-03-15
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QMenu, QAction

from core.gui.date_range_selector import DateRangeSelector as DateRangeSelectorModel

class DateRangeSelector(QObject):
    def __init__(self, mainwindow, view):
        QObject.__init__(self)
        self.mainwindow = mainwindow
        self.view = view
        self.model = DateRangeSelectorModel(self, mainwindow.model)
        self._setupUi()
    
    def _setupUi(self):
        # Create actions
        self.actionNext = QAction("Next", self)
        self.actionNext.setShortcut("Ctrl+Alt+]")
        self.actionNext.triggered.connect(self.model.select_next_date_range)
        self.actionPrevious = QAction("Previous", self)
        self.actionPrevious.setShortcut("Ctrl+Alt+[")
        self.actionPrevious.triggered.connect(self.model.select_prev_date_range)
        self.actionToday = QAction("Today", self)
        self.actionToday.setShortcut("Ctrl+Alt+T")
        self.actionToday.triggered.connect(self.model.select_today_date_range)
        self.actionChangeToMonth = QAction("Month", self)
        self.actionChangeToMonth.setShortcut("Ctrl+Alt+1")
        self.actionChangeToMonth.triggered.connect(self.model.select_month_range)
        self.actionChangeToQuarter = QAction("Quarter", self)
        self.actionChangeToQuarter.setShortcut("Ctrl+Alt+2")
        self.actionChangeToQuarter.triggered.connect(self.model.select_quarter_range)
        self.actionChangeToYear = QAction("Year", self)
        self.actionChangeToYear.setShortcut("Ctrl+Alt+3")
        self.actionChangeToYear.triggered.connect(self.model.select_year_range)
        self.actionChangeToYearToDate = QAction("Year to date", self)
        self.actionChangeToYearToDate.setShortcut("Ctrl+Alt+4")
        self.actionChangeToYearToDate.triggered.connect(self.model.select_year_to_date_range)
        self.actionChangeToRunningYear = QAction("Running Year", self)
        self.actionChangeToRunningYear.setShortcut("Ctrl+Alt+5")
        self.actionChangeToRunningYear.triggered.connect(self.model.select_running_year_range)
        self.actionChangeToAllTransactions = QAction("All Transactions", self)
        self.actionChangeToAllTransactions.setShortcut("Ctrl+Alt+6")
        self.actionChangeToAllTransactions.triggered.connect(self.model.select_all_transactions_range)
        self.actionChangeToCustom = QAction("Custom...", self)
        self.actionChangeToCustom.setShortcut("Ctrl+Alt+7")
        self.actionChangeToCustom.triggered.connect(self.model.select_custom_date_range)
        
        # set typeButton menu
        menu = QMenu(self.view.typeButton)
        menu.addAction(self.actionChangeToMonth)
        menu.addAction(self.actionChangeToQuarter)
        menu.addAction(self.actionChangeToYear)
        menu.addAction(self.actionChangeToYearToDate)
        menu.addAction(self.actionChangeToRunningYear)
        menu.addAction(self.actionChangeToAllTransactions)
        menu.addAction(self.actionChangeToCustom)
        self.view.typeButton.setMenu(menu)
        
        # set mainwindow's date range menu
        m = self.mainwindow.menuDateRange
        m.addAction(self.actionChangeToMonth)
        m.addAction(self.actionChangeToQuarter)
        m.addAction(self.actionChangeToYear)
        m.addAction(self.actionChangeToYearToDate)
        m.addAction(self.actionChangeToRunningYear)
        m.addAction(self.actionChangeToAllTransactions)
        m.addAction(self.actionChangeToCustom)
        m.addAction(self.actionPrevious)
        m.addAction(self.actionNext)
        m.addAction(self.actionToday)
        
        # bind prev/next button
        self.view.prevButton.clicked.connect(self.model.select_prev_date_range)
        self.view.nextButton.clicked.connect(self.model.select_next_date_range)
    
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
        self.view.typeButton.setText(self.model.display)
        canNavigateDateRange = self.model.can_navigate
        self.actionNext.setEnabled(canNavigateDateRange)
        self.actionPrevious.setEnabled(canNavigateDateRange)
        self.actionToday.setEnabled(canNavigateDateRange)
        self.view.prevButton.setEnabled(canNavigateDateRange)
        self.view.nextButton.setEnabled(canNavigateDateRange)
    
