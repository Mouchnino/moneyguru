# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-26
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, pyqtSignal
from PyQt4.QtGui import QAbstractItemView, QTableView, QTreeView, QItemSelectionModel

from hsutil.misc import first

# The big problem with tableview/treeview and multiple inheritance...
# Like with Cocoa, when you start to want to add common behavior to both your treeviews and
# tableviews, you have a problem because you need multiple inheritance (You first make a
# QAbstractItemView subclass in which you add your common behavior, then create 2 other classes
# which subclass (QTableView, YourCustomSubclass) and (QTreeView, YourCustomSubclass). However,
# multiple inheritance doesn't work so well: signals only work on the first subclass, and overrides
# you make of Qt's classes won't be called on the second part of the subclass (YourCustomSubclass).
# SO, what do we do? Well, the easiest solution I could think of is to create a mixin that just
# contains helper methods and put as much common code together as possible. But even with that,
# there's a lot of duplicated code.

class ItemViewMixIn(object): # Must be mixed with a QAbstractItemView subclass
    def _headerView(self):
        raise NotImplementedError()
    
    def _firstEditableIndex(self, originalIndex):
        # As a side effect, this method will change selection's currentIndex to the editableIndex
        model = self.model()
        h = self._headerView()
        editedRow = originalIndex.row()
        columnIndexes = (h.logicalIndex(i) for i in xrange(h.count()))
        create = lambda col: model.createIndex(editedRow, col, originalIndex.internalPointer())
        scannedIndexes = (create(i) for i in columnIndexes if not h.isSectionHidden(i))
        editableIndex = first(index for index in scannedIndexes if model.flags(index) & Qt.ItemIsEditable)
        if editableIndex is not None:
            # If we want the tabbing to be correct, we have to set the selection's currentIndex() as
            # well.
            self.selectionModel().setCurrentIndex(editableIndex, QItemSelectionModel.Current)
        return editableIndex
    
    def _shouldEditFromKeyPress(self, trigger):
        # Returns True if the trigger is a key press and that this type of trigger is allowed in
        # the edit triggers. Moreover, this only returns True if we're not already in edition state.
        if self.state() == QAbstractItemView.EditingState:
            return False
        if not (trigger & (QAbstractItemView.EditKeyPressed | QAbstractItemView.AnyKeyPressed)):
            return False
        if not (trigger & self.editTriggers()):
            return False
        return True
    

class TableView(QTableView, ItemViewMixIn):
    #--- QTableView override
    def edit(self, index, trigger, event):
        # When an edit is triggered by a key, rather than editing the selected cell (default
        # behavior), we want to look at the row and edit the first editable cell in it.
        if self._shouldEditFromKeyPress(trigger):
            editableIndex = self._firstEditableIndex(index)
            if editableIndex is not None:
                return QTableView.edit(self, editableIndex, trigger, event)
            else:
                return False
        else:
            return QTableView.edit(self, index, trigger, event)
    
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self.spacePressed.emit()
        elif key in (Qt.Key_Backspace, Qt.Key_Delete):
            self.deletePressed.emit()
        else:
            QTableView.keyPressEvent(self, event)
    
    #--- ItemViewMixIn overrides
    def _headerView(self):
        return self.horizontalHeader()
    
    #--- Public
    def editSelected(self):
        # By overriding edit(), we lose the PyQt ability to do method overloading, so the simple
        # edit(index) slot is not reachable anymore. We can use this one instead.
        selectedRows = self.selectionModel().selectedRows()
        if not selectedRows:
            return
        selectedIndex = selectedRows[0]
        QTableView.edit(self, selectedIndex)
    
    #--- Signals
    deletePressed = pyqtSignal()
    spacePressed = pyqtSignal()

class TreeView(QTreeView, ItemViewMixIn): # Same as in TableView, see comments there
    #--- QTreeView override
    def edit(self, index, trigger, event):
        if self._shouldEditFromKeyPress(trigger):
            editableIndex = self._firstEditableIndex(index)
            if editableIndex is not None:
                return QTreeView.edit(self, editableIndex, trigger, event)
            else:
                return False
        else:
            return QTreeView.edit(self, index, trigger, event)
    
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self.spacePressed.emit()
        elif key in (Qt.Key_Backspace, Qt.Key_Delete):
            self.deletePressed.emit()
        else:
            QTreeView.keyPressEvent(self, event)
    
    #--- ItemViewMixIn overrides
    def _headerView(self):
        return self.header()
    
    #--- Public
    def editSelected(self):
        selectedRows = self.selectionModel().selectedRows()
        if not selectedRows:
            return
        selectedIndex = selectedRows[0]
        QTreeView.edit(self, selectedIndex)
    
    #--- Signals
    deletePressed = pyqtSignal()
    spacePressed = pyqtSignal()
