# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from .base import BaseView

class AccountView(BaseView):
    def __init__(self, view, document, children):
        self.etable, self.balgraph, self.bargraph, self.efbar = children
        # we count the graphs separately because the connect/disconnect rules for them are special
        BaseView.__init__(self, view, document, [self.etable, self.efbar])
        self._shown_graph = self.balgraph
    
    def connect(self):
        BaseView.connect(self)
        if self.document.shown_account.is_balance_sheet_account():
            self._shown_graph = self.balgraph
            self.view.show_line_graph()
        else:
            self._shown_graph = self.bargraph
            self.view.show_bar_graph()
        self._shown_graph.connect()
        self.view.refresh_totals()
    
    def disconnect(self):
        BaseView.disconnect(self)
        self.balgraph.disconnect()
        self.bargraph.disconnect()
    
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
    
    #--- Properties
    @property
    def totals(self):
        shown = len(self.document.visible_entries)
        total = self.document.visible_unfiltered_entry_count
        # XXX It's a little hackish to have _total_* computed on etable...
        increase = self.app.format_amount(self.etable._total_increase)
        decrease = self.app.format_amount(self.etable._total_decrease)
        msg = "Showing {shown} out of {total}. Total increase: {increase} Total decrease: {decrease}"
        return msg.format(shown=shown, total=total, increase=increase, decrease=decrease)
    
    #--- Event Handlers
    def account_must_be_shown(self):
        self.disconnect()
        if self.document.shown_account is not None:
            self.connect()
    
    def transaction_changed(self):
        self.view.refresh_totals()
    transaction_deleted = transaction_changed
    filter_applied = transaction_changed
    date_range_changed = transaction_changed
