# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import csv
from io import StringIO

from hscommon.gui import tree
from hscommon.trans import tr
from hscommon.gui.column import Columns

from ..exception import DuplicateAccountNameError
from .base import ViewChild, SheetViewNotificationsMixin, MESSAGES_DOCUMENT_CHANGED

# used in both bsheet and istatement
def get_delta_perc(delta_amount, start_amount):
    if start_amount:
        return '%+1.1f%%' % (delta_amount.value / abs(start_amount.value) * 100)
    else:
        return '---'

class Report(ViewChild, tree.Tree, SheetViewNotificationsMixin):
    SAVENAME = ''
    COLUMNS = []
    INVALIDATING_MESSAGES = MESSAGES_DOCUMENT_CHANGED | {'accounts_excluded', 'date_range_changed'}
    
    def __init__(self, parent_view):
        ViewChild.__init__(self, None, parent_view)
        tree.Tree.__init__(self)
        self.columns = Columns(self, prefaccess=parent_view.document, savename=self.SAVENAME)
        self.edited = None
        self._expanded_paths = {(0, ), (1, )}
    
    #--- Override
    def _revalidate(self):
        self.refresh(refresh_view=False)
        self._update_selection()
        self.view.refresh()
    
    #--- Virtual
    def _compute_account_node(self, node):
        pass
    
    def _make_node(self, name):
        node = Node(name)
        node.account_number = ''
        return node
    
    def _refresh(self):
        pass
    
    #--- Protected
    def _node_of_account(self, account):
        return self.find(lambda n: getattr(n, 'account', None) is account)
    
    def _select_first(self):
        for type_node in self:
            if len(type_node) > 2: # total + blank
                self.selected = type_node[0]
                break
    
    def _update_selection(self):
        account = self.mainwindow.shown_account
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
        self.selected = self._node_of_account(account)
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
    
    def can_move(self, source_paths, dest_path):
        """Returns whether it's possible to move the nodes at 'source_paths' under the node at
        'dest_path'.
        """
        if not dest_path:  # Don't move under the root
            return False
        dest_node = self.get_node(dest_path)
        if not (dest_node.is_group or dest_node.is_type):
            # Move only under a group node or a type node
            return False
        for source_path in source_paths:
            source_node = self.get_node(source_path)
            if not source_node.is_account:
                return False
            if source_node.parent is dest_node:  # Don't move under the same node
                return False
        return True
    
    def cancel_edits(self):
        node = self.edited
        if node is None:
            return
        assert node.is_account or node.is_group
        node.name = node.account.name if node.is_account else node.group.name
        self.edited = None
    
    def collapse_node(self, node):
        self._expanded_paths.discard(tuple(node.path))
        if node.is_group:
            self.parent_view.collapse_group(node.group)
    
    def delete(self):
        if not self.can_delete():
            return
        self.view.stop_editing()
        selected_nodes = self.selected_nodes
        gnodes = [n for n in selected_nodes if n.is_group]
        if gnodes:
            groups = [n.group for n in gnodes]
            self.document.delete_groups(groups)
        anodes = [n for n in selected_nodes if n.is_account]
        if anodes:
            accounts = [n.account for n in anodes]
            if any(a.entries for a in accounts):
                self.mainwindow.account_reassign_panel.load(accounts)
            else:
                self.document.delete_accounts(accounts)
    
    def expand_node(self, node):
        self._expanded_paths.add(tuple(node.path))
        if node.is_group:
            self.parent_view.expand_group(node.group)
    
    def make_account_node(self, account):
        node = self._make_node(account.name)
        node.account = account
        node.is_account = True
        node.account_number = account.account_number
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
            node.append(self.make_total_node(node, tr('Total ') + group.name))
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
            node.append(self.make_total_node(node, tr('TOTAL ') + name))
        node.append(self.make_blank_node())
        return node

    def move(self, source_paths, dest_path):
        """Moves the nodes at 'source_paths' under the node at 'dest_path'."""
        assert self.can_move(source_paths, dest_path)
        accounts = [self.get_node(p).account for p in source_paths]
        dest_node = self.get_node(dest_path)
        if dest_node.is_type:
            self.document.change_accounts(accounts, group=None, type=dest_node.type)
        elif dest_node.is_group:
            self.document.change_accounts(accounts, group=dest_node.group, type=dest_node.group.type)
    
    def refresh(self, refresh_view=True):
        selected_accounts = self.selected_accounts
        selected_paths = self.selected_paths
        self._refresh()
        selected_nodes = []
        for account in selected_accounts:
            node_of_account = self._node_of_account(account)
            if node_of_account is not None:
                selected_nodes.append(node_of_account)
        if selected_nodes:
            self.selected_nodes = selected_nodes
        else:
            self.selected_paths = selected_paths
        if refresh_view:
            self.view.refresh()
    
    def save_edits(self):
        node = self.edited
        if node is None:
            return
        self.edited = None
        assert node.is_account or node.is_group
        try:
            if node.is_account:
                self.document.change_accounts([node.account], name=node.name)
            else:
                self.document.change_group(node.group, name=node.name)
        except DuplicateAccountNameError:
            msg = tr("The account '{0}' already exists.").format(node.name)
            # we use _name because we don't want to change self.edited
            node._name = node.account.name if node.is_account else node.group.name
            self.mainwindow.show_message(msg)
    
    def selection_as_csv(self):
        csvrows = []
        columns = (self.columns.coldata[colname] for colname in self.columns.colnames)
        columns = [col for col in columns if col.visible]
        for node in self.selected_nodes:
            csvrow = []
            for col in columns:
                try:
                    csvrow.append(getattr(node, col.name))
                except AttributeError:
                    pass
            csvrows.append(csvrow)
        fp = StringIO()
        csv.writer(fp, delimiter='\t', quotechar='"').writerows(csvrows)
        fp.seek(0)
        return fp.read()
    
    def show_selected_account(self):
        self.mainwindow.shown_account = self.selected_account
    
    def toggle_excluded(self):
        nodes = self.selected_nodes
        affected_accounts = set()
        for node in nodes:
            if node.is_type:
                affected_accounts |= set(self.document.accounts.filter(type=node.type))
            elif node.is_group:
                affected_accounts |= set(self.document.accounts.filter(group=node.group))
            elif node.is_account:
                affected_accounts.add(node.account)
        if affected_accounts:
            self.document.toggle_accounts_exclusion(affected_accounts)
    
    #--- Event handlers
    def account_added(self):
        self.refresh()
    
    def account_changed(self):
        self.refresh()
    
    def account_deleted(self):
        selected_path = self.selected_path
        self.refresh(refresh_view=False)
        next_node = self.get_node(selected_path)
        if not (next_node.is_account or next_node.is_group):
            selected_path[-1] -= 1
            if selected_path[-1] < 0:
                selected_path = selected_path[:-1]
        self.selected_path = selected_path
        self.view.refresh()
    
    def accounts_excluded(self):
        self.refresh()
    
    def date_range_changed(self):
        self.refresh()
    
    def document_will_close(self):
        # Save node expansion state
        prefname = '{0}.ExpandedPaths'.format(self.SAVENAME)
        self.document.set_default(prefname, self.expanded_paths)
        self.columns.save_columns()
    
    def document_restoring_preferences(self):
        prefname = '{0}.ExpandedPaths'.format(self.SAVENAME)
        expanded = self.document.get_default(prefname, list())
        if expanded:
            self._expanded_paths = {tuple(p) for p in expanded}
            # Expanded paths are refreshed on the basic refresh() call, but there are some
            # synchronization problems when we load a document, which makes the refresh() call
            # happen *before* the expanded paths are restored. Therefore, we must make a separate
            # call to refresh paths.
            self.view.refresh_expanded_paths()
        self.columns.restore_columns()
    
    def edition_must_stop(self):
        self.view.stop_editing()
        self.save_edits()
    
    # account might have been auto-created during import
    def transactions_imported(self):
        self.refresh(refresh_view=False)
        self._select_first()
        self.view.refresh()
    
    def document_changed(self):
        self.refresh(refresh_view=False)
        self._select_first()
        self.view.refresh()
    
    def performed_undo_or_redo(self):
        self.refresh()
    
    #--- Properties
    @property
    def can_show_selected_account(self):
        return self.selected_account is not None
    
    @property
    def expanded_paths(self):
        paths = list(self._expanded_paths)
        # We want the paths in orthe of length so that the paths are correctly expanded in the gui.
        paths.sort(key=lambda p: (len(p), ) + p)
        return paths
    
    selected = tree.Tree.selected_node
    
    @property
    def selected_account(self):
        accounts = self.selected_accounts
        if accounts:
            return accounts[0]
        else:
            return None
    
    @property
    def selected_accounts(self):
        nodes = self.selected_nodes
        return [node.account for node in nodes if node.is_account]
    

class Node(tree.Node):
    def __init__(self, name):
        tree.Node.__init__(self, name)
        self.is_account = False
        self.is_blank = False
        self.is_group = False
        self.is_total = False
        self.is_type = False
        self.is_excluded = False
    
    @property
    def is_expanded(self):
        return tuple(self.path) in self.root._expanded_paths
    
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
    
