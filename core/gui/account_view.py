# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import tr
from ..const import PaneType
from .base import BaseView, MESSAGES_DOCUMENT_CHANGED
from .filter_bar import EntryFilterBar
from .entry_table import EntryTable
from .account_balance_graph import AccountBalanceGraph
from .account_flow_graph import AccountFlowGraph
from .transaction_print import EntryPrint

class AccountView(BaseView):
    VIEW_TYPE = PaneType.Account
    PRINT_TITLE_FORMAT = tr('{account_name}\nEntries from {start_date} to {end_date}')
    PRINT_VIEW_CLASS = EntryPrint
    INVALIDATING_MESSAGES = MESSAGES_DOCUMENT_CHANGED | {'filter_applied',
        'date_range_changed', 'transactions_selected', 'area_visibility_changed'}
    
    def __init__(self, mainwindow, account):
        BaseView.__init__(self, mainwindow)
        assert account is not None
        self.account = account
        self._reconciliation_mode = False
        self.etable = EntryTable(self)
        self.maintable = self.etable
        self.columns = self.maintable.columns
        self.balgraph = AccountBalanceGraph(self)
        self.bargraph = AccountFlowGraph(self)
        self.filter_bar = EntryFilterBar(self)
        if account.is_balance_sheet_account():
            self._shown_graph = self.balgraph
        else:
            self._shown_graph = self.bargraph
        self.set_children([self.etable, self._shown_graph])
    
    #--- Private
    def _refresh_totals(self):
        account = self.account
        if account is None:
            return
        selected, total, total_debit, total_credit = self.etable.get_totals()
        if account.is_debit_account():
            increase = total_debit
            decrease = total_credit
        else:
            increase = total_credit
            decrease = total_debit
        total_increase_fmt = self.document.format_amount(increase)
        total_decrease_fmt = self.document.format_amount(decrease)
        msg = tr("{0} out of {1} selected. Increase: {2} Decrease: {3}")
        self.status_line = msg.format(selected, total, total_increase_fmt, total_decrease_fmt)
    
    #--- Override
    def _view_updated(self):
        if self._shown_graph is self.balgraph:
            self.view.show_line_graph()
        else:
            self.view.show_bar_graph()
    
    def _revalidate(self):
        self._refresh_totals()
        self.view.refresh_reconciliation_button()
        self.filter_bar.refresh()
        self.view.update_visibility()
    
    def restore_subviews_size(self):
        if self.balgraph.view_size[1]:
            # Was already restored
            return
        self.graph_height_to_restore = self.document.get_default('AccountView.GraphHeight', 0)
    
    def show(self):
        self.etable.columns.restore_columns()
        BaseView.show(self)
    
    def hide(self):
        self.etable.columns.save_columns()
        BaseView.hide(self)
    
    def save_preferences(self):
        # Unlike other views, we don't save preferences on pane closing, but much more frequently:
        # on pane swapping. We do this because AccountView columns are shared between multiple
        # instances and changing a column in a pane should result in the same change being done
        # in other tabs. That's why we save/restore in hide()/show().
        # ... Except for graph size. We don't keep separate graph size prefs for each account.
        height = self._shown_graph.view_size[1]
        # It's possible that set_view_size() has never been called. In this case, we have (0, 0).
        if height: 
            self.document.set_default('AccountView.GraphHeight', height)
    
    #--- Public
    def delete_item(self):
        self.etable.delete()
    
    def duplicate_item(self):
        self.etable.duplicate_selected()
    
    def edit_item(self):
        self.mainwindow.edit_selected_transactions()
    
    def navigate_back(self):
        """When the entry table is shown, go back to the appropriate report."""
        if self.account.is_balance_sheet_account():
            self.mainwindow.select_pane_of_type(PaneType.NetWorth)
        else:
            self.mainwindow.select_pane_of_type(PaneType.Profit)
    
    def move_down(self):
        self.etable.move_down()
    
    def move_up(self):
        self.etable.move_up()
    
    def new_item(self):
        self.etable.add()
    
    def show_account(self):
        self.etable.show_transfer_account()
    
    def toggle_reconciliation_mode(self):
        self._reconciliation_mode = not self._reconciliation_mode
        self.etable.reconciliation_mode = self._reconciliation_mode
        self.view.refresh_reconciliation_button()
    
    #--- Properties
    @property
    def can_toggle_reconciliation_mode(self):
        return self.account.is_balance_sheet_account()
    
    @property
    def reconciliation_mode(self):
        return self._reconciliation_mode
    
    #--- Event Handlers
    def area_visibility_changed(self):
        self.view.update_visibility()
    
    def date_range_changed(self):
        self._refresh_totals()
    
    def document_changed(self):
        self._refresh_totals()
    
    def filter_applied(self):
        self._refresh_totals()
        self.filter_bar.refresh()
    
    def performed_undo_or_redo(self):
        self._refresh_totals()
    
    def transactions_selected(self):
        self._refresh_totals()
    
    def transaction_changed(self):
        self._refresh_totals()
    
    def transaction_deleted(self):
        self._refresh_totals()
    
    def transactions_imported(self):
        self._refresh_totals()
    
