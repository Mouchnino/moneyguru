# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

class Node(list):
    def __init__(self, name):
        list.__init__(self)
        self._name = name
        self._parent = None
        self._path = None
    
    def __eq__(self, other):
        return self is other
    
    def __hash__(self):
        return object.__hash__(self)
    
    def __repr__(self):
        return '<Node %r>' % self.name
    
    def append(self, node):
        list.append(self, node)
        node._parent = self
        node._path = None
    
    def clear(self):
        del self[:]
    
    def find(self, predicate):
        if predicate(self):
            return self
        for child in self:
            found = child.find(predicate)
            if found is not None:
                return found
    
    def get_node(self, index_path):
        result = self
        if index_path:
            for index in index_path:
                result = result[index]
        return result
    
    def get_path(self, target_node):
        if target_node is None:
            return None
        return target_node.path
    
    @property
    def children_count(self):
        return len(self)
    
    @property
    def name(self):
        return self._name
    
    @property
    def parent(self):
        return self._parent
    
    @property
    def path(self):
        if self._path is None:
            if self._parent is None:
                self._path = []
            else:
                self._path = self._parent.path + [self._parent.index(self)]
        return self._path
    
    @property
    def root(self):
        if self._parent is None:
            return self
        else:
            return self._parent.root
    

class Tree(Node):
    def __init__(self):
        Node.__init__(self, '')
        self._selected = None

    def __hash__(self):
        return object.__hash__(self)

    @property
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, node):
        self._selected = node
    
    @property
    def selected_path(self):
        return self.get_path(self.selected)
    
    @selected_path.setter
    def selected_path(self, index_path):
        try:
            self.selected = self.get_node(index_path)
        except IndexError:
            self.selected = None
