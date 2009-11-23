# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-23
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QMimeData, QByteArray

from .table import Table

MIME_INDEXES = 'application/moneyguru.rowindexes'

# A table with transactions supports drag & drop. You can drag items, but you can only drop them
# *in between* other items.

class TableWithTransactions(Table):
    INVALID_INDEX_FLAGS = Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
    
    def _getFlags(self, row, rowattr):
        flags = Table._getFlags(self, row, rowattr)
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
    