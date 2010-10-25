# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from core.gui.view_options import ViewOptions as ViewOptionsModel

from ..ui.view_options_dialog_ui import Ui_ViewOptionsDialog

class ViewOptionsDialog(QDialog, Ui_ViewOptionsDialog):
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
        self.setupUi(self)
        self.model = ViewOptionsModel(view=self, mainwindow=mainwindow.model)
    
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
    
