# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-01
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from qtlib.table import Table as TableBase

from ..support.completable_edit import DescriptionEdit, PayeeEdit, AccountEdit
from ..support.date_edit import DateEdit
from ..support.item_delegate import ItemDelegate

DATE_EDIT = 'date_edit'
DESCRIPTION_EDIT = 'description_edit'
PAYEE_EDIT = 'payee_edit'
ACCOUNT_EDIT = 'account_edit'

class TableDelegate(ItemDelegate):
    def __init__(self, model, columns):
        ItemDelegate.__init__(self)
        self._model = model
        self._columns = columns
    
    def createEditor(self, parent, option, index):
        column = self._columns[index.column()]
        editType = column.editor
        if editType is None:
            return ItemDelegate.createEditor(self, parent, option, index)
        elif editType == DATE_EDIT:
            return DateEdit(parent)
        elif editType in (DESCRIPTION_EDIT, PAYEE_EDIT, ACCOUNT_EDIT):
            editClass = {
                DESCRIPTION_EDIT: DescriptionEdit,
                PAYEE_EDIT: PayeeEdit,
                ACCOUNT_EDIT: AccountEdit
            }[editType]
            result = editClass(parent)
            result.setMainwindow(self._model.mainwindow)
            return result
    

class Table(TableBase):
    def __init__(self, model, view):
        TableBase.__init__(self, model, view)
        self.model.columns.view = self
        self.tableDelegate = TableDelegate(self.model, self.COLUMNS)
        self.view.setItemDelegate(self.tableDelegate)
        self.view.horizontalHeader().sectionMoved.connect(self.headerSectionMoved)
        self.view.horizontalHeader().sectionResized.connect(self.headerSectionResized)
    
    #--- Event Handling
    def headerSectionMoved(self, logicalIndex, oldVisualIndex, newVisualIndex):
        attrname = self.COLUMNS[logicalIndex].attrname
        self.model.columns.move_column(attrname, newVisualIndex)
    
    def headerSectionResized(self, logicalIndex, oldSize, newSize):
        attrname = self.COLUMNS[logicalIndex].attrname
        self.model.columns.resize_column(attrname, newSize)
    
    #--- model --> view
    def restore_columns(self):
        colnames = self.model.columns.colnames
        indexes = [self.ATTR2COLUMN[name].index for name in colnames if name in self.ATTR2COLUMN]
        self.setColumnsOrder(indexes)
        widths = [self.model.columns.column_width(col.attrname) for col in self.COLUMNS]
        if not any(widths):
            widths = None
        self.setColumnsWidth(widths)
        for column in self.COLUMNS:
            visible = self.model.columns.column_is_visible(column.attrname)
            self.view.horizontalHeader().setSectionHidden(column.index, not visible)
    
    def set_column_visible(self, colname, visible):
        column = self.ATTR2COLUMN[colname]
        self.view.horizontalHeader().setSectionHidden(column.index, not visible)
    
