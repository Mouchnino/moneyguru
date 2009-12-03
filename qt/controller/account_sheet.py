# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from PyQt4.QtCore import Qt, QModelIndex, QMimeData, QByteArray, QRect
from PyQt4.QtGui import QStyledItemDelegate, QPixmap, QStyle, QItemSelection, QItemSelectionModel

from qtlib.tree_model import TreeNode, TreeModel

from .column import ColumnBearer

MIME_PATH = 'application/moneyguru.nodepath'

class Node(TreeNode):
    def __init__(self, model, parent, ref, row):
        TreeNode.__init__(self, model, parent, row)
        self.ref = ref
    
    def _createNode(self, ref, row):
        return Node(self.model, self, ref, row)
    
    def _getChildren(self):
        return self.ref[:]
    

class AccountSheetDelegate(QStyledItemDelegate):
    BOLD_ATTRS = set()
    AMOUNT_ATTRS = set()
    
    def __init__(self, model, view, columns):
        QStyledItemDelegate.__init__(self)
        self._model = model
        self._view = view
        self._columns = columns
    
    def handleClick(self, index, pos, itemRect):
        column = self._columns[index.column()]
        if column.attrname == 'name':
            node = index.internalPointer()
            currentRight = itemRect.right()
            if node.ref.is_account:
                if pos.x() >= currentRight-12:
                    self._model.show_selected_account()
                currentRight -= 12
            if not (node.ref.is_total or node.ref.is_blank):
                if (currentRight-16) <= pos.x() < currentRight:
                    self._model.toggle_excluded()
    
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        isBold = False
        isItalic = False
        column = self._columns[index.column()]
        if column.attrname == 'name':
            node = index.internalPointer()
            ref = node.ref
            if ref.is_group or ref.is_total or ref.is_type:
                isBold = True
            if ref.is_total:
                isItalic = True
                option.rect.setLeft(option.rect.left()-self._view.indentation())
            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())
            if ref.is_account:
                arrowImageName = ':/right_arrow_white_12' if option.state & QStyle.State_Selected else ':/right_arrow_gray_12'
                pixmap = QPixmap(arrowImageName)
                arrowRect = QRect(0, 0, pixmap.width(), pixmap.height())
                arrowRect.moveCenter(option.rect.center()) # centered vertically
                arrowRect.moveRight(option.rect.right())
                option.rect.setRight(arrowRect.left()-1)
                painter.drawPixmap(arrowRect, pixmap)
            if option.state & QStyle.State_Selected and not (ref.is_total or ref.is_blank):
                excludeImageName = ':/account_in_16' if ref.is_excluded else ':/account_out_16'
                pixmap = QPixmap(excludeImageName)
                excludeRect = QRect(0, 0, pixmap.width(), pixmap.height())
                excludeRect.moveCenter(option.rect.center()) # centered vertically
                excludeRect.moveRight(option.rect.right())
                option.rect.setRight(excludeRect.left()-1)
                painter.drawPixmap(excludeRect, pixmap)
        elif column.attrname in self.BOLD_ATTRS:
            isBold = True
        option.font.setBold(isBold)
        option.font.setItalic(isItalic)
        QStyledItemDelegate.paint(self, painter, option, index)
        if column.attrname in self.AMOUNT_ATTRS:
            node = index.internalPointer()
            ref = node.ref
            if ref.is_total or ref.is_subtotal:
                p1 = option.rect.bottomLeft()
                p2 = option.rect.bottomRight()
                p1.setX(p1.x()+1)
                p2.setX(p2.x()-1)
                painter.drawLine(p1, p2)
                if ref.is_total:
                    p1.setY(p1.y()-2)
                    p2.setY(p2.y()-2)
                    painter.drawLine(p1, p2)
    

class AccountSheet(TreeModel, ColumnBearer):
    EXPANDED_NODE_PREF_NAME = None # must set in subclass
    DELEGATE_CLASS = AccountSheetDelegate
    
    def __init__(self, doc, model, view):
        TreeModel.__init__(self)
        ColumnBearer.__init__(self, view.header())
        self.doc = doc
        self.app = doc.app
        self.view = view
        self._wasRestored = False
        self.model = model
        self.view.setModel(self)
        self.accountSheetDelegate = self.DELEGATE_CLASS(self.model, self.view, self.COLUMNS)
        self.view.setItemDelegate(self.accountSheetDelegate)
        self._restoreNodeExpansionState()
        
        self.view.selectionModel().currentRowChanged.connect(self.currentRowChanged)
        self.view.collapsed.connect(self.nodeCollapsed)
        self.view.expanded.connect(self.nodeExpanded)
        self.view.deletePressed.connect(self.model.delete)
        self.view.spacePressed.connect(self.model.toggle_excluded)
        self.app.willSavePrefs.connect(self._saveNodeExpansionState)
    
    #--- TreeModel overrides
    def _createNode(self, ref, row):
        return Node(self, None, ref, row)
    
    def _getChildren(self):
        return self.model[:]
    
    #--- Private
    def _restoreNodeExpansionState(self):
        paths = getattr(self.app.prefs, self.EXPANDED_NODE_PREF_NAME)
        for path in paths:
            index = self.findIndex(path)
            self.view.expand(index)
    
    def _saveNodeExpansionState(self):
        paths = []
        index = self.index(0, 0, QModelIndex())
        while index.isValid():
            if self.view.isExpanded(index):
                paths.append(self.pathForIndex(index))
            index = self.view.indexBelow(index)
        setattr(self.app.prefs, self.EXPANDED_NODE_PREF_NAME, paths)
    
    def _updateViewSelection(self):
        # Takes the selection on the model's side and update the view with it.
        selectedPath = self.model.selected_path
        if selectedPath is None:
            return
        modelIndex = self.findIndex(selectedPath)
        self.view.setCurrentIndex(modelIndex)
    
    #--- Data Model methods
    def columnCount(self, parent):
        return len(self.COLUMNS)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        if role in (Qt.DisplayRole, Qt.EditRole):
            node = index.internalPointer()
            rowattr = self.COLUMNS[index.column()].attrname
            return getattr(node.ref, rowattr)
        return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        node = index.internalPointer()
        rowattr = self.COLUMNS[index.column()].attrname
        if getattr(node.ref, 'can_edit_' + rowattr, False):
            flags |= Qt.ItemIsEditable
        if node.ref.is_group or node.ref.is_type:
            flags |= Qt.ItemIsDropEnabled
        if node.ref.is_account:
            flags |= Qt.ItemIsDragEnabled
        return flags
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self.COLUMNS):
            return self.COLUMNS[section].title
        return None
    
    def revert(self):
        self.model.cancel_edits()
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            node = index.internalPointer()
            rowattr = self.COLUMNS[index.column()].attrname
            value = unicode(value.toString())
            setattr(node.ref, rowattr, value)
            return True
        return False
    
    def submit(self):
        self.model.save_edits()
        return True
    
    #--- Drag & Drop
    def dropMimeData(self, mimeData, action, row, column, parentIndex):
        if not mimeData.hasFormat(MIME_PATH):
            return False
        if not parentIndex.isValid():
            return False
        path = map(int, unicode(mimeData.data(MIME_PATH)).split(','))
        destPath = self.pathForIndex(parentIndex)
        if not self.model.can_move(path, destPath):
            return False
        self.model.move(path, destPath)
        return True
    
    def mimeData(self, indexes):
        index = indexes[0]
        path = self.pathForIndex(index)
        data = ','.join(map(unicode, path))
        mimeData = QMimeData()
        mimeData.setData(MIME_PATH, QByteArray(data))
        return mimeData
    
    def mimeTypes(self):
        return [MIME_PATH]
    
    def supportedDropActions(self):
        return Qt.MoveAction
    
    #--- Events
    def currentRowChanged(self, current, previous):
        if not current.isValid():
            return
        node = current.internalPointer()
        self.model.selected = node.ref
    
    def nodeCollapsed(self, index):
        node = index.internalPointer()
        self.model.collapse_node(node.ref)
    
    def nodeExpanded(self, index):
        node = index.internalPointer()
        self.model.expand_node(node.ref)
    
    #--- model --> view
    def refresh(self):
        if self._wasRestored:
            self._saveNodeExpansionState()
        self.reset()
        self._restoreNodeExpansionState()
        self._wasRestored = True
        self._updateViewSelection()
    
    def start_editing(self):
        self.view.editSelected()
    
    def stop_editing(self):
        self.view.setFocus() # enough to stop editing
    
    def update_selection(self):
        self._updateViewSelection()
    
