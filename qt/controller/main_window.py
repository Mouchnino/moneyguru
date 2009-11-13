# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op
import tempfile

from PyQt4.QtCore import SIGNAL, QFile
from PyQt4.QtGui import QMainWindow, QFileDialog, QMenu

from moneyguru.gui.main_window import MainWindow as MainWindowModel

from support.recent import Recent
from .networth_view import NetWorthView
from .profit_view import ProfitView
from .transaction_view import TransactionView
from .entry_view import EntryView
from .account_panel import AccountPanel
from .transaction_panel import TransactionPanel
from .custom_date_range_panel import CustomDateRangePanel
from ui.main_window_ui import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, doc):
        QMainWindow.__init__(self, None)
        self.doc = doc
        self.nwview = NetWorthView(doc=doc)
        self.pview = ProfitView(doc=doc)
        self.tview = TransactionView(doc=doc)
        self.eview = EntryView(doc=doc)
        self.apanel = AccountPanel(doc=doc)
        self.tpanel = TransactionPanel(doc=doc)
        self.cdrpanel = CustomDateRangePanel(doc=doc)
        self._setupUi()
        children = [self.nwview.nwsheet.model, self.pview.psheet.model, self.tview.ttable.model,
            self.eview.etable.model, None, None, self.apanel.model, self.tpanel.model, None, None,
            None]
        self.model = MainWindowModel(view=self, document=doc.model, children=children)
        self.model.connect()
        
        # Recent Menu
        self.recentDocuments = Recent(self.menuOpenRecent, 'RecentDocuments', filterFunc=op.exists)
        self.connect(self.recentDocuments, SIGNAL('mustOpenItem(QString)'), self.mustOpenRecentDocument)
        
        # Actions
        # Date range
        self.connect(self.actionNextDateRange, SIGNAL('triggered()'), self.nextDateRangeTriggered)
        self.connect(self.actionPreviousDateRange, SIGNAL('triggered()'), self.previousDateRangeTriggered)
        self.connect(self.actionTodayDateRange, SIGNAL('triggered()'), self.todayDateRangeTriggered)
        self.connect(self.actionChangeDateRangeMonth, SIGNAL('triggered()'), self.changeDateRangeMonthTriggered)
        self.connect(self.actionChangeDateRangeQuarter, SIGNAL('triggered()'), self.changeDateRangeQuarterTriggered)
        self.connect(self.actionChangeDateRangeYear, SIGNAL('triggered()'), self.changeDateRangeYearTriggered)
        self.connect(self.actionChangeDateRangeYearToDate, SIGNAL('triggered()'), self.changeDateRangeYearToDateTriggered)
        self.connect(self.actionChangeDateRangeRunningYear, SIGNAL('triggered()'), self.changeDateRangeRunningYearTriggered)
        self.connect(self.actionChangeDateRangeCustom, SIGNAL('triggered()'), self.changeDateRangeCustomTriggered)
        
        # Views
        self.connect(self.actionShowNetWorth, SIGNAL('triggered()'), self.showNetWorthTriggered)        
        self.connect(self.actionShowProfitLoss, SIGNAL('triggered()'), self.showProfitLossTriggered)        
        self.connect(self.actionShowTransactions, SIGNAL('triggered()'), self.showTransactionsTriggered)        
        self.connect(self.actionShowAccount, SIGNAL('triggered()'), self.showAccountTriggered)        
        self.connect(self.actionShowPreviousView, SIGNAL('triggered()'), self.showPreviousViewTriggered)        
        self.connect(self.actionShowNextView, SIGNAL('triggered()'), self.showNextViewTriggered)        
        
        # Document Edition
        self.connect(self.actionNewItem, SIGNAL('triggered()'), self.newItemTriggered)
        self.connect(self.actionNewAccountGroup, SIGNAL('triggered()'), self.newAccountGroupTriggered)
        self.connect(self.actionDeleteItem, SIGNAL('triggered()'), self.deleteItemTriggered)
        self.connect(self.actionEditItem, SIGNAL('triggered()'), self.editItemTriggered)
        self.connect(self.actionMoveUp, SIGNAL('triggered()'), self.moveUpTriggered)
        self.connect(self.actionMoveDown, SIGNAL('triggered()'), self.moveDownTriggered)
        
        # Misc
        self.connect(self.actionNewDocument, SIGNAL('triggered()'), self.newDocumentTriggered)
        self.connect(self.actionOpenDocument, SIGNAL('triggered()'), self.openDocumentTriggered)
        self.actionOpenExampleDocument.triggered.connect(self.openExampleDocumentTriggered)
        self.connect(self.actionShowSelectedAccount, SIGNAL('triggered()'), self.showSelectedAccountTriggered)
        self.connect(self.actionNavigateBack, SIGNAL('triggered()'), self.navigateBackTriggered)
    
    def _setupUi(self):
        self.setupUi(self)
        self.mainView.addWidget(self.nwview)
        self.mainView.addWidget(self.pview)
        self.mainView.addWidget(self.tview)
        self.mainView.addWidget(self.eview)
        
        # Date range menu
        menu = QMenu(self.dateRangeButton)
        menu.addAction(self.actionChangeDateRangeMonth)
        menu.addAction(self.actionChangeDateRangeQuarter)
        menu.addAction(self.actionChangeDateRangeYear)
        menu.addAction(self.actionChangeDateRangeYearToDate)
        menu.addAction(self.actionChangeDateRangeRunningYear)
        menu.addAction(self.actionChangeDateRangeCustom)
        self.dateRangeButton.setMenu(menu)
    
    def _setMainWidgetIndex(self, index):
        self.mainView.currentWidget().disconnect()
        self.mainView.setCurrentIndex(index)
        self.mainView.currentWidget().connect()
    
    #--- Actions
    # Date range
    def changeDateRangeCustomTriggered(self):
        self.doc.model.select_custom_date_range()
    
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
    
    def todayDateRangeTriggered(self):
        self.doc.model.select_today_date_range()
    
    # Views
    def showNetWorthTriggered(self):
        self.model.select_balance_sheet()
    
    def showProfitLossTriggered(self):
        self.model.select_income_statement()
    
    def showTransactionsTriggered(self):
        self.model.select_transaction_table()
    
    def showAccountTriggered(self):
        self.model.select_entry_table()
    
    def showPreviousViewTriggered(self):
        self.model.select_previous_view()
    
    def showNextViewTriggered(self):
        self.model.select_next_view()
    
    # Document Edition
    def newItemTriggered(self):
        self.model.new_item()
    
    def newAccountGroupTriggered(self):
        self.model.new_group()
    
    def deleteItemTriggered(self):
        self.model.delete_item()
    
    def editItemTriggered(self):
        self.model.edit_item()
    
    def moveUpTriggered(self):
        self.model.move_up()
    
    def moveDownTriggered(self):
        self.model.move_down()
    
    # Misc
    def newDocumentTriggered(self):
        self.doc.model.clear()
    
    def openDocumentTriggered(self):
        title = "Select a document to load"
        docpath = unicode(QFileDialog.getOpenFileName(self, title))
        if docpath:
            self.doc.model.load_from_xml(docpath)
            self.recentDocuments.itemWasOpened(docpath)
    
    def openExampleDocumentTriggered(self):
        dirpath = tempfile.mkdtemp()
        destpath = op.join(dirpath, 'example.moneyguru')
        QFile.copy(':/example.moneyguru', destpath)
        self.doc.model.load_from_xml(destpath)
        self.doc.model.adjust_example_file()
    
    def showSelectedAccountTriggered(self):
        self.doc.model.show_selected_account()
    
    def navigateBackTriggered(self):
        self.model.navigate_back()
    
    def mustOpenRecentDocument(self, docpath):
        self.doc.model.load_from_xml(docpath)
    
    #--- model --> view
    def animate_date_range_backward(self):
        pass
    
    def animate_date_range_forward(self):
        pass
    
    def refresh_date_range_selector(self):
        self.dateRangeButton.setText(self.doc.model.date_range.display)
    
    def show_balance_sheet(self):
        self._setMainWidgetIndex(0)        
    
    def show_bar_graph(self):
        self.eview.showBarGraph()
    
    def show_custom_date_range_panel(self):
        self.cdrpanel.load()
    
    def show_entry_table(self):
        self._setMainWidgetIndex(3)
    
    def show_line_graph(self):
        self.eview.showLineGraph()
    
    def show_income_statement(self):
        self._setMainWidgetIndex(1)        
    
    def show_transaction_table(self):
        self._setMainWidgetIndex(2)
    
