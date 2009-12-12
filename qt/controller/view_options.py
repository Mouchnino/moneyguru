# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-24
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from ui.view_options_dialog_ui import Ui_ViewOptionsDialog

class ViewOptionsDialog(QDialog, Ui_ViewOptionsDialog):
    WIDGET2PREF = {
        'nwGraphCheckBox': 'networthGraphVisible',
        'nwPieChartsCheckBox': 'networthPieChartsVisible',
        'plGraphCheckBox': 'profitGraphVisible',
        'plPieChartsCheckBox': 'profitPieChartsVisible',
        'accGraphCheckBox': 'entryGraphVisible',
    }
    # widgetName: (prefName, columnName)
    # The preference refers to *hidden* columns!
    WIDGET2COLUMN = {
        'nwChangeCheckBox': ('networthHiddenColumns', 'delta'),
        'nwChangePercCheckBox': ('networthHiddenColumns', 'delta_perc'),
        'nwStartCheckBox': ('networthHiddenColumns', 'start'),
        'nwBudgetedCheckBox': ('networthHiddenColumns', 'budgeted'),
        'plChangeCheckBox': ('profitHiddenColumns', 'delta'),
        'plChangePercCheckBox': ('profitHiddenColumns', 'delta_perc'),
        'plLastCheckBox': ('profitHiddenColumns', 'last_cash_flow'),
        'plBudgetedCheckBox': ('profitHiddenColumns', 'budgeted'),
        'txnDescriptionCheckBox': ('transactionHiddenColumns', 'description'),
        'txnPayeeCheckBox': ('transactionHiddenColumns', 'payee'),
        'txnChecknoCheckBox': ('transactionHiddenColumns', 'checkno'),
        'accDescriptionCheckBox': ('entryHiddenColumns', 'description'),
        'accPayeeCheckBox': ('entryHiddenColumns', 'payee'),
        'accChecknoCheckBox': ('entryHiddenColumns', 'checkno'),
        'schDescriptionCheckBox': ('scheduleHiddenColumns', 'description'),
        'schPayeeCheckBox': ('scheduleHiddenColumns', 'payee'),
        'schChecknoCheckBox': ('scheduleHiddenColumns', 'checkno'),
    }
    
    def __init__(self, parent, app):
        # The flags we pass are that so we don't get the "What's this" button in the title bar
        QDialog.__init__(self, parent, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.app = app
        self._setupUi()
    
    def _setupUi(self):
        self.setupUi(self)
    
    def loadFromPrefs(self):
        for widgetName, prefName in self.WIDGET2PREF.items():
            widget = getattr(self, widgetName)
            widget.setChecked(getattr(self.app.prefs, prefName))
        for widgetName, (prefName, columnName) in self.WIDGET2COLUMN.items():
            widget = getattr(self, widgetName)
            hiddenColumns = getattr(self.app.prefs, prefName)
            # We use "not in" because the preference stores hidden columns
            widget.setChecked(columnName not in hiddenColumns)
    
    def saveToPrefs(self):
        for widgetName, prefName in self.WIDGET2PREF.items():
            widget = getattr(self, widgetName)
            setattr(self.app.prefs, prefName, bool(widget.isChecked()))
        for widgetName, (prefName, columnName) in self.WIDGET2COLUMN.items():
            widget = getattr(self, widgetName)
            hiddenColumns = getattr(self.app.prefs, prefName)
            if widget.isChecked():
                hiddenColumns.discard(columnName)
            else:
                hiddenColumns.add(columnName)
    
