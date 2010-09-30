# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-03-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from ..model.sort import sort_string
from .lookup import Lookup

class CompletionLookup(Lookup):
    def __init__(self, view, mainwindow):
        Lookup.__init__(self, view, mainwindow)
        self._completable_edit = None
    
    def _generate_lookup_names(self):
        if self._completable_edit is not None:
            names = self._completable_edit.candidates[:]
            return sorted(names, key=sort_string)
        else:
            return []
    
    def _go(self, name):
        self._completable_edit.set_lookup_choice(name)
    
    def show(self, completable_edit):
        self._completable_edit = completable_edit
        Lookup.show(self)
        if completable_edit.text:
            self.search_query = completable_edit.text
    
