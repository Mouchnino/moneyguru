# Created By: Virgil Dupras
# Created On: 2010-03-04
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from collections import defaultdict
from itertools import combinations

from hscommon.util import extract

from ..model.sort import sort_string
from .base import DocumentGUIObject

def has_letters(s, query):
    s_letters = defaultdict(int)
    query_letters = defaultdict(int)
    for letter in query:
        query_letters[letter] += 1
    for letter in s:
        s_letters[letter] += 1
    for letter, count in query_letters.items():
        if s_letters[letter] < count:
            return False
    return True

def letter_distance(s, letter1, letter2):
    indexes1 = [i for i, l in enumerate(s) if l == letter1]
    indexes2 = [i for i, l in enumerate(s) if l == letter2]
    return min(abs(i-j) for i in indexes1 for j in indexes2 if i != j)

def letters_distance(s, query):
    return sum(letter_distance(s, l1, l2) for l1, l2 in combinations(query, 2))

class Lookup(DocumentGUIObject):
    def __init__(self, view, mainwindow):
        DocumentGUIObject.__init__(self, view, mainwindow.document)
        self.mainwindow = mainwindow
        self._original_names = []
        self._filtered_names = []
        self._search_query = ''
        self.selected_index = 0
    
    def _apply_query(self):
        # On top, we want exact matches (the name starts with the query). Then, we want matches
        # that contain all the letters, sorted in order of names that have query letters as close
        # to each other as possible.
        q = sort_string(self._search_query)
        matches1, rest = extract(lambda n: n.startswith(q), self._original_names)
        matches2, rest = extract(lambda n: q in n, rest)
        matches3, rest = extract(lambda n: has_letters(n, q), rest)
        matches3.sort(key=lambda n: letters_distance(n, q))
        self._filtered_names = matches1 + matches2 + matches3
        self.selected_index = max(self.selected_index, 0)
        self.selected_index = min(self.selected_index, len(self._filtered_names)-1)
    
    def _generate_lookup_names(self): # Virtual
        return []
    
    def _go(self, name): #Virtual
        pass
    
    def _refresh(self):
        self._search_query = ''
        self.selected_index = 0
        names = self._generate_lookup_names()
        normalized_names = [sort_string(n) for n in names]
        self._normalized2original = {}
        for normalized, original in zip(normalized_names, names):
            self._normalized2original[normalized] = original
        self._original_names = normalized_names
        self._filtered_names = normalized_names
    
    def go(self):
        try:
            name = self.names[self.selected_index]
            self._go(name)
        except IndexError:
            pass # No result, do nothing
        self.view.hide()
    
    def show(self):
        self._refresh()
        self.view.refresh()
        self.view.show()
    
    #--- Properties
    @property
    def names(self):
        return [self._normalized2original[n] for n in self._filtered_names]
    
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
    
