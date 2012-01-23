# Created By: Virgil Dupras
# Created On: 2009-11-13
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWidget, QTabBar

from hscommon.trans import trget

from core.gui.import_window import ImportWindow as ImportWindowModel
from ...support.item_view import TableView
from .table import ImportTable

tr = trget('ui')

class ImportWindow(QWidget):
    def __init__(self, parent, doc):
        QWidget.__init__(self, parent, Qt.Window)
        self._setupUi()
        self.doc = doc
        self.model = ImportWindowModel(view=self, document=doc.model)
        self.table = ImportTable(model=self.model.import_table, view=self.tableView)
        self._setupColumns() # Can only be done after the model has been connected
        
        self.tabView.tabCloseRequested.connect(self.tabCloseRequested)
        self.tabView.currentChanged.connect(self.currentTabChanged)
        self.targetAccountComboBox.currentIndexChanged.connect(self.targetAccountChanged)
        self.importButton.clicked.connect(self.importClicked)
        self.swapOptionsComboBox.currentIndexChanged.connect(self.swapTypeChanged)
        self.swapButton.clicked.connect(self.swapClicked)
    
    def _setupUi(self):
        self.setWindowTitle(tr("Import"))
        self.resize(557, 407)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.tabView = QTabBar(self)
        self.tabView.setMinimumSize(QtCore.QSize(0, 20))
        self.verticalLayout.addWidget(self.tabView)
        self.targetAccountLayout = QtGui.QHBoxLayout()
        self.targetAccountLabel = QtGui.QLabel(tr("Target Account:"))
        self.targetAccountLayout.addWidget(self.targetAccountLabel)
        self.targetAccountComboBox = QtGui.QComboBox(self)
        self.targetAccountComboBox.setMinimumSize(QtCore.QSize(150, 0))
        self.targetAccountLayout.addWidget(self.targetAccountComboBox)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.targetAccountLayout.addItem(spacerItem)
        self.groupBox = QtGui.QGroupBox(tr("Some fields are wrong? Swap them!"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.swapOptionsComboBox = QtGui.QComboBox(self.groupBox)
        self.swapOptionsComboBox.addItem(tr("Day <--> Month"))
        self.swapOptionsComboBox.addItem(tr("Month <--> Year"))
        self.swapOptionsComboBox.addItem(tr("Day <--> Year"))
        self.swapOptionsComboBox.addItem(tr("Description <--> Payee"))
        self.swapOptionsComboBox.addItem(tr("Invert Amounts"))
        self.gridLayout.addWidget(self.swapOptionsComboBox, 0, 0, 1, 2)
        self.applyToAllCheckBox = QtGui.QCheckBox(tr("Apply to all accounts"))
        self.gridLayout.addWidget(self.applyToAllCheckBox, 1, 0, 1, 1)
        self.swapButton = QtGui.QPushButton(tr("Swap"))
        self.gridLayout.addWidget(self.swapButton, 1, 1, 1, 1)
        self.targetAccountLayout.addWidget(self.groupBox)
        self.verticalLayout.addLayout(self.targetAccountLayout)
        self.tableView = TableView(self)
        self.tableView.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableView.setDragEnabled(True)
        self.tableView.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.tableView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.tableView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableView.horizontalHeader().setHighlightSections(False)
        self.tableView.horizontalHeader().setMinimumSectionSize(18)
        self.tableView.verticalHeader().setVisible(False)
        self.tableView.verticalHeader().setDefaultSectionSize(18)
        self.verticalLayout.addWidget(self.tableView)
        self.horizontalLayout = QtGui.QHBoxLayout()
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.importButton = QtGui.QPushButton(tr("Import"))
        self.horizontalLayout.addWidget(self.importButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tabView.setTabsClosable(True)
        self.tabView.setDrawBase(False)
        self.tabView.setDocumentMode(True)
        self.tabView.setUsesScrollButtons(True)
    
    def _setupColumns(self):
        # Can't set widget alignment in a layout in the Designer
        l = self.targetAccountLayout
        l.setAlignment(self.targetAccountLabel, Qt.AlignTop)
        l.setAlignment(self.targetAccountComboBox, Qt.AlignTop)
    
    #--- Event Handlers
    def currentTabChanged(self, index):
        self.model.selected_pane_index = index
    
    def importClicked(self):
        self.model.import_selected_pane()
    
    def swapClicked(self):
        if self.model.can_perform_swap():
            applyToAll = self.applyToAllCheckBox.isChecked()
            self.model.perform_swap(applyToAll)
    
    def swapTypeChanged(self, index):
        self.model.swap_type_index = index
        self.swapButton.setEnabled(self.model.can_perform_swap())
    
    def tabCloseRequested(self, index):
        self.model.close_pane(index)
        self.tabView.removeTab(index)
    
    def targetAccountChanged(self, index):
        self.model.selected_target_account_index = index
        self.table.updateColumnsVisibility()
    
    #--- model --> view
    def close(self):
        self.hide()
    
    def close_selected_tab(self):
        self.tabView.removeTab(self.tabView.currentIndex())
    
    def refresh_target_accounts(self):
        # We disconnect the combobox because we don't want the clear() call to set the selected 
        # target index in the model.
        self.targetAccountComboBox.currentIndexChanged.disconnect(self.targetAccountChanged)
        self.targetAccountComboBox.clear()
        self.targetAccountComboBox.addItems(self.model.target_account_names)
        self.targetAccountComboBox.currentIndexChanged.connect(self.targetAccountChanged)
    
    def refresh_tabs(self):
        while self.tabView.count():
            self.tabView.removeTab(0)
        for pane in self.model.panes:
            self.tabView.addTab(pane.name)
    
    def show(self):
        # For non-modal dialogs, show() is not enough to bring the window at the forefront, we have
        # to call raise() as well
        QWidget.show(self)
        self.raise_()
    
    def update_selected_pane(self):
        index = self.model.selected_pane_index
        if index != self.tabView.currentIndex(): # this prevents infinite loops
            self.tabView.setCurrentIndex(index)
        self.targetAccountComboBox.setCurrentIndex(self.model.selected_target_account_index)
        self.table.updateColumnsVisibility()
        self.swapButton.setEnabled(self.model.can_perform_swap())
    
