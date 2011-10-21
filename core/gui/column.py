# Created By: Virgil Dupras
# Created On: 2010-07-25
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import copy

class Column:
    def __init__(self, name, display='', visible=True, optional=False):
        self.name = name
        self.index = 0
        self.width = 0
        self.display = display
        self.visible = visible
        self.optional = optional
    

class Columns:
    def __init__(self, table):
        self.table = table
        self.document = table.document
        self.savename = table.SAVENAME
        # Set this view as soon as the GUI layer column instance is created
        self.view = None
        # We use copy here for test isolation. If we don't, changing a column affects all tests.
        columns = list(map(copy.copy, table.COLUMNS))
        for i, column in enumerate(columns):
            column.index = i
        self.coldata = {col.name: col for col in columns}
    
    #--- Private
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
    
    def _optional_columns(self):
        return [c for c in self.ordered_columns if c.optional]
    
    #--- Public
    def column_display(self, colname):
        return self._get_colname_attr(colname, 'display', '')
    
    def column_is_visible(self, colname):
        return self._get_colname_attr(colname, 'visible', True)
    
    def column_width(self, colname):
        return self._get_colname_attr(colname, 'width', 0)
    
    def columns_to_right(self, colname):
        column = self.coldata[colname]
        index = column.index
        return [col.name for col in self.coldata.values() if (col.visible and col.index > index)]
    
    def menu_items(self):
        # Returns a list of (display_name, marked) items for each optional column in the current
        # view (marked means that it's visible).
        return [(c.display, c.visible) for c in self._optional_columns()]
    
    def toggle_menu_item(self, index):
        col = self._optional_columns()[index]
        self.set_column_visible(col.name, not col.visible)
    
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
        for col in self.coldata.values():
            pref_name = '{0}.Columns.{1}'.format(self.savename, col.name)
            coldata = self.document.get_default(pref_name, fallback_value={})
            if 'index' in coldata:
                col.index = coldata['index']
            if 'width' in coldata:
                col.width = coldata['width']
            if 'visible' in coldata:
                col.visible = coldata['visible']
        self.view.restore_columns()
    
    def save_columns(self):
        if not (self.savename and self.coldata):
            return
        for col in self.coldata.values():
            pref_name = '{0}.Columns.{1}'.format(self.savename, col.name)
            coldata = {'index': col.index, 'width': col.width, 'visible': col.visible}
            self.document.set_default(pref_name, coldata)
    
    def set_column_order(self, colnames):
        colnames = (name for name in colnames if name in self.coldata)
        for i, colname in enumerate(colnames):
            col = self.coldata[colname]
            col.index = i
    
    def set_column_visible(self, colname, visible):
        self.table.save_edits() # the table on the GUI side will stop editing when the columns change
        self._set_colname_attr(colname, 'visible', visible)
        self.view.set_column_visible(colname, visible)
    
    #--- Properties
    @property
    def ordered_columns(self):
        return [col for col in sorted(iter(self.coldata.values()), key=lambda col: col.index)]
    
    @property
    def colnames(self):
        return [col.name for col in self.ordered_columns]
    
