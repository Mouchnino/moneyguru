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

from PyQt4.QtCore import Qt, QModelIndex, QMimeData, QByteArray

from qtlib.tree_model import TreeNode, TreeModel

MIME_PATH = 'application/moneyguru.nodepath'

class Node(TreeNode):
    def __init__(self, model, parent, ref, row):
        TreeNode.__init__(self, model, parent, row)
        self.ref = ref
    
    def _createNode(self, ref, row):
        return Node(self.model, self, ref, row)
    
    def _getChildren(self):
        return self.ref[:]
    

class AccountSheet(TreeModel):
    HEADER = ['Account']
    ROWATTRS = ['name']
    EXPANDED_NODE_PREF_NAME = None # must set in subclass
    
    def __init__(self, doc, view):
        TreeModel.__init__(self)
        self.doc = doc
        self.app = doc.app
        self.view = view
        self._wasRestored = False
        self.model = self._getModel()
        self.view.setModel(self)
        self._restoreNodeExpansionState()
        
        self.view.selectionModel().currentRowChanged.connect(self.currentRowChanged)
        self.view.collapsed.connect(self.nodeCollapsed)
        self.view.expanded.connect(self.nodeExpanded)
        self.app.willSavePrefs.connect(self._saveNodeExpansionState)
    
    #--- Virtual
    def _getModel(self):
        raise NotImplementedError()
    
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
    
    #--- Data Model methods
    def columnCount(self, parent):
        return len(self.HEADER)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            node = index.internalPointer()
            rowattr = self.ROWATTRS[index.column()]
            return getattr(node.ref, rowattr)
        return None
    
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
        node = index.internalPointer()
        rowattr = self.ROWATTRS[index.column()]
        if getattr(node.ref, 'can_edit_' + rowattr, False):
            flags |= Qt.ItemIsEditable
        if node.ref.is_group or node.ref.is_type:
            flags |= Qt.ItemIsDropEnabled
        if node.ref.is_account:
            flags |= Qt.ItemIsDragEnabled
        return flags
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self.HEADER):
            return self.HEADER[section]
        return None
    
    def revert(self):
        self.model.cancel_edits()
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == Qt.EditRole:
            node = index.internalPointer()
            rowattr = self.ROWATTRS[index.column()]
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
    
    def start_editing(self):
        selectedIndex = self.view.selectionModel().selectedRows()[0]
        self.view.edit(selectedIndex)
    
    def stop_editing(self):
        pass
    
    def update_selection(self):
        selectedPath = self.model.selected_path
        modelIndex = self.findIndex(selectedPath)
        self.view.setCurrentIndex(modelIndex)
    
