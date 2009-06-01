# Unit Name: moneyguru.gui.complete
# Created By: Virgil Dupras
# Created On: 2008-07-13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from operator import attrgetter

from hsutil.misc import flatten

from ..document.completion import CompletionList

class CompletionMixIn(object):
    _completions = None
    
    def _build_candidates(self, attrname):
        pass # virtual
    
    def complete(self, value, attrname):
        candidates = self._build_candidates(attrname)
        if not candidates:
            return None
        self._completions = CompletionList(value, candidates)
        return self.current_completion()
    
    def current_completion(self):
        return self._completions.current() if self._completions else None
    
    def next_completion(self):
        return self._completions.next() if self._completions else None

    def prev_completion(self):
        return self._completions.prev() if self._completions else None
    
    def stop_completion(self):
        self._completions = None
    

# XXX The _build_candidates method is called at each keystroke. Doing some kind of caching would be
# wise because the number of entries/transactions involved can be big!

class EntryCompletionMixIn(CompletionMixIn):
    def _build_candidates(self, attrname):
        if self.document.selected_account is None:
            return None
        entries = sorted(self.document.selected_account.entries, key=attrgetter('mtime'), reverse=True)
        if attrname == 'description':
            return [x.description for x in entries]
        elif attrname == 'payee':
            return [x.payee for x in entries]
        elif attrname == 'transfer':
            splits = flatten(e.splits for e in entries)
            candidates = [s.account.name for s in splits if s.account]
            candidates += [account.name for account in self.document.accounts if account is not self.document.selected_account]
            return candidates
    

class TransactionCompletionMixIn(CompletionMixIn):
    def _build_candidates(self, attrname):
        if attrname == 'description':
            return [x.description for x in sorted(self.document.transactions, key=attrgetter('mtime'), reverse=True)]
        elif attrname == 'payee':
            return [x.payee for x in sorted(self.document.transactions, key=attrgetter('mtime'), reverse=True)]
        elif attrname in ('from', 'to', 'account'):
            candidates = []
            for t in sorted(self.document.transactions, key=attrgetter('mtime'), reverse=True):
                candidates += [a.name for a in t.affected_accounts()]
            candidates += [a.name for a in self.document.accounts]
            return candidates
    