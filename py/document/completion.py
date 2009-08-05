# Created By: Eric Mc Sween
# Created On: 2007-05-08
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

class CompletionList(object):
    def __init__(self, partial, candidates):
        """Build a completion list.

        'partial' is the partial value to be completed
        'candidates' is the list of candidate values to be tried, the most likely candidate first."""
        if not partial:
            self._completions = None
            return
        partial = partial.lower()
        self._completions = []
        for candidate in candidates:
            candidate = candidate.strip()
            if candidate.lower().startswith(partial) and candidate not in self._completions:
                self._completions.insert(0, candidate)
        if self._completions:
            self._index = len(self._completions) - 1

    def current(self):
        return self._completions[self._index] if self._completions else None

    def next(self):
        if not self._completions:
            return None
        self._index = (self._index + 1) % len(self._completions)
        return self.current()

    def prev(self):
        if not self._completions:
            return None
        self._index = (self._index - 1) % len(self._completions)
        return self.current()
