# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from ..const import PaneType
from ..document import FilterType
from ..trans import tr
from .base import BaseView, MESSAGES_DOCUMENT_CHANGED

class AccountView(BaseView):
    VIEW_TYPE = PaneType.Account
    INVALIDATING_MESSAGES = MESSAGES_DOCUMENT_CHANGED | set(['filter_applied',
        'date_range_changed', 'transactions_selected', 'shown_account_changed'])
    
    def __init__(self, view, mainwindow):
        BaseView.__init__(self, view, mainwindow)
        self._shown_graph = None
        self._reconciliation_mode = False
        self._visible_entries = None
    
    def set_children(self, children):
        self.etable, self.balgraph, self.bargraph, self.efbar = children
        self._shown_graph = self.balgraph
        # we count the graphs separately because the show/hide rules for them are special
        BaseView.set_children(self, [self.etable, self.efbar])
        self.balgraph.connect()
        self.bargraph.connect()
    
    def _revalidate(self):
        # XXX Huh oh, this is very inefficient (but for now the only way to make tests pass)! Once
        # the view refactoring is over, the views will have to be connected at all times to make
        # the invalidation of their cache more efficient. Then, we'll have show()/hide() methods
        # where children will be refreshed.
        self._invalidate_cache()
        self.view.refresh_reconciliation_button()
    
    def show(self):
        BaseView.show(self)
        account = self.mainwindow.shown_account
        if account is None:
            return
        if account.is_balance_sheet_account():
            self._shown_graph = self.balgraph
            self.view.show_line_graph()
        else:
            self._shown_graph = self.bargraph
            self.view.show_bar_graph()
        self._shown_graph.show()
    
    def hide(self):
        BaseView.hide(self)
        self.balgraph.hide()
        self.bargraph.hide()
    
    #--- Private
    def _invalidate_cache(self):
        self._visible_entries = None
        self._refresh_totals()
    
    def _refresh_totals(self):
        account = self.mainwindow.shown_account
        if account is None:
            return
        selected = len(self.mainwindow.selected_transactions)
        total = len(self.visible_entries)
        amounts = [t.amount_for_account(account, account.currency) for t in self.mainwindow.selected_transactions]
        total_increase = sum(a for a in amounts if a > 0)
        total_decrease = abs(sum(a for a in amounts if a < 0))
        total_increase_fmt = self.app.format_amount(total_increase)
        total_decrease_fmt = self.app.format_amount(total_decrease)
        msg = tr("{0} out of {1} selected. Increase: {2} Decrease: {3}")
        self.status_line = msg.format(selected, total, total_increase_fmt, total_decrease_fmt)
    
    def _set_visible_entries(self):
        account = self.mainwindow.shown_account
        if account is None:
            self._visible_entries = []
            return
        date_range = self.document.date_range
        entries = [e for e in account.entries if e.date in date_range]
        query_string = self.document.filter_string
        filter_type = self.document.filter_type
        if query_string:
            query = self.app.parse_search_query(query_string)
            entries = [e for e in entries if e.transaction.matches(query)]
        if filter_type is FilterType.Unassigned:
            entries = [e for e in entries if not e.transfer]
        elif (filter_type is FilterType.Income) or (filter_type is FilterType.Expense):
            if account.is_credit_account():
                want_positive = filter_type is FilterType.Expense
            else:
                want_positive = filter_type is FilterType.Income
            if want_positive:
                entries = [e for e in entries if e.amount > 0]
            else:
                entries = [e for e in entries if e.amount < 0]
        elif filter_type is FilterType.Transfer:
            entries = [e for e in entries if
                any(s.account is not None and s.account.is_balance_sheet_account() for s in e.splits)]
        elif filter_type is FilterType.Reconciled:
            entries = [e for e in entries if e.reconciled]
        elif filter_type is FilterType.NotReconciled:
            entries = [e for e in entries if not e.reconciled]
        self._visible_entries = entries
    
    #--- Public
    def delete_item(self):
        self.etable.delete()
    
    def duplicate_item(self):
        self.etable.duplicate_selected()
    
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
        shown_account = self.mainwindow.shown_account
        return shown_account is not None and shown_account.is_balance_sheet_account()
    
    @property
    def reconciliation_mode(self):
        return self._reconciliation_mode
    
    @property
    def visible_entries(self):
        if self._visible_entries is None:
            self._set_visible_entries()
        return self._visible_entries
    
    #--- Event Handlers
    def date_range_changed(self):
        self._invalidate_cache()
    
    def document_changed(self):
        self._invalidate_cache()
    
    def filter_applied(self):
        self._invalidate_cache()
    
    def performed_undo_or_redo(self):
        self._invalidate_cache()
    
    # If the account view is visible when the message is broadcasted, we won't get automatically
    # invalidated, so we have to do it automatically.
    def shown_account_changed(self):
        self._invalidated = True
    
    def transactions_selected(self):
        self._refresh_totals()
    
    def transaction_changed(self):
        self._invalidate_cache()
    
    def transaction_deleted(self):
        self._invalidate_cache()
    
    def transactions_imported(self):
        self._invalidate_cache()
    
