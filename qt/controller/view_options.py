# Created By: Virgil Dupras
# Created On: 2009-11-24
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from hscommon.trans import tr
from core.gui.view_options import ViewOptions as ViewOptionsModel

class ViewOptionsDialog(QDialog):
    WIDGET2PREF = {
        'nwGraphCheckBox': 'networthGraphVisible',
        'nwPieChartsCheckBox': 'networthPieChartsVisible',
        'plGraphCheckBox': 'profitGraphVisible',
        'plPieChartsCheckBox': 'profitPieChartsVisible',
        'accGraphCheckBox': 'entryGraphVisible',
    }
    # widgetName: attrname
    WIDGET2COLUMN = {
        'nwChangeCheckBox': 'networth_sheet_delta',
        'nwChangePercCheckBox': 'networth_sheet_delta_perc',
        'nwStartCheckBox': 'networth_sheet_start',
        'nwBudgetedCheckBox': 'networth_sheet_budgeted',
        'nwAccountNumberCheckBox': 'networth_sheet_account_number',
        'plChangeCheckBox': 'profit_sheet_delta',
        'plChangePercCheckBox': 'profit_sheet_delta_perc',
        'plLastCheckBox': 'profit_sheet_last_cash_flow',
        'plBudgetedCheckBox': 'profit_sheet_budgeted',
        'plAccountNumberCheckBox': 'profit_sheet_account_number',
        'txnDescriptionCheckBox': 'transaction_table_description',
        'txnPayeeCheckBox': 'transaction_table_payee',
        'txnChecknoCheckBox': 'transaction_table_checkno',
        'accDescriptionCheckBox': 'entry_table_description',
        'accPayeeCheckBox': 'entry_table_payee',
        'accChecknoCheckBox': 'entry_table_checkno',
        'accReconciliationDateCheckBox': 'entry_table_reconciliation_date',
        'accDebitCreditCheckBox': 'entry_table_debit_credit',
        'schDescriptionCheckBox': 'schedule_table_description',
        'schPayeeCheckBox': 'schedule_table_payee',
        'schChecknoCheckBox': 'schedule_table_checkno',
        'gldDescriptionCheckBox': 'gledger_table_description',
        'gldPayeeCheckBox': 'gledger_table_payee',
        'gldChecknoCheckBox': 'gledger_table_checkno',
        'gldReconciliationDateCheckBox': 'gledger_table_reconciliation_date',
    }
    
    def __init__(self, mainwindow):
        # The flags we pass are that so we don't get the "What's this" button in the title bar
        QDialog.__init__(self, mainwindow, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.mainwindow = mainwindow
        self.app = mainwindow.app
        self._setupUi()
        self.model = ViewOptionsModel(view=self, mainwindow=mainwindow.model)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def _setupUi(self):
        trui = lambda s: tr(s, 'ViewOptionsDialog')
        self.resize(385, 452)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.groupBox = QtGui.QGroupBox(self)
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.nwChangeCheckBox = QtGui.QCheckBox(self.groupBox)
        self.gridLayout.addWidget(self.nwChangeCheckBox, 0, 0, 1, 1)
        self.nwChangePercCheckBox = QtGui.QCheckBox(self.groupBox)
        self.gridLayout.addWidget(self.nwChangePercCheckBox, 0, 1, 1, 1)
        self.nwStartCheckBox = QtGui.QCheckBox(self.groupBox)
        self.gridLayout.addWidget(self.nwStartCheckBox, 0, 2, 1, 1)
        self.nwBudgetedCheckBox = QtGui.QCheckBox(self.groupBox)
        self.gridLayout.addWidget(self.nwBudgetedCheckBox, 0, 3, 1, 1)
        self.nwGraphCheckBox = QtGui.QCheckBox(self.groupBox)
        self.gridLayout.addWidget(self.nwGraphCheckBox, 1, 0, 1, 1)
        self.nwPieChartsCheckBox = QtGui.QCheckBox(self.groupBox)
        self.gridLayout.addWidget(self.nwPieChartsCheckBox, 1, 1, 1, 1)
        self.nwAccountNumberCheckBox = QtGui.QCheckBox(self.groupBox)
        self.gridLayout.addWidget(self.nwAccountNumberCheckBox, 0, 4, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self)
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.plChangeCheckBox = QtGui.QCheckBox(self.groupBox_2)
        self.gridLayout_2.addWidget(self.plChangeCheckBox, 0, 0, 1, 1)
        self.plChangePercCheckBox = QtGui.QCheckBox(self.groupBox_2)
        self.gridLayout_2.addWidget(self.plChangePercCheckBox, 0, 1, 1, 1)
        self.plLastCheckBox = QtGui.QCheckBox(self.groupBox_2)
        self.gridLayout_2.addWidget(self.plLastCheckBox, 0, 2, 1, 1)
        self.plBudgetedCheckBox = QtGui.QCheckBox(self.groupBox_2)
        self.gridLayout_2.addWidget(self.plBudgetedCheckBox, 0, 3, 1, 1)
        self.plGraphCheckBox = QtGui.QCheckBox(self.groupBox_2)
        self.gridLayout_2.addWidget(self.plGraphCheckBox, 1, 0, 1, 1)
        self.plPieChartsCheckBox = QtGui.QCheckBox(self.groupBox_2)
        self.gridLayout_2.addWidget(self.plPieChartsCheckBox, 1, 1, 1, 1)
        self.plAccountNumberCheckBox = QtGui.QCheckBox(self.groupBox_2)
        self.gridLayout_2.addWidget(self.plAccountNumberCheckBox, 0, 4, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(self)
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
        self.txnDescriptionCheckBox = QtGui.QCheckBox(self.groupBox_3)
        self.gridLayout_3.addWidget(self.txnDescriptionCheckBox, 0, 0, 1, 1)
        self.txnPayeeCheckBox = QtGui.QCheckBox(self.groupBox_3)
        self.gridLayout_3.addWidget(self.txnPayeeCheckBox, 0, 1, 1, 1)
        self.txnChecknoCheckBox = QtGui.QCheckBox(self.groupBox_3)
        self.gridLayout_3.addWidget(self.txnChecknoCheckBox, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 0, 3, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox_4 = QtGui.QGroupBox(self)
        self.gridLayout_4 = QtGui.QGridLayout(self.groupBox_4)
        self.accDescriptionCheckBox = QtGui.QCheckBox(self.groupBox_4)
        self.gridLayout_4.addWidget(self.accDescriptionCheckBox, 0, 0, 1, 1)
        self.accPayeeCheckBox = QtGui.QCheckBox(self.groupBox_4)
        self.gridLayout_4.addWidget(self.accPayeeCheckBox, 0, 1, 1, 1)
        self.accChecknoCheckBox = QtGui.QCheckBox(self.groupBox_4)
        self.gridLayout_4.addWidget(self.accChecknoCheckBox, 0, 2, 1, 1)
        self.accReconciliationDateCheckBox = QtGui.QCheckBox(self.groupBox_4)
        self.gridLayout_4.addWidget(self.accReconciliationDateCheckBox, 1, 0, 1, 1)
        self.accDebitCreditCheckBox = QtGui.QCheckBox(self.groupBox_4)
        self.gridLayout_4.addWidget(self.accDebitCreditCheckBox, 1, 1, 1, 1)
        self.accGraphCheckBox = QtGui.QCheckBox(self.groupBox_4)
        self.gridLayout_4.addWidget(self.accGraphCheckBox, 1, 2, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_4)
        self.groupBox_5 = QtGui.QGroupBox(self)
        self.gridLayout_5 = QtGui.QGridLayout(self.groupBox_5)
        self.schDescriptionCheckBox = QtGui.QCheckBox(self.groupBox_5)
        self.gridLayout_5.addWidget(self.schDescriptionCheckBox, 0, 0, 1, 1)
        self.schPayeeCheckBox = QtGui.QCheckBox(self.groupBox_5)
        self.gridLayout_5.addWidget(self.schPayeeCheckBox, 0, 1, 1, 1)
        self.schChecknoCheckBox = QtGui.QCheckBox(self.groupBox_5)
        self.gridLayout_5.addWidget(self.schChecknoCheckBox, 0, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_5.addItem(spacerItem1, 0, 3, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_5)
        self.groupBox_6 = QtGui.QGroupBox(self)
        self.gridLayout_6 = QtGui.QGridLayout(self.groupBox_6)
        self.gldDescriptionCheckBox = QtGui.QCheckBox(self.groupBox_6)
        self.gridLayout_6.addWidget(self.gldDescriptionCheckBox, 0, 0, 1, 1)
        self.gldPayeeCheckBox = QtGui.QCheckBox(self.groupBox_6)
        self.gridLayout_6.addWidget(self.gldPayeeCheckBox, 0, 1, 1, 1)
        self.gldChecknoCheckBox = QtGui.QCheckBox(self.groupBox_6)
        self.gridLayout_6.addWidget(self.gldChecknoCheckBox, 0, 2, 1, 1)
        self.gldReconciliationDateCheckBox = QtGui.QCheckBox(self.groupBox_6)
        self.gridLayout_6.addWidget(self.gldReconciliationDateCheckBox, 0, 3, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_6)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.verticalLayout.addWidget(self.buttonBox)
        self.setWindowTitle(trui("View Options"))
        self.groupBox.setTitle(trui("Net Worth"))
        self.nwChangeCheckBox.setText(trui("Change"))
        self.nwChangePercCheckBox.setText(trui("Change %"))
        self.nwStartCheckBox.setText(trui("Start"))
        self.nwBudgetedCheckBox.setText(trui("Budgeted"))
        self.nwGraphCheckBox.setText(trui("Graph"))
        self.nwPieChartsCheckBox.setText(trui("Pie Charts"))
        self.nwAccountNumberCheckBox.setText(trui("Account #"))
        self.groupBox_2.setTitle(trui("Profit & Loss"))
        self.plChangeCheckBox.setText(trui("Change"))
        self.plChangePercCheckBox.setText(trui("Change %"))
        self.plLastCheckBox.setText(trui("Last"))
        self.plBudgetedCheckBox.setText(trui("Budgeted"))
        self.plGraphCheckBox.setText(trui("Graph"))
        self.plPieChartsCheckBox.setText(trui("Pie Charts"))
        self.plAccountNumberCheckBox.setText(trui("Account #"))
        self.groupBox_3.setTitle(trui("Transactions"))
        self.txnDescriptionCheckBox.setText(trui("Description"))
        self.txnPayeeCheckBox.setText(trui("Payee"))
        self.txnChecknoCheckBox.setText(trui("Check #"))
        self.groupBox_4.setTitle(trui("Account"))
        self.accDescriptionCheckBox.setText(trui("Description"))
        self.accPayeeCheckBox.setText(trui("Payee"))
        self.accChecknoCheckBox.setText(trui("Check #"))
        self.accReconciliationDateCheckBox.setText(trui("Reconciliation Date"))
        self.accDebitCreditCheckBox.setText(trui("Debit/Credit"))
        self.accGraphCheckBox.setText(trui("Graph"))
        self.groupBox_5.setTitle(trui("Schedules"))
        self.schDescriptionCheckBox.setText(trui("Description"))
        self.schPayeeCheckBox.setText(trui("Payee"))
        self.schChecknoCheckBox.setText(trui("Check #"))
        self.groupBox_6.setTitle(trui("General Ledger"))
        self.gldDescriptionCheckBox.setText(trui("Description"))
        self.gldPayeeCheckBox.setText(trui("Payee"))
        self.gldChecknoCheckBox.setText(trui("Check #"))
        self.gldReconciliationDateCheckBox.setText(trui("Reconciliation Date"))
    
    def loadFromPrefs(self):
        for widgetName, prefName in self.WIDGET2PREF.items():
            widget = getattr(self, widgetName)
            widget.setChecked(getattr(self.app.prefs, prefName))
        for widgetName, attrName in self.WIDGET2COLUMN.items():
            widget = getattr(self, widgetName)
            widget.setChecked(getattr(self.model, attrName))
    
    def saveToPrefs(self):
        for widgetName, prefName in self.WIDGET2PREF.items():
            widget = getattr(self, widgetName)
            setattr(self.app.prefs, prefName, bool(widget.isChecked()))
        for widgetName, attrName in self.WIDGET2COLUMN.items():
            widget = getattr(self, widgetName)
            setattr(self.model, attrName, bool(widget.isChecked()))
    
