# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..exception import OperationAborted
from ..model.budget import BudgetSpawn
from .base import DocumentGUIObject

class MainWindow(DocumentGUIObject):
    def __init__(self, view, document, children):
        DocumentGUIObject.__init__(self, view, document)
        (self.nwview, self.pview, self.tview, self.aview, self.scview, self.bview,
            self.apanel, self.tpanel, self.mepanel, self.scpanel, self.bpanel) = children
        self._current_view = None
        self.show_balance_sheet()
    
    def connect(self):
        DocumentGUIObject.connect(self)
        self.view.refresh_date_range_selector()
    
    #--- Private
    def _change_current_view(self, view):
        if self._current_view is view:
            return False
        if self._current_view is not None:
            self._current_view.disconnect()
        self._current_view = view
        self._current_view.connect()
        return True
    
    def show_balance_sheet(self):
        if self._change_current_view(self.nwview):
            self.view.show_balance_sheet()
    
    def show_budget_table(self):
        if self._change_current_view(self.bview):
            self.view.show_budget_table()
    
    def show_entry_table(self):
        if self._change_current_view(self.aview):
            self.view.show_entry_table()
    
    def show_income_statement(self):
        if self._change_current_view(self.pview):
            self.view.show_income_statement()
    
    def show_schedule_table(self):
        if self._change_current_view(self.scview):
            self.view.show_schedule_table()
    
    def show_transaction_table(self):
        if self._change_current_view(self.tview):
            self.view.show_transaction_table()
    
    #--- Public
    def edit_item(self):
        try:
            if self._current_view in (self.nwview, self.pview):
                self.apanel.load()
            elif self._current_view in (self.aview, self.tview):
                editable_txns = [txn for txn in self.document.selected_transactions if not isinstance(txn, BudgetSpawn)]
                if len(editable_txns) > 1:
                    self.mepanel.load()
                elif len(editable_txns) == 1:
                    self.tpanel.load()
            elif self._current_view is self.scview:
                self.scpanel.load()
            elif self._current_view is self.bview:
                self.bpanel.load()
        except OperationAborted:
            pass
    
    def delete_item(self):
        if self._current_view in (self.nwview, self.pview, self.tview, self.aview, self.scview, self.bview):
            self._current_view.delete_item()
    
    def duplicate_item(self):
        if self._current_view in (self.tview, self.aview):
            self._current_view.duplicate_item()
    
    def make_schedule_from_selected(self):
        if self._current_view in (self.tview, self.aview):
            self.document.make_schedule_from_selected()
    
    def move_down(self):
        if self._current_view in (self.tview, self.aview):
            self._current_view.move_down()
    
    def move_up(self):
        if self._current_view in (self.tview, self.aview):
            self._current_view.move_up()
    
    def navigate_back(self):
        """When the entry table is shown, go back to the appropriate report"""
        assert self._current_view is self.aview # not supposed to be called outside the entry_table context
        if self.document.shown_account.is_balance_sheet_account():
            self.select_balance_sheet()
        else:
            self.select_income_statement()
    
    def new_item(self):
        try:
            if self._current_view in (self.nwview, self.pview, self.tview, self.aview):
                self._current_view.new_item()
            elif self._current_view is self.scview:
                self.scpanel.new()
            elif self._current_view is self.bview:
                self.bpanel.new()
        except OperationAborted as e:
            if e.message:
                self.view.show_message(e.message)
    
    def new_group(self):
        if self._current_view in (self.nwview, self.pview):
            self._current_view.new_group()
    
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
        self.document.filter_string = ''
        self.show_entry_table()
    
    def select_schedule_table(self):
        self.document.filter_string = ''
        self.show_schedule_table()
    
    def select_budget_table(self):
        self.document.filter_string = ''
        self.show_budget_table()
    
    def select_next_view(self):
        if self._current_view is self.nwview:
            self.select_income_statement()
        elif self._current_view is self.pview:
            self.select_transaction_table()
        elif self._current_view is self.tview:
            if self.document.shown_account is not None:
                self.select_entry_table()
            else:
                self.select_schedule_table()
        elif self._current_view is self.aview:
            self.select_schedule_table()
        elif self._current_view is self.scview:
            self.select_budget_table()
    
    def select_previous_view(self):
        if self._current_view is self.pview:
            self.select_balance_sheet()
        elif self._current_view is self.tview:
            self.select_income_statement()
        elif self._current_view is self.aview:
            self.select_transaction_table()
        elif self._current_view is self.scview:
            if self.document.shown_account is not None:
                self.select_entry_table()
            else:
                self.select_transaction_table()
        elif self._current_view is self.bview:
            self.select_schedule_table()
    
    def show_account(self):
        """Shows the currently selected account in the Account view.
        
        If a sheet is selected, the selected account will be shown.
        If the Transaction or Account view is selected, the related account (From, To, Transfer)
        of the selected transaction will be shown.
        """
        if self._current_view in (self.nwview, self.pview, self.tview, self.aview):
            self._current_view.show_account()
    
    #--- Event callbacks
    def _undo_stack_changed(self):
        self.view.refresh_undo_actions()
    
    account_added = _undo_stack_changed
    account_changed = _undo_stack_changed
    account_deleted = _undo_stack_changed
    
    def account_must_be_shown(self):
        if self.document.shown_account is not None:
            self.select_entry_table()
        elif self._current_view is self.aview:
            self.select_balance_sheet()
    
    def account_needs_reassignment(self):
        self.view.show_account_reassign_panel()
    
    budget_changed = _undo_stack_changed
    budget_deleted = _undo_stack_changed
    
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
    
    def document_changed(self):
        if self.document.shown_account is None and self._current_view is self.aview:
            self.select_balance_sheet()
        self._undo_stack_changed()
    
    def filter_applied(self):
        if self.document.filter_string and self._current_view not in (self.tview, self.aview):
            self.show_transaction_table()
    
    performed_undo_or_redo = _undo_stack_changed
    
    def reconciliation_changed(self):
        self.view.refresh_reconciliation_button()
    
    schedule_changed = _undo_stack_changed
    schedule_deleted = _undo_stack_changed
    
    def schedule_table_must_be_shown(self):
        self.select_schedule_table()
    
    def selected_must_be_edited(self):
        self.edit_item()
    
    transaction_changed = _undo_stack_changed
    transaction_deleted = _undo_stack_changed
    transaction_imported = _undo_stack_changed
