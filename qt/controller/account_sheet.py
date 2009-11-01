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

from PyQt4.QtCore import Qt, SIGNAL, QMimeData, QByteArray
from PyQt4.QtGui import QPixmap

from qtlib.tree_model import TreeNode, TreeModel

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
    
    def __init__(self, doc, view):
        TreeModel.__init__(self)
        self.doc = doc
        self.view = view
        self.model = self._getModel()
        self.view.setModel(self)
    
    def _createNode(self, ref, row):
        return Node(self, None, ref, row)
    
    def _getChildren(self):
        return self.model[:]
    
    def _getModel(self):
        raise NotImplementedError()
    
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
        if index.column() == 0:
            flags |= Qt.ItemIsEditable
        return flags
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole and section < len(self.HEADER):
            return self.HEADER[section]
        return None
    
    #--- model --> view
    def refresh(self):
        self.reset()
    
    def stop_editing(self):
        pass
    
