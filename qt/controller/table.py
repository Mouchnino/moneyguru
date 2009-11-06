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

class TableDelegate(QStyledItemDelegate):
    def __init__(self, dateColumnIndexes):
        QStyledItemDelegate.__init__(self)
        self._dateColumnIndexes = dateColumnIndexes
    
    def createEditor(self, parent, option, index):
        if index.column() in self._dateColumnIndexes:
            return DateEdit(parent)
        else:
            return QStyledItemDelegate.createEditor(self, parent, option, index)
    

class Table(QAbstractTableModel):
    HEADER = []
    ROWATTRS = []
    DATECOLUMNS = frozenset()
    
    def __init__(self, doc, view):
        QAbstractTableModel.__init__(self)
        self.doc = doc
        self.view = view
        self.model = self._getModel()
        self.view.setModel(self)
        dateColumnIndexes = frozenset(i for i, attr in enumerate(self.ROWATTRS) if attr in self.DATECOLUMNS)
        self.tableDelegate = TableDelegate(dateColumnIndexes)
        self.view.setItemDelegate(self.tableDelegate)
        
        self.connect(self.view.selectionModel(), SIGNAL('selectionChanged(QItemSelection,QItemSelection)'), self.selectionChanged)
    
    def _getModel(self):
        raise NotImplementedError()
    
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
    def columnCount(self, index):
        return len(self.HEADER)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        if role in (Qt.DisplayRole, Qt.EditRole):
            row = self.model[index.row()]
            rowattr = self.ROWATTRS[index.column()]
            return getattr(row, rowattr)
        return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        rowattr = self.ROWATTRS[index.column()]
        if self.model.can_edit_cell(rowattr, index.row()):
            flags |= Qt.ItemIsEditable
        return flags
    
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
        if role == Qt.EditRole:
            row = self.model[index.row()]
            rowattr = self.ROWATTRS[index.column()]
            value = unicode(value.toString())
            setattr(row, rowattr, value)
            return True
        return False
    
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
    
