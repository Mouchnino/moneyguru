# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QProcess
from PyQt4.QtGui import QMainWindow, QIcon, QPixmap, QPrintDialog, QLabel, QFont, QMessageBox

from core.gui.main_window import MainWindow as MainWindowModel

from print_ import ViewPrinter
from support.recent import Recent
from support.search_edit import SearchEdit
from .account.view import EntryView
from .budget.view import BudgetView
from .networth.view import NetWorthView
from .profit.view import ProfitView
from .transaction.view import TransactionView
from .schedule.view import ScheduleView
from .lookup import AccountLookup, CompletionLookup
from .account_panel import AccountPanel
from .account_reassign_panel import AccountReassignPanel
from .transaction_panel import TransactionPanel
from .mass_edition_panel import MassEditionPanel
from .schedule_panel import SchedulePanel
from .budget_panel import BudgetPanel
from .custom_date_range_panel import CustomDateRangePanel
from .search_field import SearchField
from .date_range_selector import DateRangeSelector
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
        
        self._setupUi()
        
        # Create base elements
        self.model = MainWindowModel(view=self, document=doc.model)
        self.nwview = NetWorthView(mainwindow=self)
        self.pview = ProfitView(mainwindow=self)
        self.tview = TransactionView(mainwindow=self)
        self.eview = EntryView(mainwindow=self)
        self.scview = ScheduleView(mainwindow=self)
        self.bview = BudgetView(mainwindow=self)
        self.apanel = AccountPanel(mainwindow=self)
        self.tpanel = TransactionPanel(mainwindow=self)
        self.mepanel = MassEditionPanel(mainwindow=self)
        self.scpanel = SchedulePanel(mainwindow=self)
        self.bpanel = BudgetPanel(mainwindow=self)
        self.cdrpanel = CustomDateRangePanel(self, mainwindow=self)
        self.arpanel = AccountReassignPanel(self, doc=doc)
        self.alookup = AccountLookup(self, mainwindow=self)
        self.clookup = CompletionLookup(self, mainwindow=self)
        self.drsel = DateRangeSelector(mainwindow=self, view=self.dateRangeSelectorView)
        self.sfield = SearchField(mainwindow=self, view=self.searchLineEdit)
        self.recentDocuments = Recent(self.app, self.menuOpenRecent, 'recentDocuments')
        
        # Set main views
        self.mainView.addWidget(self.nwview)
        self.mainView.addWidget(self.pview)
        self.mainView.addWidget(self.tview)
        self.mainView.addWidget(self.eview)
        self.mainView.addWidget(self.scview)
        self.mainView.addWidget(self.bview)
        
        # set_children() and connect() calls have to happen after _setupUiPost()
        children = [self.nwview.model, self.pview.model, self.tview.model, self.eview.model,
            self.scview.model, self.bview.model, self.apanel.model, self.tpanel.model,
            self.mepanel.model, self.scpanel.model, self.bpanel.model, self.cdrpanel.model,
            self.alookup.model, self.clookup.model, self.drsel.model]
        self.model.set_children(children)
        self.model.connect()
        self.sfield.model.connect()
        
        self._updateUndoActions()
        self._bindSignals()
    
    def _setupUi(self): # has to take place *before* base elements creation
        self.setupUi(self)
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
        
        # Restore window size
        # We don't set geometry if the window was maximized so that if the user de-maximize the
        # window, it actually shrinks.
        if self.app.prefs.mainWindowRect is not None and not self.app.prefs.mainWindowIsMaximized:
            self.setGeometry(self.app.prefs.mainWindowRect)
    
    def _bindSignals(self):
        self.recentDocuments.mustOpenItem.connect(self.doc.open)
        self.doc.documentOpened.connect(self.recentDocuments.insertItem)
        self.doc.documentSavedAs.connect(self.recentDocuments.insertItem)
        self.app.willSavePrefs.connect(self._savePrefs)
        
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
        self.actionDuplicateTransaction.triggered.connect(self.model.duplicate_item)
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
        self.actionShowSelectedAccount.triggered.connect(self.model.show_account)
        self.actionNavigateBack.triggered.connect(self.navigateBackTriggered)
        self.actionJumpToAccount.triggered.connect(self.jumpToAccountTriggered)
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
        self.app.prefs.mainWindowIsMaximized = self.isMaximized()
        self.app.prefs.mainWindowRect = self.geometry()
    
    def _setMainWidgetIndex(self, index):
        self.mainView.setCurrentIndex(index)
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
        self.actionDuplicateTransaction.setEnabled(isTransactionOrEntryTable)
        self.actionMakeScheduleFromSelected.setEnabled(isTransactionOrEntryTable)
        self.actionReconcileSelected.setEnabled(viewIndex == ACCOUNT_INDEX and self.doc.model.in_reconciliation_mode())
        self.actionShowNextView.setEnabled(viewIndex != BUDGET_INDEX)
        self.actionShowPreviousView.setEnabled(viewIndex != NETWORTH_INDEX)
        self.actionShowAccount.setEnabled(shownAccount is not None)
        self.actionShowSelectedAccount.setEnabled(isSheet or isTransactionOrEntryTable)
        self.actionNavigateBack.setEnabled(viewIndex == ACCOUNT_INDEX)
        self.actionToggleReconciliationMode.setEnabled(canToggleReconciliation)
        self.actionToggleReconciliationModeToolbar.setEnabled(canToggleReconciliation)
    
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
    def navigateBackTriggered(self):
        self.model.navigate_back()
    
    def jumpToAccountTriggered(self):
        self.model.jump_to_account()
    
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
    
    def show_budget_table(self):
        self._setMainWidgetIndex(BUDGET_INDEX)
    
    def show_entry_table(self):
        self._setMainWidgetIndex(ACCOUNT_INDEX)
    
    def show_income_statement(self):
        self._setMainWidgetIndex(PROFIT_INDEX)
    
    def show_schedule_table(self):
        self._setMainWidgetIndex(SCHEDULE_INDEX)
    
    def show_transaction_table(self):
        self._setMainWidgetIndex(TRANSACTION_INDEX)
    
    def show_message(self, msg):
        title = "Warning"
        QMessageBox.warning(self, title, msg)
    
