# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import SIGNAL
from PyQt4.QtGui import QMainWindow, QFileDialog

from moneyguru.gui.main_window import MainWindow as MainWindowModel

from ui.main_window_ui import Ui_MainWindow

from .transaction_view import TransactionView

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, doc):
        QMainWindow.__init__(self, None)
        self.doc = doc
        self.tview = TransactionView(doc=doc)
        children = [None, None, self.tview.ttable.model, None, None, None, None, None, None, None,
            None]
        self.model = MainWindowModel(view=self, document=doc.model, children=children)
        self._setupUi()
        self.model.connect()
        self.model.select_transaction_table()
        
        # Actions
        # Date range
        self.connect(self.actionNextDateRange, SIGNAL('triggered()'), self.nextDateRangeTriggered)
        self.connect(self.actionPreviousDateRange, SIGNAL('triggered()'), self.previousDateRangeTriggered)
        self.connect(self.actionChangeDateRangeMonth, SIGNAL('triggered()'), self.changeDateRangeMonthTriggered)
        self.connect(self.actionChangeDateRangeQuarter, SIGNAL('triggered()'), self.changeDateRangeQuarterTriggered)
        self.connect(self.actionChangeDateRangeYear, SIGNAL('triggered()'), self.changeDateRangeYearTriggered)
        self.connect(self.actionChangeDateRangeYearToDate, SIGNAL('triggered()'), self.changeDateRangeYearToDateTriggered)
        self.connect(self.actionChangeDateRangeRunningYear, SIGNAL('triggered()'), self.changeDateRangeRunningYearTriggered)
        self.connect(self.actionChangeDateRangeCustom, SIGNAL('triggered()'), self.changeDateRangeCustomTriggered)
        
        # Views
        self.connect(self.actionShowTransactions, SIGNAL('triggered()'), self.showTransactionsTriggered)        
    
        # Misc
        self.connect(self.actionLoadFile, SIGNAL('triggered()'), self.loadFileTriggered)
        
    def _setupUi(self):
        self.setupUi(self)
        self.mainView.addWidget(self.tview)
        self.dateRangeMenuButton.setMenu(self.menuDateRange)
    
    #--- Actions
    # Date range
    def changeDateRangeCustomTriggered(self):
        self.doc.model.select_custom_range()
    
    def changeDateRangeMonthTriggered(self):
        self.doc.model.select_month_range()
    
    def changeDateRangeQuarterTriggered(self):
        self.doc.model.select_quarter_range()
    
    def changeDateRangeRunningYearTriggered(self):
        self.doc.model.select_running_year_range()
    
    def changeDateRangeYearTriggered(self):
        self.doc.model.select_year_range()
    
    def changeDateRangeYearToDateTriggered(self):
        self.doc.model.select_year_to_date_range()
    
    def nextDateRangeTriggered(self):
        self.doc.model.select_next_date_range()
    
    def previousDateRangeTriggered(self):
        self.doc.model.select_prev_date_range()
    
    # Views
    def showTransactionsTriggered(self):
        self.model.select_transaction_table()
    
    # Misc
    def loadFileTriggered(self):
        title = "Select a document to load"
        docpath = unicode(QFileDialog.getOpenFileName(self, title))
        if docpath:
            self.doc.model.load_from_xml(docpath)
    
    #--- model --> view
    def animate_date_range_backward(self):
        pass
    
    def animate_date_range_forward(self):
        pass
    
    def refresh_date_range_selector(self):
        self.dateRangeDisplayLabel.setText(self.doc.model.date_range.display)
    
    def show_transaction_table(self):
        self.mainView.currentWidget().disconnect()
        self.mainView.setCurrentIndex(0)
        self.mainView.currentWidget().connect()
    
