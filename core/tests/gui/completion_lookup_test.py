# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-03-04
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license



from hsutil.testutil import eq_

from ..base import TestApp, with_app

def app_default():
    app = TestApp()
    app.add_txn(description='Bazooka', payee='payée', from_='account1', to='account2', amount='42')
    app.add_txn(description='buz', payee='kyle', from_='account1', to='account2', amount='42')
    app.add_txn(description='bar', payee='kate')
    app.add_txn(description='foo')
    app.ce = app.completable_edit('description')
    return app

@with_app(app_default)
def test_dont_put_empty_lines(app):
    # There are no empty lines in the lookup list
    app.add_txn(description='')
    app.add_txn(description=' ')
    app.ce = app.completable_edit('description') # refresh candidates
    app.ce.lookup()
    assert '' not in app.clookup.names
    assert ' ' not in app.clookup.names

@with_app(app_default)
def test_ignore_accents_in_lookups(app):
    # Letters with accents count as letters without in a lookup query.
    app.ce = app.completable_edit('payee')
    app.ce.lookup()
    app.clookup.search_query = 'ee'
    eq_(app.clookup.names, ['payée'])
    app.clookup.search_query = 'ée'
    eq_(app.clookup.names, ['payée'])
    
@with_app(app_default)
def test_lookup_lists_descriptions(app):
    # The lookup, when the edit is empty, show values in alphabetical order
    app.ce.lookup()
    eq_(app.clookup.names, ['bar', 'Bazooka', 'buz', 'foo'])

@with_app(app_default)
def test_lookup_list_has_no_dupe(app):
    # Remove duplicate names from the list.
    app.ce = app.completable_edit('account')
    app.ce.lookup()
    eq_(app.clookup.names, ['account1', 'account2'])

@with_app(app_default)
def test_lookup_with_non_empty_edit(app):
    # If there was already something in the edit, put in the lookup search query. When go() is
    # called afterwards, edit's completion is cleared.
    app.ce.text = 'b'
    app.ce.lookup()
    eq_(app.clookup.search_query, 'b')
    eq_(app.clookup.names, ['bar', 'Bazooka', 'buz'])
    app.clookup.go()
    eq_(app.ce.completion, '')    

@with_app(app_default)
def test_select_name_then_go(app):
    # calling go() changes the text of the completable_edit that called the lookup
    app.ce.lookup()
    app.clookup.search_query = 'b'
    app.clookup.selected_index = 1
    app.clookup.go()
    eq_(app.ce.text, 'Bazooka')

@with_app(app_default)
def test_uppercase_letters_in_query(app):
    # The query works even if there's uppercase letters in it.
    app.ce.lookup()
    app.clookup.search_query = 'B'
    eq_(app.clookup.names, ['bar', 'Bazooka', 'buz'])
