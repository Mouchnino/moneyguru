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

from .column import ColumnBearer, DATE_EDIT, DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT

from support.date_edit import DateEdit
from support.completable_edit import DescriptionEdit, PayeeEdit, AccountEdit

class TableDelegate(QStyledItemDelegate):
    def __init__(self, model, columns):
        QStyledItemDelegate.__init__(self)
        self._model = model
        self._columns = columns
    
    def createEditor(self, parent, option, index):
        column = self._columns[index.column()]
        editType = column.editor
        if editType is None:
            return QStyledItemDelegate.createEditor(self, parent, option, index)
        elif editType == DATE_EDIT:
            return DateEdit(parent)
        elif editType in (DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT):
            editClass = {
                DESCRIPTION_EDIT: DescriptionEdit,
                PAYEE_EDIT: PayeeEdit,
                ACCOUNT_EDIT: AccountEdit
            }[editType]
            result = editClass(parent)
            result.model = self._model
            return result
    

class Table(QAbstractTableModel, ColumnBearer):
    # Flags you want when index.isValid() is False. In those cases, _getFlags() is never called.
    INVALID_INDEX_FLAGS = Qt.ItemIsEnabled
    
    def __init__(self, model, view):
        QAbstractTableModel.__init__(self)
        ColumnBearer.__init__(self, view.horizontalHeader())
        self.model = model
        self.view = view
        self.view.setModel(self)
        self.tableDelegate = TableDelegate(self.model, self.COLUMNS)
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
        return len(self.COLUMNS)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        row = self.model[index.row()]
        rowattr = self.COLUMNS[index.column()].attrname
        return self._getData(row, rowattr, role)
    
    def flags(self, index):
        if not index.isValid():
            return self.INVALID_INDEX_FLAGS
        row = self.model[index.row()]
        rowattr = self.COLUMNS[index.column()].attrname
        return self._getFlags(row, rowattr)
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self.COLUMNS):
            return self.COLUMNS[section].title
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
        rowattr = self.COLUMNS[index.column()].attrname
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
    
