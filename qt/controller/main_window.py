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

from PyQt4.QtGui import QMainWindow, QMenu, QIcon, QPixmap, QLineEdit

from moneyguru.gui.main_window import MainWindow as MainWindowModel

from support.recent import Recent
from .networth_view import NetWorthView
from .profit_view import ProfitView
from .transaction_view import TransactionView
from .entry_view import EntryView
from .schedule_view import ScheduleView
from .budget_view import BudgetView
from .account_panel import AccountPanel
from .transaction_panel import TransactionPanel
from .schedule_panel import SchedulePanel
from .custom_date_range_panel import CustomDateRangePanel
from .import_window import ImportWindow
from .search_field import SearchField
from ui.main_window_ui import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, doc):
        QMainWindow.__init__(self, None)
        self.doc = doc
        self.app = doc.app
        self.nwview = NetWorthView(doc=doc)
        self.pview = ProfitView(doc=doc)
        self.tview = TransactionView(doc=doc)
        self.eview = EntryView(doc=doc)
        self.scview = ScheduleView(doc=doc)
        self.bview = BudgetView(doc=doc)
        self.apanel = AccountPanel(doc=doc)
        self.tpanel = TransactionPanel(doc=doc)
        self.scpanel = SchedulePanel(doc=doc)
        self.cdrpanel = CustomDateRangePanel(doc=doc)
        self._setupUi()
        children = [self.nwview.nwsheet.model, self.pview.psheet.model, self.tview.ttable.model,
            self.eview.etable.model, self.scview.sctable.model, self.bview.btable.model,
            self.apanel.model, self.tpanel.model, None, self.scpanel.model, None]
        self.model = MainWindowModel(view=self, document=doc.model, children=children)
        self.model.connect()
        self.iwindow = ImportWindow(doc=doc)
        self.iwindow.model.connect()
        self.sfield = SearchField(doc=doc, view=self.searchLineEdit)
        self.sfield.model.connect()
        
        # Recent Menu
        self.recentDocuments = Recent(self.menuOpenRecent, 'RecentDocuments', filterFunc=op.exists)
        self.recentDocuments.mustOpenItem.connect(self.doc.open)
        self.doc.documentOpened.connect(self.recentDocuments.insertItem)
        self.doc.documentSavedAs.connect(self.recentDocuments.insertItem)
        
        # Actions
        # Date range
        self.actionNextDateRange.triggered.connect(self.nextDateRangeTriggered)
        self.actionPreviousDateRange.triggered.connect(self.previousDateRangeTriggered)
        self.actionTodayDateRange.triggered.connect(self.todayDateRangeTriggered)
        self.actionChangeDateRangeMonth.triggered.connect(self.changeDateRangeMonthTriggered)
        self.actionChangeDateRangeQuarter.triggered.connect(self.changeDateRangeQuarterTriggered)
        self.actionChangeDateRangeYear.triggered.connect(self.changeDateRangeYearTriggered)
        self.actionChangeDateRangeYearToDate.triggered.connect(self.changeDateRangeYearToDateTriggered)
        self.actionChangeDateRangeRunningYear.triggered.connect(self.changeDateRangeRunningYearTriggered)
        self.actionChangeDateRangeCustom.triggered.connect(self.changeDateRangeCustomTriggered)
        
        # Views
        self.actionShowNetWorth.triggered.connect(self.showNetWorthTriggered)        
        self.actionShowProfitLoss.triggered.connect(self.showProfitLossTriggered)        
        self.actionShowTransactions.triggered.connect(self.showTransactionsTriggered)        
        self.actionShowAccount.triggered.connect(self.showAccountTriggered)        
        self.actionShowSchedules.triggered.connect(self.showSchedulesTriggered)        
        self.actionShowBudgets.triggered.connect(self.showBudgetsTriggered)        
        self.actionShowPreviousView.triggered.connect(self.showPreviousViewTriggered)        
        self.actionShowNextView.triggered.connect(self.showNextViewTriggered)        
        
        # Document Edition
        self.actionNewItem.triggered.connect(self.newItemTriggered)
        self.actionNewAccountGroup.triggered.connect(self.newAccountGroupTriggered)
        self.actionDeleteItem.triggered.connect(self.deleteItemTriggered)
        self.actionEditItem.triggered.connect(self.editItemTriggered)
        self.actionMoveUp.triggered.connect(self.moveUpTriggered)
        self.actionMoveDown.triggered.connect(self.moveDownTriggered)
        
        # Open / Save / Import / Export / New
        self.actionNewDocument.triggered.connect(self.doc.new)
        self.actionOpenDocument.triggered.connect(self.doc.openDocument)
        self.actionOpenExampleDocument.triggered.connect(self.doc.openExampleDocument)
        self.actionImport.triggered.connect(self.doc.importDocument)
        self.actionSave.triggered.connect(self.doc.save)
        self.actionSaveAs.triggered.connect(self.doc.saveAs)
        self.actionExportToQIF.triggered.connect(self.doc.exportToQIF)
        
        # Misc
        self.actionShowSelectedAccount.triggered.connect(self.showSelectedAccountTriggered)
        self.actionNavigateBack.triggered.connect(self.navigateBackTriggered)
        self.actionToggleReconciliationMode.triggered.connect(self.toggleReconciliationModeTriggered)
        self.actionToggleReconciliationModeToolbar.triggered.connect(self.toggleReconciliationModeTriggered)
        self.actionRegister.triggered.connect(self.registerTriggered)
        self.actionAbout.triggered.connect(self.aboutTriggered)
    
    def _setupUi(self):
        self.setupUi(self)
        self.mainView.addWidget(self.nwview)
        self.mainView.addWidget(self.pview)
        self.mainView.addWidget(self.tview)
        self.mainView.addWidget(self.eview)
        self.mainView.addWidget(self.scview)
        self.mainView.addWidget(self.bview)
        
        # Date range menu
        menu = QMenu(self.dateRangeButton)
        menu.addAction(self.actionChangeDateRangeMonth)
        menu.addAction(self.actionChangeDateRangeQuarter)
        menu.addAction(self.actionChangeDateRangeYear)
        menu.addAction(self.actionChangeDateRangeYearToDate)
        menu.addAction(self.actionChangeDateRangeRunningYear)
        menu.addAction(self.actionChangeDateRangeCustom)
        self.dateRangeButton.setMenu(menu)
        
        # Filter field
        self.searchLineEdit = QLineEdit()
        self.toolBar.addWidget(self.searchLineEdit)
    
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
    
    def showSchedulesTriggered(self):
        self.model.select_schedule_table()
    
    def showBudgetsTriggered(self):
        self.model.select_budget_table()
    
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
    def showSelectedAccountTriggered(self):
        self.doc.model.show_selected_account()
    
    def navigateBackTriggered(self):
        self.model.navigate_back()
    
    def toggleReconciliationModeTriggered(self):
        self.doc.model.toggle_reconciliation_mode()
    
    def registerTriggered(self):
        self.app.askForRegCode()
    
    def aboutTriggered(self):
        self.app.showAboutBox()
    
    #--- model --> view
    def animate_date_range_backward(self):
        pass
    
    def animate_date_range_forward(self):
        pass
    
    def refresh_date_range_selector(self):
        self.dateRangeButton.setText(self.doc.model.date_range.display)
    
    def refresh_reconciliation_button(self):
        imgname = ':/reconcile_check_48' if self.doc.model.in_reconciliation_mode() else ':/reconcile_48'
        self.actionToggleReconciliationModeToolbar.setIcon(QIcon(QPixmap(imgname)))
    
    def show_balance_sheet(self):
        self._setMainWidgetIndex(0)
    
    def show_bar_graph(self):
        self.eview.showBarGraph()
    
    def show_budget_table(self):
        self._setMainWidgetIndex(5)
    
    def show_custom_date_range_panel(self):
        self.cdrpanel.load()
    
    def show_entry_table(self):
        self._setMainWidgetIndex(3)
    
    def show_line_graph(self):
        self.eview.showLineGraph()
    
    def show_income_statement(self):
        self._setMainWidgetIndex(1)        
    
    def show_schedule_table(self):
        self._setMainWidgetIndex(4)
    
    def show_transaction_table(self):
        self._setMainWidgetIndex(2)
    
