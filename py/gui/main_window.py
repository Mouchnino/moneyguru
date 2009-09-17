# Created By: Virgil Dupras
# Created On: 2008-07-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..exception import OperationAborted
from ..model.budget import BudgetSpawn
from .base import DocumentGUIObject

LINE_GRAPH, BAR_GRAPH = range(2)

class MainWindow(DocumentGUIObject):
    def __init__(self, view, document, children):
        DocumentGUIObject.__init__(self, view, document)
        (self.bsheet, self.istatement, self.ttable, self.etable, self.sctable, self.btable,
            self.apanel, self.tpanel, self.mepanel, self.scpanel, self.bpanel) = children
        self.top = None
        self.bottom = None
        self.show_balance_sheet()
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.view.refresh_date_range_selector()
    
    #--- Private
    def show_balance_sheet(self):
        if self.top is not self.bsheet:
            self.view.show_balance_sheet()
            self.top = self.bsheet
    
    def show_bar_graph(self):
        if self.bottom != BAR_GRAPH:
            self.view.show_bar_graph()
            self.bottom = BAR_GRAPH
    
    def show_budget_table(self):
        if self.top is not self.btable:
            self.view.show_budget_table()
            self.top = self.btable
    
    def show_entry_table(self):
        if self.top is not self.etable:
            self.view.show_entry_table()
            self.top = self.etable
    
    def show_income_statement(self):
        if self.top is not self.istatement:
            self.view.show_income_statement()
            self.top = self.istatement
    
    def show_line_graph(self):
        if self.bottom != LINE_GRAPH:
            self.view.show_line_graph()
            self.bottom = LINE_GRAPH
    
    def show_schedule_table(self):
        if self.top is not self.sctable:
            self.view.show_schedule_table()
            self.top = self.sctable
    
    def show_transaction_table(self):
        if self.top is not self.ttable:
            self.view.show_transaction_table()
            self.top = self.ttable
    
    #--- Public
    def edit_item(self):
        try:
            if self.top in (self.bsheet, self.istatement):
                self.apanel.load()
            elif self.top in (self.etable, self.ttable):
                editable_txns = [txn for txn in self.document.selected_transactions if not isinstance(txn, BudgetSpawn)]
                if len(editable_txns) > 1:
                    self.mepanel.load()
                elif len(editable_txns) == 1:
                    self.tpanel.load()
            elif self.top is self.sctable:
                self.scpanel.load()
            elif self.top is self.btable:
                self.bpanel.load()
        except OperationAborted:
            pass
    
    def delete_item(self):
        if self.top in (self.bsheet, self.istatement, self.ttable, self.etable, self.sctable, self.btable):
            self.top.delete()
    
    def make_schedule_from_selected(self):
        if self.top in (self.ttable, self.etable):
            self.document.make_schedule_from_selected()
    
    def move_down(self):
        if self.top in (self.ttable, self.etable):
            self.top.move_down()
    
    def move_up(self):
        if self.top in (self.ttable, self.etable):
            self.top.move_up()
    
    def navigate_back(self):
        """When the entry table is shown, go back to the appropriate report"""
        assert self.top is self.etable # not supposed to be called outside the entry_table context
        if self.document.shown_account.is_balance_sheet_account():
            self.select_balance_sheet()
        else:
            self.select_income_statement()
    
    def new_item(self):
        if self.top in (self.bsheet, self.istatement):
            self.top.add_account()
        elif self.top in (self.etable, self.ttable):
            self.top.add()
        elif self.top is self.sctable:
            self.scpanel.new()
        elif self.top is self.btable:
            self.bpanel.new()
    
    def new_group(self):
        if self.top in (self.bsheet, self.istatement):
            self.top.add_account_group()
    
    def select_balance_sheet(self):
        self.document.filter_string = ''
        self.show_balance_sheet()
    
    def select_income_statement(self):
        self.document.filter_string = ''
        self.show_income_statement()
    
    def select_transaction_table(self):
        self.document.filter_string = ''
        self.show_transaction_table()
    
    def select_entry_table(self):
        if self.document.shown_account is None:
            return
        self.document.select_account(self.document.shown_account)
        self.document.filter_string = ''
        self.show_entry_table()
        if self.document.shown_account.is_balance_sheet_account():
            self.show_line_graph()
        else:
            self.show_bar_graph()
    
    def select_schedule_table(self):
        self.document.filter_string = ''
        self.show_schedule_table()
    
    def select_budget_table(self):
        self.document.filter_string = ''
        self.show_budget_table()
    
    def select_next_view(self):
        if self.top is self.bsheet:
            self.select_income_statement()
        elif self.top is self.istatement:
            self.select_transaction_table()
        elif self.top is self.ttable:
            if self.document.shown_account is not None:
                self.select_entry_table()
            else:
                self.select_schedule_table()
        elif self.top is self.etable:
            self.select_schedule_table()
        elif self.top is self.sctable:
            self.select_budget_table()
    
    def select_previous_view(self):
        if self.top is self.istatement:
            self.select_balance_sheet()
        elif self.top is self.ttable:
            self.select_income_statement()
        elif self.top is self.etable:
            self.select_transaction_table()
        elif self.top is self.sctable:
            if self.document.shown_account is not None:
                self.select_entry_table()
            else:
                self.select_transaction_table()
        elif self.top is self.btable:
            self.select_schedule_table()
    
    #--- Event callbacks
    def account_must_be_shown(self):
        self.select_entry_table()
    
    def account_needs_reassignment(self):
        self.view.show_account_reassign_panel()
    
    def custom_date_range_selected(self):
        self.view.show_custom_date_range_panel()
    
    def date_range_will_change(self):
        self._old_date_range = self.document.date_range
    
    def date_range_changed(self):
        self.view.refresh_date_range_selector()
        old = self._old_date_range
        new = self.document.date_range
        if type(new) == type(old):
            if new.start > old.start:
                self.view.animate_date_range_forward()
            else:
                self.view.animate_date_range_backward()
    
    def filter_applied(self):
        if self.document.filter_string and self.top not in (self.ttable, self.etable):
            self.show_transaction_table()
    
    def reconciliation_changed(self):
        self.view.refresh_reconciliation_button()
    
    def schedule_table_must_be_shown(self):
        self.select_schedule_table()
    
    def selected_must_be_edited(self):
        self.edit_item()
    
    def undone(self):
        if self.document.selected_account is None and self.top is self.etable:
            self.select_balance_sheet()
    
    def redone(self):
        if self.document.selected_account is None and self.top is self.etable:
            self.select_balance_sheet()
    
