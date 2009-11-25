# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

DATE_EDIT = 'date_edit'
DESCRIPTION_EDIT = 'description_edit'
PAYEE_EDIT = 'payee_edit'
ACCOUNT_EDIT = 'account_edit'

class Column(object):
    def __init__(self, attrname, title, defaultWidth, editor=None):
        self.index = None # Is set when the column list is read
        self.attrname = attrname
        self.title = title
        self.width = defaultWidth
        self.editor = editor
    

class ColumnBearer(object):
    COLUMNS = []
    
    def __init__(self, headerView):
        self._headerView = headerView
        for index, col in enumerate(self.COLUMNS):
            col.index = index
        # A map attrname:column is useful sometimes, so we create it here
        self.ATTR2COLUMN = dict((col.attrname, col) for col in self.COLUMNS)
    
    #--- Public
    def resizeColumns(self):
        """Resizes headerView's columns according to widths in `COLUMNS`."""
        for column in self.COLUMNS:
            self._headerView.resizeSection(column.index, column.width)
    
    def setColumnsWidth(self, newWidths):
        """Set `COLUMNS` widths according to `newWidths` which is a list of numbers."""
        for column, newWidth in zip(self.COLUMNS, newWidths):
            column.width = newWidth
    
