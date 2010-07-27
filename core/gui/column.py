# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-07-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

class Column(object):
    def __init__(self, name):
        self.name = name
        self.index = 0
        self.width = 0
    

class Columns(object):
    def __init__(self, app, savename, colnames):
        self.app = app
        self.savename = savename
        columns = [Column(name) for name in colnames]
        for i, column in enumerate(columns):
            column.index = i
        self.coldata = dict((col.name, col) for col in columns)
        self.restore_columns()
    
    def column_width(self, colname):
        try:
            return self.coldata[colname].width
        except KeyError:
            return 0
    
    def columns_to_right(self, colname):
        column = self.coldata[colname]
        index = column.index
        return [col.name for col in self.coldata.itervalues() if col.index > index]
    
    def move_column(self, colname, index):
        colnames = self.colnames
        colnames.remove(colname)
        colnames.insert(index, colname)
        self.set_column_order(colnames)
    
    def resize_column(self, colname, newwidth):
        try:
            col = self.coldata[colname]
            col.width = newwidth
        except KeyError:
            pass
    
    def restore_columns(self):
        if not (self.savename and self.coldata):
            return
        for col in self.coldata.itervalues():
            pref_name = '{0}.Columns.{1}'.format(self.savename, col.name)
            coldata = self.app.get_default(pref_name)
            if coldata:
                col.index = coldata.get('index', 0)
                col.width = coldata.get('width', 0)
    
    def save_columns(self):
        if not (self.savename and self.coldata):
            return
        for col in self.coldata.itervalues():
            pref_name = '{0}.Columns.{1}'.format(self.savename, col.name)
            coldata = {'index': col.index, 'width': col.width}
            self.app.set_default(pref_name, coldata)
    
    def set_column_order(self, colnames):
        colnames = (name for name in colnames if name in self.coldata)
        for i, colname in enumerate(colnames):
            col = self.coldata[colname]
            col.index = i
    
    #--- Properties
    @property
    def colnames(self):
        return [col.name for col in sorted(self.coldata.itervalues(), key=lambda col: col.index)]
    
