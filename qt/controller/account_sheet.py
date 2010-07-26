# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from PyQt4.QtCore import Qt, QModelIndex, QMimeData, QByteArray
from PyQt4.QtGui import QPixmap, QPalette, QFont, QMessageBox

from hsutil.misc import nonone
from qtlib.column import ColumnBearer
from qtlib.tree_model import TreeNode, TreeModel

from const import (MIME_NODEPATH, INDENTATION_OFFSET_ROLE, EXTRA_ROLE, EXTRA_UNDERLINED,
    EXTRA_UNDERLINED_DOUBLE)
from support.item_delegate import ItemDelegate, ItemDecoration

class Node(TreeNode):
    def __init__(self, model, parent, ref, row):
        TreeNode.__init__(self, model, parent, row)
        self.ref = ref
    
    def _createNode(self, ref, row):
        return Node(self.model, self, ref, row)
    
    def _getChildren(self):
        return self.ref[:]
    

class AccountSheetDelegate(ItemDelegate):
    def __init__(self, model):
        ItemDelegate.__init__(self)
        self._model = model
        arrow = QPixmap(':/right_arrow_gray_12')
        arrowSelected = QPixmap(':/right_arrow_white_12')
        accountOut = QPixmap(':/account_out_12')
        accountIn = QPixmap(':/account_in_12')
        self._decoArrow = ItemDecoration(arrow, self._model.model.show_selected_account)
        self._decoArrowSelected = ItemDecoration(arrowSelected, self._model.model.show_selected_account)
        self._decoAccountOut = ItemDecoration(accountOut, self._model.model.toggle_excluded)
        self._decoAccountIn = ItemDecoration(accountIn, self._model.model.toggle_excluded)
    
    def _get_decorations(self, index, isSelected):
        column = self._model.COLUMNS[index.column()]
        if column.attrname != 'name':
            return []
        result = []
        node = index.internalPointer()
        ref = node.ref
        if ref.is_account:
            deco = self._decoArrowSelected if isSelected else self._decoArrow
            result.append(deco)
        if isSelected and not (ref.is_total or ref.is_blank):
            deco = self._decoAccountIn if ref.is_excluded else self._decoAccountOut
            result.append(deco)
        return result
    
    def _prepare_paint_options(self, option, index):
        column = self._model.COLUMNS[index.column()]
        node = index.internalPointer()
        ref = node.ref
        if ref.is_excluded:
            option.palette.setColor(QPalette.Text, Qt.gray)
        indentationOffset = self._model.data(index, INDENTATION_OFFSET_ROLE)
        if indentationOffset:
            option.rect.setLeft(option.rect.left()+indentationOffset)
    
    def paint(self, painter, option, index):
        ItemDelegate.paint(self, painter, option, index)
        extraFlags = nonone(self._model.data(index, EXTRA_ROLE), 0)
        if extraFlags & (EXTRA_UNDERLINED | EXTRA_UNDERLINED_DOUBLE):
            p1 = option.rect.bottomLeft()
            p2 = option.rect.bottomRight()
            p1.setX(p1.x()+1)
            p2.setX(p2.x()-1)
            painter.drawLine(p1, p2)
            if extraFlags & EXTRA_UNDERLINED_DOUBLE:
                # Yes, yes, we step over the item's bounds, but we have no choice because under
                # Windows, there's not enough height for double lines. Moreover, the line under
                # a total line is a blank line, so we have plenty of space.
                p1.setY(p1.y()+2)
                p2.setY(p2.y()+2)
                painter.drawLine(p1, p2)
    

class AccountSheet(TreeModel, ColumnBearer):
    AMOUNT_ATTRS = set()
    BOLD_ATTRS = set()
    
    def __init__(self, doc, model, view):
        TreeModel.__init__(self)
        ColumnBearer.__init__(self, view.header())
        self.doc = doc
        self.app = doc.app
        self.view = view
        self.model = model
        self.view.setModel(self)
        self.accountSheetDelegate = AccountSheetDelegate(self)
        self.view.setItemDelegate(self.accountSheetDelegate)
        
        self.view.selectionModel().currentRowChanged.connect(self.currentRowChanged)
        self.view.collapsed.connect(self.nodeCollapsed)
        self.view.expanded.connect(self.nodeExpanded)
        self.view.deletePressed.connect(self.model.delete)
        self.view.spacePressed.connect(self.model.toggle_excluded)
        self.view.doubleClicked.connect(self.model.show_selected_account)
        self.view.header().sectionMoved.connect(self.headerSectionMoved)
    
    #--- TreeModel overrides
    def _createNode(self, ref, row):
        return Node(self, None, ref, row)
    
    def _getChildren(self):
        return self.model[:]
    
    #--- Private
    def _updateViewSelection(self):
        # Takes the selection on the model's side and update the view with it.
        selectedPath = self.model.selected_path
        if selectedPath is None:
            return
        modelIndex = self.findIndex(selectedPath)
        self.view.setCurrentIndex(modelIndex)
    
    #--- Public
    def setColumnsOrder(self):
        colnames = self.model.columns.colnames
        indexes = [self.ATTR2COLUMN[name].index for name in colnames if name in self.ATTR2COLUMN]
        ColumnBearer.setColumnsOrder(self, indexes)
    
    #--- Data Model methods
    def columnCount(self, parent):
        return len(self.COLUMNS)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        ref = node.ref
        column = self.COLUMNS[index.column()]
        rowattr = column.attrname
        if role in (Qt.DisplayRole, Qt.EditRole):
            return getattr(node.ref, rowattr)
        elif role == Qt.FontRole:
            isBold = False
            if rowattr == 'name':
                if ref.is_group or ref.is_total or ref.is_type:
                    isBold = True
            elif rowattr in self.BOLD_ATTRS:
                isBold = True
            font = QFont(self.view.font())
            font.setBold(isBold)
            return font
        elif role == Qt.TextAlignmentRole:
            return column.alignment
        elif role == INDENTATION_OFFSET_ROLE:
            # index.parent().isValid(): we don't want the grand total line to be unindented
            if rowattr == 'name' and ref.is_total and index.parent().isValid():
                return -self.view.indentation()
        elif role == EXTRA_ROLE:
            flags = 0
            if rowattr in self.AMOUNT_ATTRS:
                if ref.is_subtotal:
                    flags |= EXTRA_UNDERLINED
                elif ref.is_total:
                    flags |= EXTRA_UNDERLINED_DOUBLE
            return flags
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
        if not mimeData.hasFormat(MIME_NODEPATH):
            return False
        if not parentIndex.isValid():
            return False
        path = map(int, unicode(mimeData.data(MIME_NODEPATH)).split(','))
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
        mimeData.setData(MIME_NODEPATH, QByteArray(data))
        return mimeData
    
    def mimeTypes(self):
        return [MIME_NODEPATH]
    
    def supportedDropActions(self):
        return Qt.MoveAction
    
    #--- Events
    def currentRowChanged(self, current, previous):
        if not current.isValid():
            return
        node = current.internalPointer()
        self.model.selected = node.ref
    
    def headerSectionMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        attrname = self.COLUMNS[logicalIndex].attrname
        self.model.columns.move_column(attrname, newVisualIndex)
    
    def nodeCollapsed(self, index):
        node = index.internalPointer()
        self.model.collapse_node(node.ref)
    
    def nodeExpanded(self, index):
        node = index.internalPointer()
        self.model.expand_node(node.ref)
    
    #--- model --> view
    def refresh(self):
        self.reset()
        for path in self.model.expanded_paths:
            index = self.findIndex(path)
            self.view.expand(index)
        self._updateViewSelection()
    
    def start_editing(self):
        self.view.editSelected()
    
    def stop_editing(self):
        self.view.setFocus() # enough to stop editing
    
    def update_selection(self):
        self._updateViewSelection()
    
