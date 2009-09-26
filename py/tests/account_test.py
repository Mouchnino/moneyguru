# coding=utf-8
# Created By: Virgil Dupras
# Created On: 2008-06-15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os.path as op

from nose.tools import eq_

from hsutil.currency import EUR

from .base import TestCase, TestSaveLoadMixin
from ..exception import FileFormatError
from ..model.account import ASSET, LIABILITY, INCOME

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
    
    def test_delete_account(self):
        """No crash occurs when trying to delete a group that can't be deleted"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets
        self.assertFalse(self.bsheet.can_delete())
        self.bsheet.delete()
    
    def test_delete_special_accounts(self):
        """special accounts cannot be deleted"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets
        self.assertFalse(self.bsheet.can_delete())
        self.bsheet.selected = self.bsheet.assets[0] # total node
        self.assertFalse(self.bsheet.can_delete())
        self.bsheet.selected = self.bsheet.assets[1] # blank node
        self.assertFalse(self.bsheet.can_delete())
    

class OneEmptyAccount(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('Checking', EUR)
    
    def test_accounts_count(self):
        """Check that the account is put in the assets section"""
        self.assertEqual(self.account_names(), ['Checking'])
        self.assertEqual(self.bsheet.assets.children_count, 3)
    
    def test_can_edit_account_name(self):
        """The name of base groups and the Imbalance account cannot be edited"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.assertTrue(self.bsheet.selected.can_edit_name)
        self.bsheet.selected = self.bsheet.assets
        self.assertFalse(self.bsheet.selected.can_edit_name)
        self.bsheet.selected = self.bsheet.assets[1] # total node
        self.assertFalse(self.bsheet.selected.can_edit_name)
        self.bsheet.selected = self.bsheet.assets[2] # blank node
        self.assertFalse(self.bsheet.selected.can_edit_name)
    
    def test_empty_account_name(self):
        """An empty account name is not allowed"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.selected.name = ''
        self.assertEqual(self.bsheet.assets[0].name, 'Checking')

    def test_get_account_attribute_value(self):
        """get_account_*() returns the correct values"""
        self.apanel.load()
        self.assertEqual(self.apanel.name, 'Checking')
        self.assertEqual(self.apanel.currency, EUR)
        self.assertEqual(self.apanel.type, ASSET)
    
    def test_keep_old_accounts_on_load_failure(self):
        """When a load result in a failure, keep the data that was there previously"""
        filename = self.filepath('randomfile')
        try:
            self.document.load_from_xml(filename)
        except FileFormatError:
            pass
        self.assertEqual(self.account_names(), ['Checking'])
    
    def test_move_account(self):
        """move_account() methods to change the account type and move it to the correct section"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.move([0, 0], [1])
        self.assertEqual(self.bsheet.get_node([0]).children_count, 2) # 1 total node, 1 blank node
        self.assertEqual(self.bsheet.get_node([1]).children_count, 3) # 1 total node, 1 blank node
        self.bsheet.move([1, 0], [0])
        self.assertEqual(self.bsheet.get_node([0]).children_count, 3) # 1 total node, 1 blank node
        self.assertEqual(self.bsheet.get_node([1]).children_count, 2) # 1 total node, 1 blank node
    
    def test_move_account_makes_the_app_dirty(self):
        """calling make_account_asset() makes the app dirty"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.move([0, 0], [1])
        self.assertTrue(self.document.is_dirty())
    

class ThreeEmptyAccounts(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('one')
        self.add_account('two')
        self.add_account('three') # This is the selected account (in second position)
    
    def test_accent_sorting(self):
        """Letters with accents should be sorted according to their decomposed form"""
        self.add_account_legacy(u'é')
        self.assertEqual(self.account_names(), [u'é', 'one', 'three', 'two'])
    
    def test_account_sort(self):
        """Accounts are sorted alphabetically"""
        self.assertEqual(self.account_names(), ['one', 'three', 'two'])
    
    def test_account_sort_is_case_insensitive(self):
        """The account sort is case insensitive"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # three
        self.bsheet.selected.name = 'THREE'
        self.bsheet.save_edits()
        self.assertEqual(self.account_names(), ['one', 'THREE', 'two'])
    
    def test_can_move_account(self):
        """An account can only be moved in an account group that is on the 2nd or 3rd level"""
        self.mainwindow.select_balance_sheet()
        self.assertTrue(self.bsheet.can_move([0, 0], [1])) # Can move into Liabilities
        self.assertFalse(self.bsheet.can_move([0, 0], [])) # Cannot move in Root
        self.assertFalse(self.bsheet.can_move([0, 0], [0])) # Cannot move in Assets
        self.assertFalse(self.bsheet.can_move([0, 0], [0, 1])) # Cannot move in another account
    
    def test_delete_first_account(self):
        """Keep the selection there"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.delete()
        self.assertEqual(self.account_names(), ['three', 'two'])
        self.assertEqual(self.bsheet.selected_path, [0, 0])
    
    def test_delete_last_account(self):
        """When a deletion causes the account selection to go in the next section, stay in the current section."""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.delete()
        self.assertEqual(self.account_names(), ['one', 'two']) 
        self.assertEqual(self.bsheet.selected_path, [0, 1])
    
    def test_account_name(self):
        """account_name() uses the index arg"""
        self.assertEqual(self.bsheet.assets[2].name, 'two')
    
    def test_set_account_name_duplicate(self):
        """save_edits() reverts to the old name when the name already exists (case insensitive)"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # three
        self.bsheet.selected.name = 'ONE'
        self.bsheet.save_edits()
        self.assertEqual(self.bsheet.selected.name, 'three')
    
    def test_set_account_name_same_name(self):
        """Don't raise DuplicateAccountNameError when the duplicate name is the account being
        edited.
        """
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # three
        self.bsheet.selected.name = 'Three'
        self.bsheet.save_edits()
        self.assertEqual(self.bsheet.selected.name, 'Three')
    

class OneAccountAndOneGroup(TestCase, TestSaveLoadMixin):
    # TestSaveLoadMixin is to make sure that empty groups are kept when saving/loading
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_group()
        # The group is selected
    
    def test_can_delete_group(self):
        """can_delete_account() returns True for user created groups"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.assertTrue(self.bsheet.can_delete())
    
    def test_delete_group(self):
        """delete_account() on a user created group removes the group"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.delete()
        self.assertEqual(self.bsheet.assets.children_count, 3) # total + blank
    
    def test_move_account_to_group(self):
        """Accounts can be moved into user created groups"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected_path = [0, 0] # select the group
        self.assertTrue(self.bsheet.can_move([0, 1], [0, 0]))
        self.bsheet.move([0, 1], [0, 0])
        self.assertEqual(self.bsheet.get_node([0]).children_count, 3) # 1 total node, 1 blank node
        self.assertEqual(self.bsheet.get_node([0, 0]).children_count, 3) # 1 total node, 1 blank node
    
    def test_move_two_accounts(self):
        """Account groups can contain more than one account"""
        # Refresh was previously bugged when more than one account were in the same group
        self.add_account_legacy()
        self.mainwindow.select_balance_sheet()
        self.bsheet.move([0, 1], [0, 0])
        self.bsheet.move([0, 1], [0, 0])
        self.assertEqual(self.bsheet.get_node([0, 0]).children_count, 4) # 1 total node, 1 blank node
    
    def test_sort_order(self):
        """Groups are always first"""
        self.mainwindow.select_balance_sheet()
        self.assertEqual(self.bsheet.assets[0].name, 'New group')
        self.assertEqual(self.bsheet.assets[1].name, 'New account')
    
    def test_user_groups_are_editable(self):
        """User created groups can have their name edited"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.assertTrue(self.bsheet.selected.can_edit_name)
        self.bsheet.selected.name = 'foobar'
        self.assertEqual(self.bsheet.assets[0].name, 'foobar')
    

class OneAccountInOneGroup(TestCase, TestSaveLoadMixin):
    # TestSaveLoadMixin is to make sure that groups are saved
    def setUp(self):
        self.create_instances()
        self.add_group('group')
        self.add_account_legacy(group_name='group')
        self.mainwindow.select_balance_sheet()
    
    def test_change_account_type(self):
        # When changing the account type through apanel, an account under a group wouldn't want to
        # leave its group, thus refusing to go to its real type's base node.
        self.bsheet.selected = self.bsheet.assets[0][0]
        self.apanel.load()
        self.apanel.type_index = 1 # liability
        self.apanel.save()
        eq_(len(self.bsheet.assets[0]), 2) # group is empty (2 is for the total nodes)
        eq_(len(self.bsheet.liabilities), 3) # the account is in liabilities
    
    def test_delete_account(self):
        """It's possible to delete an account that is inside a user created group"""
        self.bsheet.selected = self.bsheet.assets[0][0]
        self.bsheet.delete()
        self.assertEqual(self.bsheet.assets[0].children_count, 2) # total + blank
    
    def test_delete_group(self):
        """Deleteing a group with an account in it removes the group and put the account back at the
        base group level
        """
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.delete()
        self.assertFalse(self.bsheet.assets[0].is_group)
    
    def test_move_account_in_another_base_group(self):
        """Moving the account in another account base group does not result in a crash"""
        # Previously, the edit system was working with None values to indicate "no edition", which
        # made it impossible to set the group to None.
        self.bsheet.move([0, 0, 0], [1])
        self.assertEqual(self.bsheet.get_node([0, 0]).children_count, 2) # 1 total node, 1 blank node
        self.assertEqual(self.bsheet.get_node([1]).children_count, 3) # 1 total node, 1 blank node
    

class TwoGroups(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_group()
        self.add_group()
        self.mainwindow.select_balance_sheet()
    
    def test_new_group_name(self):
        """When 'New group' already exists, another new group is created with a number"""
        self.assertEqual(self.bsheet.assets[1].name, 'New group 1')
    
    def test_rename_clash(self):
        """A group cannot be renamed to a name with the same name as another group *in the same type*"""
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.selected.name = 'neW grOup'
        self.bsheet.save_edits()
        self.assertEqual(self.bsheet.selected.name, 'New group 1')
    

class TwoGroupsInTwoBaseTypes(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_group()
        self.add_group(account_type=LIABILITY)
        self.mainwindow.select_balance_sheet()
    
    def test_new_group_name(self):
        """Groups in different base types can have the same name"""
        self.assertEqual(self.bsheet.liabilities[0].name, 'New group')
    

class AccountAndGroupWithTheSameName(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_group()
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.selected.name = 'some_name'
        self.bsheet.save_edits()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.selected.name = 'some_name'
    
    def test_move_account_in_group(self):
        """Moving an account in a group of the same name doesn't cause any problem"""
        self.bsheet.move([0, 1], [0, 0])
        self.assertEqual(self.bsheet.get_node([0, 0]).children_count, 3) # 1 total node, 1 blank node
    

class DifferentAccountTypes(TestCase):
    """Two accounts of asset type, and one account of income type."""
    def setUp(self):
        self.create_instances()
        self.add_account('one')
        self.add_account_legacy('two')
        self.add_entry(transfer='three')
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0] # 'three'
        self.istatement.show_selected_account()
    
    def test_account_name(self):
        """account_name() can get the name of an account even if it's an income account"""
        self.assertEqual(self.istatement.income[0].name, 'three')
    
    def test_account_names(self):
        """the income account comes after the assets accounts"""
        self.assertEqual(self.account_names(), ['one', 'two', 'three'])
    
    def test_delete_account(self):
        """delete_account() takes place in the currently selected account type"""
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0] # three
        self.istatement.delete()
        self.arpanel.ok() # continue deletion
        self.assertEqual(self.account_names(), ['one', 'two'])
    
    def test_account_group_size(self):
        """The account group counts correct"""
        self.mainwindow.select_balance_sheet()
        self.assertEqual(self.bsheet.assets.children_count, 4)
        self.assertEqual(self.bsheet.liabilities.children_count, 2)
        self.mainwindow.select_income_statement()
        self.assertEqual(self.istatement.income.children_count, 3)
        self.assertEqual(self.istatement.expenses.children_count, 2)
    
    def test_select_another_type_then_set_attribute_value(self):
        """select_account() works across accounts sections"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1]
        self.bsheet.selected.name = 'foo'
        self.bsheet.save_edits()
        self.assertEqual(self.account_names(), ['foo', 'one', 'three'])
    

class EntryWithoutTransfer(TestCase):
    """An entry without a transfer account set"""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_entry(description='foobar', decrease='130')
    
    def test_delete_account(self):
        """Deleting an account don't rebind imbalanced entries, but delete them instead"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.delete()
        self.arpanel.ok() # continue deletion
        self.mainwindow.select_transaction_table()
        self.assertEqual(len(self.ttable), 0)
    

class TwoBoundEntries(TestCase):
    """2 entries in 2 accounts 'first' and 'second' that are part of the same transaction. There is 
    a 'third', empty account. 'second' is selected.
    """
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('first')
        self.add_account_legacy('second')
        self.add_entry(description='transfer', transfer='first', increase='42')
        self.add_account_legacy('third')
    
    def test_delete_account(self):
        """Deleting an account unbinds every entries in it, but does *not* delete the bound entries
        """
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[1] # second
        self.bsheet.delete()
        self.bsheet.selected = self.bsheet.assets[0] # second
        self.bsheet.show_selected_account()
        self.assertEqual(len(self.etable), 1)
        self.etable.delete() # Doesn't crash, the entry has been unbound
    

class TwoEntriesWithTransfer(TestCase):
    """Two entries, in range, both having a different transfer"""
    def setUp(self):
        self.create_instances()
        self.add_account_legacy()
        self.add_entry('1/10/2007', 'entry1', transfer='transfer1', increase='1')
        self.add_entry('2/10/2007', 'entry2', transfer='transfer2', increase='2')
    
    def test_delete_asset_account(self):
        """When deleting the asset account, entry1 and entry2 go to imbalance"""
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.delete()
        self.arpanel.ok() # continue deletion
        self.assertEqual(self.account_names(), ['transfer1', 'transfer2'])
        self.mainwindow.select_transaction_table()
        self.assertEqual(len(self.ttable), 2)
        self.assertEqual(self.ttable[0].to, '')
        self.assertEqual(self.ttable[1].to, '')
    
    def test_delete_transfer1_account(self):
        """When deleting transfer1, entry1 goes to imbalance"""
        self.mainwindow.select_income_statement()
        self.istatement.selected = self.istatement.income[0] # transfer1
        self.istatement.delete()
        self.arpanel.ok() # continue deletion
        self.assertEqual(self.account_names(), ['New account', 'transfer2'])
        self.mainwindow.select_transaction_table()
        self.assertEqual(len(self.ttable), 2)
        self.assertEqual(self.ttable[0].from_, '')
    

class ManuallyCreatedIncome(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('income', account_type=INCOME)
        self.add_account_legacy('asset')
    
    def test_auto_clean_doesnt_clean_manually_created(self):
        # We add & remove an entry to trigger auto clean. The manually created account must not be 
        # removed.
        self.add_entry()
        self.etable.delete()
        self.mainwindow.select_income_statement()
        self.assertEqual(self.istatement.income[0].name, 'income')
    
