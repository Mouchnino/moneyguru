# Unit Name: moneyguru.document
# Created By: Virgil Dupras
# Created On: 2007-10-25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

import datetime
import logging
import xml.etree.cElementTree as ET
from itertools import dropwhile

from hsutil.currency import Currency
from hsutil.notify import Broadcaster, Listener
from hsutil.misc import nonone, flatten, allsame

from ..const import (NOEDIT, REPEAT_NEVER, UNRECONCILIATION_CONTINUE,
    UNRECONCILIATION_CONTINUE_DONT_UNRECONCILE)
from ..exception import FileFormatError, OperationAborted
from ..loader import csv_, qif, ofx, native
from ..model.account import (Account, Group, AccountList, GroupList, INCOME, EXPENSE, LIABILITY)
from ..model.amount import Amount
from ..model.date import (MonthRange, QuarterRange, YearRange, YearToDateRange, RunningYearRange,
    CustomDateRange, format_date)
from ..model.oven import Oven
from ..model.recurrence import Recurrence, Spawn
from ..model.transaction import Transaction, Entry
from ..model.transaction_list import TransactionList
from .undo import Undoer, Action

SELECTED_DATE_RANGE_PREFERENCE = 'SelectedDateRange'
SELECTED_DATE_RANGE_START_PREFERENCE = 'SelectedDateRangeStart'
SELECTED_DATE_RANGE_END_PREFERENCE = 'SelectedDateRangeEnd'
EXCLUDED_ACCOUNTS_PREFERENCE = 'ExcludedAccounts'

DATE_RANGE_MONTH = 'month'
DATE_RANGE_QUARTER = 'quarter'
DATE_RANGE_YEAR = 'year'
DATE_RANGE_YTD = 'ytd'
DATE_RANGE_RUNNING_YEAR = 'running_year'
DATE_RANGE_CUSTOM = 'custom'

DATE_FORMAT_FOR_PREFERENCES = '%d/%m/%Y'

FILTER_UNASSIGNED = object()
FILTER_INCOME = object() # in etable, the filter is for increase
FILTER_EXPENSE = object() # in etable, the filter is for decrease
FILTER_TRANSFER = object()
FILTER_RECONCILED = object()
FILTER_NOTRECONCILED = object()

class Document(Broadcaster, Listener):
    def __init__(self, view, app):
        Broadcaster.__init__(self)
        Listener.__init__(self, app)
        self.app = app
        self.view = view
        self.accounts = AccountList(self.app.default_currency)
        self.excluded_accounts = set()
        self.groups = GroupList()
        self.transactions = TransactionList()
        # I did not manage to create a repeatable test for it, but self._scheduled has to be ordered
        # because the order in which the spawns are created must stay the same
        self._scheduled = []
        self.oven = Oven(self.accounts, self.transactions, self._scheduled)
        self._undoer = Undoer(self.accounts, self.groups, self.transactions, self._scheduled)
        self._date_range = YearRange(datetime.date.today())
        self._in_reconciliation_mode = False
        self._selected_account = None
        self._shown_account = None # the account that is shown when the entry table is selected
        self._selected_transactions = []
        self._explicitly_selected_transactions = []
        self._selected_splits = []
        self._filter_string = ''
        self._filter_type = None
        self._visible_transactions = None
        self._visible_unfiltered_transaction_count = 0
        self._visible_entries = None
        self._visible_unfiltered_entry_count = 0
        self._restore_preferences()
    
    #--- Private
    def _adjust_date_range(self, new_date):
        if not self.date_range.can_navigate:
            return False
        new_date_range = self.date_range.around(new_date)
        if new_date_range == self.date_range:
            return False
        # We have to manually set the date range and send notifications because ENTRY_CHANGED
        # must happen between DATE_RANGE_WILL_CHANGE and DATE_RANGE_CHANGED
        # Note that there are no tests for this, as the current doesn't really allow to test
        # for the order of the gui calls (and this exception doesn't mean that we should).
        self.notify('date_range_will_change')
        self._date_range = new_date_range
        self.oven.continue_cooking(new_date_range.end)
        self.notify('entry_changed')
        self.notify('date_range_changed')
        return True
    
    def _change_transaction(self, transaction, date=NOEDIT, description=NOEDIT, payee=NOEDIT, 
                            checkno=NOEDIT, from_=NOEDIT, to=NOEDIT, amount=NOEDIT, currency=NOEDIT,
                            force_local_scope=False):
        date_changed = date is not NOEDIT and date != transaction.date
        transaction.change(date=date, description=description, payee=payee, checkno=checkno,
                           from_=from_, to=to, amount=amount, currency=currency)
        if isinstance(transaction, Spawn):
            global_scope = False if force_local_scope else self.view.query_for_schedule_scope()
            if global_scope:
                transaction.recurrence.change_globally(transaction)
            else:
                transaction.recurrence.add_exception(transaction)
        else:
            if transaction not in self.transactions:
                self.transactions.add(transaction)
            elif date_changed:
                self.transactions.move_last(transaction)
    
    def _clean_empty_categories(self):
        for account in list(self.accounts.auto_created):
            if account is self.selected_account:
                continue
            if not account.entries:
                self.accounts.remove(account)
    
    def _commit_reconciliation(self):
        # process pending reconciliation
        splits = flatten(t.splits for t in self.oven.transactions)
        splits = [split for split in splits if split.reconciliation_pending]
        for split in splits:
            split.reconciled = True
            split.reconciliation_pending = False
        spawns = set(s.transaction for s in splits if isinstance(s.transaction, Spawn))
        for spawn in spawns:
            spawn.recurrence.delete(spawn)
            self.transactions.add(spawn.replicate())
        if spawns:
            self._cook(from_date=min(spawn.date for spawn in spawns))
    
    def _cook(self, from_date=None):
        self.oven.cook(from_date=from_date, until_date=self.date_range.end)
        self._visible_transactions = None
        self._visible_entries = None
    
    def _delete_account(self, account, reassign_to=None):
        action = Action('Remove account')
        action.delete_account(account)
        self._undoer.record(action)
        self.transactions.reassign_account(account, reassign_to)
        self.accounts.remove(account)
        self._cook()
        self.notify('account_deleted')
    
    def _get_action_from_changed_transactions(self, transactions):
        if len(transactions) == 1 and not isinstance(transactions[0], Spawn) and transactions[0] not in self.transactions:
            action = Action('Add transaction')
            action.added_transactions.add(transactions[0])
        else:
            action = Action('Change transaction')
            action.change_transactions(transactions)
        return action
    
    def _get_splits_to_unreconcile(self, changed_splits):
        """Return a list of all the splits affected by the change in 'changed_splits'
        """
        # The goal is to unreconcile every *reconciled* split in 'splits' *as well as* the splits
        # following it *but only in the same account*.
        splits = set([s for s in changed_splits if s.reconciled])
        if not splits:
            return []
        allsplits = flatten(t.splits for t in self.transactions)
        found_accounts = set()
        result = []
        for split in allsplits:
            if split in splits:
                found_accounts.add(split.account)
            if split.reconciled and split.account in found_accounts:
                result.append(split)
        return result
    
    def _parse_search_query(self, query_string):
        # Returns a dict of query arguments
        query_string = query_string.lower()
        if query_string.startswith('account:'):
            accounts = query_string[len('account:'):].split(',')
            accounts = set([s.strip().lower() for s in accounts])
            return {'account': accounts}
        if query_string.startswith('group:'):
            groups = query_string[len('group:'):].split(',')
            groups = set([s.strip().lower() for s in groups])
            return {'group': groups}
        query = {'all': query_string}
        try:
            query['amount'] = abs(self.app.parse_amount(query_string))
        except ValueError:
            pass
        return query
    
    def _perform_action(self, prepare_func, perform_func):
        # prepare_func must return an Action
        action = prepare_func()
        if self.app.dont_unreconcile:
            to_unreconcile = set()
        else:
            to_unreconcile = self._get_splits_to_unreconcile(action.will_unreconcile)
        result = UNRECONCILIATION_CONTINUE
        if to_unreconcile:
            result = self.view.confirm_unreconciliation(len(to_unreconcile))
        if result not in (UNRECONCILIATION_CONTINUE, UNRECONCILIATION_CONTINUE_DONT_UNRECONCILE):
            return # Abort
        action.change_splits(to_unreconcile)
        self._undoer.record(action)
        if result != UNRECONCILIATION_CONTINUE_DONT_UNRECONCILE:
            for split in to_unreconcile:
                split.reconciled = False
        perform_func()
    
    def _restore_preferences(self):
        start_date = self.app.get_default(SELECTED_DATE_RANGE_START_PREFERENCE)
        if start_date:
            start_date = datetime.datetime.strptime(start_date, DATE_FORMAT_FOR_PREFERENCES).date()
        end_date = self.app.get_default(SELECTED_DATE_RANGE_END_PREFERENCE)
        if end_date:
            end_date = datetime.datetime.strptime(end_date, DATE_FORMAT_FOR_PREFERENCES).date()
        selected_range = self.app.get_default(SELECTED_DATE_RANGE_PREFERENCE)
        if selected_range == DATE_RANGE_MONTH:
            self.select_month_range(start_date)
        elif selected_range == DATE_RANGE_QUARTER:
            self.select_quarter_range(start_date)
        elif selected_range == DATE_RANGE_YEAR:
            self.select_year_range(start_date)
        elif selected_range == DATE_RANGE_YTD:
            self.select_year_to_date_range()
        elif selected_range == DATE_RANGE_RUNNING_YEAR:
            self.select_running_year_range()
        elif selected_range == DATE_RANGE_CUSTOM and start_date and end_date:
            self.select_custom_date_range(start_date, end_date)
    
    def _restore_preferences_after_load(self):
        # some preference need the file loaded before attempting a restore
        excluded_account_names = set(nonone(self.app.get_default(EXCLUDED_ACCOUNTS_PREFERENCE), []))
        self.excluded_accounts = set(a for a in self.accounts if a.name in excluded_account_names)
    
    def _save_preferences(self):
        dr = self.date_range
        selected_range = DATE_RANGE_MONTH
        if isinstance(dr, QuarterRange):
            selected_range = DATE_RANGE_QUARTER
        elif isinstance(dr, YearRange):
            selected_range = DATE_RANGE_YEAR
        elif isinstance(dr, YearToDateRange):
            selected_range = DATE_RANGE_YTD
        elif isinstance(dr, RunningYearRange):
            selected_range = DATE_RANGE_RUNNING_YEAR
        elif isinstance(dr, CustomDateRange):
            selected_range = DATE_RANGE_CUSTOM
        self.app.set_default(SELECTED_DATE_RANGE_PREFERENCE, selected_range)
        str_start_date = dr.start.strftime(DATE_FORMAT_FOR_PREFERENCES)
        self.app.set_default(SELECTED_DATE_RANGE_START_PREFERENCE, str_start_date)
        str_end_date = dr.end.strftime(DATE_FORMAT_FOR_PREFERENCES)
        self.app.set_default(SELECTED_DATE_RANGE_END_PREFERENCE, str_end_date)
        excluded_account_names = [a.name for a in self.excluded_accounts]
        self.app.set_default(EXCLUDED_ACCOUNTS_PREFERENCE, excluded_account_names)
    
    def _set_visible_entries(self):
        account = self.selected_account
        if account is None:
            self._visible_entries = []
            self._visible_unfiltered_entry_count = 0
            return
        date_range = self.date_range
        entries = [e for e in account.entries if e.date in date_range]
        self._visible_unfiltered_entry_count = len(entries)
        if self.filter_type is FILTER_UNASSIGNED:
            entries = [e for e in entries if not e.transfer]
        elif (self.filter_type is FILTER_INCOME) or (self.filter_type is FILTER_EXPENSE):
            if account.is_credit_account():
                want_positive = self.filter_type is FILTER_EXPENSE
            else:
                want_positive = self.filter_type is FILTER_INCOME
            if want_positive:
                entries = [e for e in entries if e.amount > 0]
            else:
                entries = [e for e in entries if e.amount < 0]
        elif self.filter_type is FILTER_TRANSFER:
            entries = [e for e in entries if any(s.account is not None and s.account.is_balance_sheet_account() for s in e.splits)]
        elif self.filter_type is FILTER_RECONCILED:
            entries = [e for e in entries if e.reconciled]
        elif self.filter_type is FILTER_NOTRECONCILED:
            entries = [e for e in entries if not e.reconciled]
        self._visible_entries = entries
    
    def _set_visible_transactions(self):
        date_range = self.date_range
        txns = [t for t in self.oven.transactions if t.date in date_range]
        self._visible_unfiltered_transaction_count = len(txns)
        query_string = self.filter_string
        filter_type = self.filter_type
        if not query_string and filter_type is None:
            self._visible_transactions = txns
            return
        if query_string:
            query = self._parse_search_query(query_string)
            txns = [t for t in txns if t.matches(query)]
        if filter_type is FILTER_UNASSIGNED:
            txns = [t for t in txns if t.has_unassigned_split]
        elif filter_type is FILTER_INCOME:
            txns = [t for t in txns if any(getattr(s.account, 'type', '') == INCOME for s in t.splits)]
        elif filter_type is FILTER_EXPENSE:
            txns = [t for t in txns if any(getattr(s.account, 'type', '') == EXPENSE for s in t.splits)]
        elif filter_type is FILTER_TRANSFER:
            def is_transfer(t):
                return len([s for s in t.splits if s.account is not None and s.account.is_balance_sheet_account()]) >= 2
            txns = filter(is_transfer, txns)
        elif filter_type is FILTER_RECONCILED:
            txns = [t for t in txns if any(s.reconciled for s in t.splits)]
        elif filter_type is FILTER_NOTRECONCILED:
            txns = [t for t in txns if all(not s.reconciled for s in t.splits)]
        self._visible_transactions = txns
    
    def _update_schedule(self, txn, recurrence):
        """Update the schedule of txn if needed. if a new recurrence is defined, create a schedule
        for it, and if txn is a spawn and the current change is of global scope, stop the current
        recurrence and start a new one.
        """
        if isinstance(txn, Spawn):
            if recurrence != txn.recurrence:
                txn.recurrence.stop_at(txn)
                if recurrence is not None:
                    txn.recurrence.delete(txn)
                    recurrence = Recurrence(txn.replicate(), recurrence.repeat_type, recurrence.repeat_every, include_first=True)
                    self._scheduled.append(recurrence)
        elif recurrence is not None:
            self._scheduled.append(recurrence)
    
    #--- Account
    def change_account(self, account, name=NOEDIT, type=NOEDIT, currency=NOEDIT, group=NOEDIT,
                       budget=NOEDIT, budget_target=NOEDIT):
        assert account is not None
        action = Action('Change account')
        action.change_accounts([account])
        if name is not NOEDIT:
            self.accounts.set_account_name(account, name)
        if type is not NOEDIT:
            account.type = type
        if currency is not NOEDIT:
            account.currency = currency
        if group is not NOEDIT:
            account.group = group
        if budget is not NOEDIT:
            account.budget = budget
        if budget_target is not NOEDIT:
            account.budget_target = budget_target
        self._undoer.record(action)
        self._cook()
        self.notify('account_changed')
    
    def delete_selected_account(self):
        account = self.selected_account
        if account.entries:
            self.notify('account_needs_reassignment')
        else:
            self._delete_account(account)
    
    def new_account(self, type, group):
        name = self.accounts.new_name('New account')
        account = Account(name, self.app.default_currency, type)
        account.group = group
        action = Action('Add account')
        action.added_accounts.add(account)
        self._undoer.record(action)
        self.accounts.add(account)
        self.notify('account_added')
        return account
    
    def reassign_and_delete_selected_account(self, reassign_to):
        account = self.selected_account
        self._delete_account(account, reassign_to=reassign_to)
    
    def toggle_accounts_exclusion(self, accounts):
        if accounts <= self.excluded_accounts: # all accounts are already excluded. re-include all
            self.excluded_accounts -= accounts
        else:
            self.excluded_accounts |= accounts
        self.notify('accounts_excluded')
    
    #--- Group
    def change_group(self, group, name=NOEDIT):
        assert group is not None
        action = Action('Change group')
        action.change_groups([group])
        if name is not NOEDIT:
            self.groups.set_group_name(group, name)
        self._undoer.record(action)
        self.notify('account_changed')
    
    def collapse_group(self, group):
        group.expanded = False
        self.notify('group_expanded_state_changed')
    
    def delete_group(self, group):
        accounts = [a for a in self.accounts if a.group is group]
        action = Action('Remove group')
        action.deleted_groups.add(group)
        action.change_accounts(accounts)
        self._undoer.record(action)
        self.groups.remove(group)
        for account in accounts:
            account.group = None
        self.notify('account_deleted')
    
    def expand_group(self, group):
        group.expanded = True
        self.notify('group_expanded_state_changed')
    
    def new_group(self, type):
        name = self.groups.new_name('New group', type)
        group = Group(name, type)
        action = Action('Add group')
        action.added_groups.add(group)
        self._undoer.record(action)
        self.groups.append(group)
        self.notify('account_added')
        return group
    
    #--- Transaction
    def can_move_transactions(self, transactions, before, after):
        assert transactions
        if any(isinstance(txn, Spawn) for txn in transactions):
            return False
        if not allsame(txn.date for txn in transactions):
            return False
        from_date = transactions[0].date
        before_date = before.date if before else None
        after_date = after.date if after else None
        return from_date in (before_date, after_date)
    
    def change_transaction(self, original, new, repeat_type, repeat_every):
        date_changed = new.date != original.date
        recurrence = Recurrence(original, repeat_type, repeat_every) if repeat_type != REPEAT_NEVER else None
        
        def prepare():
            action = Action('Change transaction')
            action.change_transactions([original])
            if not isinstance(original, Spawn) and recurrence is not None:
                action.added_schedules.add(recurrence)
            if date_changed:
                action.will_unreconcile |= set(original.splits)
            # Here, we don't just look for splits to unreconcile, we prepare the splits as well
            original_splits = set(s.original for s in new.splits if hasattr(s, 'original'))
            deleted_splits = set(original.splits) - original_splits
            action.will_unreconcile |= set(deleted_splits)
            for split in new.splits:
                if split.account is not None:
                    # don't forget that account up here is an external instance. Even if an account of
                    # the same name exists in self.accounts, it's not gonna be the same instance.
                    split.account = self.accounts.find(split.account.name, split.account.type)
                if hasattr(split, 'original'):
                    if split.original.amount != split.amount or split.original.account is not split.account:
                        split.reconciled = False
                        split.transaction = split.original.transaction
                        action.will_unreconcile.add(split.original)
                    del split.original
            return action
        
        def perform():
            min_date = min(original.date, new.date)
            original.set_splits(new.splits)
            self._change_transaction(original, date=new.date, description=new.description,
                                     payee=new.payee, checkno=new.checkno)
            self._update_schedule(original, recurrence)
            self._cook(from_date=min_date)
            self._clean_empty_categories()
            if not self._adjust_date_range(original.date):
                self.notify('entry_changed')
        
        self._perform_action(prepare, perform)
    
    def change_transactions(self, transactions, date=NOEDIT, description=NOEDIT, payee=NOEDIT, 
                            checkno=NOEDIT, from_=NOEDIT, to=NOEDIT, amount=NOEDIT, currency=NOEDIT):
        if from_ is not NOEDIT:
            from_ = self.accounts.find(from_, INCOME) if from_ else None
        if to is not NOEDIT:
            to = self.accounts.find(to, EXPENSE) if to else None
        
        def prepare():
            action = self._get_action_from_changed_transactions(transactions)
            for transaction in transactions:
                if date is not NOEDIT and date != transaction.date:
                    action.will_unreconcile |= set(transaction.splits)
                if any(x is not NOEDIT for x in [from_, to, amount]):
                    fsplits, tsplits = transaction.splitted_splits()
                    fsplit = fsplits[0] if len(fsplits) == 1 else None
                    tsplit = tsplits[0] if len(tsplits) == 1 else None
                    if from_ is not NOEDIT and fsplit is not None and from_ is not fsplit.account:
                        action.will_unreconcile.add(fsplit)
                    if to is not NOEDIT and tsplit is not None and to is not tsplit.account:
                        action.will_unreconcile.add(tsplit)
                    if amount is not NOEDIT and fsplit is not None and tsplit is not None and amount != tsplit.amount:
                        action.will_unreconcile.add(fsplit)
                        action.will_unreconcile.add(tsplit)
                if currency is not NOEDIT:
                    tochange = (s for s in transaction.splits if s.amount and s.amount.currency != currency)
                    action.will_unreconcile |= set(tochange)
            return action
        
        def perform():
            min_date = date if date is not NOEDIT else datetime.date.max
            force_local_scope = len(transactions) > 1
            for transaction in transactions:
                min_date = min(min_date, transaction.date)
                self._change_transaction(transaction, date=date, description=description, 
                                         payee=payee, checkno=checkno, from_=from_, to=to, 
                                         amount=amount, currency=currency, 
                                         force_local_scope=force_local_scope)
            self._cook(from_date=min_date)
            self._clean_empty_categories()
            if not self._adjust_date_range(transaction.date):
                self.notify('entry_changed')
            transaction = transactions[0]
        
        if date is not NOEDIT and amount is not NOEDIT and amount != 0:
            currencies_to_ensure = [amount.currency.code, self.app.default_currency.code]
            Currency.get_rates_db().ensure_rates(date, currencies_to_ensure)
        self._perform_action(prepare, perform)
    
    def delete_transactions(self, transactions):
        def prepare():
            action = Action('Remove transaction')
            action.deleted_transactions |= set(transactions)
            action.will_unreconcile |= set(flatten(t.splits for t in transactions))
            return action
        
        def perform():
            for txn in transactions:
                if isinstance(txn, Spawn):
                    global_scope = self.view.query_for_schedule_scope()
                    if global_scope:
                        txn.recurrence.stop_before(txn)
                    else:
                        txn.recurrence.delete(txn)
                else:
                    self.transactions.remove(txn)
                if txn in self._explicitly_selected_transactions:
                    self._explicitly_selected_transactions.remove(txn)
            min_date = min(t.date for t in transactions)
            self._cook(from_date=min_date)
            self._clean_empty_categories()
            self.notify('entry_deleted')
        
        self._perform_action(prepare, perform)
    
    def move_transactions(self, transactions, to_transaction):
        affected = set(transactions)
        affected_date = transactions[0].date
        affected |= set(self.transactions.transactions_at_date(affected_date))
        
        def prepare():
            action = Action('Move transaction')
            action.change_transactions(affected)
            action.will_unreconcile |= set(flatten(t.splits for t in affected))
            return action
        
        def perform():
            for transaction in transactions:
                self.transactions.move_before(transaction, to_transaction)
            self._cook()
            self.notify('entry_changed')
        
        self._perform_action(prepare, perform)
    
    def new_transaction(self):
        date = self.selected_transaction.date if self.selected_transaction else datetime.date.today()
        return Transaction(date, amount=0)
    
    @property
    def visible_transactions(self):
        if self._visible_transactions is None:
            self._set_visible_transactions()
        return self._visible_transactions
    
    @property
    def visible_unfiltered_transaction_count(self):
        return self._visible_unfiltered_transaction_count
    
    #--- Entry
    def change_entry(self, entry, date=NOEDIT, description=NOEDIT, payee=NOEDIT, checkno=NOEDIT, 
                     transfer=NOEDIT, amount=NOEDIT):
        assert entry is not None
        if date is not NOEDIT and amount is not NOEDIT and amount != 0:
            Currency.get_rates_db().ensure_rates(date, [amount.currency.code, entry.account.currency.code])
        date_changed = date is not NOEDIT and date != entry.date
        amount_changed = amount is not NOEDIT and amount != entry.amount
        transfer_changed = len(entry.splits) == 1 and transfer is not NOEDIT and transfer != entry.transfer
        
        def prepare():
            action = self._get_action_from_changed_transactions([entry.transaction])
            if date_changed or amount_changed or transfer_changed:
                action.will_unreconcile = set(entry.splits)
                if date_changed or amount_changed:
                    action.will_unreconcile.add(entry.split)
            return action
        
        def perform():
            min_date = entry.date if date is NOEDIT else min(entry.date, date)
            if amount is not NOEDIT:
                entry.split.amount = amount
            # if the entry is part of a Split entry, we don't need to balance, because the balancing
            # occurs in set_split_amount()
            if len(entry.splits) == 1:
                entry.transaction.balance_two_way(entry.split)
                if transfer_changed:
                    auto_create_type = EXPENSE if entry.split.amount < 0 else INCOME
                    transfer_account = self.accounts.find(transfer, auto_create_type) if transfer else None
                    entry.splits[0].account = transfer_account
            self._change_transaction(entry.transaction, date=date, description=description, 
                                     payee=payee, checkno=checkno)
            self._cook(from_date=min_date)
            self._clean_empty_categories()
            if not self._adjust_date_range(entry.date):
                self.notify('entry_changed')
        
        self._perform_action(prepare, perform)
    
    def delete_entries(self, entries):
        transactions = [e.transaction for e in entries]
        self.delete_transactions(transactions)
    
    def move_entries(self, entries, to_entry):
        transactions = [e.transaction for e in entries]
        to_transaction = to_entry.transaction if to_entry is not None else None
        self.move_transactions(transactions, to_transaction)
    
    def new_entry(self):
        account = self.selected_account
        date = self.selected_transaction.date if self.selected_transaction else datetime.date.today()
        balance = 0
        reconciled_balance = 0
        previous_entry = account.last_entry(date=date)
        if previous_entry:
            balance = previous_entry.balance
            reconciled_balance = previous_entry.reconciled_balance
        transaction = Transaction(date, account=self.selected_account, amount=0)
        split = transaction.splits[0]
        entry = Entry(split, 0, balance, reconciled_balance)
        return entry
    
    def toggle_entries_reconciled(self, entries):
        """Toggle the reconcile flag of 'entries'"""
        if not self._in_reconciliation_mode:
            return
        entries = set(entries)
        reconciled_entries = set(e for e in entries if e.reconciled)
        entries -= reconciled_entries
        all_reconciled = not entries or all(entry.reconciliation_pending for entry in entries)
        newvalue = not all_reconciled
        
        def prepare():
            # if 'newvalue' is false, we want to unreconcile all reconciled entries.
            # if it's true, since we are not changing any of the reconciled entries, we only want to
            # unreconcile all reconciled entries that are after the first entry to be put in 'pending'
            # state.
            action = Action('Change reconciliation')
            if newvalue:
                entry = iter(entries).next()
                account = entry.account
                action.will_unreconcile = [e.split for e in dropwhile(lambda e: e not in entries, account.entries)]
            else:
                action.will_unreconcile = [e.split for e in reconciled_entries]
            return action
        
        def perform():
            min_date = datetime.date.max
            if entries:
                for entry in entries:
                    entry.split.reconciliation_pending = newvalue
                    min_date = min(min_date, entry.date)
            else: 
                # a reconciled entry has been unreconciled, and the user chose "Continue, but don't 
                # unreconcile", which means that _perform_action() didn't take care of unreconciliation
                # We have to take care of it (but this only unreconciles selected entries, rather
                # than all those that follow selected entries).
                for entry in reconciled_entries:
                    entry.split.reconciled = False
            self._cook(from_date=min_date)
            self.notify('entry_changed')
        
        self._perform_action(prepare, perform)
    
    @property
    def previous_entry(self): # the entry just before the date range
        account = self.selected_account
        if account is None:
            return None
        date_range = self.date_range
        prev_entries = [entry for entry in account.entries if entry.date < date_range.start]
        return prev_entries[-1] if prev_entries else None
    
    @property
    def visible_entries(self):
        if self._visible_entries is None:
            self._set_visible_entries()
        return self._visible_entries
    
    @property
    def visible_unfiltered_entry_count(self):
        return self._visible_unfiltered_entry_count
    
    #--- Budget
    def budgeted_amount(self, account, date_range, currency=None):
        if not (account.budget and date_range.future):
            return 0
        currency = currency or account.currency
        budget_txns = [t for t in self.oven.transactions if getattr(t, 'is_budget', False)]
        return sum(bt.budget_for_account(account, date_range, currency) for bt in budget_txns)
    
    def budgeted_amount_for_target(self, target, date_range):
        """Returns the sum of all the budgeted amounts targeting 'target'. The currency of the 
        result is target's currency. The result is normalized (reverted if target is a liability).
        If target is None, all accounts are used.
        """
        accounts = set(a for a in self.accounts if a.is_income_statement_account())
        accounts -= self.excluded_accounts
        if target is None:
            targeters = [a for a in accounts if a.budget and a.budget_target not in self.excluded_accounts]
            currency = self.app.default_currency
        else:
            targeters = [a for a in accounts if a.budget_target is target]
            currency = target.currency
        if not targeters:
            return 0
        budgeted_amount = sum(self.budgeted_amount(a, date_range, currency=currency) for a in targeters)
        if target is not None:
            budgeted_amount = target._normalize_amount(budgeted_amount)
        return budgeted_amount
    
    def normal_budgeted_amount(self, account, date_range, currency=None):
        budgeted_amount = self.budgeted_amount(account, date_range, currency)
        return account._normalize_amount(budgeted_amount)
    
    #--- Selection
    @property
    def selected_account(self):
        return self._selected_account
    
    def select_account(self, account):
        self._selected_account = account
    
    @property
    def shown_account(self):
        return self._shown_account
    
    def show_selected_account(self):
        if self._selected_account is not self._shown_account:
            self._visible_entries = None
        self._shown_account = self._selected_account
        self.select_entry_table()
    
    @property
    def selected_transactions(self):
        return self._selected_transactions
    
    @property
    def selected_transaction(self):
        return self._selected_transactions[0] if self._selected_transactions else None
    
    def select_transactions(self, transactions):
        self._selected_transactions = transactions
    
    @property
    def explicitly_selected_transactions(self):
        return self._explicitly_selected_transactions
    
    def explicitly_select_transactions(self, transactions):
        self._explicitly_selected_transactions = transactions
        self.select_transactions(transactions)
    
    @property
    def selected_splits(self):
        return self._selected_splits
    
    def select_splits(self, splits):
        self._selected_splits = splits
    
    def select_balance_sheet(self):
        self.filter_string = ''
        self.notify('balance_sheet_selected')
    
    def select_entry_table(self):
        if self.shown_account is not None:
            self.select_account(self.shown_account)
            self.filter_string = ''
            self.notify('entry_table_selected')
    
    def select_income_statement(self):
        self.filter_string = ''
        self.notify('income_statement_selected')
    
    def select_transaction_table(self):
        self.notify('transaction_table_selected')
    
    #--- Load / Save / Import
    def load_from_xml(self, filename):
        loader = native.Loader(self.app.default_currency)
        try:
            loader.parse(filename)
        except FileFormatError:
            raise FileFormatError('"%s" is not a moneyGuru file' % filename)
        loader.load()
        self.accounts.clear()
        self.transactions.clear()
        self.groups.clear()
        del self._scheduled[:]
        self._undoer.clear()
        for group in loader.groups:
            self.groups.append(group)
        for account in loader.accounts:
            self.accounts.add(account)
        for transaction in loader.transactions:
            self.transactions.add(transaction, position=transaction.position)
        for recurrence in loader.scheduled:
            self._scheduled.append(recurrence)
        self._cook()
        self._restore_preferences_after_load()
        self.notify('file_loaded')
        self._undoer.set_save_point()
    
    def save_to_xml(self, filename):
        def write_transaction_element(parent_element, transaction):
            transaction_element = ET.SubElement(parent_element, 'transaction')
            attrib = transaction_element.attrib
            attrib['date'] = transaction.date.strftime('%Y-%m-%d')
            attrib['description'] = transaction.description
            attrib['payee'] = transaction.payee
            attrib['checkno'] = transaction.checkno
            attrib['mtime'] = str(int(transaction.mtime))
            for split in transaction.splits:
                split_element = ET.SubElement(transaction_element, 'split')
                attrib = split_element.attrib
                attrib['account'] = split.account_name
                attrib['amount'] = str(split.amount)
                attrib['memo'] = split.memo
                if split.reference is not None:
                    attrib['reference'] = split.reference
                attrib['reconciled'] = 'y' if split.reconciled else 'n'
        
        self.stop_edition()
        self._commit_reconciliation()
        self.notify('reconciliation_changed')
        root = ET.Element('moneyguru-file')
        for group in self.groups:
            group_element = ET.SubElement(root, 'group')
            attrib = group_element.attrib
            attrib['name'] = group.name
            attrib['type'] = group.type
        for account in self.accounts:
            account_element = ET.SubElement(root, 'account')
            attrib = account_element.attrib
            attrib['name'] = account.name
            attrib['currency'] = account.currency.code
            attrib['type'] = account.type
            if account.group:
                attrib['group'] = account.group.name
            if account.budget:
                attrib['budget'] = str(account.budget)
                assert account.budget_target is not None
                attrib['budget_target'] = account.budget_target.name
            if account.reference is not None:
                attrib['reference'] = account.reference
        for transaction in self.transactions:
            write_transaction_element(root, transaction)
        # the functionality of the line below is untested because it's an optimisation
        scheduled = [s for s in self._scheduled if s.is_alive]
        for recurrence in scheduled:
            recurrence_element = ET.SubElement(root, 'recurrence')
            attrib = recurrence_element.attrib
            attrib['type'] = recurrence.repeat_type
            attrib['every'] = str(recurrence.repeat_every)
            if recurrence.stop_date is not None:
                attrib['stop_date'] = recurrence.stop_date.strftime('%Y-%m-%d')
            for date, change in recurrence.date2globalchange.items():
                change_element = ET.SubElement(recurrence_element, 'change')
                change_element.attrib['date'] = date.strftime('%Y-%m-%d')
                if change is not None:
                    write_transaction_element(change_element, change)
            for date, exception in recurrence.date2exception.items():
                exception_element = ET.SubElement(recurrence_element, 'exception')
                exception_element.attrib['date'] = date.strftime('%Y-%m-%d')
                if exception is not None:
                    write_transaction_element(exception_element, exception)
            write_transaction_element(recurrence_element, recurrence.ref)
        tree = ET.ElementTree(root)
        tree.write(filename, 'utf-8')
        self._undoer.set_save_point()
    
    def save_to_qif(self, filename):
        def format_amount_for_qif(amount):
            return '%1.2f' % amount.value if amount else '0.00'
        
        accounts = [a for a in self.accounts if a.is_balance_sheet_account()]
        txns_seen = set()
        lines = []
        for account in accounts:
            qif_account_type = 'Oth L' if account.type == LIABILITY else 'Bank'
            lines.append('!Account')
            lines.append('N%s' % account.name)
            lines.append('B%s' % format_amount_for_qif(account.balance()))
            lines.append('T%s' % qif_account_type)
            lines.append('^')
            lines.append('!Type:%s' % qif_account_type)
            for entry in account.entries:
                if entry.transaction in txns_seen:
                    continue
                txns_seen.add(entry.transaction)
                lines.append('D%s' % format_date(entry.date, 'MM/dd/yy'))
                lines.append('T%s' % format_amount_for_qif(entry.amount))
                if entry.description:
                    lines.append('M%s' % entry.description)
                if entry.payee:
                    lines.append('P%s' % entry.payee)
                if entry.checkno:
                    lines.append('N%s' % entry.checkno)
                if len(entry.splits) > 1 or any(s.memo for s in entry.transaction.splits):
                    for split in entry.splits:
                        if split.account is not None:
                            lines.append('S%s' % split.account.name)
                        if split.memo:
                            lines.append('E%s' % split.memo)
                        if split.reconciled:
                            lines.append('CR')
                        lines.append('$%s' % format_amount_for_qif(-split.amount))
                else:
                    if entry.transfer:
                        lines.append('L%s' % entry.transfer[0].name)
                    if entry.reconciled:
                        lines.append('CR')
                lines.append('^')
        fd = open(filename, 'w')
        data = u'\n'.join(lines)
        fd.write(data.encode('utf-8'))
        fd.close()
    
    def parse_file_for_import(self, filename):
        try:
            for loaderclass in (native.Loader, ofx.Loader, qif.Loader, csv_.Loader):
                try:
                    loader = loaderclass(self.app.default_currency)
                    loader.parse(filename)
                    break
                except FileFormatError:
                    pass
            else:
                # No file fitted
                raise FileFormatError('%s is of an unknown format.' % filename)
        except Exception as e:
            logging.warning('An unexpected error was raised during file load: %r' % e)
            msg = 'An unexpected error occurred while importing. Please contact support@hardcoded.net'\
                  ' with the content of your Console (in /Applications/Utilities/Console)'
            raise FileFormatError(msg)
        self.loader = loader
        if isinstance(self.loader, csv_.Loader):
            self.notify('csv_options_needed')
        else:
            self.load_parsed_file_for_import()
        
    
    def load_parsed_file_for_import(self):
        self.loader.load()
        if self.loader.accounts:
            self.notify('file_loaded_for_import')
        else:
            raise FileFormatError('%s does not contain any account to import.' % filename)
    
    def import_entries(self, target_account, ref_account, matches):
        # Matches is a list of 2 sized tuples (entry, ref), ref being the existing entry that 'entry'
        # has been matched with. 'ref' can be None
        # PREPARATION
        # We have to look which transactions are added, which are changed. We have to see which 
        # accounts will be added. Those with a name clash must be replaced (in the splits).
        added_transactions = set()
        added_accounts = set()
        to_unreconcile = set()
        if target_account is ref_account and target_account not in self.accounts:
            added_accounts.add(target_account)
        for entry, ref in matches:
            if ref is not None:
                for split in ref.transaction.splits:
                    to_unreconcile.add(split)
            else:
                if entry.transaction not in self.transactions:
                    added_transactions.add(entry.transaction)
            for split in entry.splits:
                if split.account is None:
                    continue
                account = self.accounts.find(split.account.name)
                if account is None:
                    added_accounts.add(split.account)
                else:
                    split.account = account
            if target_account is not ref_account:
                entry.split.account = target_account
        to_unreconcile = self._get_splits_to_unreconcile(to_unreconcile)
        if to_unreconcile and not self.view.confirm_unreconciliation(len(to_unreconcile)):
            raise OperationAborted()
        action = Action('Import')
        action.added_accounts |= added_accounts
        action.added_transactions |= added_transactions
        action.change_splits(to_unreconcile)
        self._undoer.record(action)
        
        # PERFORM
        for split in to_unreconcile:
            split.reconciled = False
        for account in added_accounts:
            account.name = self.accounts.new_name(account.name)
            self.accounts.add(account)
        if target_account is not ref_account and ref_account.reference is not None:
            target_account.reference = ref_account.reference
        for entry, ref in matches:
            if ref is not None:
                ref.transaction.date = entry.date
                ref.split.amount = entry.split.amount
                ref.split.reference = entry.split.reference
            else:
                if entry.transaction not in self.transactions:
                    self.transactions.add(entry.transaction)
        self._cook()
        self.notify('entries_imported')
    
    def is_dirty(self):
        return self._undoer.modified
    
    #--- Date Range
    def select_month_range(self, starting_point=None):
        if starting_point is None:
            starting_point = self.selected_transaction.date if self.selected_transaction else self.date_range
        self.date_range = MonthRange(starting_point)
    
    def select_quarter_range(self, starting_point=None):
        if starting_point is None:
            starting_point = self.selected_transaction.date if self.selected_transaction else self.date_range
        self.date_range = QuarterRange(starting_point)
    
    def select_year_range(self, starting_point=None):
        if starting_point is None:
            starting_point = self.selected_transaction.date if self.selected_transaction else self.date_range
        self.date_range = YearRange(starting_point)
    
    def select_year_to_date_range(self):
        self.date_range = YearToDateRange()
    
    def select_running_year_range(self):
        self.date_range = RunningYearRange(ahead_months=self.app.ahead_months)
    
    def select_custom_date_range(self, start_date=None, end_date=None):
        if start_date is not None and end_date is not None:
            self.date_range = CustomDateRange(start_date, end_date, self.app.format_date)
        else: # summon the panel
            self.notify('custom_date_range_selected')
    
    def select_prev_date_range(self):
        if self.date_range.can_navigate:
            self.date_range = self.date_range.prev()
    
    def select_next_date_range(self):
        if self.date_range.can_navigate:
            self.date_range = self.date_range.next()
    
    def select_today_date_range(self):
        if self.date_range.can_navigate:
            self.date_range = self.date_range.around(datetime.date.today())
    
    @property
    def date_range(self):
        return self._date_range
    
    @date_range.setter
    def date_range(self, date_range):
        if date_range == self._date_range:
            return
        self.stop_edition()
        self.notify('date_range_will_change')
        self._date_range = date_range
        self.oven.continue_cooking(date_range.end)
        self._visible_transactions = None
        self._visible_entries = None
        self.notify('date_range_changed')
    
    #--- Undo
    def can_undo(self):
        return self._undoer.can_undo()
    
    def undo_description(self):
        return self._undoer.undo_description()
    
    def undo(self):
        self.stop_edition()
        self._undoer.undo()
        if self.selected_account is not None and self.selected_account not in self.accounts:
            self.select_account(None)
        self._cook()
        self.notify('undone')
    
    def can_redo(self):
        return self._undoer.can_redo()
    
    def redo_description(self):
        return self._undoer.redo_description()
    
    def redo(self):
        self.stop_edition()
        self._undoer.redo()
        if self.selected_account is not None and self.selected_account not in self.accounts:
            self.select_account(None)
        self._cook()
        self.notify('redone')
    
    #--- Misc
    def close(self):
        self._save_preferences()
        self.notify('document_will_close')
    
    def in_reconciliation_mode(self):
        return self._in_reconciliation_mode
    
    def toggle_reconciliation_mode(self):
        if self._in_reconciliation_mode:
            self._commit_reconciliation()
        self._in_reconciliation_mode = not self._in_reconciliation_mode
        self.notify('reconciliation_changed')
    
    def stop_edition(self):
        """Call this when some operation (such as a panel loading) requires the other GUIs to save
        their edits and stop edition.
        """
        self.notify('edition_must_stop')
    
    #--- Properties
    @property
    def filter_string(self):
        return self._filter_string
    
    @filter_string.setter
    def filter_string(self, value):
        value = nonone(value, '').strip()
        if value == self._filter_string:
            return
        self._filter_string = value
        self._visible_transactions = None
        self._visible_entries = None
        self.select_transaction_table()
        self.notify('filter_applied')
    
    # use FILTER_* consts or None
    @property
    def filter_type(self):
        return self._filter_type
    
    @filter_type.setter
    def filter_type(self, value):
        if value is self._filter_type:
            return
        self._filter_type = value
        self._visible_transactions = None
        self._visible_entries = None
        self.notify('filter_applied')
    
    #--- Events
    def ahead_months_changed(self):
        if isinstance(self.date_range, RunningYearRange):
            self.date_range = RunningYearRange(ahead_months=self.app.ahead_months)
    
    def first_weekday_changed(self):
        self.notify('first_weekday_changed')
    
