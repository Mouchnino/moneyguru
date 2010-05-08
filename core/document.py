# Created By: Virgil Dupras
# Created On: 2007-10-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import datetime
import time

from hsutil import io
from hsutil.currency import Currency
from hsutil.notify import Broadcaster, Listener
from hsutil.misc import nonone, allsame, dedupe, extract, first

from .const import NOEDIT, DATE_FORMAT_FOR_PREFERENCES
from .exception import FileFormatError, OperationAborted
from .loader import csv, qif, ofx, native
from .model.account import Account, Group, AccountList, GroupList, AccountType
from .model.budget import BudgetList
from .model.date import (MonthRange, QuarterRange, YearRange, YearToDateRange, RunningYearRange,
    AllTransactionsRange, CustomDateRange, inc_month)
from .model.oven import Oven
from .model.recurrence import Spawn
from .model.transaction import Transaction
from .model.transaction_list import TransactionList
from .model.undo import Undoer, Action
from .saver.native import save as save_native
from .saver.qif import save as save_qif

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

class FilterType(object):
    Unassigned = object()
    Income = object() # in etable, the filter is for increase
    Expense = object() # in etable, the filter is for decrease
    Transfer = object()
    Reconciled = object()
    NotReconciled = object()

class ScheduleScope(object):
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
        # I did not manage to create a repeatable test for it, but self.schedules has to be ordered
        # because the order in which the spawns are created must stay the same
        self.schedules = []
        self.budgets = BudgetList()
        self.oven = Oven(self.accounts, self.transactions, self.schedules, self.budgets)
        self._undoer = Undoer(self.accounts, self.groups, self.transactions, self.schedules, self.budgets)
        self._date_range = YearRange(datetime.date.today())
        self._selected_account = None
        self._selected_transactions = []
        self._explicitly_selected_transactions = []
        self._filter_string = ''
        self._filter_type = None
        self._visible_transactions = None
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
            new_date_range = AllTransactionsRange(start=new_date, ahead_months=self.app.ahead_months)
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
        self.save_to_xml(unicode(self.app.cache_path + autosave_name), autosave=True)
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
    
    # XXX When this is called, close all affected account tabs
    def _clean_empty_categories(self, from_account=None):
        for account in list(self.accounts.auto_created):
            if account is from_account:
                continue
            if not account.entries:
                self.accounts.remove(account)
    
    def _clear(self):
        self._selected_account = None
        self.accounts.clear()
        self.transactions.clear()
        self.groups.clear()
        del self.schedules[:]
        del self.budgets[:]
        self._undoer.clear()
        self._cook()
    
    def _cook(self, from_date=None):
        self.oven.cook(from_date=from_date, until_date=self.date_range.end)
        self._visible_transactions = None
    
    def _date_range_starting_point(self):
        if self.selected_transaction:
            return self.selected_transaction.date
        elif datetime.date.today() in self.date_range:
            return datetime.date.today()
        else:
            return self.date_range
    
    def _get_action_from_changed_transactions(self, transactions):
        if len(transactions) == 1 and not isinstance(transactions[0], Spawn) \
                and transactions[0] not in self.transactions:
            action = Action('Add transaction')
            action.added_transactions.add(transactions[0])
        else:
            action = Action('Change transaction')
            action.change_transactions(transactions)
        return action
    
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
        selected_range = self.app.get_default(SELECTED_DATE_RANGE_PREFERENCE)
        if selected_range == DATE_RANGE_ALL_TRANSACTIONS: # only works after load
            self.select_all_transactions_range()
    
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
        self.app.set_default(EXCLUDED_ACCOUNTS_PREFERENCE, excluded_account_names)
    
    def _set_visible_transactions(self):
        date_range = self.date_range
        txns = [t for t in self.oven.transactions if t.date in date_range]
        query_string = self.filter_string
        filter_type = self.filter_type
        if not query_string and filter_type is None:
            self._visible_transactions = txns
            return
        if query_string:
            query = self._parse_search_query(query_string)
            txns = [t for t in txns if t.matches(query)]
        if filter_type is FilterType.Unassigned:
            txns = [t for t in txns if t.has_unassigned_split]
        elif filter_type is FilterType.Income:
            txns = [t for t in txns if any(getattr(s.account, 'type', '') == AccountType.Income for s in t.splits)]
        elif filter_type is FilterType.Expense:
            txns = [t for t in txns if any(getattr(s.account, 'type', '') == AccountType.Expense for s in t.splits)]
        elif filter_type is FilterType.Transfer:
            def is_transfer(t):
                return len([s for s in t.splits if s.account is not None and s.account.is_balance_sheet_account()]) >= 2
            txns = filter(is_transfer, txns)
        elif filter_type is FilterType.Reconciled:
            txns = [t for t in txns if any(s.reconciled for s in t.splits)]
        elif filter_type is FilterType.NotReconciled:
            txns = [t for t in txns if all(not s.reconciled for s in t.splits)]
        self._visible_transactions = txns
    
    #--- Account
    def change_account(self, account, name=NOEDIT, type=NOEDIT, currency=NOEDIT, group=NOEDIT,
            account_number=NOEDIT):
        assert account is not None
        action = Action('Change account')
        action.change_accounts([account])
        if name is not NOEDIT:
            self.accounts.set_account_name(account, name)
        if (type is not NOEDIT) and (type != account.type):
            account.type = type
            account.group = None
        if currency is not NOEDIT:
            account.currency = currency
        if group is not NOEDIT:
            account.group = group
        if account_number is not NOEDIT:
            account.account_number = account_number
        self._undoer.record(action)
        self._cook()
        self.notify('account_changed')
    
    def delete_account(self, account, reassign_to=None):
        action = Action('Remove account')
        action.delete_account(account)
        affected_schedules = [s for s in self.schedules if account in s.ref.affected_accounts()]
        map(action.change_schedule, affected_schedules)
        affected_budgets = [b for b in self.budgets if b.account is account or b.target is account]
        if account.is_income_statement_account() and reassign_to is None:
            action.deleted_budgets |= set(affected_budgets)
        else:
            map(action.change_budget, affected_budgets)
        self._undoer.record(action)
        self.transactions.reassign_account(account, reassign_to)
        for schedule in affected_schedules:
            schedule.ref.reassign_account(account, reassign_to)
            schedule.reset_spawn_cache()
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
        name = self.accounts.new_name('New account')
        account = Account(name, self.app.default_currency, type)
        account.group = group
        action = Action('Add account')
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
    
    @handle_abort
    def change_transaction(self, original, new):
        date_changed = new.date != original.date
        global_scope = self._query_for_scope_if_needed([original])
        action = Action('Change transaction')
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
            currencies_to_ensure = [amount.currency.code, self.app.default_currency.code]
            Currency.get_rates_db().ensure_rates(date, currencies_to_ensure)
        if len(transactions) == 1:
            global_scope = self._query_for_scope_if_needed(transactions)
        else:
            global_scope = False
        action = self._get_action_from_changed_transactions(transactions)
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
    
    @handle_abort
    def delete_transactions(self, transactions, from_account=None):
        action = Action('Remove transaction')
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
            if txn in self._explicitly_selected_transactions:
                self._explicitly_selected_transactions.remove(txn)
        min_date = min(t.date for t in transactions)
        self._cook(from_date=min_date)
        self._clean_empty_categories(from_account=from_account)
        self.notify('transaction_deleted')
    
    def duplicate_transactions(self, transactions):
        if not transactions:
            return
        action = Action('Duplicate transactions')
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
        action = Action('Move transaction')
        action.change_transactions(affected)
        self._undoer.record(action)
        
        for transaction in transactions:
            self.transactions.move_before(transaction, to_transaction)
        self._cook()
        self.notify('transaction_changed')
    
    def new_transaction(self):
        date = self.selected_transaction.date if self.selected_transaction else datetime.date.today()
        return Transaction(date, amount=0)
    
    @property
    def visible_transactions(self):
        if self._visible_transactions is None:
            self._set_visible_transactions()
        return self._visible_transactions
    
    #--- Entry
    @handle_abort
    def change_entry(self, entry, date=NOEDIT, reconciliation_date=NOEDIT, description=NOEDIT, 
            payee=NOEDIT, checkno=NOEDIT, transfer=NOEDIT, amount=NOEDIT):
        assert entry is not None
        if date is not NOEDIT and amount is not NOEDIT and amount != 0:
            Currency.get_rates_db().ensure_rates(date, [amount.currency.code, entry.account.currency.code])
        global_scope = self._query_for_scope_if_needed([entry.transaction])
        action = self._get_action_from_changed_transactions([entry.transaction])
        self._undoer.record(action)
        
        min_date = entry.date if date is NOEDIT else min(entry.date, date)
        if reconciliation_date is not NOEDIT:
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
        action = Action('Change reconciliation')
        action.change_splits([e.split for e in entries])
        self._undoer.record(action)
        
        min_date = min(entry.date for entry in entries)
        splits = [entry.split for entry in entries]
        spawns, splits = extract(lambda s: isinstance(s.transaction, Spawn), splits)
        if newvalue:
            for split in splits:
                split.reconciliation_date = split.transaction.date
            for spawn in spawns:
                #XXX update transaction selection
                spawn.reconciliation_date = spawn.transaction.date
                spawn.transaction.recurrence.delete(spawn.transaction)
                self.transactions.add(spawn.transaction.replicate())
        else:
            for split in splits:
                split.reconciliation_date = None
        self._cook(from_date=min_date)
        self.notify('transaction_changed')
    
    #--- Budget
    def budgeted_amount_for_target(self, target, date_range):
        """Returns the sum of all the budgeted amounts targeting 'target'. The currency of the 
        result is target's currency. The result is normalized (reverted if target is a liability).
        If target is None, all accounts are used.
        """
        if target is None:
            budgets = self.budgets[:]
            currency = self.app.default_currency
        else:
            budgets = self.budgets.budgets_for_target(target)
            currency = target.currency
        # we must remove any budget touching an excluded account.
        is_not_excluded = lambda b: b.account not in self.excluded_accounts and b.target not in self.excluded_accounts
        budgets = filter(is_not_excluded, budgets)
        if not budgets:
            return 0
        budgeted_amount = sum(-b.amount_for_date_range(date_range, currency=currency) for b in budgets)
        if target is not None:
            budgeted_amount = target._normalize_amount(budgeted_amount)
        return budgeted_amount
    
    def change_budget(self, original, new):
        if original in self.budgets:
            action = Action('Change Budget')
            action.change_budget(original)
        else:
            action = Action('Add Budget')
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
        action = Action('Remove Budget')
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
            action = Action('Change Schedule')
            action.change_schedule(schedule)
        else:
            action = Action('Add Schedule')
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
        action = Action('Remove Schedule')
        action.deleted_schedules |= set(schedules)
        self._undoer.record(action)
        for schedule in schedules:
            self.schedules.remove(schedule)
        min_date = min(s.ref.date for s in schedules)
        self._cook(from_date=min_date)
        self.notify('schedule_deleted')
    
    #--- Selection
    @property
    def selected_account(self):
        return self._selected_account
    
    def select_account(self, account):
        self._selected_account = account
    
    @property
    def selected_transactions(self):
        return self._selected_transactions
    
    @property
    def selected_transaction(self):
        return self._selected_transactions[0] if self._selected_transactions else None
    
    def select_transactions(self, transactions):
        self._selected_transactions = transactions
        self.notify('transactions_selected')
    
    @property
    def explicitly_selected_transactions(self):
        return self._explicitly_selected_transactions
    
    def explicitly_select_transactions(self, transactions):
        self._explicitly_selected_transactions = transactions
        self.select_transactions(transactions)
    
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
            for date, exception in date2exception.items():
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
        loader = native.Loader(self.app.default_currency)
        try:
            loader.parse(filename)
        except FileFormatError:
            raise FileFormatError('"%s" is not a moneyGuru file' % filename)
        loader.load()
        self._clear()
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
        self._cook()
        self._restore_preferences_after_load()
        self.notify('document_changed')
        self._undoer.set_save_point()
    
    def save_to_xml(self, filename, autosave=False):
        # When called from _async_autosave, it should not disrupt the user: no stop edition, no
        # change in the save state.
        if not autosave:
            self.stop_edition()
        save_native(filename, self.accounts, self.groups, self.transactions, self.schedules,
            self.budgets)
        if not autosave:
            self._undoer.set_save_point()
    
    def save_to_qif(self, filename):
        save_qif(filename, self.accounts)
    
    def parse_file_for_import(self, filename):
        for loaderclass in (native.Loader, ofx.Loader, qif.Loader, csv.Loader):
            try:
                loader = loaderclass(self.app.default_currency)
                loader.parse(filename)
                break
            except FileFormatError:
                pass
        else:
            # No file fitted
            raise FileFormatError('%s is of an unknown format.' % filename)
        self.loader = loader
        if isinstance(self.loader, csv.Loader):
            self.notify('csv_options_needed')
        else:
            self.load_parsed_file_for_import()
        
    
    def load_parsed_file_for_import(self):
        self.loader.load()
        if self.loader.accounts:
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
        action = Action('Import')
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
        return self._undoer.modified
    
    #--- Date Range
    def select_month_range(self, starting_point=None):
        if starting_point is None:
            starting_point = self._date_range_starting_point()
        self.date_range = MonthRange(starting_point)
    
    def select_quarter_range(self, starting_point=None):
        if starting_point is None:
            starting_point = self._date_range_starting_point()
        self.date_range = QuarterRange(starting_point)
    
    def select_year_range(self, starting_point=None):
        if starting_point is None:
            starting_point = self._date_range_starting_point()
        self.date_range = YearRange(starting_point, year_start_month=self.app.year_start_month)
    
    def select_year_to_date_range(self):
        self.date_range = YearToDateRange(year_start_month=self.app.year_start_month)
    
    def select_running_year_range(self):
        self.date_range = RunningYearRange(ahead_months=self.app.ahead_months)
    
    def select_all_transactions_range(self):
        if not self.transactions:
            return
        start_date = self.transactions[0].date
        self.date_range = AllTransactionsRange(start=start_date, ahead_months=self.app.ahead_months)
    
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
        if self.selected_account is not None and self.selected_account not in self.accounts:
            self.select_account(None)
        self.notify('performed_undo_or_redo')
    
    def can_redo(self):
        return self._undoer.can_redo()
    
    def redo_description(self):
        return self._undoer.redo_description()
    
    def redo(self):
        self.stop_edition()
        self._undoer.redo()
        self._cook()
        if self.selected_account is not None and self.selected_account not in self.accounts:
            self.select_account(None)
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
        self.notify('filter_applied')
    
    # use FilterType.* consts or None
    @property
    def filter_type(self):
        return self._filter_type
    
    @filter_type.setter
    def filter_type(self, value):
        if value is self._filter_type:
            return
        self._filter_type = value
        self._visible_transactions = None
        self.notify('filter_applied')
    
    #--- Events
    def ahead_months_changed(self):
        if isinstance(self.date_range, RunningYearRange):
            self.select_running_year_range()
        elif isinstance(self.date_range, AllTransactionsRange):
            self.select_all_transactions_range()
    
    def default_currency_changed(self):
        self.notify('document_changed')
    
    def first_weekday_changed(self):
        self.notify('first_weekday_changed')
    
    def must_autosave(self):
        # this is called async
        self._async_autosave()
    
    def saved_custom_ranges_changed(self):
        self.notify('saved_custom_ranges_changed')
    
    def year_start_month_changed(self):
        if isinstance(self.date_range, YearRange):
            self.select_year_range()
        elif isinstance(self.date_range, YearToDateRange):
            self.select_year_to_date_range()
    
