# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-27
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_

from hsutil.currency import PLN, CAD

from ..model.account import AccountType
from ..model.date import MonthRange
from .base import TestCase, TestSaveLoadMixin, TestQIFExportImportMixin

class LoadFile(TestCase):
    # Loads 'simple.moneyguru', a file with 2 accounts and 2 entries in each. Select the first entry.
    def setUp(self):
        self.mock_today(2008, 2, 20) # so that the entries are shown
        self.create_instances()
        self.add_account() # This is to set the modified flag to true so we can make sure it has been put back to false
        self.document.load_from_xml(self.filepath('moneyguru', 'simple.moneyguru'))
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
    
    def test_add_entry(self):
        # Adding an entry sets the modified flag.
        self.add_entry()
        assert self.document.is_dirty()
    
    def test_change_account_currency(self):
        # Changing an account currency sets the modified flag.
        self.apanel.load()
        self.apanel.currency = PLN
        self.apanel.save()
        assert self.document.is_dirty()
    
    def test_delete_account(self):
        # Removing an account sets the modified flag.
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.delete()
        self.arpanel.ok() # continue deletion
        assert self.document.is_dirty()
    
    def test_delete_entries(self):
        # Deleting an entry sets the modified flag.
        self.etable.delete()
        assert self.document.is_dirty()
    
    def test_delete_transactions(self):
        # Deleting a transaction sets the modified flag.
        self.mainwindow.select_transaction_table()
        self.ttable.select([0]) # will be automatic at some point
        self.ttable.delete()
        assert self.document.is_dirty()
    
    def test_change_split(self):
        # Changing a split in the tpanel doesn't make the app dirty unless it's saved.
        self.etable.select([1])
        self.tpanel.load()
        self.stable.delete()
        assert not self.document.is_dirty()
    
    def test_edit_entry(self):
        # When about to save the document, if an entry is in edition, the document saves the edits first
        row = self.etable.selected_row
        row.description = 'foo'
        self.document.stop_edition()
        assert self.document.is_dirty() # We started editing, the flag is on
        self.etable.save_edits()
        assert self.document.is_dirty()
    
    def test_initial_selection(self):
        # Right after load, the last entry is selected.
        eq_(self.etable.selected_indexes, [1])
    
    def test_not_modified(self):
        # Loading a file resets the modified flag.
        assert not self.document.is_dirty()
    
    def test_rename_account(self):
        # Renaming an account sets the modified flag.
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.selected.name = 'some other name'
        self.bsheet.save_edits()
        assert self.document.is_dirty()
    
    def test_save_edit_without_edit(self):
        # Calling save_entry() without having made changes doesn't set the modified flag.
        self.etable.save_edits()
        assert not self.document.is_dirty()
    

class LoadTwice(TestCase, TestSaveLoadMixin):
    # Loads 'simple.moneyguru' twice. Mixed in with TestSaveLoadMixin to make sure that loading 
    # completely wipes out previous transactions (If it doesn't, old transaction end up in the save 
    # file, making them being re-added to the account in the next load).
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.document.load_from_xml(self.filepath('moneyguru', 'simple.moneyguru'))
        self.document.load_from_xml(self.filepath('moneyguru', 'simple.moneyguru'))
    

class LoadMultiCurrency(TestCase):
    # Loads 'multi_currency.moneyguru', a file with 2 accounts and a multi-currency transaction.
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 2, 1))
        self.document.load_from_xml(self.filepath('moneyguru', 'multi_currency.moneyguru'))
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.show_selected_account()
        self.etable.select([0])
    
    def test_amounts(self):
        # The amounts are correctly loaded and the logical imbalance has been dealt with.
        eq_(self.etable[0].increase, '200.00')
        self.tpanel.load()
        eq_(len(self.stable), 4)
        eq_(self.stable[0].debit, '200.00')
        eq_(self.stable[1].debit, 'PLN 123.45')
        expected = set(['200.00', 'PLN 123.45'])
        assert self.stable[2].credit in expected
        assert self.stable[3].credit in expected
    

class LoadPayeeDescription(TestCase):
    def setUp(self):
        self.create_instances()
        self.document.date_range = MonthRange(date(2008, 3, 1))
        self.document.load_from_xml(self.filepath('moneyguru', 'payee_description.moneyguru'))
        self.mainwindow.select_transaction_table()
    
    def test_attributes(self):
        # description and payee attributes load correctly, even when some of them are missing.
        eq_(self.ttable[0].description, 'description')
        eq_(self.ttable[0].payee, 'payee')
        eq_(self.ttable[1].description, 'description')
        eq_(self.ttable[1].payee, '')
        eq_(self.ttable[2].description, '')
        eq_(self.ttable[2].payee, 'payee')
    

class TwoAccountTwoEntriesInEachWithNonAsciiStrings(TestCase, TestSaveLoadMixin, TestQIFExportImportMixin):
    # Two accounts, two entries in each. Descriptions, categories and account names contain
    # non-latin characters (a polish 'l'). currencies are set to non-default values. first account
    # is selected.
    
    # Mixin with TestSaveLoadMixin to make sure all those values come back up alright
    # Same for TestQIFExportImportMixin
    def setUp(self):
        self.create_instances()
        self.add_account(u'first_account\u0142', currency=PLN)
        self.document.show_selected_account()
        self.add_entry('3/10/2007', u'first\u0142', transfer='other account', increase='1 usd')
        self.add_entry('4/10/2007', u'second\u0142', increase='2 usd') # Imbalance
        self.add_account(u'second_account\u0142', currency=CAD)
        self.document.show_selected_account()
        self.add_entry('5/10/2007', u'third\u0142', transfer=u'first_account\u0142', decrease='1 usd')
        self.add_entry('6/10/2007', u'fourth\u0142', transfer='yet another account', decrease='2 usd')
    

class LoadInvalidAccountType(TestCase):
    #Loads 'invalid_account_type.moneyguru' which contains a single account with an invalid type.
    def setUp(self):
        self.create_instances()
        self.document.load_from_xml(self.filepath('moneyguru', 'invalid_account_type.moneyguru'))
    
    def test_account_type(self):
        # The account with the invalid type is imported as an asset account.
        eq_(self.bsheet.assets.children_count, 3)
    

class LoadImportWithTransactionInTheFuture(TestCase):
    def setUp(self):
        self.mock_today(2008, 2, 1) # before any txn date
        self.create_instances()
        self.document.parse_file_for_import(unicode(self.filepath('moneyguru', 'simple.moneyguru')))
    
    def test_transactions_show_up(self):
        # even when there are txns in the future, they show up in the import panel
        eq_(len(self.itable), 2)
    

class LoadWithReferences1(TestCase):
    # Loads 'with_references1.moneyguru' which also have boolean (y/n) reconciliation attributes.
    def setUp(self):
        self.mock_today(2008, 2, 1) # before any txn date
        self.create_instances()
        self.document.load_from_xml(self.filepath('moneyguru', 'with_references1.moneyguru'))
    
    def test_reconciliation(self):
        # legacy boolean reconciliation was correctly loaded
        self.bsheet.selected = self.bsheet.assets[0] # Account 1
        self.document.show_selected_account()
        # 2 entries, first is not reconciled, second is.
        assert not self.etable[0].reconciled
        assert self.etable[1].reconciled
    

class AccountWithBudget(TestCase, TestSaveLoadMixin):
    # TestSaveLoadMixin: Budgets are correctly saved/loaded
    def setUp(self):
        # Weeks of Jan: 31-6 7-13 14-20 21-27 28-3
        self.create_instances()
        self.add_account_legacy('asset')
        self.add_account_legacy('income', account_type=AccountType.Income)
        self.apanel.load()
        self.apanel.budget = '400'
        self.apanel.save()
    

class TransactionWithPayeeAndChackno(TestCase, TestSaveLoadMixin, TestQIFExportImportMixin):
    # TestSaveLoadMixin: Make sure that the payee and checkno field is saved/loaded
    # TestQIFExportImportMixin: the same
    def setUp(self):
        self.create_instances()
        self.add_account('Checking')
        self.document.show_selected_account()
        self.add_entry('10/10/2007', 'Deposit', payee='Payee', transfer='Salary', increase='42.00', checkno='42')
    
