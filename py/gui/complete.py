# Created By: Virgil Dupras
# Created On: 2008-07-13
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..model.completion import CompletionList

class CompletionMixIn(object):
    _completions = None
    
    def _build_candidates(self, attrname):
        if attrname == 'description':
            return self.document.transactions.descriptions
        elif attrname == 'payee':
            return self.document.transactions.payees
        elif attrname in ('from', 'to', 'account', 'transfer'):
            result = self.document.transactions.account_names
            # `result` doesn't contain empty accounts' name, so we'll add them.
            result += [a.name for a in self.document.accounts]
            if attrname == 'transfer' and self.document.selected_account is not None:
                result = [name for name in result if name != self.document.selected_account.name]
            return result
    
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
    
