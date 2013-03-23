# Created By: Eric Mc Sween
# Created On: 2007-05-08
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.util import dedupe

from .sort import sort_string

class CompletionList:
    def __init__(self, partial, candidates):
        """Build a completion list.

        'partial' is the partial value to be completed
        'candidates' is the list of candidate values to be tried, the most likely candidate first."""
        if not partial:
            self._completions = None
            return
        partial = sort_string(partial)
        candidates = dedupe(c.strip() for c in candidates)
        self._completions = []
        for candidate in candidates:
            normalized = sort_string(candidate)
            if normalized.startswith(partial):
                self._completions.append(candidate)
        self._completions.reverse()
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
