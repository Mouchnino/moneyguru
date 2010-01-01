# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-23
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QMimeData, QByteArray
from PyQt4.QtGui import QPixmap

from .table import Table

MIME_INDEXES = 'application/moneyguru.rowindexes'

# A table with transactions supports drag & drop. You can drag items, but you can only drop them
# *in between* other items.

class TableWithTransactions(Table):
    INVALID_INDEX_FLAGS = Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
    
    def _getStatusData(self, row, role):
        if role == Qt.DecorationRole:
            iconName = None
            if row is self.model.edited and row.is_date_in_future():
                iconName = 'forward_16'
            elif row is self.model.edited and row.is_date_in_past():
                iconName = 'backward_16'
            elif row.reconciled:
                iconName = 'check_16'
            elif row.is_budget:
                iconName = 'budget_16'
            elif row.recurrent:
                iconName = 'recurrent_16'
            if iconName:
                return QPixmap(':/' + iconName)
            else:
                return None
        else:
            return None
    
    def _getData(self, row, column, role):
        if column.attrname == 'status':
            return self._getStatusData(row, role)
        else:
            return Table._getData(self, row, column, role)
    
    def _getFlags(self, row, column):
        flags = Table._getFlags(self, row, column)
        return flags | Qt.ItemIsDragEnabled
    
    #--- Drag & Drop
    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        if not mimeData.hasFormat(MIME_INDEXES):
            return False
        # Since we only drop in between items, parentIndex must be invalid, and we use the row arg
        # to know where the drop took place.
        if parentIndex.isValid():
            return False
        indexes = map(int, unicode(mimeData.data(MIME_INDEXES)).split(','))
        if not self.model.can_move(indexes, row):
            return False
        self.model.move(indexes, row)
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
    