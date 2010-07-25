# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-07-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

class Columns(object):
    def __init__(self, colnames):
        self.colnames = colnames[:] # We're altering the list, make a copy
    
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
    
    def set_columns(self, colnames):
        self.colnames = colnames
    
