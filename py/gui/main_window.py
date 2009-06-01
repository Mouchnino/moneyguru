# Unit Name: moneyguru.gui.main_window
# Created By: Virgil Dupras
# Created On: 2008-07-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from .base import DocumentGUIObject

ENTRY_TABLE, BALANCE_SHEET, TRANSACTION_TABLE, INCOME_STATEMENT = range(4)
LINE_GRAPH, BAR_GRAPH = range(2)


class MainWindow(DocumentGUIObject):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        self.top = None
        self.bottom = None
        self.show_balance_sheet()
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.view.refresh_date_range_selector()
    
    #--- Private
    def show_balance_sheet(self):
        if self.top != BALANCE_SHEET:
            self.view.show_balance_sheet()
            self.top = BALANCE_SHEET
    
    def show_income_statement(self):
        if self.top != INCOME_STATEMENT:
            self.view.show_income_statement()
            self.top = INCOME_STATEMENT
    
    def show_bar_graph(self):
        if self.bottom != BAR_GRAPH:
            self.view.show_bar_graph()
            self.bottom = BAR_GRAPH
    
    def show_entry_table(self):
        if self.top != ENTRY_TABLE:
            self.view.show_entry_table()
            self.top = ENTRY_TABLE
    
    def show_line_graph(self):
        if self.bottom != LINE_GRAPH:
            self.view.show_line_graph()
            self.bottom = LINE_GRAPH
    
    def show_transaction_table(self):
        if self.top != TRANSACTION_TABLE:
            self.view.show_transaction_table()
            self.top = TRANSACTION_TABLE
    
    #--- Public
    def navigate_back(self):
        """When the entry table is shown, go back to the appropriate report"""
        assert self.top == ENTRY_TABLE # not supposed to be called outside the entry_table context
        if self.document.shown_account.is_balance_sheet_account():
            self.document.select_balance_sheet()
        else:
            self.document.select_income_statement()
    
    #--- Event callbacks
    def account_needs_reassignment(self):
        self.view.show_account_reassign_panel()
    
    def balance_sheet_selected(self):
        self.show_balance_sheet()
    
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
    
    def entry_table_selected(self):
        assert self.document.selected_account is not None
        self.show_entry_table()
        if self.document.selected_account.is_balance_sheet_account():
            self.show_line_graph()
        else:
            self.show_bar_graph()
    
    def income_statement_selected(self):
        self.show_income_statement()
    
    def reconciliation_changed(self):
        self.view.refresh_reconciliation_button()
    
    def transaction_table_selected(self):
        self.show_transaction_table()
    
    def undone(self):
        if self.document.selected_account is None and self.top == ENTRY_TABLE:
            self.document.select_balance_sheet()
    
    def redone(self):
        if self.document.selected_account is None and self.top == ENTRY_TABLE:
            self.document.select_balance_sheet()
    
