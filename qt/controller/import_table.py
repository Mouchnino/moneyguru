# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QMimeData, QByteArray
from PyQt4.QtGui import QPixmap

from moneyguru.gui.import_table import ImportTable as ImportTableModel
from .column import Column
from .table import Table

MIME_INDEXES = 'application/moneyguru.rowindexes'

class ImportTable(Table):
    COLUMNS = [
        Column('will_import', '', 28),
        Column('date', 'Date', 120),
        Column('description', 'Description', 150),
        Column('amount', 'Amount', 120),
        Column('bound', '', 28),
        Column('date_import', 'Date', 120),
        Column('description_import', 'Description', 150),
        Column('payee_import', 'Payee', 150),
        Column('checkno_import', 'Check #', 100),
        Column('transfer_import', 'Transfer', 100),
        Column('amount_import', 'Amount', 120),
    ]
    HEADER = ['', 'Date', 'Description', 'Amount', '', 'Date', 'Description', 'Payee', 'Check #',
        'Transfer', 'Amount']
        
    def __init__(self, importWindow, view):
        model = ImportTableModel(view=self, import_window=importWindow.model)
        Table.__init__(self, model, view)
        self.view.clicked.connect(self.cellClicked)
    
    #--- Data methods override
    def _getData(self, row, rowattr, role):
        if rowattr == 'will_import':
            if role == Qt.CheckStateRole:
                return Qt.Checked if row.will_import else Qt.Unchecked
            else:
                return None
        elif rowattr == 'bound':
            if role == Qt.DecorationRole:
                return QPixmap(':/lock_12') if row.bound else None
            else:
                return None
        else:
            return Table._getData(self, row, rowattr, role)
    
    def _getFlags(self, row, rowattr):
        flags = Table._getFlags(self, row, rowattr)
        if rowattr == 'will_import':
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
            if not row.can_edit_will_import:
                flags &= ~Qt.ItemIsEnabled
        if not row.bound:
            flags |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return flags
    
    def _setData(self, row, rowattr, value, role):
        if rowattr == 'will_import':
            if role == Qt.CheckStateRole:
                row.will_import = value.toBool()
                return True
            else:
                return False
        else:
            return Table._setData(self, row, rowattr, value, role)
    
    #--- Drag & Drop
    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        if not mimeData.hasFormat(MIME_INDEXES):
            return False
        if not parentIndex.isValid():
            return False
        indexes = map(int, unicode(mimeData.data(MIME_INDEXES)).split(','))
        if len(indexes) != 1:
            return False
        index = indexes[0]
        if not self.model.can_bind(index, parentIndex.row()):
            return False
        self.model.bind(index, parentIndex.row())
        return True
    
    def mimeData(self, indexes):
        rows = set(unicode(index.row()) for index in indexes)
        data = ','.join(rows)
        mimeData = QMimeData()
        mimeData.setData(MIME_INDEXES, QByteArray(data))
        return mimeData
    
    def mimeTypes(self):
        return [MIME_INDEXES]
    
    def supportedDropActions(self):
        return Qt.MoveAction
    
    #--- Event Handling
    def cellClicked(self, index):
        rowattr = self.COLUMNS[index.column()].attrname
        if rowattr == 'bound':
            self.model.unbind(index.row())
    
