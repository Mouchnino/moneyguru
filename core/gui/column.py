# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-07-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import copy

class Column(object):
    def __init__(self, name, optional=False, visible=True):
        self.name = name
        self.index = 0
        self.width = 0
        self.optional = optional # If not optional, a column is never restored as invisible
        self.visible = visible
    

class Columns(object):
    def __init__(self, app, savename, columns):
        self.app = app
        self.savename = savename
        # We use copy here for test isolation. If we don't, changing a column affects all tests.
        columns = map(copy.copy, columns)
        for i, column in enumerate(columns):
            column.index = i
        self.coldata = dict((col.name, col) for col in columns)
        self.restore_columns()
    
    def _get_colname_attr(self, colname, attrname, default):
        try:
            return getattr(self.coldata[colname], attrname)
        except KeyError:
            return default
    
    def _set_colname_attr(self, colname, attrname, value):
        try:
            col = self.coldata[colname]
            setattr(col, attrname, value)
        except KeyError:
            pass
    
    def column_is_visible(self, colname):
        return self._get_colname_attr(colname, 'visible', True)
    
    def column_width(self, colname):
        return self._get_colname_attr(colname, 'width', 0)
    
    def columns_to_right(self, colname):
        column = self.coldata[colname]
        index = column.index
        return [col.name for col in self.coldata.itervalues() if (col.visible and col.index > index)]
    
    def move_column(self, colname, index):
        colnames = self.colnames
        colnames.remove(colname)
        colnames.insert(index, colname)
        self.set_column_order(colnames)
    
    def resize_column(self, colname, newwidth):
        self._set_colname_attr(colname, 'width', newwidth)
    
    def restore_columns(self):
        if not (self.savename and self.coldata):
            return
        for col in self.coldata.itervalues():
            pref_name = '{0}.Columns.{1}'.format(self.savename, col.name)
            coldata = self.app.get_default(pref_name)
            if coldata:
                col.index = coldata.get('index', 0)
                col.width = coldata.get('width', 0)
                if col.optional:
                    col.visible = coldata.get('visible', True)
    
    def save_columns(self):
        if not (self.savename and self.coldata):
            return
        for col in self.coldata.itervalues():
            pref_name = '{0}.Columns.{1}'.format(self.savename, col.name)
            coldata = {'index': col.index, 'width': col.width}
            if col.optional:
                coldata['visible'] = col.visible
            self.app.set_default(pref_name, coldata)
    
    def set_column_order(self, colnames):
        colnames = (name for name in colnames if name in self.coldata)
        for i, colname in enumerate(colnames):
            col = self.coldata[colname]
            col.index = i
    
    def set_column_visible(self, colname, visible):
        self._set_colname_attr(colname, 'visible', visible)
    
    #--- Properties
    @property
    def colnames(self):
        return [col.name for col in sorted(self.coldata.itervalues(), key=lambda col: col.index)]
    
