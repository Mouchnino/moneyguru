# Created By: Virgil Dupras
# Created On: 2010-10-25
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QHeaderView

from qtlib.column import Column
from .table import Table

class ExportAccountTable(Table):
    COLUMNS = [
        Column('name', 80),
        Column('export', 60),
    ]
        
    def __init__(self, model, view):
        Table.__init__(self, model, view)
        view.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        view.horizontalHeader().setResizeMode(1, QHeaderView.Fixed)
    
    #--- Data methods override
    def _getData(self, row, column, role):
        if column.name == 'export':
            if role == Qt.CheckStateRole:
                return Qt.Checked if row.export else Qt.Unchecked
            else:
                return None
        else:
            return Table._getData(self, row, column, role)
    
    def _getFlags(self, row, column):
        flags = Table._getFlags(self, row, column)
        if column.name == 'export':
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return flags
    
    def _setData(self, row, column, value, role):
        if column.name == 'export':
            if role == Qt.CheckStateRole:
                row.export = value
                return True
            else:
                return False
        else:
            return Table._setData(self, row, column, value, role)
    
