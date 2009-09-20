# Created By: Virgil Dupras
# Created On: 2008-07-13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from operator import attrgetter

from hsutil.misc import flatten

from ..model.completion import CompletionList

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

class TransactionCompletionMixIn(CompletionMixIn):
    def _build_candidates(self, attrname):
        if attrname == 'description':
            return [x.description for x in sorted(self.document.transactions, key=attrgetter('mtime'), reverse=True)]
        elif attrname == 'payee':
            return [x.payee for x in sorted(self.document.transactions, key=attrgetter('mtime'), reverse=True)]
        elif attrname in ('from', 'to', 'account', 'transfer'):
            candidates = []
            for t in sorted(self.document.transactions, key=attrgetter('mtime'), reverse=True):
                candidates += list(t.affected_accounts())
            candidates += self.document.accounts[:]
            if attrname == 'transfer' and self.document.selected_account is not None:
                candidates = [a for a in candidates if a is not self.document.selected_account]
            return [a.name for a in candidates]
    