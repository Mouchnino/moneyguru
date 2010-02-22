# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QMimeData, QByteArray
from PyQt4.QtGui import QFont

from core.gui.split_table import SplitTable as SplitTableModel
from .column import Column, ACCOUNT_EDIT
from .table import Table

MIME_INDEX = 'application/moneyguru.splitindex'

class SplitTable(Table):
    COLUMNS = [
        Column('account', 'Account', 100, editor=ACCOUNT_EDIT),
        Column('memo', 'Memo', 70),
        Column('debit', 'Debit', 90, alignment=Qt.AlignRight),
        Column('credit', 'Credit', 90, alignment=Qt.AlignRight),
    ]
    INVALID_INDEX_FLAGS = Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
    
    def __init__(self, transactionPanel, view):
        model = SplitTableModel(view=self, transaction_panel=transactionPanel.model)
        Table.__init__(self, model, view)
        self.setColumnsWidth(None)
    
    def _getData(self, row, column, role):
        if role == Qt.FontRole:
            font = QFont(self.view.font())
            font.setBold(row.is_main)
            return font
        return Table._getData(self, row, column, role)
    
    def _getFlags(self, row, column):
        flags = Table._getFlags(self, row, column)
        return flags | Qt.ItemIsDragEnabled
    
    #--- Drag & Drop
    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        if not mimeData.hasFormat(MIME_INDEX):
            return False
        # Since we only drop in between items, parentIndex must be invalid, and we use the row arg
        # to know where the drop took place.
        if parentIndex.isValid():
            return False
        index = int(unicode(mimeData.data(MIME_INDEX)))
        self.model.move_split(index, row)
        return True
    
    def mimeData(self, indexes):
        data = unicode(indexes[0].row())
        mimeData = QMimeData()
        mimeData.setData(MIME_INDEX, QByteArray(data))
        return mimeData
    
    def mimeTypes(self):
        return [MIME_INDEX]
    
    def supportedDropActions(self):
        return Qt.MoveAction
    
