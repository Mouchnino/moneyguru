# Created By: Virgil Dupras
# Created On: 2008-06-15
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.testutil import eq_
from hscommon.currency import EUR

from .base import TestApp, with_app, testdata
from ..exception import FileFormatError
from ..model.account import AccountType

#--- Pristine
@with_app(TestApp)
def test_account_names_are_stripped(app):
    # Whitespaces are removed from account names when typed.
    app.add_accounts('foo ', ' bar')
    eq_(app.bsheet.assets[0].name, 'bar')
    eq_(app.bsheet.assets[1].name, 'foo')

@with_app(TestApp)
def test_delete_account(app):
    # No crash occurs when trying to delete a group that can't be deleted.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets
    assert not app.bsheet.can_delete()
    app.bsheet.delete() # no crash

@with_app(TestApp)
def test_delete_root_type_nodes(app):
    # root type nodes cannot be deleted.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets
    assert not app.bsheet.can_delete()
    app.bsheet.selected = app.bsheet.assets[0] # total node
    assert not app.bsheet.can_delete()
    app.bsheet.selected = app.bsheet.assets[1] # blank node
    assert not app.bsheet.can_delete()

#--- One empty account
def app_one_empty_account():
    app = TestApp()
    app.add_account('Checking', EUR, account_number='4242')
    return app

@with_app(app_one_empty_account)
def test_accounts_count(app):
    # Check that the account is put in the assets section.
    eq_(app.account_names(), ['Checking'])
    eq_(app.bsheet.assets.children_count, 3)

@with_app(app_one_empty_account)
def test_can_edit_account_name(app):
    # The name of base groups and the Imbalance account cannot be edited.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    assert app.bsheet.selected.can_edit_name
    app.bsheet.selected = app.bsheet.assets
    assert not app.bsheet.selected.can_edit_name
    app.bsheet.selected = app.bsheet.assets[1] # total node
    assert not app.bsheet.selected.can_edit_name
    app.bsheet.selected = app.bsheet.assets[2] # blank node
    assert not app.bsheet.selected.can_edit_name

@with_app(app_one_empty_account)
def test_empty_account_name(app):
    # An empty account name is not allowed.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.selected.name = ''
    eq_(app.bsheet.assets[0].name, 'Checking')

@with_app(app_one_empty_account)
def test_detect_duplicate_account_names_with_whitespaces(app):
    # Trying to add an account with the same name as another, with only whitespaces as difference
    # is correctly detected as a duplicate account name.
    app.add_account(' checking ')
    eq_(app.account_names(), ['Checking', 'New account'])

@with_app(app_one_empty_account)
def test_get_account_attribute_value(app):
    # get_account_*() returns the correct values.
    app.mw.edit_item()
    eq_(app.apanel.name, 'Checking')
    eq_(app.apanel.currency, EUR)
    eq_(app.apanel.type, AccountType.Asset)

@with_app(app_one_empty_account)
def test_keep_old_accounts_on_load_failure(app):
    # When a load result in a failure, keep the data that was there previously.
    filename = testdata.filepath('randomfile')
    try:
        app.doc.load_from_xml(filename)
    except FileFormatError:
        pass
    eq_(app.account_names(), ['Checking'])

@with_app(app_one_empty_account)
def test_move_account(app):
    # move_account() methods to change the account type and move it to the correct section.
    app.show_nwview()
    app.bsheet.move([[0, 0]], [1])
    eq_(app.account_node_subaccount_count(app.bsheet.get_node([0])), 0)
    eq_(app.account_node_subaccount_count(app.bsheet.get_node([1])), 1)
    app.bsheet.move([[1, 0]], [0])                                
    eq_(app.account_node_subaccount_count(app.bsheet.get_node([0])), 1)
    eq_(app.account_node_subaccount_count(app.bsheet.get_node([1])), 0)

@with_app(app_one_empty_account)
def test_move_account_makes_the_app_dirty(app):
    # calling make_account_asset() makes the app dirty.
    app.show_nwview()
    app.bsheet.move([[0, 0]], [1])
    assert app.doc.is_dirty()

@with_app(app_one_empty_account)
def test_save_and_load(app):
    # account_number is kept when saving and reloading
    newapp = app.save_and_load()
    newapp.show_nwview()
    eq_(newapp.bsheet.assets[0].account_number, '4242')

#--- Three empty accounts
def app_three_empty_accounts():
    app = TestApp()
    app.add_accounts('one', 'two', 'three')
    app.show_nwview()
    return app

@with_app(app_three_empty_accounts)
def test_accent_sorting(app):
    # Letters with accents should be sorted according to their decomposed form.
    app.add_account('é')
    eq_(app.account_names(), ['é', 'one', 'three', 'two'])

@with_app(app_three_empty_accounts)
def test_account_sort(app):
    # Accounts are sorted alphabetically.
    eq_(app.account_names(), ['one', 'three', 'two'])

@with_app(app_three_empty_accounts)
def test_account_sort_is_case_insensitive(app):
    # The account sort is case insensitive.
    app.bsheet.selected = app.bsheet.assets[1] # three
    app.bsheet.selected.name = 'THREE'
    app.bsheet.save_edits()
    eq_(app.account_names(), ['one', 'THREE', 'two'])

@with_app(app_three_empty_accounts)
def test_can_move_account(app):
    # An account can only be moved in an account group that is on the 2nd or 3rd level.
    assert app.bsheet.can_move([[0, 0]], [1]) # Can move into Liabilities
    assert not app.bsheet.can_move([[0, 0]], []) # Cannot move in Root
    assert not app.bsheet.can_move([[0, 0]], [0]) # Cannot move in Assets
    assert not app.bsheet.can_move([[0, 0]], [0, 1]) # Cannot move in another account

@with_app(app_three_empty_accounts)
def test_can_move_multiple_accounts(app):
    # When multiple accounts are selected, it's possible to move them too.
    assert app.bsheet.can_move([[0, 0], [0, 1]], [1]) # can move one and three
    assert not app.bsheet.can_move([[0], [0, 0]], [1]) # can't move when one node in the selection can't be moved

@with_app(app_three_empty_accounts)
def test_delete_first_account(app):
    # Keep the selection there.
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    eq_(app.account_names(), ['three', 'two'])
    eq_(app.bsheet.selected_path, [0, 0])

@with_app(app_three_empty_accounts)
def test_delete_last_account(app):
    # When a deletion causes the account selection to go in the next section, stay in the
    # current section.
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.delete()
    eq_(app.account_names(), ['one', 'two']) 
    eq_(app.bsheet.selected_path, [0, 1])

@with_app(app_three_empty_accounts)
def test_move_multiple_accounts(app):
    # move_account() methods to change the account type and move it to the correct section.
    app.bsheet.move([[0, 0], [0, 1]], [1])
    eq_(app.account_node_subaccount_count(app.bsheet.assets), 1)
    eq_(app.account_node_subaccount_count(app.bsheet.liabilities), 2)

@with_app(app_three_empty_accounts)
def test_set_account_name_duplicate(app):
    # save_edits() reverts to the old name when the name already exists (case insensitive).
    app.bsheet.selected = app.bsheet.assets[1] # three
    app.bsheet.selected.name = 'ONE'
    app.bsheet.save_edits()
    eq_(app.bsheet.selected.name, 'three')

@with_app(app_three_empty_accounts)
def test_set_account_name_same_name(app):
    # Don't raise DuplicateAccountNameError when the duplicate name is the account being edited.
    app.bsheet.selected = app.bsheet.assets[1] # three
    app.bsheet.selected.name = 'Three'
    app.bsheet.save_edits()
    eq_(app.bsheet.selected.name, 'Three')

#--- One account and one group
def app_one_account_and_one_group():
    app = TestApp()
    app.add_account()
    app.add_group() # The group is selected
    return app

@with_app(app_one_account_and_one_group)
def test_can_delete_group(app):
    # can_delete_account() returns True for user created groups.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    assert app.bsheet.can_delete()

@with_app(app_one_account_and_one_group)
def test_delete_group(app):
    # delete_account() on a user created group removes the group.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    eq_(app.bsheet.assets.children_count, 3) # total + blank

@with_app(app_one_account_and_one_group)
def test_move_account_to_group(app):
    # Accounts can be moved into user created groups.
    app.show_nwview()
    app.bsheet.selected_path = [0, 0] # select the group
    assert app.bsheet.can_move([[0, 1]], [0, 0])
    app.bsheet.move([[0, 1]], [0, 0])
    eq_(app.bsheet.get_node([0]).children_count, 3) # 1 total node, 1 blank node
    eq_(app.bsheet.get_node([0, 0]).children_count, 3) # 1 total node, 1 blank node

@with_app(app_one_account_and_one_group)
def test_move_two_accounts(app):
    # Account groups can contain more than one account.
    # Refresh was previously bugged when more than one account were in the same group
    app.add_account()
    app.bsheet.move([[0, 1]], [0, 0])
    app.bsheet.move([[0, 1]], [0, 0])
    eq_(app.bsheet.get_node([0, 0]).children_count, 4) # 1 total node, 1 blank node

@with_app(app_one_account_and_one_group)
def test_sort_order(app):
    # Groups are always first.
    app.show_nwview()
    eq_(app.bsheet.assets[0].name, 'New group')
    eq_(app.bsheet.assets[1].name, 'New account')

@with_app(app_one_account_and_one_group)
def test_user_groups_are_editable(app):
    # User created groups can have their name edited.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    assert app.bsheet.selected.can_edit_name
    app.bsheet.selected.name = 'foobar'
    eq_(app.bsheet.assets[0].name, 'foobar')

#--- One account in one group
def app_one_account_in_one_group():
    app = TestApp()
    app.add_group('group')
    app.add_account(group_name='group')
    return app

@with_app(app_one_account_in_one_group)
def test_change_account_type(app):
    # When changing the account type through apanel, an account under a group wouldn't want to
    # leave its group, thus refusing to go to its real type's base node.
    app.bsheet.selected = app.bsheet.assets[0][0]
    app.mw.edit_item()
    app.apanel.type_list.select(1) # liability
    app.apanel.save()
    eq_(app.account_node_subaccount_count(app.bsheet.assets[0]), 0) # group is empty
    eq_(app.account_node_subaccount_count(app.bsheet.liabilities), 1) # the account is in liabilities

@with_app(app_one_account_in_one_group)
def test_delete_account_inside_group(app):
    # It's possible to delete an account that is inside a user created group.
    app.bsheet.selected = app.bsheet.assets[0][0]
    app.bsheet.delete()
    eq_(app.account_node_subaccount_count(app.bsheet.assets[0]), 0)

@with_app(app_one_account_in_one_group)
def test_delete_group_with_account_in_it(app):
    # Deleteing a group with an account in it removes the group and put the account back at the
    # base group level.
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    assert not app.bsheet.assets[0].is_group

@with_app(app_one_account_in_one_group)
def test_move_account_in_another_base_group(app):
    # Moving the account in another account base group does not result in a crash.
    # Previously, the edit system was working with None values to indicate "no edition", which
    # made it impossible to set the group to None.
    app.bsheet.move([[0, 0, 0]], [1])
    eq_(app.account_node_subaccount_count(app.bsheet.get_node([0, 0])), 0)
    eq_(app.account_node_subaccount_count(app.bsheet.get_node([1])), 1)

#--- Two groups
def app_two_groups():
    app = TestApp()
    app.add_group()
    app.add_group()
    app.show_nwview()
    return app

@with_app(app_two_groups)
def test_new_group_name(app):
    # When 'New group' already exists, another new group is created with a number.
    eq_(app.bsheet.assets[1].name, 'New group 1')

@with_app(app_two_groups)
def test_rename_clash(app):
    # A group cannot be renamed to a name with the same name as another group *in the same type*.
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.selected.name = 'neW grOup'
    app.bsheet.save_edits()
    eq_(app.bsheet.selected.name, 'New group 1')

#--- Two groups in two base types
def app_two_groups_in_two_base_types():
    app = TestApp()
    app.add_group()
    app.add_group(account_type=AccountType.Liability)
    app.show_nwview()
    return app

@with_app(app_two_groups_in_two_base_types)
def test_same_group_name_in_different_type(app):
    # Groups in different base types can have the same name.
    eq_(app.bsheet.liabilities[0].name, 'New group')

#--- Account and group with same name
def app_account_and_group_with_same_name():
    app = TestApp()
    app.add_account()
    app.add_group()
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.selected.name = 'some_name'
    app.bsheet.save_edits()
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.selected.name = 'some_name'
    return app

@with_app(app_account_and_group_with_same_name)
def test_move_account_in_group(app):
    # Moving an account in a group of the same name doesn't cause any problem.
    app.bsheet.move([[0, 1]], [0, 0])
    eq_(app.bsheet.get_node([0, 0]).children_count, 3) # 1 total node, 1 blank node

#--- Different account types
def app_different_account_types():
    app = TestApp()
    app.add_account('one')
    app.add_account('two')
    app.show_account()
    app.add_entry(transfer='three')
    app.show_pview()
    app.istatement.selected = app.istatement.income[0] # 'three'
    app.show_account()
    return app

@with_app(app_different_account_types)
def test_account_group_size(app):
    # The account group counts correct.
    app.show_nwview()
    eq_(app.account_node_subaccount_count(app.bsheet.assets), 2)
    eq_(app.account_node_subaccount_count(app.bsheet.liabilities), 0)
    app.show_pview()
    eq_(app.account_node_subaccount_count(app.istatement.income), 1)
    eq_(app.account_node_subaccount_count(app.istatement.expenses), 0)

@with_app(app_different_account_types)
def test_select_another_type_then_set_attribute_value(app):
    # select_account() works across accounts sections.
    app.show_nwview()
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.selected.name = 'foo'
    app.bsheet.save_edits()
    eq_(app.account_names(), ['foo', 'one', 'three'])

#--- One Transaction
def app_one_transaction():
    app = TestApp()
    app.add_account('first')
    app.add_account('second')
    app.add_account('third')
    app.add_txn(description='transfer', from_='first', to='second', amount='42')
    app.show_nwview()
    return app

@with_app(app_one_transaction)
def test_delete_account_unbinds_transactions(app):
    # Deleting an account unbinds every entries in it, but does *not* delete the bound txns.
    app.bsheet.selected = app.bsheet.assets[1] # second
    app.bsheet.delete()
    app.arpanel.save()
    app.show_tview()
    eq_(app.ttable.row_count, 1)
    eq_(app.ttable[0].from_, 'first')
    eq_(app.ttable[0].to, '')

#--- Manually created income
def app_manually_created_income():
    app = TestApp()
    app.add_account('income', account_type=AccountType.Income)
    app.add_account('asset')
    return app

@with_app(app_manually_created_income)
def test_auto_clean_doesnt_clean_manually_created(app):
    # We add & remove an entry to trigger auto clean. The manually created account must not be 
    # removed.
    app.show_account('asset')
    app.add_entry()
    app.etable.delete()
    app.show_pview()
    eq_(app.istatement.income[0].name, 'income')

#--- Account with accents and number
def app_account_with_accents_and_number():
    app = TestApp()
    app.add_account('fooé', account_number='123')
    return app

@with_app(app_account_with_accents_and_number)
def test_add_txn(app):
    # When the from/to columns are populated (using combined_display), don't crash because of unicode.
    app.add_txn(from_='fooé', amount='42') # no crash
    eq_(app.ttable[0].from_, '123 - fooé')
