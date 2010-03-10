# Created By: Virgil Dupras
# Created On: 2008-07-25
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_, assert_raises
from hsutil.testutil import with_tmpdir, patch_today

from ..base import TestCase, TestApp
from ...exception import OperationAborted

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
    
    def test_can_load(self):
        # When there's no selection, loading the panel raises OperationAborted
        assert_raises(OperationAborted, self.mepanel.load)
    

class TwoTransactions(TestCase):
    def setUp(self):
        self.create_instances()
        self.mainwindow.select_transaction_table()
        self.ttable.add()
        self.ttable.save_edits()
        self.ttable.add()
        self.ttable.save_edits()
    
    def test_can_load(self):
        # When there is only one txn selected, loading the panel raises OperationAborted
        assert_raises(OperationAborted, self.mepanel.load)
    
    def test_can_load_after_selection(self):
        # When there is more than one txn selected, load() can be called
        # This test has a collateral, which is to make sure that mepanel doesn't have a problem
        # loading txns with splits with None accounts.
        self.ttable.select([0, 1])
        self.mepanel.load() # No OperationAborted
    

#--- Two transactions different values
def app_two_transactions_different_value():
    app = TestApp()
    app.add_account('from1')
    app.mainwindow.show_account()
    app.add_entry(date='06/07/2008', description='description1', payee='payee1', checkno='42', transfer='to1', decrease='42')
    app.add_account('from2')
    app.mainwindow.show_account()
    app.add_entry(date='07/07/2008', description='description2', payee='payee2', checkno='43', transfer='to2', decrease='43')
    app.mainwindow.select_transaction_table()
    app.ttable.select([0, 1])
    app.mepanel.load()
    return app

@patch_today(2010, 2, 20)
def test_attributes():
    # All fields are disabled and empty.
    app = app_two_transactions_different_value()
    assert app.mepanel.can_change_accounts
    assert app.mepanel.can_change_amount
    assert not app.mepanel.date_enabled
    assert not app.mepanel.description_enabled
    assert not app.mepanel.payee_enabled
    assert not app.mepanel.checkno_enabled
    assert not app.mepanel.from_enabled
    assert not app.mepanel.to_enabled
    assert not app.mepanel.amount_enabled
    eq_(app.mepanel.date, '20/02/2010')
    eq_(app.mepanel.description, '')
    eq_(app.mepanel.payee, '')
    eq_(app.mepanel.checkno, '')
    eq_(app.mepanel.from_, '')
    eq_(app.mepanel.to, '')
    eq_(app.mepanel.amount, '0.00')

def test_change_field():
    # Changing a field enables the associated checkbox
    app = app_two_transactions_different_value()
    app.clear_gui_calls()
    app.mepanel.date = '08/07/2008'
    assert app.mepanel.date_enabled
    # just make sure they are not changed all at once
    assert not app.mepanel.description_enabled
    app.check_gui_calls(app.mepanel_gui, ['refresh'])
    app.mepanel.description = 'foobar'
    assert app.mepanel.description_enabled
    app.check_gui_calls(app.mepanel_gui, ['refresh'])
    app.mepanel.payee = 'foobar'
    assert app.mepanel.payee_enabled
    app.check_gui_calls(app.mepanel_gui, ['refresh'])
    app.mepanel.checkno = '44'
    assert app.mepanel.checkno_enabled
    app.check_gui_calls(app.mepanel_gui, ['refresh'])
    app.mepanel.from_ = 'foobar'
    assert app.mepanel.from_enabled
    app.check_gui_calls(app.mepanel_gui, ['refresh'])
    app.mepanel.to = 'foobar'
    assert app.mepanel.to_enabled
    app.check_gui_calls(app.mepanel_gui, ['refresh'])
    app.mepanel.amount = '44'
    assert app.mepanel.amount_enabled
    app.check_gui_calls(app.mepanel_gui, ['refresh'])

def test_change_field_to_none():
    # the mass panel considers replaces None values with ''.
    app = app_two_transactions_different_value()
    app.mepanel.description = None
    app.mepanel.payee = None
    app.mepanel.checkno = None
    app.mepanel.from_ = None
    app.mepanel.to = None
    app.mepanel.amount = None
    assert not app.mepanel.description_enabled
    assert not app.mepanel.payee_enabled
    assert not app.mepanel.checkno_enabled
    assert not app.mepanel.from_enabled
    assert not app.mepanel.to_enabled
    assert not app.mepanel.amount_enabled
    eq_(app.mepanel.description, '')
    eq_(app.mepanel.payee, '')
    eq_(app.mepanel.checkno, '')
    eq_(app.mepanel.from_, '')
    eq_(app.mepanel.to, '')
    eq_(app.mepanel.amount, '0.00')

@with_tmpdir
def test_change_and_save(tmppath):
    # save() performs mass edits on selected transactions.
    app = app_two_transactions_different_value()
    app.tmppath = tmppath
    app.save_file()
    app.mepanel.date = '08/07/2008'
    app.mepanel.description = 'description3'
    app.mepanel.payee = 'payee3'
    app.mepanel.checkno = '44'
    app.mepanel.from_ = 'from3'
    app.mepanel.to = 'to3'
    app.mepanel.amount = '44'
    app.mepanel.save()
    assert app.doc.is_dirty()
    for row in app.ttable.rows:
        eq_(row.date, '08/07/2008')
        eq_(row.description, 'description3')
        eq_(row.payee, 'payee3')
        eq_(row.checkno, '44')
        eq_(row.from_, 'from3')
        eq_(row.to, 'to3')
        eq_(row.amount, '44.00')

def test_change_date_only():
    # Only change checked fields.
    app = app_two_transactions_different_value()
    app.mepanel.date = '08/07/2008'
    app.mepanel.description = 'description3'
    app.mepanel.payee = 'payee3'
    app.mepanel.checkno = '44'
    app.mepanel.from_ = 'from3'
    app.mepanel.to = 'to3'
    app.mepanel.amount = '44'
    app.mepanel.description_enabled = False
    app.mepanel.payee_enabled = False
    app.mepanel.checkno_enabled = False
    app.mepanel.from_enabled = False
    app.mepanel.to_enabled = False
    app.mepanel.amount_enabled = False
    app.mepanel.save()
    row = app.ttable[0]
    eq_(row.date, '08/07/2008')
    eq_(row.description, 'description1')
    eq_(row.payee, 'payee1')
    eq_(row.checkno, '42')
    eq_(row.from_, 'from1')
    eq_(row.to, 'to1')
    eq_(row.amount, '42.00')

def test_change_description_only():
    # test_change_date_only is not enough for complete coverage.
    app = app_two_transactions_different_value()
    app.mepanel.date = '08/07/2008'
    app.mepanel.description = 'description3'
    app.mepanel.date_enabled = False
    app.mepanel.save()
    row = app.ttable[0]
    eq_(row.date, '06/07/2008')
    eq_(row.description, 'description3')

class TwoTransactionsSameValues(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('account1')
        self.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
        self.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
        self.etable.select([0, 1])
        self.mepanel.load()
    
    def test_attributes(self):
        """All fields are disabled but contain the values common to all selection"""
        self.assertFalse(self.mepanel.date_enabled)
        self.assertFalse(self.mepanel.description_enabled)
        self.assertFalse(self.mepanel.payee_enabled)
        self.assertFalse(self.mepanel.checkno_enabled)
        self.assertFalse(self.mepanel.from_enabled)
        self.assertFalse(self.mepanel.to_enabled)
        self.assertFalse(self.mepanel.amount_enabled)
        self.assertEqual(self.mepanel.date, '06/07/2008')
        self.assertEqual(self.mepanel.description, 'description')
        self.assertEqual(self.mepanel.payee, 'payee')
        self.assertEqual(self.mepanel.checkno, '42')
        self.assertEqual(self.mepanel.from_, 'account2')
        self.assertEqual(self.mepanel.to, 'account1')
        self.assertEqual(self.mepanel.amount, '42.00')
    
    def test_change_field_same(self):
        """Don't auto-enable when changing a field to the same value"""
        self.mepanel.date = '06/07/2008'
        self.assertFalse(self.mepanel.date_enabled)
        self.mepanel.description = 'description'
        self.assertFalse(self.mepanel.description_enabled)
        self.mepanel.payee = 'payee'
        self.assertFalse(self.mepanel.payee_enabled)
        self.mepanel.checkno = '42'
        self.assertFalse(self.mepanel.checkno_enabled)
        self.mepanel.from_ = 'account2'
        self.assertFalse(self.mepanel.from_enabled)
        self.mepanel.to = 'account1'
        self.assertFalse(self.mepanel.to_enabled)
        self.mepanel.amount = '42'
        self.assertFalse(self.mepanel.amount_enabled)
    
    def test_load_again(self):
        """load() blanks values when necessary"""
        self.mock_today(2010, 2, 20)
        self.mepanel.date_enabled = True
        self.mepanel.description_enabled = True
        self.mepanel.payee_enabled = True
        self.mepanel.checkno_enabled = True
        self.mepanel.from_enabled = True
        self.mepanel.amount_enabled = True
        self.add_entry(date='07/07/2008') # Now, none of the values are common
        self.etable.select([0, 1, 2])
        self.mepanel.load()
        self.assertFalse(self.mepanel.date_enabled)
        self.assertFalse(self.mepanel.description_enabled)
        self.assertFalse(self.mepanel.payee_enabled)
        self.assertFalse(self.mepanel.checkno_enabled)
        self.assertFalse(self.mepanel.from_enabled)
        self.assertFalse(self.mepanel.to_enabled)
        self.assertFalse(self.mepanel.amount_enabled)
        self.assertEqual(self.mepanel.date, '20/02/2010')
        self.assertEqual(self.mepanel.description, '')
        self.assertEqual(self.mepanel.payee, '')
        self.assertEqual(self.mepanel.checkno, '')
        

#--- Two transactions one split
def app_two_transactions_one_split():
    app = TestApp()
    app.add_account('account1')
    app.mainwindow.show_account()
    app.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
    app.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
    app.tpanel.load()
    app.stable.add()
    row = app.stable.selected_row
    row.account = 'account3'
    row.debit = '24'
    app.stable.save_edits()
    app.tpanel.save()
    app.etable.select([0, 1])
    app.mepanel.load()
    return app
    
def test_cant_change_accounts():
    app = app_two_transactions_one_split()
    assert not app.mepanel.can_change_accounts


#--- Two foreign transactions
def app_two_foreign_transactions():
    app = TestApp()
    app.add_account('account1')
    app.mainwindow.show_account()
    app.add_entry(increase='42 eur')
    app.add_entry(increase='42 eur')
    app.mainwindow.select_transaction_table()
    app.ttable.select([0, 1])
    app.mepanel.load()
    return app

def test_amount_has_correct_currency():
    #The amount is shown with a currency code and the selected currency is the correct one
    app = app_two_foreign_transactions()
    eq_(app.mepanel.amount, 'EUR 42.00')
    eq_(app.mepanel.currency_index, 1) # EUR

def test_change_currency():
    # It's possible to mass edit currency
    app = app_two_foreign_transactions()
    app.mepanel.currency_index = 3 # CAD
    assert app.mepanel.currency_enabled
    app.mepanel.currency_index = -1
    assert not app.mepanel.currency_enabled
    app.mepanel.currency_index = 3 # CAD
    assert app.mepanel.currency_enabled
    app.mepanel.save()
    eq_(app.ttable[0].amount, 'CAD 42.00')
    eq_(app.ttable[1].amount, 'CAD 42.00')

#--- Two transactions with a multi-currency one
def app_two_transactions_with_a_multi_currency_one():
    app = TestApp()
    app.add_txn('20/02/2010')
    app.tpanel.load()
    app.stable[0].credit = '44 usd'
    app.stable.save_edits()
    app.stable.select([1])
    app.stable[1].debit = '42 cad'
    app.stable.save_edits()
    app.tpanel.save()
    app.add_txn('20/02/2010')
    app.ttable.select([0, 1])
    app.mepanel.load()
    return app

#--- Generators
def test_can_change_amount():
    def check(app, expected):
        eq_(app.mepanel.can_change_amount, expected)
    
    # Splits don't prevent the Amount field from being enabled
    app = app_two_transactions_one_split()
    yield check, app, True
    
    # If a MCT is selected, amount is not editable
    app = app_two_transactions_with_a_multi_currency_one()
    yield check, app, False
