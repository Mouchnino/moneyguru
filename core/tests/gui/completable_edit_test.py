# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ...gui.complete import CompletionMixIn
from ...gui.completable_edit import CompletableEdit

class CompletionSource(CompletionMixIn):
    def __init__(self, attrname, strings):
        self.attrname = attrname
        self.strings = strings
    
    def _build_candidates(self, attrname):
        if attrname == self.attrname:
            return self.strings[:]
        else:
            return []
    

SOME_STRINGS = ['foo', 'bar', 'buz', 'Bazooka']

#--- Default edit
def edit_default():
    edit = CompletableEdit(CompletionSource('someattr', SOME_STRINGS))
    edit.attrname = 'someattr'
    return edit

def test_set_text_matching():
    # When text is set with text that matches something in the source, the text is completed.
    e = edit_default()
    e.text = 'f'
    eq_(e.completion, 'oo')

def test_set_text_not_matching():
    # When the text doesn't match, there's no completion
    e = edit_default()
    e.text = 'z'
    eq_(e.completion, '')

def test_commit_partial():
    # Commit takes the current completion and sets the text with it, overriding previous upper or
    # lowercase in existing text. That is, however, only if the text is partial to the completion.
    e = edit_default()
    e.text = 'baz'
    e.commit()
    eq_(e.text, 'Bazooka')
    eq_(e.completion, '')

def test_commit_complete():
    # When the user completly types a string, we keep his case intact.
    e = edit_default()
    e.text = 'Buz'
    e.commit()
    eq_(e.text, 'Buz')
    eq_(e.completion, '')

#--- Edit with match
def edit_with_match():
    edit = CompletableEdit(CompletionSource('someattr', SOME_STRINGS))
    edit.attrname = 'someattr'
    edit.text = 'b'
    return edit

def test_add_text_without_match():
    # Settings the text to something that doesn't match makes the completion empty.
    e = edit_with_match()
    e.text = 'bz'
    eq_(e.completion, '')

def test_up():
    # up() makes the completion go up in the list
    e = edit_with_match()
    e.up()
    eq_(e.completion, 'azooka')

def test_down():
    # down() makes the completion go down in the list
    e = edit_with_match()
    e.down()
    eq_(e.completion, 'uz')

def test_set_source():
    # Setting the source resets text and completion
    e = edit_with_match()
    e.source = e.source
    e.commit()
    eq_(e.text, '')
    eq_(e.completion, '')

def test_set_attrname():
    # Setting the attrname resets text and completion
    e = edit_with_match()
    e.attrname = 'foo'
    e.commit()
    eq_(e.text, '')
    eq_(e.completion, '')
