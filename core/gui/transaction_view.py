# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from ..const import ViewType
from ..model.amount import convert_amount
from .base import BaseView

class TransactionView(BaseView):
    VIEW_TYPE = ViewType.Transaction
    
    def __init__(self, view, mainwindow, children):
        BaseView.__init__(self, view, mainwindow.document, children)
        self.ttable, self.tfbar = children
        self.totals = ''
    
    def connect(self):
        BaseView.connect(self)
        self.view.refresh_totals()
    
    #--- Private
    def _refresh_totals(self):
        selected = len(self.document.selected_transactions)
        total = len(self.document.visible_transactions)
        currency = self.app.default_currency
        total_amount = sum(convert_amount(t.amount, currency, t.date) for t in self.document.selected_transactions)
        total_amount_fmt = self.app.format_amount(total_amount)
        msg = "{0} out of {1} selected. Amount: {2}"
        self.totals = msg.format(selected, total, total_amount_fmt)
    
    #--- Public
    def delete_item(self):
        self.ttable.delete()
    
    def duplicate_item(self):
        self.ttable.duplicate_selected()
    
    def move_down(self):
        self.ttable.move_down()
    
    def move_up(self):
        self.ttable.move_up()
    
    def new_item(self):
        self.ttable.add()
    
    def show_account(self):
        self.ttable.show_from_account()
    
    #--- Event Handlers
    def transactions_selected(self):
        self._refresh_totals()
        self.view.refresh_totals()
    
    # We also listen to transaction_changed because when we change transaction, selection doesn't
    # change and amounts might have been changed.
    transaction_changed = transactions_selected
