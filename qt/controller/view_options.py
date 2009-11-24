# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-24
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QDialog

from ui.view_options_dialog_ui import Ui_ViewOptionsDialog

class ViewOptionsDialog(QDialog, Ui_ViewOptionsDialog):
    WIDGET2PREF = {
        'nwChangeCheckBox': 'networthSheetChangeColumnVisible',
        'nwChangePercCheckBox': 'networthSheetChangePercColumnVisible',
        'nwStartCheckBox': 'networthSheetStartColumnVisible',
        'nwBudgetedCheckBox': 'networthSheetBudgetedColumnVisible',
        'nwGraphCheckBox': 'networthSheetGraphVisible',
        'nwPieChartsCheckBox': 'networthSheetPieChartsVisible',
        'plChangeCheckBox': 'profitSheetChangeColumnVisible',
        'plChangePercCheckBox': 'profitSheetChangePercColumnVisible',
        'plLastCheckBox': 'profitSheetLastColumnVisible',
        'plBudgetedCheckBox': 'profitSheetBudgetedColumnVisible',
        'plGraphCheckBox': 'profitSheetGraphVisible',
        'plPieChartsCheckBox': 'profitSheetPieChartsVisible',
        'txnDescriptionCheckBox': 'transactionTableDescriptionColumnVisible',
        'txnPayeeCheckBox': 'transactionTablePayeeColumnVisible',
        'txnChecknoCheckBox': 'transactionTableChecknoColumnVisible',
        'accDescriptionCheckBox': 'entryTableDescriptionColumnVisible',
        'accPayeeCheckBox': 'entryTablePayeeColumnVisible',
        'accChecknoCheckBox': 'entryTableChecknoColumnVisible',
        'accGraphCheckBox': 'entryTableGraphVisible',
        'schDescriptionCheckBox': 'scheduleTableDescriptionColumnVisible',
        'schPayeeCheckBox': 'scheduleTablePayeeColumnVisible',
        'schChecknoCheckBox': 'scheduleTableChecknoColumnVisible',
    }
    
    def __init__(self, app):
        QDialog.__init__(self, None)
        self.app = app
        self._setupUi()
    
    def _setupUi(self):
        self.setupUi(self)
    
    def loadFromPrefs(self):
        for widgetName, prefName in self.WIDGET2PREF.items():
            widget = getattr(self, widgetName)
            widget.setChecked(getattr(self.app.prefs, prefName))
    
    def saveToPrefs(self):
        for widgetName, prefName in self.WIDGET2PREF.items():
            widget = getattr(self, widgetName)
            setattr(self.app.prefs, prefName, bool(widget.isChecked()))
    
