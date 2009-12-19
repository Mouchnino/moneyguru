# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from ..exception import DuplicateAccountNameError
from .base import DocumentGUIObject
from . import tree

# used in both bsheet and istatement
def get_delta_perc(delta_amount, start_amount):
    if start_amount > 0:
        return '%+1.1f%%' % (delta_amount.value / start_amount.value * 100)
    else:
        return '---'

class Report(DocumentGUIObject, tree.Tree):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        tree.Tree.__init__(self)
        self.edited = None
    
    #--- Override
    def connect(self):
        DocumentGUIObject.connect(self)
        self.refresh()
        self._update_selection()
        self.view.refresh()
    
    #--- Virtual
    def _compute_account_node(self, node):
        pass
    
    def _make_node(self, name):
        return Node(name)
    
    def _refresh(self):
        pass
    
    #--- Protected
    def _select_first(self):
        for type_node in self:
            if len(type_node) > 2: # total + blank
                self.selected = type_node[0]
                break
    
    def _update_selection(self):
        account = self.document.shown_account
        if account is not None:
            self.selected = self.find(lambda n: getattr(n, 'account', None) is account)
        if not (isinstance(self.selected, Node) and self.selected.is_account):
            self._select_first()        
    
    #--- Public
    def add_account(self):
        self.view.stop_editing()
        self.save_edits()
        node = self.selected
        if isinstance(node, Node) and node.is_group:
            account_type = node.group.type
            account_group = node.group
        elif isinstance(node, Node) and node.is_account:
            account_type = node.account.type
            account_group = node.account.group
        else:
            # there are only 2 types per report
            path = self.selected_path
            account_type = self[1].type if path and path[0] == 1 else self[0].type
            account_group = None
        if account_group is not None:
            account_group.expanded = True
        account = self.document.new_account(account_type, account_group) # refresh happens on account_added
        self.selected = self.find(lambda n: getattr(n, 'account', None) is account)
        self.view.update_selection()
        self.view.start_editing()
    
    def add_account_group(self):
        self.view.stop_editing()
        self.save_edits()
        node = self.selected
        if isinstance(node, Node) and node.is_group:
            account_type = node.group.type
        elif isinstance(node, Node) and node.is_account:
            account_type = node.account.type
        else:
            path = self.selected_path
            account_type = self[1].type if path and path[0] == 1 else self[0].type
        group = self.document.new_group(account_type)
        self.selected = self.find(lambda n: getattr(n, 'group', None) is group)
        self.view.update_selection()
        self.view.start_editing()
    
    def can_delete(self):
        node = self.selected
        return isinstance(node, Node) and (node.is_account or node.is_group)
    
    def can_move(self, source_path, dest_path):
        """Returns whether it's possible to move the node at 'source_path' under the node at 'dest_path'."""
        if not dest_path:  # Don't move under the root
            return False
        if source_path[:-1] == dest_path:  # Don't move under the same node
            return False
        node = self.get_node(dest_path)
        return node.is_group or node.is_type  # Move only under a group node or a type node
    
    def cancel_edits(self):
        node = self.edited
        if node is None:
            return
        assert node.is_account or node.is_group
        node.name = node.account.name if node.is_account else node.group.name
        self.edited = None
    
    def collapse_node(self, node):
        if node.is_group:
            node.is_expanded = False
            self.document.collapse_group(node.group)
    
    def delete(self):
        if not self.can_delete():
            return
        self.view.stop_editing()
        node = self.selected
        selected_path = self.selected_path
        if node.is_account:
            self.document.delete_selected_account()
        else:
            group = node.group
            self.document.delete_group(group)
    
    def expand_node(self, node):
        if node.is_group:
            node.is_expanded = True
            self.document.expand_group(node.group)
    
    def make_account_node(self, account):
        node = self._make_node(account.name)
        node.account = account
        node.is_account = True
        node.is_excluded = account in self.document.excluded_accounts
        if not node.is_excluded:
            self._compute_account_node(node)
        return node
    
    def make_blank_node(self):
        node = self._make_node(None)
        node.is_blank = True
        return node

    def make_group_node(self, group):
        node = self._make_node(group.name)
        node.group = group
        node.is_group = True
        accounts = self.document.accounts.filter(group=group)
        for account in sorted(accounts):
            node.append(self.make_account_node(account))
        node.is_excluded = bool(accounts) and set(accounts) <= self.document.excluded_accounts # all accounts excluded
        if not node.is_excluded:
            node.append(self.make_total_node(node, 'Total ' + group.name))
        node.append(self.make_blank_node())
        return node

    def make_total_node(self, name):
        node = self._make_node(name)
        node.is_total = True
        return node

    def make_type_node(self, name, type):
        node = self._make_node(name)
        node.type = type
        node.is_type = True
        for group in sorted(self.document.groups.filter(type=type)):
            node.append(self.make_group_node(group))
        for account in sorted(self.document.accounts.filter(type=type, group=None)):
            node.append(self.make_account_node(account))
        accounts = self.document.accounts.filter(type=type)
        node.is_excluded = bool(accounts) and set(accounts) <= self.document.excluded_accounts # all accounts excluded
        if not node.is_excluded:
            node.append(self.make_total_node(node, 'TOTAL ' + name))
        node.append(self.make_blank_node())
        return node

    def move(self, source_path, dest_path):
        """Moves the node at 'source_path' under the node at 'dest_path'."""
        assert self.can_move(source_path, dest_path)
        account = self.get_node(source_path).account
        dest_node = self.get_node(dest_path)
        if dest_node.is_type:
            self.document.change_account(account, group=None, type=dest_node.type)
        elif dest_node.is_group:
            self.document.change_account(account, group=dest_node.group, type=dest_node.group.type)
    
    def refresh(self):
        selected_path = self.selected_path
        self._refresh()
        self.selected_path = selected_path
    
    def save_edits(self):
        node = self.edited
        if node is None:
            return
        self.edited = None
        assert node.is_account or node.is_group
        try:
            if node.is_account:
                self.document.change_account(node.account, name=node.name)
            else:
                self.document.change_group(node.group, name=node.name)
        except DuplicateAccountNameError:
            msg = "The account '{0}' already exists.".format(node.name)
            node.name = node.account.name if node.is_account else node.group.name
            self.view.show_message(msg)
    
    def show_selected_account(self):
        self.document.show_selected_account()
    
    def toggle_excluded(self):
        node = self.selected
        if node.is_type:
            affected_accounts = set(self.document.accounts.filter(type=node.type))
        elif node.is_group:
            affected_accounts = set(self.document.accounts.filter(group=node.group))
        elif node.is_account:
            affected_accounts = set([node.account])
        else:
            return
        self.document.toggle_accounts_exclusion(affected_accounts)
    
    #--- Event handlers
    def account_added(self):
        self.refresh()
        self.view.refresh()
    
    def account_changed(self):
        self.refresh()
        self.view.refresh()
    
    def account_deleted(self):
        selected_path = self.selected_path
        self.refresh()
        next_node = self.get_node(selected_path)
        if not (next_node.is_account or next_node.is_group):
            selected_path[-1] -= 1
            if selected_path[-1] < 0:
                selected_path = selected_path[:-1]
        self.selected_path = selected_path
        self.view.refresh()
    
    def accounts_excluded(self):
        self.refresh()
        self.view.refresh()
    
    def date_range_changed(self):
        self.refresh()
        self.view.refresh()
    
    def edition_must_stop(self):
        self.view.stop_editing()
        self.save_edits()
    
    # account might have been auto-created during import
    def transactions_imported(self):
        self.refresh()
        self._select_first()
        self.view.refresh()
    
    def document_changed(self):
        self.refresh()
        self._select_first()
        self.view.refresh()
    
    def performed_undo_or_redo(self):
        self.refresh()
        self.view.refresh()
    
    #--- Properties
    @property
    def can_show_selected_account(self):
        return self.document.selected_account is not None
    
    @property
    def selected(self):
        return self._selected
    
    @selected.setter
    def selected(self, node):
        self._selected = node
        account = node.account if isinstance(node, Node) and node.is_account else None
        self.document.select_account(account)
    

class Node(tree.Node):
    def __init__(self, name):
        tree.Node.__init__(self, name)
        self.is_account = False
        self.is_blank = False
        self.is_group = False
        self.is_total = False
        self.is_type = False
        self.is_excluded = False
        self.is_expanded = False
    
    @property
    def is_subtotal(self):
        if not (self.is_account or self.is_group):
            return False
        if len(self) and self.is_expanded: # an expanded group can't be considered a subtotal
            return False
        parent = self.parent
        if parent is None:
            return False
        index = parent.index(self)
        try:
            next_node = parent[index+1]
            return next_node.is_total
        except IndexError:
            return False
    
    @property
    def can_edit_name(self):
        return self.is_account or self.is_group
    
    @tree.Node.name.setter
    def name(self, value):
        root = self.root
        assert root.edited is None or root.edited is self
        if not value:
            return
        self._name = value
        root.edited = self
    
