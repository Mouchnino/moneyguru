# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from hsutil.misc import nonone

class CompletableEdit(object):
    def __init__(self, source=None):
        # `source` must be a CompletionMixIn subclass
        self._source = source
        self._attrname = ''
        self._complete_completion = ''
        self.completion = ''
        self._text = ''
    
    #--- Private
    def _set_completion(self, completion):
        completion = nonone(completion, '')
        self._complete_completion = completion
        self.completion = completion[len(self._text):]
    
    #--- Public
    def commit(self):
        """Accepts current completion and updates the text with it.
        
        If the text is a substring of the completion, completion's case will prevail. If, however,
        the completion is the same length as the text, it means that the user completly types the
        string. In this case, we assume that the user wants his own case to prevail.
        """
        if len(self._text) < len(self._complete_completion):
            self._text = self._complete_completion
            self.completion = ''
    
    def down(self):
        self._set_completion(self.source.prev_completion())
    
    def up(self):
        self._set_completion(self.source.next_completion())
    
    #--- Properties
    @property
    def attrname(self):
        return self._attrname
    
    @attrname.setter
    def attrname(self, value):
        self._attrname = value
        self._text = ''
        self._set_completion('')
    
    @property
    def source(self):
        return self._source
    
    @source.setter
    def source(self, value):
        self._source = value
        self._text = ''
        self._set_completion('')
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = value
        self._set_completion(self.source.complete(self._text, self.attrname))
    
