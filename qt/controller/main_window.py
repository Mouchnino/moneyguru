# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QProcess
from PyQt4.QtGui import QMainWindow, QMenu, QIcon, QPixmap, QPrintDialog, QLabel, QFont

from moneyguru.gui.main_window import MainWindow as MainWindowModel

from print_ import ViewPrinter
from support.recent import Recent
from support.search_edit import SearchEdit
from .account.view import EntryView
from .budget.view import BudgetView
from .networth.view import NetWorthView
from .profit.view import ProfitView
from .transaction.view import TransactionView
from .schedule.view import ScheduleView
from .account_panel import AccountPanel
from .account_reassign_panel import AccountReassignPanel
from .transaction_panel import TransactionPanel
from .mass_edition_panel import MassEditionPanel
from .schedule_panel import SchedulePanel
from .budget_panel import BudgetPanel
from .custom_date_range_panel import CustomDateRangePanel
from .search_field import SearchField
from ui.main_window_ui import Ui_MainWindow

NETWORTH_INDEX = 0
PROFIT_INDEX = 1
TRANSACTION_INDEX = 2
ACCOUNT_INDEX = 3
SCHEDULE_INDEX = 4
BUDGET_INDEX = 5

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
        self.apanel = AccountPanel(self, doc=doc)
        self.tpanel = TransactionPanel(self, doc=doc)
        self.mepanel = MassEditionPanel(self, doc=doc)
        self.scpanel = SchedulePanel(self, doc=doc)
        self.bpanel = BudgetPanel(self, doc=doc)
        self.cdrpanel = CustomDateRangePanel(self, doc=doc)
        self.arpanel = AccountReassignPanel(self, doc=doc)
        self._setupUi()
        if self.app.prefs.mainWindowRect is not None:
            self.setGeometry(self.app.prefs.mainWindowRect)
        children = [self.nwview.nwsheet.model, self.pview.psheet.model, self.tview.ttable.model,
            self.eview.etable.model, self.scview.sctable.model, self.bview.btable.model,
            self.apanel.model, self.tpanel.model, self.mepanel.model, self.scpanel.model,
            self.bpanel.model]
        self.model = MainWindowModel(view=self, document=doc.model, children=children)
        self.model.connect()
        self.sfield = SearchField(doc=doc, view=self.searchLineEdit)
        self.sfield.model.connect()
        self._updateUndoActions()
        
        # Recent Menu
        self.recentDocuments = Recent(self.app, self.menuOpenRecent, 'recentDocuments')
        self.recentDocuments.mustOpenItem.connect(self.doc.open)
        self.doc.documentOpened.connect(self.recentDocuments.insertItem)
        self.doc.documentSavedAs.connect(self.recentDocuments.insertItem)
        
        self.app.willSavePrefs.connect(self._savePrefs)
        
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
        self.actionUndo.triggered.connect(self.doc.model.undo)
        self.actionRedo.triggered.connect(self.doc.model.redo)
        
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
        self.actionMakeScheduleFromSelected.triggered.connect(self.makeScheduleFromSelectedTriggered)
        self.actionReconcileSelected.triggered.connect(self.reconcileSelectedTriggered)
        self.actionToggleReconciliationMode.triggered.connect(self.toggleReconciliationModeTriggered)
        self.actionToggleReconciliationModeToolbar.triggered.connect(self.toggleReconciliationModeTriggered)
        self.actionShowPreferences.triggered.connect(self.app.showPreferences)
        self.actionShowViewOptions.triggered.connect(self.app.showViewOptions)
        self.actionPrint.triggered.connect(self._print)
        self.actionShowHelp.triggered.connect(self.app.showHelp)
        self.actionRegister.triggered.connect(self.registerTriggered)
        self.actionCheckForUpdate.triggered.connect(self.checkForUpdateTriggered)
        self.actionAbout.triggered.connect(self.aboutTriggered)
        self.actionQuit.triggered.connect(self.close)
    
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
        
        # Toolbar setup. We have to do it manually because it's tricky to insert the view title
        # label otherwise.
        self.toolBar.addAction(self.actionShowNetWorth)
        self.toolBar.addAction(self.actionShowProfitLoss)
        self.toolBar.addAction(self.actionShowTransactions)
        self.toolBar.addAction(self.actionShowAccount)
        self.toolBar.addAction(self.actionShowSchedules)
        self.toolBar.addAction(self.actionShowBudgets)
        self.viewTitleLabel = QLabel()
        font = QFont(self.viewTitleLabel.font())
        font.setBold(True)
        self.viewTitleLabel.setFont(font)
        self.viewTitleLabel.setMinimumWidth(82) # just enough for the widest title
        self.viewTitleLabel.setMargin(4)
        self.toolBar.addWidget(self.viewTitleLabel)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionToggleReconciliationModeToolbar)
        self.toolBar.addSeparator()
        self.searchLineEdit = SearchEdit()
        self.searchLineEdit.setMaximumWidth(240)
        self.toolBar.addWidget(self.searchLineEdit)
    
    #--- QWidget overrides
    def closeEvent(self, event):
        if self.doc.confirmDestructiveAction():
            event.accept()
        else:
            event.ignore()
    
    #--- Private
    def _print(self):
        dialog = QPrintDialog(self)
        if dialog.exec_() != QPrintDialog.Accepted:
            return
        printer = dialog.printer()
        currentView = self.mainView.currentWidget()
        viewPrinter = ViewPrinter(printer, self.doc, currentView.PRINT_TITLE_FORMAT)
        currentView.fitViewsForPrint(viewPrinter)
        viewPrinter.render()
    
    def _savePrefs(self):
        self.app.prefs.mainWindowRect = self.geometry()
    
    def _setMainWidgetIndex(self, index):
        self.mainView.currentWidget().disconnect()
        self.mainView.setCurrentIndex(index)
        self.mainView.currentWidget().connect()
        self._updateActionsState()
        self.mainView.currentWidget().setFocus()
    
    def _updateActionsState(self):
        # Updates enable/disable checked/unchecked state of all actions. These state can change
        # under various conditions: main view change, date range type change and when reconciliation
        # mode is toggled
        
        # Determine what view action is checked
        actionsInOrder = [
            self.actionShowNetWorth,
            self.actionShowProfitLoss,
            self.actionShowTransactions,
            self.actionShowAccount,
            self.actionShowSchedules,
            self.actionShowBudgets,
        ]
        viewIndex = self.mainView.currentIndex()
        for index, action in enumerate(actionsInOrder):
            checked = viewIndex == index
            action.setCheckable(checked)
            action.setChecked(checked)
            if checked:
                self.viewTitleLabel.setText(action.text())
        
        # Determine what actions are enabled
        isSheet = viewIndex in (NETWORTH_INDEX, PROFIT_INDEX)
        isTransactionOrEntryTable = viewIndex in (TRANSACTION_INDEX, ACCOUNT_INDEX)
        shownAccount = self.doc.model.shown_account
        canToggleReconciliation = viewIndex == ACCOUNT_INDEX and shownAccount is not None and \
            shownAccount.is_balance_sheet_account()
        canNavigateDateRange = self.doc.model.date_range.can_navigate
        
        newItemLabel = {
            NETWORTH_INDEX: "New Account",
            PROFIT_INDEX: "New Account",
            TRANSACTION_INDEX: "New Transaction",
            ACCOUNT_INDEX: "New Transaction",
            SCHEDULE_INDEX: "New Schedule",
            BUDGET_INDEX: "New Budget",
        }[viewIndex]
        self.actionNewItem.setText(newItemLabel)
        self.actionNewAccountGroup.setEnabled(isSheet)
        self.actionMoveDown.setEnabled(isTransactionOrEntryTable)
        self.actionMoveUp.setEnabled(isTransactionOrEntryTable)
        self.actionMakeScheduleFromSelected.setEnabled(isTransactionOrEntryTable)
        self.actionReconcileSelected.setEnabled(viewIndex == ACCOUNT_INDEX and self.doc.model.in_reconciliation_mode())
        self.actionShowNextView.setEnabled(viewIndex != BUDGET_INDEX)
        self.actionShowPreviousView.setEnabled(viewIndex != NETWORTH_INDEX)
        self.actionShowAccount.setEnabled(shownAccount is not None)
        self.actionShowSelectedAccount.setEnabled(isSheet)
        self.actionNavigateBack.setEnabled(viewIndex == ACCOUNT_INDEX)
        self.actionToggleReconciliationMode.setEnabled(canToggleReconciliation)
        self.actionToggleReconciliationModeToolbar.setEnabled(canToggleReconciliation)
        self.actionNextDateRange.setEnabled(canNavigateDateRange)
        self.actionPreviousDateRange.setEnabled(canNavigateDateRange)
        self.actionTodayDateRange.setEnabled(canNavigateDateRange)
    
    def _updateUndoActions(self):
        if self.doc.model.can_undo():
            self.actionUndo.setEnabled(True)
            self.actionUndo.setText("Undo {0}".format(self.doc.model.undo_description()))
        else:
            self.actionUndo.setEnabled(False)
            self.actionUndo.setText("Undo")
        if self.doc.model.can_redo():
            self.actionRedo.setEnabled(True)
            self.actionRedo.setText("Redo {0}".format(self.doc.model.redo_description()))
        else:
            self.actionRedo.setEnabled(False)
            self.actionRedo.setText("Redo")
    
    #--- Public
    def updateOptionalWidgetsVisibility(self):
        self.nwview.updateOptionalWidgetsVisibility()
        self.pview.updateOptionalWidgetsVisibility()
        self.tview.updateOptionalWidgetsVisibility()
        self.eview.updateOptionalWidgetsVisibility()
        self.scview.updateOptionalWidgetsVisibility()
    
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
    
    def makeScheduleFromSelectedTriggered(self):
        self.model.make_schedule_from_selected()
    
    def reconcileSelectedTriggered(self):
        self.eview.etable.model.toggle_reconciled()
    
    def toggleReconciliationModeTriggered(self):
        self.doc.model.toggle_reconciliation_mode()
    
    def registerTriggered(self):
        self.app.askForRegCode()
    
    def checkForUpdateTriggered(self):
        QProcess.execute('updater.exe', ['/checknow'])
    
    def aboutTriggered(self):
        self.app.showAboutBox()
    
    #--- model --> view
    def animate_date_range_backward(self):
        # I didn't find a way to have a nice fading effect like we do on the Cocoa side in Qt.
        # The animation framework seems to be mainly for the QGraphicsScene framework. Since QWidget
        # doesn't have an opacity property, we're kind of screwed. However, since the date range
        # widget now displays the dates of the current range, this animation is less important than
        # it used to be.
        pass
    
    def animate_date_range_forward(self):
        pass
    
    def refresh_date_range_selector(self):
        self.dateRangeButton.setText(self.doc.model.date_range.display)
        self._updateActionsState()
    
    def refresh_reconciliation_button(self):
        imgname = ':/reconcile_check_48' if self.doc.model.in_reconciliation_mode() else ':/reconcile_48'
        self.actionToggleReconciliationModeToolbar.setIcon(QIcon(QPixmap(imgname)))
        self._updateActionsState()
    
    def refresh_undo_actions(self):
        self._updateUndoActions()
    
    def show_account_reassign_panel(self):
        self.arpanel.load()
    
    def show_balance_sheet(self):
        self._setMainWidgetIndex(NETWORTH_INDEX)
    
    def show_bar_graph(self):
        self.eview.showBarGraph()
    
    def show_budget_table(self):
        self._setMainWidgetIndex(BUDGET_INDEX)
    
    def show_custom_date_range_panel(self):
        self.cdrpanel.load()
    
    def show_entry_table(self):
        self._setMainWidgetIndex(ACCOUNT_INDEX)
    
    def show_line_graph(self):
        self.eview.showLineGraph()
    
    def show_income_statement(self):
        self._setMainWidgetIndex(PROFIT_INDEX)
    
    def show_schedule_table(self):
        self._setMainWidgetIndex(SCHEDULE_INDEX)
    
    def show_transaction_table(self):
        self._setMainWidgetIndex(TRANSACTION_INDEX)
    
