# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-02-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ...model.account import AccountType
from ..base import TestApp, with_app

#--- Some accounts
def app_accounts():
    app = TestApp()
    app.add_accounts('foo', 'bar', 'Zo-of')
    app.add_account('bo--o-f', AccountType.Income)
    app.mainwindow.jump_to_account()
    return app

@with_app(app_accounts)
def test_adjust_selection_when_narrowing_results(app):
    # When the results go narrower, if the selection goes out of bounds, adjust it.
    app.alookup.selected_index = 2
    app.alookup.search_query = 'b' # now, there's only 2 results
    eq_(app.alookup.selected_index, 1)

@with_app(app_accounts)
def test_search_one_letter(app):
    # Setting the search query triggers a fuzzy search in the name list. Since we're looking for
    # only one letter, there's no result matching more than the other (except for those not matching
    # at all). Therefore, the order in which we show the name stays the same as before.
    app.alookup.search_query = 'o'
    eq_(app.alookup.names, ['bo--o-f', 'foo', 'Zo-of'])

@with_app(app_accounts)
def test_search_two_letters(app):
    # With two letters, it's possible that some names match more than others. Names that start with
    # the exact query are on top. Then, names with those letters closest to each other come next.
    app.alookup.search_query = 'fo'
    eq_(app.alookup.names, ['foo', 'Zo-of', 'bo--o-f'])

@with_app(app_accounts)
def test_search_doesnt_count_the_same_letter_twice(app):
    # When checking if all letters are there, don't count the same letter twice
    app.alookup.search_query = 'ff'
    eq_(app.alookup.names, [])

@with_app(app_accounts)
def test_search_doesnt_count_zero_distance(app):
    # When computing letter distance, ignore indexes that point to the same letter
    app.alookup.search_query = 'oo'
    # first 2 has the same distance, so we stay in alpha sort. Last one has more distance between
    # 'o' chars.
    eq_(app.alookup.names, ['foo', 'Zo-of', 'bo--o-f'])

@with_app(app_accounts)
def test_search_then_search_something_else(app):
    # make sure that the names searched are always the original ones, not the one last filtered
    app.alookup.search_query = 'b'
    app.alookup.search_query = 'foo'
    eq_(app.alookup.names, ['foo', 'Zo-of', 'bo--o-f'])

@with_app(app_accounts)
def test_search_then_jump_again(app):
    # Calling jump_to_account re-initialize fields and selected index
    app.alookup.search_query = 'o'
    app.alookup.selected_index = 1
    app.mainwindow.jump_to_account()
    eq_(app.alookup.search_query, '')
    eq_(app.alookup.selected_index, 0)

@with_app(app_accounts)
def test_search_ignore_case(app):
    # The matching is case-insensitive
    app.alookup.search_query = 'z'
    eq_(app.alookup.names, ['Zo-of'])

@with_app(app_accounts)
def test_search_puts_names_that_start_with_query_first(app):
    # When 2 names have the whole query in them, give priority to names that start with that query.
    app.alookup.search_query = 'f'
    eq_(app.alookup.names, ['foo', 'bo--o-f', 'Zo-of'])

@with_app(app_accounts)
def test_select_and_go(app):
    # Selecting a name and pressing return (go()) shows the account.
    app.alookup.selected_index = 2
    app.alookup.go()
    eq_(app.doc.shown_account.name, 'foo')

#--- Accounts with numbers
def app_accounts_with_number():
    app = TestApp()
    app.add_account('bar')
    app.add_account('foo', account_number='007')
    app.mainwindow.jump_to_account()
    return app

#--- Generators
def test_account_order():
    def check(app, expected):
        eq_(app.alookup.names, expected)
    
    # Accounts are sorted in alphabetical order
    app = app_accounts()
    yield check, app, ['bar', 'bo--o-f', 'foo', 'Zo-of']
    
    # Accounts with numbers are sorted according to their combined display
    app = app_accounts_with_number()
    yield check, app, ['007 - foo', 'bar']
