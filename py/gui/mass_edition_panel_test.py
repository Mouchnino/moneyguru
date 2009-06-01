# Unit Name: moneyguru.gui.mass_edition_panel_test
# Created By: Virgil Dupras
# Created On: 2008-07-25
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

from datetime import date

from hsutil.currency import EUR

from ..main_test import TestCase

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
    
    def test_can_load(self):
        """When there is no selection, can_load() is False"""
        self.assertFalse(self.mepanel.can_load())
    

class TwoTransactions(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.select_transaction_table()
        self.ttable.add()
        self.ttable.save_edits()
        self.ttable.add()
        self.ttable.save_edits()
    
    def test_can_load(self):
        """When there is only one txn selected, can_load() is False"""
        self.assertFalse(self.mepanel.can_load())
    
    def test_can_load_after_selection(self):
        """When there is more than one txn selected, can_load() is True"""
        self.ttable.select([0, 1])
        self.assertTrue(self.mepanel.can_load())
    
    def test_load(self):
        """No crash occurs when loading totally empty txns"""
        # Previously, None accounts in the splits were a problem.
        self.mepanel.load() # no crash
    

class TwoTransactionsDifferentValues(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('from1')
        self.add_entry(date='06/07/2008', description='description1', payee='payee1', checkno='42', transfer='to1', decrease='42')
        self.add_account('from2')
        self.add_entry(date='07/07/2008', description='description2', payee='payee2', checkno='43', transfer='to2', decrease='43')
        self.document.select_transaction_table()
        self.ttable.select([0, 1])
        self.mepanel.load()
    
    def test_attributes(self):
        """All fields are disabled and empty"""
        self.assertTrue(self.mepanel.can_change_accounts_and_amount)
        self.assertFalse(self.mepanel.date_enabled)
        self.assertFalse(self.mepanel.description_enabled)
        self.assertFalse(self.mepanel.payee_enabled)
        self.assertFalse(self.mepanel.checkno_enabled)
        self.assertFalse(self.mepanel.from_enabled)
        self.assertFalse(self.mepanel.to_enabled)
        self.assertFalse(self.mepanel.amount_enabled)
        self.assertEqual(self.mepanel.date, self.app.format_date(date.today()))
        self.assertEqual(self.mepanel.description, '')
        self.assertEqual(self.mepanel.payee, '')
        self.assertEqual(self.mepanel.checkno, '')
        self.assertEqual(self.mepanel.from_, '')
        self.assertEqual(self.mepanel.to, '')
        self.assertEqual(self.mepanel.amount, '0.00')
    
    def test_change_field(self):
        """Changing a field enables the associated checkbox"""
        self.clear_gui_calls()
        self.mepanel.date = '08/07/2008'
        self.assertTrue(self.mepanel.date_enabled)
        # just make sure they are not changed all at once
        self.assertFalse(self.mepanel.description_enabled)
        self.check_gui_calls(self.mepanel_gui, refresh=1)
        self.mepanel.description = 'foobar'
        self.assertTrue(self.mepanel.description_enabled)
        self.check_gui_calls(self.mepanel_gui, refresh=1)
        self.mepanel.payee = 'foobar'
        self.assertTrue(self.mepanel.payee_enabled)
        self.check_gui_calls(self.mepanel_gui, refresh=1)
        self.mepanel.checkno = '44'
        self.assertTrue(self.mepanel.checkno_enabled)
        self.check_gui_calls(self.mepanel_gui, refresh=1)
        self.mepanel.from_ = 'foobar'
        self.assertTrue(self.mepanel.from_enabled)
        self.check_gui_calls(self.mepanel_gui, refresh=1)
        self.mepanel.to = 'foobar'
        self.assertTrue(self.mepanel.to_enabled)
        self.check_gui_calls(self.mepanel_gui, refresh=1)
        self.mepanel.amount = '44'
        self.assertTrue(self.mepanel.amount_enabled)
        self.check_gui_calls(self.mepanel_gui, refresh=1)
    
    def test_change_field_to_none(self):
        """the mass panel considers replaces None values with ''"""
        self.mepanel.description = None
        self.mepanel.payee = None
        self.mepanel.checkno = None
        self.mepanel.from_ = None
        self.mepanel.to = None
        self.mepanel.amount = None
        self.assertFalse(self.mepanel.description_enabled)
        self.assertFalse(self.mepanel.payee_enabled)
        self.assertFalse(self.mepanel.checkno_enabled)
        self.assertFalse(self.mepanel.from_enabled)
        self.assertFalse(self.mepanel.to_enabled)
        self.assertFalse(self.mepanel.amount_enabled)
        self.assertEqual(self.mepanel.description, '')
        self.assertEqual(self.mepanel.payee, '')
        self.assertEqual(self.mepanel.checkno, '')
        self.assertEqual(self.mepanel.from_, '')
        self.assertEqual(self.mepanel.to, '')
        self.assertEqual(self.mepanel.amount, '0.00')
    
    def test_change_and_save(self):
        """save() performs mass edits on selected transactions"""
        self.save_file()
        self.mepanel.date = '08/07/2008'
        self.mepanel.description = 'description3'
        self.mepanel.payee = 'payee3'
        self.mepanel.checkno = '44'
        self.mepanel.from_ = 'from3'
        self.mepanel.to = 'to3'
        self.mepanel.amount = '44'
        self.mepanel.save()
        self.assertTrue(self.document.is_dirty())
        for row in self.ttable:
            self.assertEqual(row.date, '08/07/2008')
            self.assertEqual(row.description, 'description3')
            self.assertEqual(row.payee, 'payee3')
            self.assertEqual(row.checkno, '44')
            self.assertEqual(row.from_, 'from3')
            self.assertEqual(row.to, 'to3')
            self.assertEqual(row.amount, '44.00')
    
    def test_change_date_only(self):
        """Only change checked fields"""
        self.mepanel.date = '08/07/2008'
        self.mepanel.description = 'description3'
        self.mepanel.payee = 'payee3'
        self.mepanel.checkno = '44'
        self.mepanel.from_ = 'from3'
        self.mepanel.to = 'to3'
        self.mepanel.amount = '44'
        self.mepanel.description_enabled = False
        self.mepanel.payee_enabled = False
        self.mepanel.checkno_enabled = False
        self.mepanel.from_enabled = False
        self.mepanel.to_enabled = False
        self.mepanel.amount_enabled = False
        self.mepanel.save()
        row = self.ttable[0]
        self.assertEqual(row.date, '08/07/2008')
        self.assertEqual(row.description, 'description1')
        self.assertEqual(row.payee, 'payee1')
        self.assertEqual(row.checkno, '42')
        self.assertEqual(row.from_, 'from1')
        self.assertEqual(row.to, 'to1')
        self.assertEqual(row.amount, '42.00')
    
    def test_change_description_only(self):
        """test_change_date_only is not enough for complete coverage"""
        self.mepanel.date = '08/07/2008'
        self.mepanel.description = 'description3'
        self.mepanel.date_enabled = False
        self.mepanel.save()
        row = self.ttable[0]
        self.assertEqual(row.date, '06/07/2008')
        self.assertEqual(row.description, 'description3')
    
    def test_completion(self):
        """Here, we just want to make sure that complete() responds. We don't want to re-test 
        completion, we just want to make sure that the panel is of the right subclass"""
        self.add_account() # the tpanel's completion must not be ependant on the selected account (like entries)
        self.assertEqual(self.mepanel.complete('d', 'description'), 'description2')
    

class TwoTransactionsSameValues(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('account1')
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
        self.assertEqual(self.mepanel.date, self.app.format_date(date.today()))
        self.assertEqual(self.mepanel.description, '')
        self.assertEqual(self.mepanel.payee, '')
        self.assertEqual(self.mepanel.checkno, '')
        

class TwoTransactionsOneSplit(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('account1')
        self.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
        self.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42', transfer='account2', increase='42')
        self.tpanel.load()
        self.stable.add()
        row = self.stable.selected_row
        row.account = 'account3'
        row.debit = '24'
        self.stable.save_edits()
        self.tpanel.save()
        self.mepanel.load()
    
    def test_attributes(self):
        self.assertFalse(self.mepanel.can_change_accounts_and_amount)
    
    

class TwoForeignTransactions(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('account1')
        self.add_entry(increase='42 eur')
        self.add_entry(increase='42 eur')
        self.document.select_transaction_table()
        self.ttable.select([0, 1])
        self.mepanel.load()
    
    def test_attributes(self):
        #The amount is shown with a currency code and the selected currency is the correct one
        self.assertEqual(self.mepanel.amount, 'EUR 42.00')
        self.assertEqual(self.mepanel.currency_index, 1) # EUR
    
    def test_change_currency(self):
        # It's possible to mass edit currency
        self.mepanel.currency_index = 3 # CAD
        self.assertTrue(self.mepanel.currency_enabled)
        self.mepanel.currency_index = -1
        self.assertFalse(self.mepanel.currency_enabled)
        self.mepanel.currency_index = 3 # CAD
        self.assertTrue(self.mepanel.currency_enabled)
        self.mepanel.save()
        self.assertEqual(self.ttable[0].amount, 'CAD 42.00')
        self.assertEqual(self.ttable[1].amount, 'CAD 42.00')
    
class TwoForeignReconciledTransactions(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account('account1', EUR)
        self.add_entry(increase='42 eur')
        self.add_entry(increase='42 eur')
        self.document.toggle_reconciliation_mode()
        self.etable.select([0, 1])
        self.etable.toggle_reconciled()
        self.document.toggle_reconciliation_mode() # commit
        self.mepanel.load()
    
    def test_change_currency(self):
        # Warnings and unreconciliation happen as expected when a currency is mass changed
        self.mepanel.currency_index = 3 # CAD
        self.mepanel.save()
        self.assertFalse(self.etable[0].reconciled)
        self.assertFalse(self.etable[1].reconciled)
        self.check_gui_calls(self.document_gui, confirm_unreconciliation=1)
    
