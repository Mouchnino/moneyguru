# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-26
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt4.QtGui import QAbstractItemView, QTableView, QTreeView, QAbstractItemDelegate

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
    
    def _firstEditableIndex(self, originalIndex, columnIndexes=None):
        """Returns the first editable index in `originalIndex`'s row or None.
        
        If `columnIndexes` is not None, the scan for an editable index will be limited to these
        columns.
        """
        model = self.model()
        h = self._headerView()
        editedRow = originalIndex.row()
        if columnIndexes is None:
            columnIndexes = (h.logicalIndex(i) for i in xrange(h.count()))
        create = lambda col: model.createIndex(editedRow, col, originalIndex.internalPointer())
        scannedIndexes = (create(i) for i in columnIndexes if not h.isSectionHidden(i))
        editableIndex = first(index for index in scannedIndexes if model.flags(index) & Qt.ItemIsEditable)
        return editableIndex
    
    def _previousEditableIndex(self, originalIndex):
        """Returns the first editable index at the left of `originalIndex` or None.
        """
        h = self._headerView()
        myCol = originalIndex.column()
        columnIndexes = [h.logicalIndex(i) for i in xrange(h.count())]
        # keep only columns before myCol
        columnIndexes = columnIndexes[:columnIndexes.index(myCol)]
        # We want the previous item, the columns have to be in reverse order
        columnIndexes = reversed(columnIndexes)
        return self._firstEditableIndex(originalIndex, columnIndexes)
    
    def _nextEditableIndex(self, originalIndex):
        """Returns the first editable index at the right of `originalIndex` or None.
        """
        h = self._headerView()
        myCol = originalIndex.column()
        columnIndexes = [h.logicalIndex(i) for i in xrange(h.count())]
        # keep only columns after myCol
        columnIndexes = columnIndexes[columnIndexes.index(myCol)+1:]
        return self._firstEditableIndex(originalIndex, columnIndexes)
    
    def _handleCloseEditor(self, editor, hint, superMethod):
        # The problem we're trying to solve here is the edit-and-go-away problem. When ending the
        # editing with escape or return, there's no problem, the model's submit()/revert() is
        # correctly called. However, when ending editing by clicking away, submit() is never called.
        # Fortunately, closeEditor is called, and AFAIK, it's the only case where it's called with
        # NoHint (0). So, in these cases, we want to call model.submit()
        if hint == QAbstractItemDelegate.NoHint:
            superMethod(self, editor, QAbstractItemDelegate.SubmitModelCache)
        
        # And here, what we're trying to solve is the problem with editing next/previous lines.
        # If there are no more editable indexes, stop edition right there. Additionally, we are
        # making tabbing step over non-editable cells
        elif hint in (QAbstractItemDelegate.EditNextItem, QAbstractItemDelegate.EditPreviousItem):
            if hint == QAbstractItemDelegate.EditNextItem:
                editableIndex = self._nextEditableIndex(self.currentIndex())
            else:
                editableIndex = self._previousEditableIndex(self.currentIndex())
            if editableIndex is None:
                superMethod(self, editor, QAbstractItemDelegate.SubmitModelCache)
            else:
                superMethod(self, editor, 0)
                self.setCurrentIndex(editableIndex)
                self.edit(editableIndex, QAbstractItemView.AllEditTriggers, None)
        else:
            superMethod(self, editor, hint)
    
    def _handleKeyPressEvent(self, event, superMethod):
        key = event.key()
        if key == Qt.Key_Space:
            self.spacePressed.emit()
        elif key in (Qt.Key_Backspace, Qt.Key_Delete):
            self.deletePressed.emit()
        elif (key == Qt.Key_Return) and (self.state() != QAbstractItemView.EditingState):
            # I have no freaking idea why, but under Windows, somehow, the Return key doesn't
            # trigger edit() calls (even in Qt demos...). Gotta do it manually.
            self.editSelected()
        else:
            superMethod(self, event)
    
    def _handleMousePressEvent(self, event, superMethod):
        pos = event.pos()
        index = self.indexAt(pos)
        selected = index in self.selectedIndexes()
        superMethod(self, event)
        if not index.isValid():
            return
        rect = self.visualRect(index)
        relativePos = QPoint(pos.x()-rect.x(), pos.y()-rect.y())
        delegate = self.itemDelegate(index)
        # handleClick(index, relativePos, itemRect, selected)
        if hasattr(delegate, 'handleClick'):
            rect = QRect(0, 0, rect.width(), rect.height())
            delegate.handleClick(index, relativePos, rect, selected)
    
    #--- Public
    def editSelected(self):
        selectedRows = self.selectionModel().selectedRows()
        if not selectedRows:
            return
        selectedIndex = selectedRows[0]
        editableIndex = self._firstEditableIndex(selectedIndex)
        if editableIndex is not None:
            self.setCurrentIndex(editableIndex)
            self.edit(editableIndex)
    

class TableView(QTableView, ItemViewMixIn):
    #--- QTableView override
    def closeEditor(self, editor, hint):
        self._handleCloseEditor(editor, hint, QTableView.closeEditor)
    
    def keyPressEvent(self, event):
        self._handleKeyPressEvent(event, QTableView.keyPressEvent)
    
    def mousePressEvent(self, event):
        self._handleMousePressEvent(event, QTableView.mousePressEvent)
    
    #--- ItemViewMixIn overrides
    def _headerView(self):
        return self.horizontalHeader()
    
    #--- Signals
    deletePressed = pyqtSignal()
    spacePressed = pyqtSignal()

class TreeView(QTreeView, ItemViewMixIn): # Same as in TableView, see comments there
    #--- QTreeView override
    def closeEditor(self, editor, hint):
        self._handleCloseEditor(editor, hint, QTreeView.closeEditor)
    
    def keyPressEvent(self, event):
        self._handleKeyPressEvent(event, QTreeView.keyPressEvent)
    
    def mousePressEvent(self, event):
        self._handleMousePressEvent(event, QTreeView.mousePressEvent)
    
    #--- ItemViewMixIn overrides
    def _headerView(self):
        return self.header()
    
    #--- Signals
    deletePressed = pyqtSignal()
    spacePressed = pyqtSignal()
