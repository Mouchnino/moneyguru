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
from hsutil.testutil import with_tmpdir

from ..model.account import AccountType
from ..model.date import MonthRange
from .base import TestCase, TestSaveLoadMixin, TestQIFExportImportMixin, compare_apps, TestApp, with_app

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
    

#--- Account with budget
def app_account_with_budget():
    app = TestApp()
    app.add_account('asset')
    app.add_account('income', account_type=AccountType.Income)
    app.add_budget('income', 'asset', '400')
    app.mainwindow.edit_item()
    app.bpanel.notes = 'foobar'
    app.bpanel.save()
    return app

#--- Transaction with payee and checkno
def app_transaction_with_payee_and_checkno():
    app = TestApp()
    app.add_account('Checking')
    app.add_txn('10/10/2007', 'Deposit', payee='Payee', from_='Salary', to='Checking',
        amount='42.00', checkno='42')
    app.mainwindow.edit_item()
    app.tpanel.notes = 'foobar\nfoobaz'
    app.tpanel.save()
    return app

#--- Entry with blank description
def app_entry_with_blank_description():
    app = TestApp()
    app.add_account()
    app.doc.show_selected_account()
    app.add_entry('10/10/2007', description='', transfer='Salary', increase='42')
    return app

#--- Account in group
def app_account_in_group():
    app = TestApp()
    app.add_group('group')
    app.add_account(group_name='group')
    app.bsheet.selected = app.bsheet.assets[0][0] # the account in the group
    return app

#--- Expanded group
def app_expanded_group():
    app = TestApp()
    app.add_group('group')
    app.bsheet.expand_node(app.bsheet.assets[0])
    return app

@with_app(app_expanded_group)
@with_tmpdir
def test_expanded_nodes_are_restored_on_load(app, tmppath):
    # We can't use the normal compare_apps mechanism here because node expansion info doesn't go into
    # the document. This test also makes sure that the nodes expansion state are saved even if the
    # sheet is not connected at close (and thus doesn't receive the document_will_close msg).
    app.mw.select_income_statement()
    filepath = unicode(tmppath + 'foo.xml')
    app.doc.save_to_xml(filepath)
    app.doc.close()
    newapp = TestApp(app=app.app)
    newapp.doc.load_from_xml(filepath)
    assert (0, 0) in newapp.bsheet.expanded_paths

#--- Transaction_with_memos
def app_transaction_with_memos():
    app = TestApp()
    app.add_account('first')
    app.add_account('second')
    app.mw.select_transaction_table()
    app.ttable.add()
    app.tpanel.load()
    app.stable[0].account = 'first'
    app.stable[0].memo = 'memo1'
    app.stable[0].credit = '42'
    app.stable.save_edits()
    app.stable.select([1])
    app.stable[1].account = 'second'
    app.stable[1].memo = 'memo2'
    app.stable.save_edits()
    app.tpanel.save()
    return app

#--- Entry in liability
def app_entry_in_liability():
    app = TestApp()
    app.add_account('Credit card', account_type=AccountType.Liability)
    app.mw.show_account()
    app.add_entry('1/1/2008', 'Payment', increase='10')
    return app

#--- Generators
def test_save_load():
    # Some (if not all!) tests yielded here have no comments attached to it. This is, unfortunately
    # because, in the old TestCase based system, had mixed in the TestCase with the TestSaveLoadMixin
    # without commenting on why I was doing that. When nose-ifying, I didn't want to lose coverage
    # so I kept them, but I'm not sure what they're testing.
    @with_tmpdir
    def check(app, tmppath):
        filepath = unicode(tmppath + 'foo.xml')
        app.doc.save_to_xml(filepath)
        app.doc.close()
        newapp = TestApp()
        newapp.doc.load_from_xml(filepath)
        newapp.doc.date_range = app.doc.date_range
        newapp.doc._cook()
        compare_apps(app.doc, newapp.doc)
    
    app = app_account_with_budget()
    yield check, app
    
    app = app_transaction_with_payee_and_checkno()
    yield check, app
    
    app = app_entry_with_blank_description()
    yield check, app
    
    # make sure that groups are saved
    app = app_account_in_group()
    yield check, app
    
    # Make sure memos are loaded/saved
    app = app_transaction_with_memos()
    yield check, app

def test_save_load_qif():
    @with_tmpdir
    def check(app, tmppath):
        filepath = unicode(tmppath + 'foo.qif')
        app.doc.save_to_qif(filepath)
        app.doc.close()
        newapp = TestApp()
        newapp.doc.parse_file_for_import(filepath)
        while newapp.iwin.panes:
            newapp.iwin.import_selected_pane()
        newapp.doc.date_range = app.doc.date_range
        newapp.doc._cook()
        compare_apps(app.doc, newapp.doc, qif_mode=True)
    
    app = app_transaction_with_payee_and_checkno()
    yield check, app
    
    # Make sure memos are loaded/saved
    app = app_transaction_with_memos()
    yield check, app
    
    # make sure liability accounts are exported/imported correctly.
    app = app_entry_in_liability()
    yield check, app
