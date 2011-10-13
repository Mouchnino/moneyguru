# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.notify import Repeater, Listener
from hscommon.util import first, minmax
from hscommon.trans import tr

from ..const import PaneType
from ..document import FilterType
from ..exception import OperationAborted
from ..model.budget import BudgetSpawn
from ..model.recurrence import Recurrence, RepeatType
from .base import MESSAGES_DOCUMENT_CHANGED

OPENED_PANES_PREFERENCE = 'OpenedPanes'
SELECTED_PANE_PREFERENCE = 'SelectedPane'

class ViewPane:
    def __init__(self, view, label, account=None):
        self.view = view
        self.label = label
        self.account = account
    
    def __repr__(self):
        return '<ViewPane {}>'.format(self.label)
    

class MainWindow(Repeater):
    #--- model -> view calls:
    # change_current_pane()
    # refresh_panes()
    # refresh_undo_actions()
    # show_custom_date_range_panel()
    # refresh_status_line()
    # show_message(message)
    # view_closed(index)
    
    def __init__(self, view, document):
        Repeater.__init__(self, document)
        self.view = view
        self.document = document
        self.app = document.app
        self._shown_account = None # the account that is shown when the entry table is selected
        self._selected_transactions = []
        self._explicitly_selected_transactions = []
        self._selected_schedules = []
        self._selected_budgets = []
        self._account2visibleentries = {}
        
        msgs = MESSAGES_DOCUMENT_CHANGED | {'filter_applied', 'date_range_changed'}
        self.bind_messages(msgs, self._invalidate_visible_entries)
    
    # After having created the main window, you *have* to call this method. This scheme is to allow
    # children to have reference to the main window.
    def set_children(self, children):
        (self.nwview, self.pview, self.tview, self.aview, self.scview, self.bview, self.ccview,
            self.glview, self.dpview, self.emptyview, self.apanel, self.tpanel, self.mepanel,
            self.scpanel, self.bpanel, self.cdrpanel, self.arpanel, self.expanel, self.alookup,
            self.completion_lookup, self.daterange_selector, self.view_options) = children
        self._restore_default_panes()
        for child in children:
            # Panels are not listeners
            if isinstance(child, Listener):
                child.connect()
    
    # We don't override disconnect because we never disconnect the main window anyway...
    #--- Private
    def _add_pane(self, pane):
        self.panes.append(pane)
        self.view.refresh_panes()
        self.current_pane_index = len(self.panes) - 1
    
    def _change_current_pane(self, pane):
        if self._current_pane is pane:
            return
        if self._current_pane is not None:
            self._current_pane.view.hide()
        self._current_pane = pane
        if pane.account is not None and pane.account is not self._shown_account:
            self._shown_account = pane.account
            self.notify('shown_account_changed')
        self._current_pane.view.show()
        self.view.change_current_pane()
        self.update_status_line()
    
    def _close_irrelevant_account_panes(self):
        indexes_to_close = []
        for index, pane in enumerate(self.panes):
            if pane.view.VIEW_TYPE == PaneType.Account and pane.account not in self.document.accounts:
                indexes_to_close.append(index)
        if self.current_pane_index in indexes_to_close:
            self.select_balance_sheet()
        for index in reversed(indexes_to_close):
            self.close_pane(index)
    
    def _create_pane(self, pane_type, account=None):
        if pane_type == PaneType.NetWorth:
            return ViewPane(self.nwview, tr("Net Worth"))
        elif pane_type == PaneType.Profit:
            return ViewPane(self.pview, tr("Profit & Loss"))
        elif pane_type == PaneType.Transaction:
            return ViewPane(self.tview, tr("Transactions"))
        elif pane_type == PaneType.Account:
            return ViewPane(self.aview, account.name, account)
        elif pane_type == PaneType.Schedule:
            return ViewPane(self.scview, tr("Schedules"))
        elif pane_type == PaneType.Budget:
            return ViewPane(self.bview, tr("Budgets"))
        elif pane_type == PaneType.Cashculator:
            return ViewPane(self.ccview, tr("Cashculator"))
        elif pane_type == PaneType.GeneralLedger:
            return ViewPane(self.glview, tr("General Ledger"))
        elif pane_type == PaneType.DocProps:
            return ViewPane(self.dpview, tr("Document Properties"))
        elif pane_type == PaneType.Empty:
            return ViewPane(self.emptyview, tr("New Tab"))
        else:
            raise ValueError("Cannot create pane of type {0}".format(pane_type))
    
    def _invalidate_visible_entries(self):
        self._account2visibleentries = {}
    
    def _restore_default_panes(self):
        pane_types = [PaneType.NetWorth, PaneType.Profit, PaneType.Transaction,
            PaneType.Schedule, PaneType.Budget]
        pane_data = list(zip(pane_types, [None] * len(pane_types)))
        self._set_panes(pane_data)
    
    def _restore_opened_panes(self):
        stored_panes = self.document.get_default(OPENED_PANES_PREFERENCE)
        if not stored_panes:
            return
        pane_data = []
        for data in stored_panes:
            pane_type = data['pane_type']
            account_name = str(data.get('account_name', '')) # str() because the value might be an int
            account = self.document.accounts.find(account_name)
            if pane_type == PaneType.Account and account is None:
                continue
            pane_data.append((pane_type, account))
        if pane_data:
            self._set_panes(pane_data)
            selected_pane_index = self.document.get_default(SELECTED_PANE_PREFERENCE)
            if selected_pane_index is not None:
                self.current_pane_index = selected_pane_index
    
    def _save_preferences(self):
        opened_panes = []
        for pane in self.panes:
            data = {}
            data['pane_type'] = pane.view.VIEW_TYPE
            if pane.account is not None:
                data['account_name'] = pane.account.name
            opened_panes.append(data)
        self.document.set_default(OPENED_PANES_PREFERENCE, opened_panes)
        self.document.set_default(SELECTED_PANE_PREFERENCE, self._current_pane_index)
    
    def _set_panes(self, pane_data):
        # Replace opened panes with new panes from `pane_data`, which is a [(pane_type, account)]
        self._current_pane = None
        self._current_pane_index = -1
        self.panes = []
        for pane_type, account in pane_data:
            try:
                self.panes.append(self._create_pane(pane_type, account=account))
            except ValueError:
                self.panes.append(self._create_pane(PaneType.NetWorth))
        self.view.refresh_panes()
        self.current_pane_index = 0
    
    def _visible_entries_for_account(self, account):
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
        return entries
    
    #--- Public
    def close_pane(self, index):
        if self.pane_count == 1: # don't close the last pane
            return
        if index == self.current_pane_index:
            # we must select another pane before we close it.
            if index == len(self.panes)-1:
                self.current_pane_index -= 1
            else:
                self.current_pane_index += 1
        del self.panes[index]
        self.view.view_closed(index)
        # The index of the current view might have changed
        newindex = self.panes.index(self._current_pane)
        if newindex != self._current_pane_index:
            self._current_pane_index = newindex
            self.view.change_current_pane()
    
    def delete_item(self):
        self._current_pane.view.delete_item()
    
    def duplicate_item(self):
        current_view = self._current_pane.view
        if current_view in (self.tview, self.aview):
            current_view.duplicate_item()
    
    def edit_item(self):
        try:
            current_view = self._current_pane.view
            if current_view in (self.nwview, self.pview):
                current_view.edit_item()
            elif current_view in (self.aview, self.tview, self.glview):
                editable_txns = [txn for txn in self.selected_transactions if not isinstance(txn, BudgetSpawn)]
                if len(editable_txns) > 1:
                    self.mepanel.load()
                elif len(editable_txns) == 1:
                    self.tpanel.load()
            elif current_view is self.scview:
                self.scpanel.load()
            elif current_view is self.bview:
                self.bpanel.load()
        except OperationAborted:
            pass
    
    def export(self):
        self.expanel.load()
    
    def jump_to_account(self):
        self.alookup.show()
    
    def make_schedule_from_selected(self):
        current_view = self._current_pane.view
        if current_view in (self.tview, self.aview):
            if not self.selected_transactions:
                return
            # There's no test case for this, but select_schedule_table() must happen before 
            # new_schedule_from_transaction() or else the sctable's selection upon view switch will
            # overwrite our selection.
            self.select_schedule_table()
            ref = self.selected_transactions[0]
            schedule = Recurrence(ref.replicate(), RepeatType.Monthly, 1)
            schedule.delete_at(ref.date)
            self.selected_schedules = [schedule]
            self.edit_item()
    
    def move_down(self):
        current_view = self._current_pane.view
        if current_view in (self.tview, self.aview):
            current_view.move_down()
    
    def move_up(self):
        current_view = self._current_pane.view
        if current_view in (self.tview, self.aview):
            current_view.move_up()
    
    def move_pane(self, pane_index, dest_index):
        pane = self.panes[pane_index]
        del self.panes[pane_index]
        self.panes.insert(dest_index, pane)
        self.current_pane_index = self.panes.index(self._current_pane)
        self.view.refresh_panes()
    
    def navigate_back(self):
        """When the entry table is shown, go back to the appropriate report"""
        assert self._current_pane.view is self.aview # not supposed to be called outside the entry_table context
        if self.shown_account.is_balance_sheet_account():
            self.select_balance_sheet()
        else:
            self.select_income_statement()
    
    def new_item(self):
        try:
            current_view = self._current_pane.view
            if current_view in (self.nwview, self.pview, self.tview, self.aview, self.glview):
                current_view.new_item()
            elif current_view is self.scview:
                self.scpanel.new()
            elif current_view is self.bview:
                self.bpanel.new()
        except OperationAborted as e:
            if e.message:
                self.view.show_message(e.message)
    
    def new_group(self):
        current_view = self._current_pane.view
        if current_view in (self.nwview, self.pview):
            current_view.new_group()
    
    def new_tab(self):
        self.panes.append(self._create_pane(PaneType.Empty))
        self.view.refresh_panes()
        self.current_pane_index = len(self.panes) - 1
    
    def pane_label(self, index):
        pane = self.panes[index]
        return pane.label
    
    def pane_type(self, index):
        pane = self.panes[index]
        return pane.view.VIEW_TYPE
    
    def select_pane_of_type(self, pane_type, clear_filter=True):
        if clear_filter:
            self.document.filter_string = ''
        index = first(i for i, p in enumerate(self.panes) if p.view.VIEW_TYPE == pane_type)
        if index is None:
            self._add_pane(self._create_pane(pane_type))
        else:
            self.current_pane_index = index
    
    def select_balance_sheet(self):
        self.select_pane_of_type(PaneType.NetWorth)
    
    def select_income_statement(self):
        self.select_pane_of_type(PaneType.Profit)
    
    def select_transaction_table(self):
        self.select_pane_of_type(PaneType.Transaction)
    
    def select_entry_table(self):
        if self.shown_account is None:
            return
        self.select_pane_of_type(PaneType.Account)
    
    def select_schedule_table(self):
        self.select_pane_of_type(PaneType.Schedule)
    
    def select_budget_table(self):
        self.select_pane_of_type(PaneType.Budget)
    
    def select_next_view(self):
        if self.current_pane_index == len(self.panes) - 1:
            return
        self.current_pane_index += 1
    
    def select_previous_view(self):
        if self.current_pane_index == 0:
            return
        self.current_pane_index -= 1
    
    def set_current_pane_type(self, pane_type):
        index = self.current_pane_index
        pane = self._create_pane(pane_type)
        self.panes[index] = pane
        self.view.refresh_panes()
        self._change_current_pane(pane)
    
    def show_account(self):
        """Shows the currently selected account in the Account view.
        
        If a sheet is selected, the selected account will be shown.
        If the Transaction or Account view is selected, the related account (From, To, Transfer)
        of the selected transaction will be shown.
        """
        current_view = self._current_pane.view
        if current_view in (self.nwview, self.pview, self.tview, self.aview):
            current_view.show_account()
    
    def show_message(self, message):
        self.view.show_message(message)
    
    def update_status_line(self):
        self.view.refresh_status_line()
    
    def visible_entries_for_account(self, account):
        if account is None:
            return []
        if account not in self._account2visibleentries:
            self._account2visibleentries[account] = self._visible_entries_for_account(account)
        return self._account2visibleentries[account]
    
    #--- Properties
    @property
    def current_pane_index(self):
        return self._current_pane_index
    
    @current_pane_index.setter
    def current_pane_index(self, value):
        if value == self._current_pane_index:
            return
        self.document.stop_edition()
        value = minmax(value, 0, len(self.panes)-1)
        pane = self.panes[value]
        self._current_pane_index = value
        self._change_current_pane(pane)
    
    @property
    def pane_count(self):
        return len(self.panes)
    
    @property
    def selected_schedules(self):
        return self._selected_schedules
    
    @selected_schedules.setter
    def selected_schedules(self, schedules):
        self._selected_schedules = schedules
    
    @property
    def selected_budgets(self):
        return self._selected_budgets
    
    @selected_budgets.setter
    def selected_budgets(self, budgets):
        self._selected_budgets = budgets
    
    @property
    def selected_transactions(self):
        return self._selected_transactions
    
    @selected_transactions.setter
    def selected_transactions(self, transactions):
        self._selected_transactions = transactions
        self.notify('transactions_selected')
    
    @property
    def explicitly_selected_transactions(self):
        return self._explicitly_selected_transactions
    
    @explicitly_selected_transactions.setter
    def explicitly_selected_transactions(self, transactions):
        self._explicitly_selected_transactions = transactions
        self.selected_transactions = transactions
    
    @property
    def shown_account(self):
        return self._shown_account
    
    @shown_account.setter
    def shown_account(self, account):
        changed = account is not self._shown_account
        self._shown_account = account
        if changed:
            self.notify('shown_account_changed')
        if account is not None:
            # Try to find a suitable pane, or add a new one
            index = first(i for i, p in enumerate(self.panes) if p.account is account)
            if index is None:
                self._add_pane(self._create_pane(PaneType.Account, account))
            else:
                self.current_pane_index = index
        elif self._current_pane.view is self.aview:
            self.select_balance_sheet()
    
    @property
    def status_line(self):
        return self._current_pane.view.status_line
    
    #--- Event callbacks
    def _undo_stack_changed(self):
        self.view.refresh_undo_actions()
    
    account_added = _undo_stack_changed
    
    def account_changed(self):
        self._undo_stack_changed()
        tochange = first(p for p in self.panes if p.account is not None and p.account.name != p.label)
        if tochange is not None:
            tochange.label = tochange.account.name
            self.view.refresh_panes()
    
    account_deleted = _undo_stack_changed
    budget_changed = _undo_stack_changed
    budget_deleted = _undo_stack_changed
    
    def custom_date_range_selected(self):
        self.cdrpanel.load()
    
    def document_changed(self):
        self._close_irrelevant_account_panes()
        self._undo_stack_changed()
    
    def document_will_close(self):
        self._save_preferences()
    
    def document_restoring_preferences(self):
        self._restore_opened_panes()
    
    def filter_applied(self):
        if self.document.filter_string and self._current_pane.view not in (self.tview, self.aview):
            self.select_pane_of_type(PaneType.Transaction, clear_filter=False)
    
    def performed_undo_or_redo(self):
        self._close_irrelevant_account_panes()
        self.view.refresh_undo_actions()
    
    schedule_changed = _undo_stack_changed
    schedule_deleted = _undo_stack_changed
    transaction_changed = _undo_stack_changed
    
    def transaction_deleted(self):
        self._explicitly_selected_transactions = []
        self._selected_transactions = []
        self._close_irrelevant_account_panes() # after an auto-clean
        self.view.refresh_undo_actions()
    
    transaction_imported = _undo_stack_changed
