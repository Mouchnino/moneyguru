# Unit Name: moneyguru.gui.tree
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

class Node(list):
    def __init__(self, name):
        list.__init__(self)
        self._name = name

    def __eq__(self, other):
        return self is other
    
    def __repr__(self):
        return '<Node %r>' % self.name
    
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
        for index, item in enumerate(self):
            if item == target_node:
                return [index]
            path = item.get_path(target_node)
            if path:
                return [index] + path
    
    @property
    def children_count(self):
        return len(self)
    
    @property
    def name(self):
        return self._name
    

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
