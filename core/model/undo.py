# Created By: Virgil Dupras
# Created On: 2008-06-24
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import copy

from hsutil.misc import extract

from ..model.recurrence import Spawn

ACCOUNT_SWAP_ATTRS = ['name', 'currency', 'type', 'group']
GROUP_SWAP_ATTRS = ['name', 'type']
TRANSACTION_SWAP_ATTRS = ['date', 'description', 'payee', 'checkno', 'position', 'splits']
SPLIT_SWAP_ATTRS = ['account', 'amount', 'reconciliation_date']
SCHEDULE_SWAP_ATTRS = ['start_date', 'repeat_type', 'repeat_every', 'stop_date', 'date2exception', 
                       'date2globalchange', 'date2instances']
BUDGET_SWAP_ATTRS = SCHEDULE_SWAP_ATTRS + ['account', 'target', 'amount']

def swapvalues(first, second, attrs):
    for attr in attrs:
        tmp = getattr(first, attr)
        setattr(first, attr, getattr(second, attr))
        setattr(second, attr, tmp)

class Action(object):
    def __init__(self, description):
        self.description = description
        self.added_accounts = set()
        self.changed_accounts = set()
        self.deleted_accounts = set()
        self.added_groups = set()
        self.changed_groups = set()
        self.deleted_groups = set()
        self.added_transactions = set()
        self.changed_transactions = set()
        self.deleted_transactions = set()
        self.changed_splits = set()
        self.added_schedules = set()
        self.changed_schedules = set()
        self.deleted_schedules = set()
        self.added_budgets = set()
        self.changed_budgets = set()
        self.deleted_budgets = set()
    
    def change_accounts(self, accounts):
        self.changed_accounts |= set((a, copy.copy(a)) for a in accounts)
    
    def change_groups(self, groups):
        self.changed_groups |= set((g, copy.copy(g)) for g in groups)
    
    def change_schedule(self, schedule):
        self.changed_schedules.add((schedule, schedule.replicate()))
        self.changed_transactions.add((schedule.ref, schedule.ref.replicate()))
    
    def change_budget(self, budget):
        self.changed_budgets.add((budget, budget.replicate()))
    
    def change_transactions(self, transactions):
        spawns, normal = extract(lambda t: isinstance(t, Spawn), transactions)
        self.changed_transactions |= set((t, t.replicate()) for t in normal)
        for schedule in set(spawn.recurrence for spawn in spawns):
            self.change_schedule(schedule)
    
    def change_splits(self, splits):
        self.changed_splits |= set((s, copy.copy(s)) for s in splits)
    
    def delete_account(self, account):
        self.deleted_accounts.add(account)
        transactions = set(e.transaction for e in account.entries if not isinstance(e.transaction, Spawn))
        transactions = set(t for t in transactions if not t.affected_accounts() - set([account]))
        self.deleted_transactions |= transactions
        self.change_splits(e.split for e in account.entries)
    

class Undoer(object):
    def __init__(self, accounts, groups, transactions, scheduled, budgets):
        self._actions = []
        self._accounts = accounts
        self._groups = groups
        self._transactions = transactions
        self._scheduled = scheduled
        self._budgets = budgets
        self._index = -1
        self._save_point = None
    
    #--- Private
    def _add_auto_created_accounts(self, transaction):
        for split in transaction.splits:
            if split.account is not None and split.account not in self._accounts:
                self._accounts.add(split.account)
                self._accounts.auto_created.add(split.account)
    
    def _do_adds(self, accounts, groups, transactions, schedules, budgets):
        for account in accounts:
            self._accounts.add(account)
        for group in groups:
            self._groups.append(group)
        for txn in transactions:
            self._transactions.add(txn, keep_position=True)
            self._add_auto_created_accounts(txn)
        for schedule in schedules:
            self._scheduled.append(schedule)
        for budget in budgets:
            self._budgets.append(budget)
    
    def _do_changes(self, action):
        for account, old in action.changed_accounts:
            swapvalues(account, old, ACCOUNT_SWAP_ATTRS)
        for group, old in action.changed_groups:
            swapvalues(group, old, GROUP_SWAP_ATTRS)
        for txn, old in action.changed_transactions:
            self._remove_auto_created_account(txn)
            swapvalues(txn, old, TRANSACTION_SWAP_ATTRS)
            for split in txn.splits:
                split.transaction = txn
            self._add_auto_created_accounts(txn)
        for split, old in action.changed_splits:
            swapvalues(split, old, SPLIT_SWAP_ATTRS)
        for schedule, old in action.changed_schedules:
            swapvalues(schedule, old, SCHEDULE_SWAP_ATTRS)
        for budget, old in action.changed_budgets:
            swapvalues(budget, old, BUDGET_SWAP_ATTRS)
    
    def _do_deletes(self, accounts, groups, transactions, schedules, budgets):
        for account in accounts:
            self._accounts.remove(account)
        for group in groups:
            self._groups.remove(group)
        for txn in transactions:
            self._remove_auto_created_account(txn)
            self._transactions.remove(txn)
        for schedule in schedules:
            self._scheduled.remove(schedule)
        for budget in budgets:
            self._budgets.remove(budget)
    
    def _remove_auto_created_account(self, transaction):
        for split in transaction.splits:
            account = split.account
            # if len(account.entries) == 1, it means that the transactions was last
            if account in self._accounts.auto_created and len(account.entries) == 1:
                self._accounts.remove(account)
    
    #--- Public
    def can_redo(self):
        return self._index < -1
    
    def can_undo(self):
        return -self._index <= len(self._actions)
    
    def clear(self):
        self._actions = []
    
    def undo_description(self):
        if self.can_undo():
            return self._actions[self._index].description
    
    def redo_description(self):
        if self.can_redo():
            return self._actions[self._index + 1].description
    
    def set_save_point(self):
        self._save_point = self._actions[-1] if self._actions else None
    
    def record(self, action):
        if self._index < -1:
            self._actions = self._actions[:self._index + 1]
        self._actions.append(action)
        self._index = -1
    
    def undo(self):
        assert self.can_undo()
        action = self._actions[self._index]
        self._do_adds(action.deleted_accounts, action.deleted_groups, action.deleted_transactions, 
            action.deleted_schedules, action.deleted_budgets)
        self._do_deletes(action.added_accounts, action.added_groups, action.added_transactions,
            action.added_schedules, action.added_budgets)
        self._do_changes(action)
        self._index -= 1
    
    def redo(self):
        assert self.can_redo()
        action = self._actions[self._index + 1]
        self._do_adds(action.added_accounts, action.added_groups, action.added_transactions,
            action.added_schedules, action.added_budgets)
        self._do_deletes(action.deleted_accounts, action.deleted_groups, action.deleted_transactions,
            action.deleted_schedules, action.deleted_budgets)
        self._do_changes(action)
        self._index += 1
    
    #--- Properties
    @property
    def modified(self):
        return self._save_point is not self._actions[self._index] if self.can_undo() else self._save_point is not None
    

