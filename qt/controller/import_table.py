# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPixmap

from moneyguru.gui.import_table import ImportTable as ImportTableModel
from .table import Table

class ImportTable(Table):
    HEADER = ['', 'Date', 'Description', 'Amount', '', 'Date', 'Description', 'Payee', 'Check #',
        'Transfer', 'Amount']
    ROWATTRS = ['will_import', 'date', 'description', 'amount', 'bound', 'date_import', 
        'description_import', 'payee_import', 'checkno_import', 'transfer_import', 'amount_import']
    
    def _getModel(self):
        return ImportTableModel(view=self, import_window=self.dataSource)
    
    #--- Public
    def cellClicked(self, index): # connect the view's clicked() signal to this
        rowattr = self.ROWATTRS[index.column()]
        if rowattr == 'bound':
            self.model.unbind(index.row())
    
    #--- Data methods override
    def data(self, index, role):
        if not index.isValid():
            return None
        rowattr = self.ROWATTRS[index.column()]
        if rowattr == 'will_import':
            if role == Qt.CheckStateRole:
                result = Table.data(self, index, Qt.DisplayRole)
                return Qt.Checked if result else Qt.Unchecked
            else:
                return None
        elif rowattr == 'bound':
            if role == Qt.DecorationRole:
                result = Table.data(self, index, Qt.DisplayRole)
                return QPixmap(':/lock_12') if result else None
            else:
                return None
        else:
            return Table.data(self, index, role)
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Table.flags(self, index)
        rowattr = self.ROWATTRS[index.column()]
        if rowattr == 'will_import':
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return flags
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        rowattr = self.ROWATTRS[index.column()]
        if rowattr == 'will_import':
            if role == Qt.CheckStateRole:
                row = self.model[index.row()]
                row.will_import = value.toBool()
                return True
            else:
                return False
        else:
            return Table.setData(self, index, value, role)
    
