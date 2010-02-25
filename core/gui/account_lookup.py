# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from collections import defaultdict
from itertools import combinations

from hsutil.misc import extract

from ..model.sort import sort_string
from .base import DocumentGUIObject

def has_letters(s, query):
    s_letters = defaultdict(int)
    query_letters = defaultdict(int)
    for letter in query:
        query_letters[letter] += 1
    for letter in s:
        s_letters[letter] += 1
    for letter, count in query_letters.iteritems():
        if s_letters[letter] < count:
            return False
    return True

def letter_distance(s, letter1, letter2):
    indexes1 = [i for i, l in enumerate(s) if l == letter1]
    indexes2 = [i for i, l in enumerate(s) if l == letter2]
    return min(abs(i-j) for i in indexes1 for j in indexes2 if i != j)

def letters_distance(s, query):
    return sum(letter_distance(s, l1, l2) for l1, l2 in combinations(query, 2))

class AccountLookup(DocumentGUIObject):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        self._original_names = []
        self.names = []
        self._search_query = ''
        self.selected_index = 0
    
    def _apply_query(self):
        # On top, we want exact matches (the name starts with the query). Then, we want matches
        # that contain all the letters, sorted in order of names that have query letters as close
        # to each other as possible.
        q = self._search_query
        matches1, rest = extract(lambda n: q in n, self._original_names)
        matches2, rest = extract(lambda n: has_letters(n, q), rest)
        matches2.sort(key=lambda n: letters_distance(n, q))
        self.names = matches1 + matches2
        self.selected_index = min(self.selected_index, len(self.names)-1)
    
    def _refresh(self):
        names = [a.combined_display for a in self.document.accounts]
        self._original_names = sorted(names, key=sort_string)
        self.names = self._original_names
    
    def go(self):
        name = self.names[self.selected_index]
        account = self.document.accounts.find(name)
        self.document.show_account(account)
    
    def show(self):
        self._refresh()
        self.view.refresh()
    
    #--- Properties
    @property
    def search_query(self):
        return self._search_query
    
    @search_query.setter
    def search_query(self, value):
        if value == self._search_query:
            return
        self._search_query = value
        self._apply_query()
        self.view.refresh()
    

    