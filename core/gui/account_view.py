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
from .base import BaseView

class AccountView(BaseView):
    VIEW_TYPE = PaneType.Account
    
    def __init__(self, view, mainwindow, children):
        self.etable, self.balgraph, self.bargraph, self.efbar = children
        # we count the graphs separately because the connect/disconnect rules for them are special
        BaseView.__init__(self, view, mainwindow.document, [self.etable, self.efbar])
        self._shown_graph = self.balgraph
        self._reconciliation_mode = False
    
    def connect(self):
        BaseView.connect(self)
        if self.document.shown_account is None:
            return
        if self.document.shown_account.is_balance_sheet_account():
            self._shown_graph = self.balgraph
            self.view.show_line_graph()
        else:
            self._shown_graph = self.bargraph
            self.view.show_bar_graph()
        self._shown_graph.connect()
        self.view.refresh_totals()
        self.view.refresh_reconciliation_button()
    
    def disconnect(self):
        BaseView.disconnect(self)
        self.balgraph.disconnect()
        self.bargraph.disconnect()
    
    #--- Private
    def _refresh_totals(self):
        selected = len(self.document.selected_transactions)
        total = len(self.document.visible_entries)
        account = self.document.shown_account
        amounts = [t.amount_for_account(account, account.currency) for t in self.document.selected_transactions]
        total_increase = sum(a for a in amounts if a > 0)
        total_decrease = abs(sum(a for a in amounts if a < 0))
        total_increase_fmt = self.app.format_amount(total_increase)
        total_decrease_fmt = self.app.format_amount(total_decrease)
        msg = "{0} out of {1} selected. Increase: {2} Decrease: {3}"
        self.totals = msg.format(selected, total, total_increase_fmt, total_decrease_fmt)
    
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
        shown_account = self.document.shown_account
        return shown_account is not None and shown_account.is_balance_sheet_account()
    
    @property
    def reconciliation_mode(self):
        return self._reconciliation_mode
    
    #--- Event Handlers
    def account_must_be_shown(self):
        self.disconnect()
        if self.document.shown_account is not None:
            self.connect()
    
    def transactions_selected(self):
        self._refresh_totals()
        self.view.refresh_totals()
    
    # We also listen to transaction_changed because when we change transaction, selection doesn't
    # change and amounts might have been changed.
    transaction_changed = transactions_selected
