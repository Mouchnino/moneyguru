# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import SIGNAL, Qt, QAbstractTableModel, QModelIndex
from PyQt4.QtGui import QItemSelectionModel, QItemSelection, QStyledItemDelegate

from support.date_edit import DateEdit
from support.completable_edit import CompletableEdit

DATE_EDIT = 'date_edit'
DESCRIPTION_EDIT = 'description_edit'
PAYEE_EDIT = 'payee_edit'
ACCOUNT_EDIT = 'account_edit'

class TableDelegate(QStyledItemDelegate):
    def __init__(self, model, specialColumns):
        QStyledItemDelegate.__init__(self)
        self._model = model
        self._specialColumns = specialColumns
    
    def createEditor(self, parent, option, index):
        editType = self._specialColumns.get(index.column())
        if editType is None:
            return QStyledItemDelegate.createEditor(self, parent, option, index)
        elif editType == DATE_EDIT:
            return DateEdit(parent)
        elif editType in (DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT):
            result = CompletableEdit(parent)
            result.model = self._model
            result.attrname = {DESCRIPTION_EDIT: 'description', PAYEE_EDIT: 'payee', ACCOUNT_EDIT: 'account'}[editType]
            return result
    

class Table(QAbstractTableModel):
    HEADER = []
    ROWATTRS = []
    SPECIAL_COLUMNS = {}
    
    def __init__(self, model, view):
        QAbstractTableModel.__init__(self)
        self.model = model
        self.view = view
        self.view.setModel(self)
        specialColumns = dict((self.ROWATTRS.index(colName), editType) for colName, editType in self.SPECIAL_COLUMNS.items())
        self.tableDelegate = TableDelegate(self.model, specialColumns)
        self.view.setItemDelegate(self.tableDelegate)
        
        self.connect(self.view.selectionModel(), SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged)
    
    def _updateModelSelection(self):
        # Takes the selection on the view's side and update the model with it.
        # an _updateViewSelection() call will normally result in an _updateModelSelection() call.
        # to avoid infinite loops, we check that the selection will actually change before calling
        # model.select()
        newIndexes = [modelIndex.row() for modelIndex in self.view.selectionModel().selectedRows()]
        if newIndexes != self.model.selected_indexes:
            self.model.select(newIndexes)
    
    def _updateViewSelection(self):
        # Takes the selection on the model's side and update the view with it.
        newSelection = QItemSelection()
        columnCount = self.columnCount(QModelIndex())
        for index in self.model.selected_indexes:
            newSelection.select(self.createIndex(index, 0), self.createIndex(index, columnCount-1))
        self.view.selectionModel().select(newSelection, QItemSelectionModel.ClearAndSelect)
        if len(newSelection.indexes()):
            self.view.selectionModel().setCurrentIndex(newSelection.indexes()[0], QItemSelectionModel.Current)
    
    #--- Data Model methods
    # Virtual
    def _getData(self, row, rowattr, role):
        if role in (Qt.DisplayRole, Qt.EditRole):
            return getattr(row, rowattr)
        return None
    
    # Virtual
    def _getFlags(self, row, rowattr):
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if row.can_edit_cell(rowattr):
            flags |= Qt.ItemIsEditable
        return flags
    
    # Virtual
    def _setData(self, row, rowattr, value, role):
        if role == Qt.EditRole:
            value = unicode(value.toString())
            setattr(row, rowattr, value)
            return True
        return False
    
    def columnCount(self, index):
        return len(self.HEADER)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        row = self.model[index.row()]
        rowattr = self.ROWATTRS[index.column()]
        return self._getData(row, rowattr, role)
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        row = self.model[index.row()]
        rowattr = self.ROWATTRS[index.column()]
        return self._getFlags(row, rowattr)
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self.HEADER):
            return self.HEADER[section]
        return None
    
    def revert(self):
        self.model.cancel_edits()
    
    def rowCount(self, index):
        if index.isValid():
            return 0
        return len(self.model)
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        row = self.model[index.row()]
        rowattr = self.ROWATTRS[index.column()]
        return self._setData(row, rowattr, value, role)
    
    def submit(self):
        self.model.save_edits()
        return True
    
    #--- Events
    def selectionChanged(self, selected, deselected):
        self._updateModelSelection()
    
    #--- model --> view
    def refresh(self):
        self.reset()
        self._updateViewSelection()
    
    def show_selected_row(self):
        pass
    
    def start_editing(self):
        selectedIndex = self.view.selectionModel().selectedRows()[0]
        self.view.edit(selectedIndex)
    
    def stop_editing(self):
        pass
    
