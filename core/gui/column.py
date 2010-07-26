# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-07-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

class Columns(object):
    def __init__(self, app, savename, colnames):
        self.app = app
        self.savename = savename
        self.colnames = colnames[:] # We're altering the list, make a copy
        self.restore_columns()
    
    def columns_to_right(self, colname):
        column_index = self.colnames.index(colname)
        return self.colnames[column_index+1:]
    
    def move_column(self, colname, index):
        try:
            self.colnames.remove(colname)
        except ValueError:
            pass # move nothing
        else:
            self.colnames.insert(index, colname)
    
    def restore_columns(self):
        if not (self.savename and self.colnames):
            return
        orderpref_name = '{0}.ColumnOrder'.format(self.savename)
        columnorder = self.app.get_default(orderpref_name)
        if columnorder:
            allcols = set(self.colnames)
            newcolumns = [col for col in columnorder if col in allcols]
            # now, add the columns which weren't in the order prefs at the end
            newcolumns += list(allcols - set(newcolumns))
            self.colnames = newcolumns
    
    def save_columns(self):
        if not (self.savename and self.colnames):
            return
        orderpref_name = '{0}.ColumnOrder'.format(self.savename)
        self.app.set_default(orderpref_name, self.colnames)
    
    def set_columns(self, colnames):
        self.colnames = colnames
    
