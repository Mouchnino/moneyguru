# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-28
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import unicode_literals

from hsutil.testutil import eq_

from ..base import TestApp, with_app

# XXX These tests are flaky on windows because completion order is defined by mtime and all txns
# have the same mtime. Fix this.

#--- Default completable edit
def app_default():
    app = TestApp()
    app.add_txn(description='Bazooka')
    app.add_txn(description='buz')
    app.add_txn(description='bar')
    app.add_txn(description='foo')
    app.add_txn(description='électrique')
    app.ce = app.completable_edit('description')
    return app

@with_app(app_default)
def test_set_text_matching(app):
    # When text is set with text that matches something in the source, the text is completed.
    app.ce.text = 'f'
    eq_(app.ce.completion, 'oo')

@with_app(app_default)
def test_set_text_not_matching(app):
    # When the text doesn't match, there's no completion
    app.ce.text = 'z'
    eq_(app.ce.completion, '')

@with_app(app_default)
def test_commit_partial(app):
    # Commit takes the current completion and sets the text with it, overriding previous upper or
    # lowercase in existing text. That is, however, only if the text is partial to the completion.
    app.ce.text = 'baz'
    app.ce.commit()
    eq_(app.ce.text, 'Bazooka')
    eq_(app.ce.completion, '')

@with_app(app_default)
def test_commit_complete(app):
    # When the user completly types a string, we keep his case intact.
    app.ce.text = 'Buz'
    app.ce.commit()
    eq_(app.ce.text, 'Buz')
    eq_(app.ce.completion, '')

@with_app(app_default)
def test_refresh_candidates_on_txn_change(app):
    # Changing transactions refreshes completion candidates. Note that we only test for transaction
    # addition here, but all transaction/account mutation notifications must be listened to.
    app.ce.text = 'b' # build candidates
    app.add_txn(description='other') # This is supposed to invalidate candidates cache
    app.ce.text = 'o'
    eq_(app.ce.completion, 'ther')

@with_app(app_default)
def test_ignore_accents(app):
    app.ce.text = 'e'
    eq_(app.ce.completion, 'lectrique')
    app.ce.text = 'é'
    eq_(app.ce.completion, 'lectrique')

#--- Edit with match
def app_with_match():
    app = TestApp()
    app.add_txn(description='Bazooka')
    app.add_txn(description='buz')
    app.add_txn(description='bar')
    app.add_txn(description='foo')
    app.ce = app.completable_edit('description')
    app.ce.text = 'b'
    return app

@with_app(app_with_match)
def test_add_text_without_match(app):
    # Settings the text to something that doesn't match makes the completion empty.
    app.ce.text = 'bz'
    eq_(app.ce.completion, '')

@with_app(app_with_match)
def test_up(app):
    # up() makes the completion go up in the list
    app.ce.up()
    eq_(app.ce.completion, 'azooka')

@with_app(app_with_match)
def test_down(app):
    # down() makes the completion go down in the list
    app.ce.down()
    eq_(app.ce.completion, 'uz')

@with_app(app_with_match)
def test_set_attrname(app):
    # Setting the attrname resets text and completion
    app.ce.attrname = 'foo'
    app.ce.commit()
    eq_(app.ce.text, '')
    eq_(app.ce.completion, '')

@with_app(app_with_match)
def test_set_attrname_then_up(app):
    # Setting the attrname has to clear the completion list (so when we press up(), we don't cycle
    # through previous completions).
    app.ce.attrname = 'foo'
    app.ce.up()
    eq_(app.ce.text, '')
    eq_(app.ce.completion, '')
