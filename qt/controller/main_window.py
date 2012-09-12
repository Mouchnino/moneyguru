# Created By: Virgil Dupras
# Created On: 2009-10-31
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import os.path as op

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QProcess, QUrl
from PyQt4.QtGui import (QMainWindow, QPrintDialog, QMessageBox, QIcon, QPixmap,
    QDesktopServices, QTabBar, QSizePolicy, QHBoxLayout, QPushButton, QMenu, QAction, QMenuBar)

from qtlib.recent import Recent
from qtlib.search_edit import SearchEdit
from qtlib.util import horizontalSpacer, setAccelKeys
from hscommon.trans import trget
from hscommon.plat import ISLINUX
from core.const import PaneType, PaneArea
from core.gui.main_window import MainWindow as MainWindowModel

from ..support.date_range_selector_view import DateRangeSelectorView
from ..print_ import ViewPrinter
from .account.view import EntryView
from .budget.view import BudgetView
from .networth.view import NetWorthView
from .profit.view import ProfitView
from .transaction.view import TransactionView
from .schedule.view import ScheduleView
from .general_ledger.view import GeneralLedgerView
from .docprops_view import DocPropsView
from .new_view import NewView
from .readonly_table_plugin_view import ReadOnlyTablePluginView
from .lookup import Lookup
from .account_panel import AccountPanel
from .account_reassign_panel import AccountReassignPanel
from .transaction_panel import TransactionPanel
from .mass_edition_panel import MassEditionPanel
from .schedule_panel import SchedulePanel
from .budget_panel import BudgetPanel
from .export_panel import ExportPanel
from .custom_date_range_panel import CustomDateRangePanel
from .search_field import SearchField
from .date_range_selector import DateRangeSelector

tr = trget('ui')

PANETYPE2ICON = {
    PaneType.NetWorth: 'balance_sheet_16',
    PaneType.Profit: 'income_statement_16',
    PaneType.Transaction: 'transaction_table_16',
    PaneType.Account: 'entry_table_16',
    PaneType.Schedule: 'schedules_16',
    PaneType.Budget: 'budget_16',
    PaneType.GeneralLedger: 'gledger_16',
    PaneType.DocProps: 'gledger_16',
}

PANETYPE2VIEWCLASS = {
    PaneType.NetWorth: NetWorthView,
    PaneType.Profit: ProfitView,
    PaneType.Transaction: TransactionView,
    PaneType.Account: EntryView,
    PaneType.Schedule: ScheduleView,
    PaneType.Budget: BudgetView,
    PaneType.GeneralLedger: GeneralLedgerView,
    PaneType.DocProps: DocPropsView,
    PaneType.Empty: NewView,
    PaneType.ReadOnlyTablePlugin: ReadOnlyTablePluginView,
}

# IMPORTANT NOTE ABOUT TABS
# Why don't we use a QTabWidget? Because it doesn't allow to add the same widget twice.

class MainWindow(QMainWindow):
    def __init__(self, doc):
        QMainWindow.__init__(self, None)
        self.doc = doc
        self.app = doc.app
        
        self._setupUi()
        
        # Create base elements
        self.model = MainWindowModel(document=doc.model)
        self.model2view = {}
        self.apanel = AccountPanel(mainwindow=self)
        self.tpanel = TransactionPanel(mainwindow=self)
        self.mepanel = MassEditionPanel(mainwindow=self)
        self.scpanel = SchedulePanel(mainwindow=self)
        self.bpanel = BudgetPanel(mainwindow=self)
        self.cdrpanel = CustomDateRangePanel(mainwindow=self)
        self.arpanel = AccountReassignPanel(mainwindow=self)
        self.expanel = ExportPanel(mainwindow=self)
        self.alookup = Lookup(self, model=self.model.account_lookup)
        self.clookup = Lookup(self, model=self.model.completion_lookup)
        self.drsel = DateRangeSelector(mainwindow=self, view=self.dateRangeSelectorView)
        self.sfield = SearchField(model=self.model.search_field, view=self.searchLineEdit)
        self.recentDocuments = Recent(self.app, 'recentDocuments')
        self.recentDocuments.addMenu(self.menuOpenRecent)
        
        self.model.view = self
        self.model.connect()
        
        self._updateUndoActions()
        self._bindSignals()
    
    def _setupUi(self): # has to take place *before* base elements creation
        self.setWindowTitle("moneyGuru")
        self.resize(700, 580)
        self.centralwidget = QtGui.QWidget(self)
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        self.topBar = QtGui.QWidget(self.centralwidget)
        self.horizontalLayout_2 = QHBoxLayout(self.topBar)
        self.horizontalLayout_2.setContentsMargins(2, 0, 2, 0)
        spacerItem = QtGui.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.dateRangeSelectorView = DateRangeSelectorView(self.topBar)
        self.dateRangeSelectorView.setMinimumSize(QtCore.QSize(220, 0))
        self.horizontalLayout_2.addWidget(self.dateRangeSelectorView)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.searchLineEdit = SearchEdit(self.topBar)
        self.searchLineEdit.setMaximumSize(QtCore.QSize(240, 16777215))
        self.horizontalLayout_2.addWidget(self.searchLineEdit)
        self.verticalLayout.addWidget(self.topBar)
        self.tabBar = QTabBar(self.centralwidget)
        self.tabBar.setMinimumSize(QtCore.QSize(0, 20))
        self.verticalLayout.addWidget(self.tabBar)
        self.mainView = QtGui.QStackedWidget(self.centralwidget)
        self.verticalLayout.addWidget(self.mainView)
        
        # Bottom buttons & status label
        self.bottomBar = QtGui.QWidget(self.centralwidget)
        self.horizontalLayout = QHBoxLayout(self.bottomBar)
        self.horizontalLayout.setMargin(2)
        self.horizontalLayout.setMargin(0)
        self.newItemButton = QPushButton(self.bottomBar)
        buttonSizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        buttonSizePolicy.setHorizontalStretch(0)
        buttonSizePolicy.setVerticalStretch(0)
        buttonSizePolicy.setHeightForWidth(self.newItemButton.sizePolicy().hasHeightForWidth())
        self.newItemButton.setSizePolicy(buttonSizePolicy)
        self.newItemButton.setIcon(QIcon(QPixmap(':/plus_8')))
        self.horizontalLayout.addWidget(self.newItemButton)
        self.deleteItemButton = QPushButton(self.bottomBar)
        self.deleteItemButton.setSizePolicy(buttonSizePolicy)
        self.deleteItemButton.setIcon(QIcon(QPixmap(':/minus_8')))
        self.horizontalLayout.addWidget(self.deleteItemButton)
        self.editItemButton = QPushButton(self.bottomBar)
        self.editItemButton.setSizePolicy(buttonSizePolicy)
        self.editItemButton.setIcon(QIcon(QPixmap(':/info_gray_12')))
        self.horizontalLayout.addWidget(self.editItemButton)
        self.horizontalLayout.addItem(horizontalSpacer(size=20))
        self.graphVisibilityButton = QPushButton()
        self.graphVisibilityButton.setSizePolicy(buttonSizePolicy)
        self.graphVisibilityButton.setIcon(QIcon(QPixmap(':/graph_visibility_on_16')))
        self.horizontalLayout.addWidget(self.graphVisibilityButton)
        self.piechartVisibilityButton = QPushButton()
        self.piechartVisibilityButton.setSizePolicy(buttonSizePolicy)
        self.piechartVisibilityButton.setIcon(QIcon(QPixmap(':/piechart_visibility_on_16')))
        self.horizontalLayout.addWidget(self.piechartVisibilityButton)
        self.columnsVisibilityButton = QPushButton()
        self.columnsVisibilityButton.setSizePolicy(buttonSizePolicy)
        self.columnsVisibilityButton.setIcon(QIcon(QPixmap(':/columns_16')))
        self.horizontalLayout.addWidget(self.columnsVisibilityButton)
        
        self.statusLabel = QtGui.QLabel(tr("Status"))
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.horizontalLayout.addWidget(self.statusLabel)
        self.verticalLayout.addWidget(self.bottomBar)
        
        
        self.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 700, 20))
        self.menuFile = QMenu(tr("File"))
        self.menuOpenRecent = QMenu(tr("Open Recent"))
        self.menuView = QMenu(tr("View"))
        self.menuDateRange = QMenu(tr("Date Range"))
        self.menuEdit = QMenu(tr("Edit"))
        self.menuHelp = QMenu(tr("Help"))
        self.setMenuBar(self.menubar)
        self.actionOpenDocument = QAction(tr("Open..."), self)
        self.actionOpenDocument.setShortcut("Ctrl+O")
        self.actionShowNetWorth = QAction(tr("Net Worth"), self)
        self.actionShowNetWorth.setShortcut("Ctrl+1")
        self.actionShowNetWorth.setIcon(QIcon(QPixmap(':/balance_sheet_48')))
        self.actionShowProfitLoss = QAction(tr("Profit & Loss"), self)
        self.actionShowProfitLoss.setShortcut("Ctrl+2")
        self.actionShowProfitLoss.setIcon(QIcon(QPixmap(':/income_statement_48')))
        self.actionShowTransactions = QAction(tr("Transactions"), self)
        self.actionShowTransactions.setShortcut("Ctrl+3")
        self.actionShowTransactions.setIcon(QIcon(QPixmap(':/transaction_table_48')))
        self.actionShowSelectedAccount = QAction(tr("Show Account"), self)
        self.actionShowSelectedAccount.setShortcut("Ctrl+]")
        self.actionNewItem = QAction(tr("New Item"), self)
        self.actionNewItem.setShortcut("Ctrl+N")
        self.actionDeleteItem = QAction(tr("Remove Selected"), self)
        self.actionEditItem = QAction(tr("Show Info"), self)
        self.actionEditItem.setShortcut("Ctrl+I")
        self.actionToggleGraph = QAction(tr("Toggle Graph"), self)
        self.actionToggleGraph.setShortcut("Ctrl+Alt+G")
        self.actionTogglePieChart = QAction(tr("Toggle Pie Chart"), self)
        self.actionTogglePieChart.setShortcut("Ctrl+Alt+P")
        self.actionMoveUp = QAction(tr("Move Up"), self)
        self.actionMoveUp.setShortcut("Ctrl++")
        self.actionMoveDown = QAction(tr("Move Down"), self)
        self.actionMoveDown.setShortcut("Ctrl+-")
        self.actionNavigateBack = QAction(tr("Go Back"), self)
        self.actionNavigateBack.setShortcut("Ctrl+[")
        self.actionNewAccountGroup = QAction(tr("New Account Group"), self)
        self.actionNewAccountGroup.setShortcut("Ctrl+Shift+N")
        self.actionShowNextView = QAction(tr("Next View"), self)
        self.actionShowNextView.setShortcut("Ctrl+Shift+]")
        self.actionShowPreviousView = QAction(tr("Previous View"), self)
        self.actionShowPreviousView.setShortcut("Ctrl+Shift+[")
        self.actionNewDocument = QAction(tr("New Document"), self)
        self.actionOpenExampleDocument = QAction(tr("Open Example Document"), self)
        self.actionOpenPluginFolder = QAction(tr("Open Plugin Folder"), self)
        self.actionImport = QAction(tr("Import..."), self)
        self.actionImport.setShortcut("Ctrl+Alt+I")
        self.actionExport = QAction(tr("Export..."), self)
        self.actionExport.setShortcut("Ctrl+Alt+E")
        self.actionSave = QAction(tr("Save"), self)
        self.actionSave.setShortcut("Ctrl+S")
        self.actionSaveAs = QAction(tr("Save As..."), self)
        self.actionSaveAs.setShortcut("Ctrl+Shift+S")
        self.actionRegister = QAction(tr("Register moneyGuru"), self)
        self.actionAbout = QAction(tr("About moneyGuru"), self)
        self.actionToggleReconciliationMode = QAction(tr("Toggle Reconciliation Mode"), self)
        self.actionToggleReconciliationMode.setShortcut("Ctrl+Shift+R")
        self.actionToggleAccountExclusion = QAction(tr("Toggle Exclusion Status of Account"), self)
        self.actionToggleAccountExclusion.setShortcut("Ctrl+Shift+X")
        self.actionShowSchedules = QAction(tr("Schedules"), self)
        self.actionShowSchedules.setShortcut("Ctrl+4")
        self.actionShowSchedules.setIcon(QIcon(QPixmap(':/schedules_48')))
        self.actionShowBudgets = QAction(tr("Budgets"), self)
        self.actionShowBudgets.setShortcut("Ctrl+5")
        self.actionShowBudgets.setIcon(QIcon(QPixmap(':/budget_48')))
        self.actionReconcileSelected = QAction(tr("Reconcile Selection"), self)
        self.actionReconcileSelected.setShortcut("Ctrl+R")
        self.actionMakeScheduleFromSelected = QAction(tr("Make Schedule from Selected"), self)
        self.actionMakeScheduleFromSelected.setShortcut("Ctrl+M")
        self.actionShowPreferences = QAction(tr("Preferences..."), self)
        self.actionPrint = QAction(tr("Print..."), self)
        self.actionPrint.setShortcut("Ctrl+P")
        self.actionQuit = QAction(tr("Quit moneyGuru"), self)
        self.actionQuit.setShortcut("Ctrl+Q")
        self.actionUndo = QAction(tr("Undo"), self)
        self.actionUndo.setShortcut("Ctrl+Z")
        self.actionRedo = QAction(tr("Redo"), self)
        self.actionRedo.setShortcut("Ctrl+Y")
        self.actionShowHelp = QAction(tr("moneyGuru Help"), self)
        self.actionShowHelp.setShortcut("F1")
        self.actionCheckForUpdate = QAction(tr("Check for update"), self)
        self.actionOpenDebugLog = QAction(tr("Open Debug Log"), self)
        self.actionDuplicateTransaction = QAction(tr("Duplicate Transaction"), self)
        self.actionDuplicateTransaction.setShortcut("Ctrl+D")
        self.actionJumpToAccount = QAction(tr("Jump to Account..."), self)
        self.actionJumpToAccount.setShortcut("Ctrl+Shift+A")
        self.actionNewTab = QAction(tr("New Tab"), self)
        self.actionNewTab.setShortcut("Ctrl+T")
        self.actionCloseTab = QAction(tr("Close Tab"), self)
        self.actionCloseTab.setShortcut("Ctrl+W")
        
        self.menuFile.addAction(self.actionNewDocument)
        self.menuFile.addAction(self.actionNewTab)
        self.menuFile.addAction(self.actionOpenDocument)
        self.menuFile.addAction(self.menuOpenRecent.menuAction())
        self.menuFile.addAction(self.actionOpenExampleDocument)
        self.menuFile.addAction(self.actionOpenPluginFolder)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionCloseTab)
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionExport)
        self.menuFile.addAction(self.actionPrint)
        self.menuFile.addAction(self.actionQuit)
        self.menuView.addAction(self.actionShowNetWorth)
        self.menuView.addAction(self.actionShowProfitLoss)
        self.menuView.addAction(self.actionShowTransactions)
        self.menuView.addAction(self.actionShowSchedules)
        self.menuView.addAction(self.actionShowBudgets)
        self.menuView.addAction(self.actionShowPreviousView)
        self.menuView.addAction(self.actionShowNextView)
        self.menuView.addAction(self.menuDateRange.menuAction())
        self.menuView.addAction(self.actionShowPreferences)
        self.menuView.addAction(self.actionToggleGraph)
        self.menuView.addAction(self.actionTogglePieChart)
        self.menuEdit.addAction(self.actionNewItem)
        self.menuEdit.addAction(self.actionNewAccountGroup)
        self.menuEdit.addAction(self.actionDeleteItem)
        self.menuEdit.addAction(self.actionEditItem)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionMoveUp)
        self.menuEdit.addAction(self.actionMoveDown)
        self.menuEdit.addAction(self.actionDuplicateTransaction)
        self.menuEdit.addAction(self.actionMakeScheduleFromSelected)
        self.menuEdit.addAction(self.actionReconcileSelected)
        self.menuEdit.addAction(self.actionToggleReconciliationMode)
        self.menuEdit.addAction(self.actionToggleAccountExclusion)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionShowSelectedAccount)
        self.menuEdit.addAction(self.actionNavigateBack)
        self.menuEdit.addAction(self.actionJumpToAccount)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuHelp.addAction(self.actionShowHelp)
        self.menuHelp.addAction(self.actionRegister)
        self.menuHelp.addAction(self.actionCheckForUpdate)
        self.menuHelp.addAction(self.actionOpenDebugLog)
        self.menuHelp.addAction(self.actionAbout)
        mainmenus = [self.menuFile, self.menuEdit, self.menuView, self.menuHelp]
        for menu in mainmenus:
            self.menubar.addAction(menu.menuAction())
            setAccelKeys(menu)
        setAccelKeys(self.menubar)
        self.tabBar.setMovable(True)
        self.tabBar.setTabsClosable(True)
        
        # Linux setup
        if ISLINUX:
            self.actionCheckForUpdate.setVisible(False) # This only works on Windows
    
    def _bindSignals(self):
        self.newItemButton.clicked.connect(self.actionNewItem.trigger)
        self.deleteItemButton.clicked.connect(self.actionDeleteItem.trigger)
        self.editItemButton.clicked.connect(self.actionEditItem.trigger)
        self.graphVisibilityButton.clicked.connect(self.actionToggleGraph.trigger)
        self.piechartVisibilityButton.clicked.connect(self.actionTogglePieChart.trigger)
        self.columnsVisibilityButton.clicked.connect(self.columnsVisibilityButtonClicked)
        self.recentDocuments.mustOpenItem.connect(self.doc.open)
        self.doc.documentOpened.connect(self.recentDocuments.insertItem)
        self.doc.documentSavedAs.connect(self.recentDocuments.insertItem)
        self.doc.documentPathChanged.connect(self.documentPathChanged)
        self.tabBar.currentChanged.connect(self.currentTabChanged)
        self.tabBar.tabCloseRequested.connect(self.tabCloseRequested)
        self.tabBar.tabMoved.connect(self.tabMoved)
        
        # Views
        self.actionShowNetWorth.triggered.connect(self.showNetWorthTriggered)        
        self.actionShowProfitLoss.triggered.connect(self.showProfitLossTriggered)        
        self.actionShowTransactions.triggered.connect(self.showTransactionsTriggered)        
        self.actionShowSchedules.triggered.connect(self.showSchedulesTriggered)        
        self.actionShowBudgets.triggered.connect(self.showBudgetsTriggered)        
        self.actionShowPreviousView.triggered.connect(self.showPreviousViewTriggered)        
        self.actionShowNextView.triggered.connect(self.showNextViewTriggered)        
        self.actionShowPreferences.triggered.connect(self.app.showPreferences)
        self.actionToggleGraph.triggered.connect(self.toggleGraphTriggered)
        self.actionTogglePieChart.triggered.connect(self.togglePieChartTriggered)
        
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
        self.actionOpenPluginFolder.triggered.connect(self.model.app.open_plugin_folder)
        self.actionImport.triggered.connect(self.doc.importDocument)
        self.actionSave.triggered.connect(self.doc.save)
        self.actionSaveAs.triggered.connect(self.doc.saveAs)
        self.actionExport.triggered.connect(self.model.export)
        
        # Misc
        self.actionNewTab.triggered.connect(self.model.new_tab)
        self.actionCloseTab.triggered.connect(self.closeTabTriggered)
        self.actionShowSelectedAccount.triggered.connect(self.model.show_account)
        self.actionNavigateBack.triggered.connect(self.navigateBackTriggered)
        self.actionJumpToAccount.triggered.connect(self.jumpToAccountTriggered)
        self.actionMakeScheduleFromSelected.triggered.connect(self.makeScheduleFromSelectedTriggered)
        self.actionReconcileSelected.triggered.connect(self.reconcileSelectedTriggered)
        self.actionToggleReconciliationMode.triggered.connect(self.toggleReconciliationModeTriggered)
        self.actionToggleAccountExclusion.triggered.connect(self.toggleAccountExclusionTriggered)
        self.actionPrint.triggered.connect(self._print)
        self.actionShowHelp.triggered.connect(self.app.showHelp)
        self.actionRegister.triggered.connect(self.registerTriggered)
        self.actionCheckForUpdate.triggered.connect(self.checkForUpdateTriggered)
        self.actionAbout.triggered.connect(self.aboutTriggered)
        self.actionOpenDebugLog.triggered.connect(self.openDebugLogTriggered)
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
        viewPrinter = ViewPrinter(printer, currentView)
        currentView.fitViewsForPrint(viewPrinter)
        viewPrinter.render()
    
    def _getViewforPane(self, pane_type, pane_view):
        if pane_view in self.model2view:
            view = self.model2view[pane_view]
        else:
            view = PANETYPE2VIEWCLASS[pane_type](model=pane_view)
            self.model2view[pane_view] = view
            self.mainView.addWidget(view)
        return view
    
    def _setTabIndex(self, index):
        if not self.tabBar.count():
            return
        self.tabBar.setCurrentIndex(index)
        self._updateActionsState()
        pane_type = self.model.pane_type(index)
        pane_view = self.model.pane_view(index)
        view = self._getViewforPane(pane_type, pane_view)
        self.mainView.setCurrentWidget(view)
        view.setFocus()
    
    def _activeView(self):
        paneIndex = self.model.current_pane_index
        return self.model.pane_view(paneIndex)
    
    def _updateActionsState(self):
        # Updates enable/disable checked/unchecked state of all actions. These state can change
        # under various conditions: main view change, date range type change and when reconciliation
        # mode is toggled
        
        # Determine what actions are enabled
        view = self._activeView()
        viewType = view.VIEW_TYPE
        isSheet = viewType in {PaneType.NetWorth, PaneType.Profit}
        isTransactionOrEntryTable = viewType in {PaneType.Transaction, PaneType.Account}
        canToggleReconciliation = viewType == PaneType.Account and view.can_toggle_reconciliation_mode
        
        newItemLabel = {
            PaneType.NetWorth: tr("New Account"),
            PaneType.Profit: tr("New Account"),
            PaneType.Transaction: tr("New Transaction"),
            PaneType.Account: tr("New Transaction"),
            PaneType.Schedule: tr("New Schedule"),
            PaneType.Budget: tr("New Budget"),
            PaneType.GeneralLedger: tr("New Transaction"),
        }.get(viewType, tr("New Item")) #XXX make "New Item" disabled
        self.actionNewItem.setText(newItemLabel)
        self.actionNewAccountGroup.setEnabled(isSheet)
        self.actionMoveDown.setEnabled(isTransactionOrEntryTable)
        self.actionMoveUp.setEnabled(isTransactionOrEntryTable)
        self.actionDuplicateTransaction.setEnabled(isTransactionOrEntryTable)
        self.actionMakeScheduleFromSelected.setEnabled(isTransactionOrEntryTable)
        self.actionReconcileSelected.setEnabled(viewType == PaneType.Account and view.reconciliation_mode)
        self.actionShowNextView.setEnabled(self.model.current_pane_index < self.model.pane_count-1)
        self.actionShowPreviousView.setEnabled(self.model.current_pane_index > 0)
        self.actionShowSelectedAccount.setEnabled(isSheet or isTransactionOrEntryTable)
        self.actionNavigateBack.setEnabled(viewType == PaneType.Account)
        self.actionToggleReconciliationMode.setEnabled(canToggleReconciliation)
        self.actionToggleAccountExclusion.setEnabled(isSheet)
    
    def _updateUndoActions(self):
        if self.doc.model.can_undo():
            self.actionUndo.setEnabled(True)
            self.actionUndo.setText(tr("Undo {0}").format(self.doc.model.undo_description()))
        else:
            self.actionUndo.setEnabled(False)
            self.actionUndo.setText(tr("Undo"))
        if self.doc.model.can_redo():
            self.actionRedo.setEnabled(True)
            self.actionRedo.setText(tr("Redo {0}").format(self.doc.model.redo_description()))
        else:
            self.actionRedo.setEnabled(False)
            self.actionRedo.setText(tr("Redo"))
    
    #--- Actions
    # Views
    def showNetWorthTriggered(self):
        self.model.select_pane_of_type(PaneType.NetWorth)
    
    def showProfitLossTriggered(self):
        self.model.select_pane_of_type(PaneType.Profit)
    
    def showTransactionsTriggered(self):
        self.model.select_pane_of_type(PaneType.Transaction)
    
    def showSchedulesTriggered(self):
        self.model.select_pane_of_type(PaneType.Schedule)
    
    def showBudgetsTriggered(self):
        self.model.select_pane_of_type(PaneType.Budget)
    
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
    def closeTabTriggered(self):
        self.model.close_pane(self.model.current_pane_index)
    
    def navigateBackTriggered(self):
        self.model.navigate_back()
    
    def jumpToAccountTriggered(self):
        self.model.jump_to_account()
    
    def makeScheduleFromSelectedTriggered(self):
        self.model.make_schedule_from_selected()
    
    def reconcileSelectedTriggered(self):
        self._activeView().etable.toggle_reconciled()
    
    def toggleReconciliationModeTriggered(self):
        self._activeView().toggle_reconciliation_mode()
        self._updateActionsState()
    
    def toggleAccountExclusionTriggered(self):
        viewType = self.model.pane_type(self.model.current_pane_index)
        if viewType in {PaneType.NetWorth, PaneType.Profit}:
            self._activeView().sheet.toggle_excluded()
    
    def toggleGraphTriggered(self):
        self.model.toggle_area_visibility(PaneArea.BottomGraph)
    
    def togglePieChartTriggered(self):
        self.model.toggle_area_visibility(PaneArea.RightChart)
    
    def columnsVisibilityButtonClicked(self):
        items = self.model.column_menu_items()
        if not items:
            return
        menu = QMenu()
        for i, (display, marked) in enumerate(items):
            action = menu.addAction(display)
            action.setCheckable(True)
            action.setChecked(marked)
            action.setData(i)
            action.triggered.connect(self.columnsMenuItemWasClicked)
        self._columnMenuHolder = menu # we need to hold a reference to it while it popups
        button = self.columnsVisibilityButton
        menu.popup(button.parentWidget().mapToGlobal(button.geometry().topLeft()))
    
    def columnsMenuItemWasClicked(self):
        action = self.sender()
        if action is not None:
            index, ok = action.data().toInt()
            self.model.toggle_column_menu_item(index)
    
    def registerTriggered(self):
        self.app.askForRegCode()
    
    def checkForUpdateTriggered(self):
        QProcess.execute('updater.exe', ['/checknow'])
    
    def aboutTriggered(self):
        self.app.showAboutBox()
    
    def openDebugLogTriggered(self):
        appdata = QDesktopServices.storageLocation(QDesktopServices.DataLocation)
        debugLogPath = op.join(appdata, 'debug.log')
        url = QUrl.fromLocalFile(debugLogPath)
        QDesktopServices.openUrl(url)
    
    #--- Other Signals
    def currentTabChanged(self, index):
        self.model.current_pane_index = index
        self._setTabIndex(index)
    
    def documentPathChanged(self):
        if self.doc.documentPath:
            title = "moneyGuru ({})".format(self.doc.documentPath)
        else:
            title = "moneyGuru"
        self.setWindowTitle(title)
    
    def tabCloseRequested(self, index):
        self.model.close_pane(index)
    
    def tabMoved(self, fromIndex, toIndex):
        self.model.move_pane(fromIndex, toIndex)
    
    #--- model --> view
    def change_current_pane(self):
        self._setTabIndex(self.model.current_pane_index)
    
    def refresh_panes(self):
        if self.tabBar.currentIndex() < self.model.pane_count:
            # Normally, we don't touch the tabBar index here and wait for change_current_pane,
            # but when we remove tabs, it's possible that currentTabChanged end up being called and
            # then the tab selection is bugged. I tried disconnecting/reconnecting the signal, but
            # this is buggy. So when a selected tab is about to be removed, we change the selection
            # to the model's one immediately.
            self.tabBar.setCurrentIndex(self.model.current_pane_index)
        while self.tabBar.count() > self.model.pane_count:
            self.tabBar.removeTab(self.tabBar.count()-1)
        while self.tabBar.count() < self.model.pane_count:
            self.tabBar.addTab('')
        for i in range(self.model.pane_count):
            pane_label = self.model.pane_label(i)
            pane_label = pane_label.replace('&', '&&')
            self.tabBar.setTabText(i, pane_label)
            pane_type = self.model.pane_type(i)
            pane_view = self.model.pane_view(i)
            # Ensure that the view's "view" has been created and bound
            self._getViewforPane(pane_type, pane_view)
            iconname = PANETYPE2ICON.get(pane_type)
            icon = QIcon(QPixmap(':/{0}'.format(iconname))) if iconname else QIcon()
            self.tabBar.setTabIcon(i, icon)
        self.tabBar.setTabsClosable(self.model.pane_count > 1)
    
    def refresh_status_line(self):
        self.statusLabel.setText(self.model.status_line)
    
    def refresh_undo_actions(self):
        self._updateUndoActions()
    
    def show_message(self, msg):
        title = tr("Warning")
        QMessageBox.warning(self, title, msg)
    
    def update_area_visibility(self):
        hidden = self.model.hidden_areas
        graphimg = ':/graph_visibility_{}_16'.format('off' if PaneArea.BottomGraph in hidden else 'on')
        pieimg = ':/piechart_visibility_{}_16'.format('off' if PaneArea.RightChart in hidden else 'on')
        self.graphVisibilityButton.setIcon(QIcon(QPixmap(graphimg)))
        self.piechartVisibilityButton.setIcon(QIcon(QPixmap(pieimg)))
    
    def view_closed(self, index):
        self.tabBar.removeTab(index)
        self.tabBar.setTabsClosable(self.model.pane_count > 1)
    
