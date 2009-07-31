# Unit Name: moneyguru.gui.import_window
# Created By: Virgil Dupras
# Created On: 2008-08-07
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from hsutil.notify import Broadcaster
from hsutil.misc import flatten, dedupe, first

from ..exception import OperationAborted
from .base import DocumentGUIObject

DAY = 'day'
MONTH = 'month'
YEAR = 'year'
MAX_MONTH = 12
MAX_DAY = 31

def last_two_digits(year):
    return year - ((year // 100) * 100)

class AccountPane(object):
    def __init__(self, account, target_account):
        self.account = account
        self._selected_target = target_account
        self.name = account.name
        self.count = len(account.entries)
        self.matches = [] # [[ref, imported]]
        self.max_day = 31
        self.max_month = 12
        self.max_year = 99 # 2 digits
        self._match_entries()
        self._get_date_maximums()
    
    def _get_date_maximums(self):
        entries = self.account.entries[:]
        if not entries:
            return
        self.max_day = max(e.date.day for e in entries)
        self.max_month = max(e.date.month for e in entries)
        self.max_year = max(last_two_digits(e.date.year) for e in entries)
    
    def _match_entries(self):
        to_import = self.account.entries[:]
        reference2entry = {}
        for entry in (e for e in to_import if e.reference):
            reference2entry[entry.reference] = entry
        self.matches = []
        if self.selected_target is not None:
            entries = self.selected_target.entries
            for entry in entries:
                if entry.reference in reference2entry:
                    other = reference2entry[entry.reference]
                    if entry.reconciled:
                        other.will_import = False
                    to_import.remove(other)
                    del reference2entry[entry.reference]
                else:
                    other = None
                if other is not None or not entry.reconciled:
                    self.matches.append([entry, other])
        self.matches += [[None, entry] for entry in to_import]
        self._sort_matches()
    
    def _sort_matches(self):
        self.matches.sort(key=lambda t: t[0].date if t[0] is not None else t[1].date)
        
    
    def bind(self, existing, imported):
        [match1] = [m for m in self.matches if m[0] is existing]
        [match2] = [m for m in self.matches if m[1] is imported]
        match1[1] = match2[1]
        self.matches.remove(match2)
    
    def can_switch_date_fields(self, first, second): # 'day', 'month', 'year'
        both_fields = (first, second)
        assert all(x in [DAY, MONTH, YEAR] for x in both_fields)
        max_value = MAX_MONTH if MONTH in both_fields else MAX_DAY
        return all(getattr(self, 'max_{0}'.format(field)) <= max_value for field in both_fields)
    
    def unbind(self, existing, imported):
        [match] = [m for m in self.matches if m[0] is existing and m[1] is imported]
        match[1] = None
        self.matches.append([None, imported])
        self._sort_matches()
    
    @property
    def selected_target(self):
        return self._selected_target
    
    @selected_target.setter
    def selected_target(self, value):
        self._selected_target = value
        self._match_entries()
    

class ImportWindow(DocumentGUIObject, Broadcaster):
    def __init__(self, view, document):
        DocumentGUIObject.__init__(self, view, document)
        Broadcaster.__init__(self)
        self._selected_pane_index = 0
        self._selected_target_index = 0
        self.panes = []
    
    def _refresh_target_selection(self):
        if not self.panes:
            return
        target = self.selected_pane.selected_target
        self._selected_target_index = 0
        if target is not None:
            try:
                self._selected_target_index = self.target_accounts.index(target) + 1
            except ValueError:
                pass
    
    def _switch_fields(self, panes, switch_func):
        entries = flatten(p.account.entries for p in panes)
        txns = dedupe(e.transaction for e in entries)
        for txn in txns:
            switch_func(txn)
        self.notify('fields_switched')
    
    def can_switch_date_fields(self, first, second): # 'day', 'month', 'year'
        pane = self.selected_pane
        if pane is None:
            return False
        return pane.can_switch_date_fields(first, second)
    
    def close_pane(self, index):
        was_selected = index == self.selected_pane_index
        del self.panes[index]
        if not self.panes:
            self.view.close()
            return
        self._selected_pane_index = min(self._selected_pane_index, len(self.panes) - 1)
        if was_selected:
            self.view.update_selected_pane()
            self.notify('pane_selected')
    
    def import_selected_pane(self):
        pane = self.selected_pane
        matches = pane.matches
        matches = [(e, ref) for ref, e in matches if e is not None and getattr(e, 'will_import', True)]
        if pane.selected_target is not None:
            # We import in an existing account, adjust all the transactions accordingly
            target_account = pane.selected_target
        else:
            target_account = pane.account # pane.account == new account
        try:
            self.document.import_entries(target_account, pane.account, matches)
        except OperationAborted:
            pass
        else:
            self.close_pane(self.selected_pane_index)
            self.view.close_selected_tab()
    
    def refresh_targets(self):
        self.target_accounts = [a for a in self.document.accounts if a.is_balance_sheet_account()]
        self.target_accounts.sort(key=lambda a: a.name.lower())
    
    def refresh_panes(self):
        if not hasattr(self.document, 'loader'):
            return
        self.refresh_targets()
        accounts = [a for a in self.document.loader.accounts if a.is_balance_sheet_account() and a.entries]
        for account in accounts:
            target_account = None
            if self.document.loader.target_account is not None:
                target_account = self.document.loader.target_account
            elif account.reference:
                target_account = first(t for t in self.target_accounts if t.reference == account.reference)
            self.panes.append(AccountPane(account, target_account))
        self._refresh_target_selection()
        self.notify('pane_selected')
    
    def switch_date_fields(self, first, second, apply_to_all=False): # 'day', 'month', 'year'
        assert self.can_switch_date_fields(first, second)
        if apply_to_all:
            panes = [p for p in self.panes if p.can_switch_date_fields(first, second)]
        else:
            panes = [self.selected_pane]
        
        def switch_func(txn):
            date = txn.date
            attrs = {DAY: date.day, MONTH: date.month, YEAR: last_two_digits(date.year)}
            newattrs = {first: attrs[second], second: attrs[first]}
            if YEAR in newattrs:
                newattrs[YEAR] += 2000
            txn.date = txn.date.replace(**newattrs)
        
        self._switch_fields(panes, switch_func)
    
    def switch_description_payee(self, apply_to_all=False):
        if apply_to_all:
            panes = self.panes
        else:
            panes = [self.selected_pane]
        
        def switch_func(txn):
            txn.description, txn.payee = txn.payee, txn.description
        
        self._switch_fields(panes, switch_func)
    
    #--- Properties
    @property
    def selected_pane(self):
        return self.panes[self.selected_pane_index] if self.panes else None
    
    @property
    def selected_pane_index(self):
        return self._selected_pane_index
    
    @selected_pane_index.setter
    def selected_pane_index(self, value):
        if value >= len(self.panes):
            return
        self._selected_pane_index = value
        self._refresh_target_selection()
        self.view.update_selected_pane()
        self.notify('pane_selected')
    
    @property
    def selected_target_account(self):
        return self.selected_pane.selected_target
    
    @property
    def selected_target_account_index(self):
        return self._selected_target_index
    
    @selected_target_account_index.setter
    def selected_target_account_index(self, value):
        target = self.target_accounts[value - 1] if value > 0 else None
        self.selected_pane.selected_target = target
        self._selected_target_index = value
        self.notify('pane_selected')
    
    @property
    def target_account_names(self):
        return ['< New Account >'] + [a.name for a in self.target_accounts]
    
    #--- Events
    def file_loaded_for_import(self):
        self.refresh_panes()
        self.view.refresh()
        self.view.show()
    
    def account_added(self):
        self.refresh_targets()
        self._refresh_target_selection()
        self.view.refresh()
    
    def account_changed(self):
        self.refresh_targets()
        self._refresh_target_selection()
        self.view.refresh()
    
    def account_deleted(self):
        self.refresh_targets()
        self._refresh_target_selection()
        self.view.refresh()
    
