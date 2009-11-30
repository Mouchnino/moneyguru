# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-29
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QAbstractTableModel
from PyQt4.QtGui import QWidget, QMenu, QCursor, QPixmap

from moneyguru.gui.csv_options import CSVOptions as CSVOptionsModel, FIELD_NAMES, FIELD_ORDER
from ui.csv_options_ui import Ui_CSVOptionsWindow

class CSVOptionsWindow(QWidget, Ui_CSVOptionsWindow):
    def __init__(self, doc):
        QWidget.__init__(self, None)
        self.setupUi(self)
        self.doc = doc
        self.model = CSVOptionsModel(view=self, document=doc.model)
        self.tableModel = CSVOptionsTableModel(self.model, self.tableView)
        
        self.cancelButton.clicked.connect(self.hide)
    
    #--- model --> view
    # show() and hide() are called from the model, but are already covered by QWidget
    def refresh_columns(self):
        self.tableModel.reset()
    
    def refresh_columns_name(self):
        self.tableModel.refreshColumnsName()
    
    def refresh_layout_menu(self):
        self.layoutComboBox.clear()
        self.layoutComboBox.addItems(self.model.layout_names)
        self.layoutComboBox.insertSeparator(self.layoutComboBox.count())
        self.layoutComboBox.addItem('New Layout...')
        self.layoutComboBox.addItem('Rename Selected Layout...')
        self.layoutComboBox.addItem('Delete Selected Layout')
    
    def refresh_lines(self):
        self.tableModel.reset()
    
    def refresh_targets(self):
        self.targetComboBox.clear()
        self.targetComboBox.addItems(self.model.target_account_names)
    

class CSVOptionsTableModel(QAbstractTableModel):
    def __init__(self, model, view):
        QAbstractTableModel.__init__(self)
        self.model = model
        self.view = view
        self.view.setModel(self)
        self._lastClickedColumn = 0
        self.columnMenu = QMenu()
        for index, fieldId in enumerate(FIELD_ORDER):
            fieldName = FIELD_NAMES[fieldId]
            action = self.columnMenu.addAction(fieldName)
            action.setData(index)
            action.triggered.connect(self.columnMenuItemClicked)
        self.view.horizontalHeader().sectionClicked.connect(self.tableSectionClicked)
    
    #--- QAbstractTableModel overrides
    def columnCount(self, index):
        return len(self.model.columns)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            line = self.model.lines[index.row()]
            return line[index.column()]
        else:
            return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def headerData(self, section, orientation, role):
        if orientation != Qt.Horizontal:
            return None
        if section >= len(self.model.columns):
            return None
        if role == Qt.DisplayRole:
            return self.model.get_column_name(section)
        elif role == Qt.DecorationRole:
            return QPixmap(':/popup_arrows')
        else:
            return None
    
    def rowCount(self, index):
        if index.isValid():
            return 0
        return len(self.model.lines)
    
    #--- Public
    def refreshColumnsName(self):
        self.headerDataChanged.emit(Qt.Horizontal, 0, len(self.model.columns)-1)
    
    #--- Event Handling
    def columnMenuItemClicked(self):
        action = self.sender()
        index, _ = action.data().toInt()
        fieldId = FIELD_ORDER[index]
        self.model.set_column_field(self._lastClickedColumn, fieldId)
    
    def tableSectionClicked(self, index):
        self._lastClickedColumn = index
        self.columnMenu.exec_(QCursor.pos())
