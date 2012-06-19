# Created By: Virgil Dupras
# Created On: 2007-10-25
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import datetime
import time
import uuid
import logging

from hscommon.currency import Currency
from hscommon.notify import Repeater
from hscommon import io
from hscommon.util import nonone, allsame, dedupe, extract, first
from hscommon.trans import tr
from hscommon.gui.base import GUIObject

from .const import NOEDIT, DATE_FORMAT_FOR_PREFERENCES
from .exception import FileFormatError, OperationAborted
from .loader import csv, qif, ofx, native
from .model.account import Account, Group, AccountList, GroupList, AccountType
from .model.amount import parse_amount, format_amount
from .model.budget import BudgetList
from .model.date import (MonthRange, QuarterRange, YearRange, YearToDateRange, RunningYearRange,
    AllTransactionsRange, CustomDateRange, inc_month)
from .model.oven import Oven
from .model.recurrence import Spawn
from .model.transaction_list import TransactionList
from .model.undo import Undoer, Action
from .saver.native import save as save_native

SELECTED_DATE_RANGE_PREFERENCE = 'SelectedDateRange'
SELECTED_DATE_RANGE_START_PREFERENCE = 'SelectedDateRangeStart'
SELECTED_DATE_RANGE_END_PREFERENCE = 'SelectedDateRangeEnd'
EXCLUDED_ACCOUNTS_PREFERENCE = 'ExcludedAccounts'

DATE_RANGE_MONTH = 'month'
DATE_RANGE_QUARTER = 'quarter'
DATE_RANGE_YEAR = 'year'
DATE_RANGE_YTD = 'ytd'
DATE_RANGE_RUNNING_YEAR = 'running_year'
DATE_RANGE_ALL_TRANSACTIONS = 'all_transactions'
DATE_RANGE_CUSTOM = 'custom'

class FilterType:
    Unassigned = object()
    Income = object() # in etable, the filter is for increase
    Expense = object() # in etable, the filter is for decrease
    Transfer = object()
    Reconciled = object()
    NotReconciled = object()

class ScheduleScope:
    Local = 0
    Global = 1
    Cancel = 2

AUTOSAVE_BUFFER_COUNT = 10 # Number of autosave files that will be kept in the cache.

def handle_abort(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except OperationAborted:
            pass
    
    return wrapper

class Document(Repeater, GUIObject):
    REPEATED_NOTIFICATIONS = {'saved_custom_ranges_changed'}
    
    def __init__(self, app):
        Repeater.__init__(self, app)
        GUIObject.__init__(self)
        self.app = app
        self._properties = {
            'first_weekday': 0,
            'ahead_months': 3,
            'year_start_month': 1,
            'default_currency': self.app._default_currency,
        }
        self.accounts = AccountList(self.default_currency)
        self.excluded_accounts = set()
        self.groups = GroupList()
        self.transactions = TransactionList()
        # I did not manage to create a repeatable test for it, but self.schedules has to be ordered
        # because the order in which the spawns are created must stay the same
        self.schedules = []
        self.budgets = BudgetList()
        self.oven = Oven(self.accounts, self.transactions, self.schedules, self.budgets)
        self._undoer = Undoer(self.accounts, self.groups, self.transactions, self.schedules, self.budgets)
        self._date_range = YearRange(datetime.date.today())
        self._filter_string = ''
        self._filter_type = None
        self._document_id = None
        self._dirty_flag = False
        self._restore_preferences()
    
    #--- Private
    def _adjust_date_range(self, new_date):
        if self.date_range.can_navigate:
            new_date_range = self.date_range.around(new_date)
            if new_date_range == self.date_range:
                return False
        elif isinstance(self.date_range, AllTransactionsRange):
            if new_date >= self.date_range.start:
                return False
            new_date_range = AllTransactionsRange(start=new_date, ahead_months=self.ahead_months)
        else:
            return False
        # We have to manually set the date range and send notifications because ENTRY_CHANGED
        # must happen between DATE_RANGE_WILL_CHANGE and DATE_RANGE_CHANGED
        # Note that there are no tests for this, as the current doesn't really allow to test
        # for the order of the gui calls (and this exception doesn't mean that we should).
        self.notify('date_range_will_change')
        self._date_range = new_date_range
        self.oven.continue_cooking(new_date_range.end)
        self.notify('transaction_changed')
        self.notify('date_range_changed')
        return True
    
    def _async_autosave(self):
        # Because this method is called asynchronously, it's possible that, if unlucky, it happens
        # exactly as the user is commiting a change. In these cases, the autosaved file might be a
        # save of the data in a quite weird state. I think this risk is acceptable. The alternative
        # is to put locks everywhere, which would complexify the application.
        existing_names = [name for name in io.listdir(self.app.cache_path) if name.startswith('autosave')]
        existing_names.sort()
        timestamp = int(time.time())
        autosave_name = 'autosave{0}.moneyguru'.format(timestamp)
        while autosave_name in existing_names:
            timestamp += 1
            autosave_name = 'autosave{0}.moneyguru'.format(timestamp)
        self.save_to_xml(str(self.app.cache_path + autosave_name), autosave=True)
        if len(existing_names) >= AUTOSAVE_BUFFER_COUNT:
            io.remove(self.app.cache_path + existing_names[0])
    
    def _change_transaction(self, transaction, date=NOEDIT, description=NOEDIT, payee=NOEDIT, 
            checkno=NOEDIT, from_=NOEDIT, to=NOEDIT, amount=NOEDIT, currency=NOEDIT, 
            notes=NOEDIT, global_scope=False):
        date_changed = date is not NOEDIT and date != transaction.date
        transaction.change(date=date, description=description, payee=payee, checkno=checkno,
            from_=from_, to=to, amount=amount, currency=currency, notes=notes)
        if isinstance(transaction, Spawn):
            if global_scope:
                transaction.recurrence.change_globally(transaction)
            else:
                transaction.recurrence.add_exception(transaction)
        else:
            if transaction not in self.transactions:
                self.transactions.add(transaction)
            elif date_changed:
                self.transactions.move_last(transaction)
        self.transactions.clear_cache()
    
    def _clean_empty_categories(self, from_account=None):
        for account in list(self.accounts.auto_created):
            if account is from_account:
                continue
            if not account.entries:
                self.accounts.remove(account)
    
    def _clear(self):
        self._document_id = None
        self.accounts.clear()
        self.transactions.clear()
        self.groups.clear()
        del self.schedules[:]
        del self.budgets[:]
        self._undoer.clear()
        self._dirty_flag = False
        self._cook()
    
    def _cook(self, from_date=None):
        self.oven.cook(from_date=from_date, until_date=self.date_range.end)
    
    def _get_action_from_changed_transactions(self, transactions, global_scope=False):
        if len(transactions) == 1 and not isinstance(transactions[0], Spawn) \
                and transactions[0] not in self.transactions:
            action = Action(tr('Add transaction'))
            action.added_transactions.add(transactions[0])
        else:
            action = Action(tr('Change transaction'))
            action.change_transactions(transactions)
        if global_scope:
            spawns, txns = extract(lambda x: isinstance(x, Spawn), transactions)
            for schedule in {spawn.recurrence for spawn in spawns}:
                action.change_schedule(schedule)
        return action
    
    def _query_for_scope_if_needed(self, transactions):
        """Queries the UI for change scope if there's any Spawn among transactions.
        
        Returns whether the chosen scope is global
        Raises OperationAborted if the user cancels the operation.
        """
        if any(isinstance(txn, Spawn) for txn in transactions):
            scope = self.view.query_for_schedule_scope()
            if scope == ScheduleScope.Cancel:
                raise OperationAborted()
            return scope == ScheduleScope.Global
        else:
            return False
    
    def _reconcile_spawn_split(self, split, reconciliation_date):
        # returns a reference to the corresponding materialized split
        split.transaction.recurrence.delete(split.transaction)
        materialized = split.transaction.replicate()
        self.transactions.add(materialized)
        split_index = split.transaction.splits.index(split)
        materialized_split = materialized.splits[split_index]
        materialized_split.reconciliation_date = reconciliation_date
        return materialized_split
    
    def _refresh_date_range(self):
        """Refreshes the date range to make sure that it's in accordance with the current date
        range related preference (year start and ahead months). Call this when these prefs changed.
        """
        if isinstance(self.date_range, RunningYearRange):
            self.select_running_year_range()
        elif isinstance(self.date_range, AllTransactionsRange):
            self.select_all_transactions_range()    
        elif isinstance(self.date_range, YearRange):
            if datetime.date.today() in self.date_range:
                starting_point = datetime.date.today()
            else:
                starting_point = self.date_range
            self.select_year_range(starting_point=starting_point)
        elif isinstance(self.date_range, YearToDateRange):
            self.select_year_to_date_range()
    
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
        logging.debug('restore_preferences_after_load() beginning')
        excluded_account_names = set(nonone(self.get_default(EXCLUDED_ACCOUNTS_PREFERENCE), []))
        self.excluded_accounts = {a for a in self.accounts if a.name in excluded_account_names}
        selected_range = self.app.get_default(SELECTED_DATE_RANGE_PREFERENCE)
        if selected_range == DATE_RANGE_ALL_TRANSACTIONS: # only works after load
            self.select_all_transactions_range()
        self.notify('document_restoring_preferences')
    
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
        elif isinstance(dr, AllTransactionsRange):
            selected_range = DATE_RANGE_ALL_TRANSACTIONS
        elif isinstance(dr, CustomDateRange):
            selected_range = DATE_RANGE_CUSTOM
        self.app.set_default(SELECTED_DATE_RANGE_PREFERENCE, selected_range)
        str_start_date = dr.start.strftime(DATE_FORMAT_FOR_PREFERENCES)
        self.app.set_default(SELECTED_DATE_RANGE_START_PREFERENCE, str_start_date)
        str_end_date = dr.end.strftime(DATE_FORMAT_FOR_PREFERENCES)
        self.app.set_default(SELECTED_DATE_RANGE_END_PREFERENCE, str_end_date)
        excluded_account_names = [a.name for a in self.excluded_accounts]
        self.set_default(EXCLUDED_ACCOUNTS_PREFERENCE, excluded_account_names)
    
    #--- Account
    def change_accounts(self, accounts, name=NOEDIT, type=NOEDIT, currency=NOEDIT, group=NOEDIT,
            account_number=NOEDIT, notes=NOEDIT):
        assert all (a is not None for a in accounts)
        action = Action(tr('Change account'))
        action.change_accounts(accounts)
        for account in accounts:
            if name is not NOEDIT:
                self.accounts.set_account_name(account, name)
            if (type is not NOEDIT) and (type != account.type):
                account.type = type
                account.group = None
            if currency is not NOEDIT:
                assert not any(e.reconciled for e in account.entries)
                account.currency = currency
            if group is not NOEDIT:
                account.group = group
            if account_number is not NOEDIT:
                account.account_number = account_number
            if notes is not NOEDIT:
                account.notes = notes
        self._undoer.record(action)
        self._cook()
        self.notify('account_changed')
    
    def delete_accounts(self, accounts, reassign_to=None):
        action = Action(tr('Remove account'))
        accounts = set(accounts)
        action.delete_accounts(accounts)
        affected_schedules = [s for s in self.schedules if accounts & s.affected_accounts()]
        for schedule in affected_schedules:
            action.change_schedule(schedule)
        for account in accounts:
            affected_budgets = [b for b in self.budgets if b.account is account or b.target is account]
            if account.is_income_statement_account() and reassign_to is None:
                action.deleted_budgets |= set(affected_budgets)
            else:
                for budget in affected_budgets:
                    action.change_budget(budget)
        self._undoer.record(action)
        for account in accounts:
            self.transactions.reassign_account(account, reassign_to)
            for schedule in affected_schedules:
                schedule.reassign_account(account, reassign_to)
            for budget in affected_budgets:
                if budget.account is account:
                    if reassign_to is None:
                        self.budgets.remove(budget)
                    else:
                        budget.account = reassign_to
                elif budget.target is account:
                    budget.target = reassign_to
            self.accounts.remove(account)
        self._cook()
        self.notify('account_deleted')
    
    def new_account(self, type, group):
        name = self.accounts.new_name(tr('New account'))
        account = Account(name, self.default_currency, type)
        account.group = group
        action = Action(tr('Add account'))
        action.added_accounts.add(account)
        self._undoer.record(action)
        self.accounts.add(account)
        self.notify('account_added')
        return account
    
    def toggle_accounts_exclusion(self, accounts):
        if accounts <= self.excluded_accounts: # all accounts are already excluded. re-include all
            self.excluded_accounts -= accounts
        else:
            self.excluded_accounts |= accounts
        self.notify('accounts_excluded')
    
    #--- Group
    def change_group(self, group, name=NOEDIT):
        assert group is not None
        action = Action(tr('Change group'))
        action.change_groups([group])
        if name is not NOEDIT:
            self.groups.set_group_name(group, name)
        self._undoer.record(action)
        self.notify('account_changed')
    
    def delete_groups(self, groups):
        groups = set(groups)
        accounts = [a for a in self.accounts if a.group in groups]
        action = Action(tr('Remove group'))
        action.deleted_groups |= groups
        action.change_accounts(accounts)
        self._undoer.record(action)
        for group in groups:
            self.groups.remove(group)
        for account in accounts:
            account.group = None
        self.notify('account_deleted')
    
    def new_group(self, type):
        name = self.groups.new_name(tr('New group'), type)
        group = Group(name, type)
        action = Action(tr('Add group'))
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
    
    @handle_abort
    def change_transaction(self, original, new):
        global_scope = self._query_for_scope_if_needed([original])
        action = Action(tr('Change transaction'))
        action.change_transactions([original])
        self._undoer.record(action)
        
        # don't forget that account up here is an external instance. Even if an account of
        # the same name exists in self.accounts, it's not gonna be the same instance.
        for split in new.splits:
            if split.account is not None:
                split.account = self.accounts.find(split.account.name, split.account.type)
        original.set_splits(new.splits)
        min_date = min(original.date, new.date)
        self._change_transaction(original, date=new.date, description=new.description,
            payee=new.payee, checkno=new.checkno, notes=new.notes, global_scope=global_scope)
        self._cook(from_date=min_date)
        self._clean_empty_categories()
        if not self._adjust_date_range(original.date):
            self.notify('transaction_changed')
    
    @handle_abort
    def change_transactions(self, transactions, date=NOEDIT, description=NOEDIT, payee=NOEDIT, 
            checkno=NOEDIT, from_=NOEDIT, to=NOEDIT, amount=NOEDIT, currency=NOEDIT):
        if from_ is not NOEDIT:
            from_ = self.accounts.find(from_, AccountType.Income) if from_ else None
        if to is not NOEDIT:
            to = self.accounts.find(to, AccountType.Expense) if to else None
        if date is not NOEDIT and amount is not NOEDIT and amount != 0:
            currencies_to_ensure = [amount.currency.code, self.default_currency.code]
            Currency.get_rates_db().ensure_rates(date, currencies_to_ensure)
        if len(transactions) == 1:
            global_scope = self._query_for_scope_if_needed(transactions)
        else:
            global_scope = False
        action = self._get_action_from_changed_transactions(transactions, global_scope)
        self._undoer.record(action)

        min_date = date if date is not NOEDIT else datetime.date.max
        for transaction in transactions:
            min_date = min(min_date, transaction.date)
            self._change_transaction(transaction, date=date, description=description, 
                payee=payee, checkno=checkno, from_=from_, to=to, amount=amount, currency=currency, 
                global_scope=global_scope)
        self._cook(from_date=min_date)
        self._clean_empty_categories()
        if not self._adjust_date_range(transaction.date):
            self.notify('transaction_changed')
        if action.changed_schedules:
            self.notify('schedule_changed')
    
    @handle_abort
    def delete_transactions(self, transactions, from_account=None):
        action = Action(tr('Remove transaction'))
        spawns, txns = extract(lambda x: isinstance(x, Spawn), transactions)
        global_scope = self._query_for_scope_if_needed(spawns)
        schedules = set(spawn.recurrence for spawn in spawns)
        action.deleted_transactions |= set(txns)
        for schedule in schedules:
            action.change_schedule(schedule)
        self._undoer.record(action)
        
        for txn in transactions:
            if isinstance(txn, Spawn):
                if global_scope:
                    txn.recurrence.stop_before(txn)
                else:
                    txn.recurrence.delete(txn)
            else:
                self.transactions.remove(txn)
        min_date = min(t.date for t in transactions)
        self._cook(from_date=min_date)
        self._clean_empty_categories(from_account=from_account)
        self.notify('transaction_deleted')
        if action.changed_schedules:
            self.notify('schedule_changed')
    
    def duplicate_transactions(self, transactions):
        if not transactions:
            return
        action = Action(tr('Duplicate transactions'))
        duplicated = [txn.replicate() for txn in transactions]
        action.added_transactions |= set(duplicated)
        self._undoer.record(action)
        
        for txn in duplicated:
            self.transactions.add(txn)
        min_date = min(t.date for t in transactions)
        self._cook(from_date=min_date)
        self.notify('transaction_changed')
    
    def move_transactions(self, transactions, to_transaction):
        affected = set(transactions)
        affected_date = transactions[0].date
        affected |= set(self.transactions.transactions_at_date(affected_date))
        action = Action(tr('Move transaction'))
        action.change_transactions(affected)
        self._undoer.record(action)
        
        for transaction in transactions:
            self.transactions.move_before(transaction, to_transaction)
        self._cook()
        self.notify('transaction_changed')
    
    #--- Entry
    @handle_abort
    def change_entry(self, entry, date=NOEDIT, reconciliation_date=NOEDIT, description=NOEDIT, 
            payee=NOEDIT, checkno=NOEDIT, transfer=NOEDIT, amount=NOEDIT):
        assert entry is not None
        if date is not NOEDIT and amount is not NOEDIT and amount != 0:
            Currency.get_rates_db().ensure_rates(date, [amount.currency.code, entry.account.currency.code])
        if reconciliation_date is NOEDIT:
            global_scope = self._query_for_scope_if_needed([entry.transaction])
        else:
            global_scope = False # It doesn't make sense to set a reconciliation date globally
        action = self._get_action_from_changed_transactions([entry.transaction], global_scope)
        self._undoer.record(action)
        
        candidate_dates = [entry.date, date, reconciliation_date, entry.reconciliation_date]
        min_date = min(d for d in candidate_dates if d is not NOEDIT and d is not None)
        if reconciliation_date is not NOEDIT:
            if isinstance(entry.split.transaction, Spawn):
                # At this point we have to hijack the entry so we modify the materialized transaction
                # It's a little hackish, but well... it takes what it takes
                entry.split = self._reconcile_spawn_split(entry.split, reconciliation_date)
                action.added_transactions.add(entry.split.transaction)
            else:
                entry.split.reconciliation_date = reconciliation_date
        if (amount is not NOEDIT) and (len(entry.splits) == 1):
            entry.change_amount(amount)
        if (transfer is not NOEDIT) and (len(entry.splits) == 1) and (transfer != entry.transfer):
            auto_create_type = AccountType.Expense if entry.split.amount < 0 else AccountType.Income
            transfer_account = self.accounts.find(transfer, auto_create_type) if transfer else None
            entry.splits[0].account = transfer_account
        self._change_transaction(entry.transaction, date=date, description=description, 
            payee=payee, checkno=checkno, global_scope=global_scope)
        self._cook(from_date=min_date)
        self._clean_empty_categories()
        if not self._adjust_date_range(entry.date):
            self.notify('transaction_changed')
    
    def delete_entries(self, entries):
        from_account = first(entries).account
        transactions = dedupe(e.transaction for e in entries)
        self.delete_transactions(transactions, from_account=from_account)
    
    def toggle_entries_reconciled(self, entries):
        """Toggle the reconcile flag of `entries`.
        """
        if not entries:
            return
        all_reconciled = not entries or all(entry.reconciled for entry in entries)
        newvalue = not all_reconciled
        action = Action(tr('Change reconciliation'))
        action.change_splits([e.split for e in entries])
        min_date = min(entry.date for entry in entries)
        splits = [entry.split for entry in entries]
        spawns, splits = extract(lambda s: isinstance(s.transaction, Spawn), splits)
        for spawn in spawns:
            action.change_schedule(spawn.transaction.recurrence)
        self._undoer.record(action)
        if newvalue:
            for split in splits:
                split.reconciliation_date = split.transaction.date
            for spawn in spawns:
                #XXX update transaction selection
                materialized_split = self._reconcile_spawn_split(spawn, spawn.transaction.date)
                action.added_transactions.add(materialized_split.transaction)
        else:
            for split in splits:
                split.reconciliation_date = None
        self._cook(from_date=min_date)
        self.notify('transaction_changed')
    
    #--- Budget
    def budgeted_amount_for_target(self, target, date_range, filter_excluded=True):
        """Returns the sum of all the budgeted amounts targeting 'target'. The currency of the 
        result is target's currency. The result is normalized (reverted if target is a liability).
        If target is None, all accounts are used.
        """
        if target is None:
            budgets = self.budgets[:]
            currency = self.default_currency
        else:
            budgets = self.budgets.budgets_for_target(target)
            currency = target.currency
        if filter_excluded:
            # we must remove any budget touching an excluded account.
            is_not_excluded = lambda b: (b.account not in self.excluded_accounts)\
                and (b.target not in self.excluded_accounts)
            budgets = list(filter(is_not_excluded, budgets))
        if not budgets:
            return 0
        budgeted_amount = sum(-b.amount_for_date_range(date_range, currency=currency) for b in budgets)
        if target is not None:
            budgeted_amount = target.normalize_amount(budgeted_amount)
        return budgeted_amount
    
    def change_budget(self, original, new):
        if original in self.budgets:
            action = Action(tr('Change Budget'))
            action.change_budget(original)
        else:
            action = Action(tr('Add Budget'))
            action.added_budgets.add(original)
        self._undoer.record(action)
        min_date = min(original.start_date, new.start_date)
        original.start_date = new.start_date
        original.repeat_type = new.repeat_type
        original.repeat_every = new.repeat_every
        original.stop_date = new.stop_date
        original.account = new.account
        original.target = new.target
        original.amount = new.amount
        original.notes = new.notes
        original.reset_spawn_cache()
        if original not in self.budgets:
            self.budgets.append(original)
        self._cook(from_date=min_date)
        self.notify('budget_changed')
    
    def delete_budgets(self, budgets):
        if not budgets:
            return
        action = Action(tr('Remove Budget'))
        action.deleted_budgets |= set(budgets)
        self._undoer.record(action)
        for budget in budgets:
            self.budgets.remove(budget)
        min_date = min(b.start_date for b in budgets)
        self._cook(from_date=min_date)
        self.notify('budget_deleted')
    
    #--- Schedule
    def change_schedule(self, schedule, new_ref, repeat_type, repeat_every, stop_date):
        for split in new_ref.splits:
            if split.account is not None:
                # same as in change_transaction()
                split.account = self.accounts.find(split.account.name, split.account.type)
        if schedule in self.schedules:
            action = Action(tr('Change Schedule'))
            action.change_schedule(schedule)
        else:
            action = Action(tr('Add Schedule'))
            action.added_schedules.add(schedule)
        self._undoer.record(action)
        original = schedule.ref
        min_date = min(original.date, new_ref.date)
        original.set_splits(new_ref.splits)
        original.change(description=new_ref.description, payee=new_ref.payee,
            checkno=new_ref.checkno, notes=new_ref.notes)
        schedule.start_date = new_ref.date
        schedule.repeat_type = repeat_type
        schedule.repeat_every = repeat_every
        schedule.stop_date = stop_date
        schedule.reset_spawn_cache()
        if schedule not in self.schedules:
            self.schedules.append(schedule)
        self._cook(from_date=min_date)
        self.notify('schedule_changed')
    
    def delete_schedules(self, schedules):
        if not schedules:
            return
        action = Action(tr('Remove Schedule'))
        action.deleted_schedules |= set(schedules)
        self._undoer.record(action)
        for schedule in schedules:
            self.schedules.remove(schedule)
        min_date = min(s.ref.date for s in schedules)
        self._cook(from_date=min_date)
        self.notify('schedule_deleted')
    
    #--- Load / Save / Import
    def adjust_example_file(self):
        def inc_month_overflow(refdate, count):
            newdate = inc_month(refdate, count)
            if newdate.day < refdate.day: # must overflow
                newdate += datetime.timedelta(days=refdate.day-newdate.day)
            return newdate
        
        latest_date = self.transactions[-1].date
        TODAY = datetime.date.today()
        year_diff = TODAY.year - latest_date.year
        month_diff = year_diff * 12 + (TODAY.month - latest_date.month)
        if month_diff < 1:
            return
        for txn in self.transactions[:]:
            txn.date = inc_month_overflow(txn.date, month_diff)
            if txn.date > TODAY:
                self.transactions.remove(txn)
            for split in txn.splits:
                if split.reconciliation_date is not None:
                    split.reconciliation_date = txn.date
        for schedule in self.schedules:
            date2exception = schedule.date2exception
            schedule.start_date = inc_month_overflow(schedule.start_date, month_diff)
            if schedule.stop_date is not None:
                schedule.stop_date = inc_month_overflow(schedule.stop_date, month_diff)
            # we delete any spawn that is not in the future
            for spawn in schedule.get_spawns(end=TODAY):
                schedule.delete(spawn)
            # This will not work for weekly schedules, but the only reason we have this here is
            # for then the student loan stops in the example document (last payment is different)
            for date, exception in list(date2exception.items()):
                if exception is None:
                    continue
                newdate = inc_month_overflow(date, month_diff)
                schedule.date2exception[newdate] = exception
        self._cook()
        self.notify('document_changed') # do it again to refresh the guis
    
    def clear(self):
        self._clear()
        self.notify('document_changed')
    
    def load_from_xml(self, filename):
        loader = native.Loader(self.default_currency)
        try:
            loader.parse(filename)
        except FileFormatError:
            raise FileFormatError(tr('"%s" is not a moneyGuru file') % filename)
        loader.load()
        self._clear()
        self._document_id = loader.document_id
        for propname in self._properties:
            if propname in loader.properties:
                self._properties[propname] = loader.properties[propname]
        for group in loader.groups:
            self.groups.append(group)
        for account in loader.accounts:
            self.accounts.add(account)
        for transaction in loader.transactions:
            self.transactions.add(transaction, position=transaction.position)
        for recurrence in loader.schedules:
            self.schedules.append(recurrence)
        for budget in loader.budgets:
            self.budgets.append(budget)
        self.accounts.default_currency = self.default_currency
        self._cook()
        self._restore_preferences_after_load()
        self.notify('document_changed')
        self._undoer.set_save_point()
        self._refresh_date_range()
    
    def save_to_xml(self, filename, autosave=False):
        # When called from _async_autosave, it should not disrupt the user: no stop edition, no
        # change in the save state.
        if not autosave:
            self.stop_edition()
        if self._document_id is None:
            self._document_id = uuid.uuid4().hex
        save_native(filename, self._document_id, self._properties, self.accounts, self.groups,
            self.transactions, self.schedules, self.budgets)
        if not autosave:
            self._undoer.set_save_point()
            self._dirty_flag = False
    
    def parse_file_for_import(self, filename):
        for loaderclass in (native.Loader, ofx.Loader, qif.Loader, csv.Loader):
            try:
                loader = loaderclass(self.default_currency)
                loader.parse(filename)
                break
            except FileFormatError:
                pass
        else:
            # No file fitted
            raise FileFormatError(tr('%s is of an unknown format.') % filename)
        self.loader = loader
        if isinstance(self.loader, csv.Loader):
            self.notify('csv_options_needed')
        else:
            self.load_parsed_file_for_import()
        
    
    def load_parsed_file_for_import(self):
        self.loader.load()
        if self.loader.accounts and self.loader.transactions:
            self.notify('file_loaded_for_import')
        else:
            raise FileFormatError('This file does not contain any account to import.')
    
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
                    entry.transaction.mtime = time.time()
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
        action = Action(tr('Import'))
        action.added_accounts |= added_accounts
        action.added_transactions |= added_transactions
        action.change_splits(to_unreconcile)
        self._undoer.record(action)
        
        for split in to_unreconcile:
            split.reconciliation_date = None
        for account in added_accounts:
            # we don't import groups, and we don't want them to mess our document
            account.group = None
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
        self.notify('transactions_imported')
    
    def is_dirty(self):
        return self._dirty_flag or self._undoer.modified
    
    def set_dirty(self):
        # is_dirty() is determined by the undoer's save point, but some actions are not undoable but
        # make the document dirty (ok, it's just one action: setting doc props). That's what this
        # flag is for.
        self._dirty_flag = True
    
    #--- Date Range
    def select_month_range(self, starting_point):
        self.date_range = MonthRange(starting_point)
    
    def select_quarter_range(self, starting_point):
        self.date_range = QuarterRange(starting_point)
    
    def select_year_range(self, starting_point):
        self.date_range = YearRange(starting_point, year_start_month=self.year_start_month)
    
    def select_year_to_date_range(self):
        self.date_range = YearToDateRange(year_start_month=self.year_start_month)
    
    def select_running_year_range(self):
        self.date_range = RunningYearRange(ahead_months=self.ahead_months)
    
    def select_all_transactions_range(self):
        if not self.transactions:
            return
        start_date = self.transactions[0].date
        self.date_range = AllTransactionsRange(start=start_date, ahead_months=self.ahead_months)
    
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
        self.notify('date_range_changed')
    
    #--- Undo
    def can_undo(self):
        return self._undoer.can_undo()
    
    def undo_description(self):
        return self._undoer.undo_description()
    
    def undo(self):
        self.stop_edition()
        self._undoer.undo()
        self._cook()
        self.notify('performed_undo_or_redo')
    
    def can_redo(self):
        return self._undoer.can_redo()
    
    def redo_description(self):
        return self._undoer.redo_description()
    
    def redo(self):
        self.stop_edition()
        self._undoer.redo()
        self._cook()
        self.notify('performed_undo_or_redo')
    
    #--- Misc
    def close(self):
        self._save_preferences()
        self.notify('document_will_close')
    
    def stop_edition(self):
        """Call this when some operation (such as a panel loading) requires the other GUIs to save
        their edits and stop edition.
        """
        self.notify('edition_must_stop')
    
    def get_default(self, key, fallback_value=None):
        if self._document_id is None:
            return fallback_value
        key = 'Doc{0}.{1}'.format(self._document_id, key)
        return self.app.get_default(key, fallback_value=fallback_value)
    
    def set_default(self, key, value):
        if self._document_id is None:
            return
        key = 'Doc{0}.{1}'.format(self._document_id, key)
        self.app.set_default(key, value)
    
    def format_amount(self, amount, **kw):
        default_currency = self.default_currency
        return format_amount(amount, default_currency, decimal_sep=self.app._decimal_sep,
            grouping_sep=self.app._grouping_sep, **kw)
    
    def parse_amount(self, amount, default_currency=None):
        if default_currency is None:
            default_currency = self.default_currency
        return parse_amount(amount, default_currency, auto_decimal_place=self.app._auto_decimal_place)
    
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
        self.notify('filter_applied')
    
    # use FilterType.* consts or None
    @property
    def filter_type(self):
        return self._filter_type
    
    @filter_type.setter
    def filter_type(self, value):
        if value is self._filter_type:
            return
        self.stop_edition()
        self._filter_type = value
        self.notify('filter_applied')
    
    # 0=monday 6=sunday
    @property
    def first_weekday(self):
        return self._properties['first_weekday']
        
    @first_weekday.setter
    def first_weekday(self, value):
        if value == self._properties['first_weekday']:
            return
        self._properties['first_weekday'] = value
        self.set_dirty()
        self.notify('first_weekday_changed')
    
    @property
    def ahead_months(self):
        return self._properties['ahead_months']
        
    @ahead_months.setter
    def ahead_months(self, value):
        assert 0 <= value <= 11
        if value == self._properties['ahead_months']:
            return
        self._properties['ahead_months'] = value
        self.set_dirty()
        self._refresh_date_range()
    
    @property
    def year_start_month(self):
        return self._properties['year_start_month']
        
    @year_start_month.setter
    def year_start_month(self, value):
        assert 1 <= value <= 12
        if value == self._properties['year_start_month']:
            return
        self._properties['year_start_month'] = value
        self.set_dirty()
        self._refresh_date_range()
    
    @property
    def default_currency(self):
        return self._properties['default_currency']
    
    @default_currency.setter
    def default_currency(self, value):
        if value == self._properties['default_currency']:
            return
        self._properties['default_currency'] = value
        self.set_dirty()
        self.accounts.default_currency = value
        self.notify('document_changed')
    
    #--- Events
    def must_autosave(self):
        # this is called async
        self._async_autosave()
    
    