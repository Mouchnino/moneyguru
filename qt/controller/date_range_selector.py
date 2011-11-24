# Created By: Virgil Dupras
# Created On: 2010-03-15
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import QObject
from PyQt4.QtGui import QMenu, QAction

from hscommon.trans import trget

tr = trget('ui')

class DateRangeSelector(QObject):
    def __init__(self, mainwindow, view):
        QObject.__init__(self)
        self.mainwindow = mainwindow
        self.view = view
        self.model = mainwindow.model.daterange_selector
        self.model.view = self
        self._setupUi()
    
    def _setupUi(self):
        # Create actions
        self.actionNext = QAction(tr("Next"), self)
        self.actionNext.setShortcut("Ctrl+Alt+]")
        self.actionNext.triggered.connect(self.model.select_next_date_range)
        self.actionPrevious = QAction(tr("Previous"), self)
        self.actionPrevious.setShortcut("Ctrl+Alt+[")
        self.actionPrevious.triggered.connect(self.model.select_prev_date_range)
        self.actionToday = QAction(tr("Today"), self)
        self.actionToday.setShortcut("Ctrl+Alt+T")
        self.actionToday.triggered.connect(self.model.select_today_date_range)
        self.actionChangeToMonth = QAction(tr("Month"), self)
        self.actionChangeToMonth.setShortcut("Ctrl+Alt+1")
        self.actionChangeToMonth.triggered.connect(self.model.select_month_range)
        self.actionChangeToQuarter = QAction(tr("Quarter"), self)
        self.actionChangeToQuarter.setShortcut("Ctrl+Alt+2")
        self.actionChangeToQuarter.triggered.connect(self.model.select_quarter_range)
        self.actionChangeToYear = QAction(tr("Year"), self)
        self.actionChangeToYear.setShortcut("Ctrl+Alt+3")
        self.actionChangeToYear.triggered.connect(self.model.select_year_range)
        self.actionChangeToYearToDate = QAction(tr("Year To Date"), self)
        self.actionChangeToYearToDate.setShortcut("Ctrl+Alt+4")
        self.actionChangeToYearToDate.triggered.connect(self.model.select_year_to_date_range)
        self.actionChangeToRunningYear = QAction(tr("Running Year"), self)
        self.actionChangeToRunningYear.setShortcut("Ctrl+Alt+5")
        self.actionChangeToRunningYear.triggered.connect(self.model.select_running_year_range)
        self.actionChangeToAllTransactions = QAction(tr("All Transactions"), self)
        self.actionChangeToAllTransactions.setShortcut("Ctrl+Alt+6")
        self.actionChangeToAllTransactions.triggered.connect(self.model.select_all_transactions_range)
        self.actionChangeToCustom = QAction(tr("Custom..."), self)
        self.actionChangeToCustom.setShortcut("Ctrl+Alt+7")
        self.actionChangeToCustom.triggered.connect(self.model.select_custom_date_range)
        self.actionChangeToCustom1 = QAction("Custom1", self)
        self.actionChangeToCustom1.setShortcut("Ctrl+Alt+8")
        self.actionChangeToCustom1.setVisible(False)
        self.actionChangeToCustom1.triggered.connect(self.custom1Triggered)
        self.actionChangeToCustom2 = QAction("Custom2", self)
        self.actionChangeToCustom2.setShortcut("Ctrl+Alt+9")
        self.actionChangeToCustom2.setVisible(False)
        self.actionChangeToCustom2.triggered.connect(self.custom2Triggered)
        self.actionChangeToCustom3 = QAction("Custom3", self)
        self.actionChangeToCustom3.setShortcut("Ctrl+Alt+0")
        self.actionChangeToCustom3.setVisible(False)
        self.actionChangeToCustom3.triggered.connect(self.custom3Triggered)
        
        # set typeButton menu
        menu = QMenu(self.view.typeButton)
        menu.addAction(self.actionChangeToMonth)
        menu.addAction(self.actionChangeToQuarter)
        menu.addAction(self.actionChangeToYear)
        menu.addAction(self.actionChangeToYearToDate)
        menu.addAction(self.actionChangeToRunningYear)
        menu.addAction(self.actionChangeToAllTransactions)
        menu.addAction(self.actionChangeToCustom)
        menu.addAction(self.actionChangeToCustom1)
        menu.addAction(self.actionChangeToCustom2)
        menu.addAction(self.actionChangeToCustom3)
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
        m.addAction(self.actionChangeToCustom1)
        m.addAction(self.actionChangeToCustom2)
        m.addAction(self.actionChangeToCustom3)
        m.addAction(self.actionPrevious)
        m.addAction(self.actionNext)
        m.addAction(self.actionToday)
        
        # bind prev/next button
        self.view.prevButton.clicked.connect(self.model.select_prev_date_range)
        self.view.nextButton.clicked.connect(self.model.select_next_date_range)
    
    #--- Event Handlers
    def custom1Triggered(self):
        self.model.select_saved_range(0)
    
    def custom2Triggered(self):
        self.model.select_saved_range(1)
    
    def custom3Triggered(self):
        self.model.select_saved_range(2)
    
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
    
    def refresh_custom_ranges(self):
        customActions = [self.actionChangeToCustom1, self.actionChangeToCustom2,
            self.actionChangeToCustom3]
        for i, name in enumerate(self.model.custom_range_names):
            action = customActions[i]
            if name is not None:
                action.setText(name)
                action.setVisible(True)
            else:
                action.setVisible(False)
    
