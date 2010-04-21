# Created By: Virgil Dupras
# Created On: 2008-07-21
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_

from ..base import TestCase, CommonSetup as CommonSetupBase

class CommonSetup(CommonSetupBase):
    def setup_two_transactions(self):
        self.add_account_legacy('Desjardins')
        self.add_entry(description='a Deposit', payee='Joe SixPack', checkno='42A', transfer='Income', increase='212.12')
        # it's important for the test that this txns has no space in its fields
        self.add_entry(description='Withdrawal', payee='Dunno-What-To-Write', checkno='24B', transfer='Cash', decrease='140')
        self.mainwindow.select_transaction_table()
    

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
    
    def test_set_query(self):
        """Setting the 'query' propsert works"""
        self.sfield.query = 'foobar'
        self.assertEqual(self.sfield.query, 'foobar')
    

class TwoTransactions(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_two_transactions()
    
    def test_account(self):
        # when using the 'account:' search form, only account are searched. Also, commas can be used
        # to specify more than one term
        self.sfield.query = 'account: withdrawal,inCome'
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].description, 'a Deposit')
    
    def test_query_amount(self):
        """Amounts can be queried, and the cents, when 0, can be ommited"""
        self.sfield.query = '140'
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].description, 'Withdrawal')
    
    def test_query_amount_exact(self):
        """Amount searches are exact"""
        self.sfield.query = '212'
        self.assertEqual(self.ttable.row_count, 0)
        self.sfield.query = '212.12'
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].description, 'a Deposit')
    
    def test_query_amount_negative(self):
        """When searching for amount, we ignore the amounts' sign"""
        self.sfield.query = '-140'
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].description, 'Withdrawal')
    
    def test_query_description(self):
        """The query is case insensitive and works on description"""
        self.sfield.query = 'wiTH'
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].description, 'Withdrawal')
    
    def test_query_checkno(self):
        """The query works on checkno"""
        self.sfield.query = '42a'
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].description, 'a Deposit')
    
    def test_query_checkno_partial(self):
        """We don't match transactions that only partially match checkno (it doesn't make much sense)"""
        self.sfield.query = '4'
        self.assertEqual(self.ttable.row_count, 0)
    
    def test_query_from(self):
        """The 'from' account can be queried"""
        self.sfield.query = 'desJ'
        self.assertEqual(self.ttable.row_count, 2)
    
    def test_query_payee(self):
        """The query is case insensitive and works on payee"""
        self.sfield.query = 'siX'
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].description, 'a Deposit')
    
    def test_query_space(self):
        # Querying for a space character doesn't cause a crash. Previously, it did because it was
        # parsed as an amount.
        self.mainwindow.select_transaction_table()
        self.sfield.query = ' ' # no crash
        self.assertEqual(self.ttable.row_count, 2) # same as no filter
    
    def test_query_to(self):
        """The 'to' account can be queried"""
        self.sfield.query = 'Come'
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].description, 'a Deposit')
    

class ThreeTransactionsOneWithZeroAmount(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_two_transactions()
        self.add_entry(description='zero-amount')
    
    def test_query_amount(self):
        # querying an amount with a zero amount in the stack doesn't cause a crash
        self.sfield.query = '212.12' # no crash
        self.assertEqual(self.ttable.row_count, 1)
    
    
class Split(TestCase):
    def setUp(self):
        self.create_instances()
        self.mainwindow.select_transaction_table()
        self.ttable.add()
        self.tpanel.load()
        # Here, we're creating a split that looks like:
        # first       42  0
        # second       0 42
        # third       12  0
        # Unasssigned  0 12
        self.stable[0].account = 'first'
        self.stable[0].memo = 'memo1'
        self.stable[0].debit = '42'
        self.stable.save_edits()
        self.stable.select([1])
        self.stable[1].account = 'second'
        self.stable[1].memo = 'memo2'
        self.stable.save_edits()
        self.stable.add()
        self.stable[2].account = 'third'
        self.stable[2].debit = '12'
        self.stable.save_edits()
        self.tpanel.save()
    
    def test_query_memo(self):
        # memo fields are part of the search query
        self.sfield.query = 'memo2'
        self.assertEqual(self.ttable.row_count, 1)
    
    def test_query_split_account(self):
        """Any account in a split can match a sfield query"""
        self.sfield.query = 'third'
        self.assertEqual(self.ttable.row_count, 1)
    

class ThreeTransactionsFiltered(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('some account')
        self.add_entry(description='foo')
        self.add_entry(description='bar')
        self.add_entry(description='bar')
        self.mainwindow.select_transaction_table()
        self.sfield.query = 'bar'
        self.clear_gui_calls()
    
    def test_change_account(self):
        """Changing selection to another account cancels the filter"""
        self.mainwindow.select_balance_sheet()
        self.assertEqual(self.sfield.query, '')
        # setting the sfield query didn't make document go to all_transactions again
        eq_(self.mainwindow.current_view_index, 0)
        self.check_gui_calls(self.sfield_gui, ['refresh'])
        self.mainwindow.select_transaction_table()
        self.assertEqual(self.ttable.row_count, 3)
    
    def test_change_account_to_bsheet(self):
        """Balance sheet is another notification, so we must also test it in addition to 
        test_change_account.
        """
        self.mainwindow.select_balance_sheet()
        self.assertEqual(self.sfield.query, '')
        self.check_gui_calls(self.sfield_gui, ['refresh'])
        self.mainwindow.select_transaction_table()
        self.assertEqual(self.ttable.row_count, 3)
    
    def test_modify_transaction_out_of_filter(self):
        """When changing a txn so it doesn't match the filter anymore, remove it"""
        row = self.ttable.selected_row
        row.description = 'baz'
        self.ttable.save_edits()
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable.selected_indexes, [0])
    

class GroupedAndUngroupedTransactions(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_group('MyGroup')
        self.add_account_legacy('Grouped', group_name='MyGroup')
        self.add_account_legacy('Ungrouped')
        self.add_txn(description='first', from_='Grouped')
        self.add_txn(description='second', from_='Ungrouped')
    
    def test_query_group(self):
        self.sfield.query = 'group:foo,mygRoup'
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].description, 'first')
    
