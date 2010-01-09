# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-01-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from .base import DocumentGUIObject

class TransactionView(DocumentGUIObject):
    def __init__(self, view, document, children):
        DocumentGUIObject.__init__(self, view, document)
        self.ttable, self.tfbar = children
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.ttable.connect()
        self.tfbar.connect()
        self.view.refresh_totals()
    
    def disconnect(self):
        DocumentGUIObject.disconnect(self)
        self.ttable.disconnect()
        self.tfbar.disconnect()
    
    #--- Public
    def delete_item(self):
        self.ttable.delete()
    
    def duplicate_item(self):
        self.ttable.delete_selected()
    
    def move_down(self):
        self.ttable.move_down()
    
    def move_up(self):
        self.ttable.move_up()
    
    def new_item(self):
        self.ttable.add()
    
    def show_account(self):
        self.ttable.show_from_account()
    
    #--- Properties
    @property
    def totals(self):
        shown = len(self.document.visible_transactions)
        total = self.document.visible_unfiltered_transaction_count
        msg = "Showing {0} out of {1}."
        return msg.format(shown, total)
    
    #--- Event Handlers
    def transaction_changed(self):
        self.view.refresh_totals()
    transaction_deleted = transaction_changed
    filter_applied = transaction_changed
