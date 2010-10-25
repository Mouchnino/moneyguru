# Created By: Virgil Dupras
# Created On: 2010-10-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QHeaderView

from qtlib.column import Column
from core.gui.export_account_table import ExportAccountTable as ExportAccountTableModel
from core.trans import tr
from .table import Table

class ExportAccountTable(Table):
    COLUMNS = [
        Column('name', tr('Account'), 80),
        Column('export', tr('Export'), 60),
    ]
        
    def __init__(self, exportPanel, view):
        model = ExportAccountTableModel(view=self, export_panel=exportPanel.model)
        Table.__init__(self, model, view)
        view.horizontalHeader().setResizeMode(0, QHeaderView.Stretch)
        view.horizontalHeader().setResizeMode(1, QHeaderView.Fixed)
        self.setColumnsWidth(None)
    
    #--- Data methods override
    def _getData(self, row, column, role):
        if column.attrname == 'export':
            if role == Qt.CheckStateRole:
                return Qt.Checked if row.export else Qt.Unchecked
            else:
                return None
        else:
            return Table._getData(self, row, column, role)
    
    def _getFlags(self, row, column):
        flags = Table._getFlags(self, row, column)
        if column.attrname == 'export':
            flags |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return flags
    
    def _setData(self, row, column, value, role):
        if column.attrname == 'export':
            if role == Qt.CheckStateRole:
                row.export = value.toBool()
                return True
            else:
                return False
        else:
            return Table._setData(self, row, column, value, role)
    
