# Created By: Virgil Dupras
# Created On: 2009-12-27
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.testutil import eq_
from hscommon.currency import PLN, CAD

from ..document import ScheduleScope
from ..model.account import AccountType
from ..model.date import MonthRange
from .base import compare_apps, TestApp, with_app, testdata

#--- Pristine
def test_dont_save_invalid_xml_characters(tmpdir):
    # It's possible that characters that are invalid in an XML file end up in a moneyGuru document
    # (mostly through imports). Don't let this happen.
    app = TestApp()
    app.add_txn(description="foo\0bar")
    filepath = str(tmpdir.join('foo.xml'))
    app.doc.save_to_xml(filepath)
    app.doc.load_from_xml(filepath) # no exception
    eq_(app.ttable[0].description, "foo bar")

def test_saved_file_starts_with_xml_header(tmpdir):
    # Make sure that moneyGuru files start with an xml header, something that elementtree doesn't
    # do automatically.
    app = TestApp()
    filepath = str(tmpdir.join('foo.xml'))
    app.doc.save_to_xml(filepath)
    fp = open(filepath)
    contents = fp.read()
    assert contents.startswith('<?xml version="1.0" encoding="utf-8"?>\n')

#---
class TestLoadFile:
    # Loads 'simple.moneyguru', a file with 2 accounts and 2 entries in each. Select the first entry.
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2008, 2, 20) # so that the entries are shown
        app = TestApp()
        app.add_account() # This is to set the modified flag to true so we can make sure it has been put back to false
        app.doc.load_from_xml(testdata.filepath('moneyguru', 'simple.moneyguru'))
        app.mainwindow.select_balance_sheet()
        app.bsheet.selected = app.bsheet.assets[0]
        app.bsheet.show_selected_account()
        return app
    
    @with_app(do_setup)
    def test_add_entry(self, app):
        # Adding an entry sets the modified flag.
        app.add_entry()
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_change_account_currency(self, app):
        # Changing an account currency sets the modified flag.
        app.mainwindow.select_balance_sheet()
        app.mainwindow.edit_item()
        app.apanel.currency = PLN
        app.apanel.save()
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_delete_account(self, app):
        # Removing an account sets the modified flag.
        app.mainwindow.select_balance_sheet()
        app.bsheet.selected = app.bsheet.assets[0]
        app.bsheet.delete()
        app.arpanel.save() # continue deletion
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_delete_entries(self, app):
        # Deleting an entry sets the modified flag.
        app.etable.delete()
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_delete_transactions(self, app):
        # Deleting a transaction sets the modified flag.
        app.mainwindow.select_transaction_table()
        app.ttable.select([0]) # will be automatic at some point
        app.ttable.delete()
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_change_split(self, app):
        # Changing a split in the tpanel doesn't make the app dirty unless it's saved.
        app.etable.select([1])
        app.tpanel.load()
        app.stable.delete()
        assert not app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_edit_entry(self, app):
        # When about to save the document, if an entry is in edition, the document saves the edits first
        app.etable[0].description = 'foo'
        app.doc.stop_edition()
        assert app.doc.is_dirty() # We started editing, the flag is on
        app.etable.save_edits()
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_initial_selection(self, app):
        # Right after load, the last entry is selected.
        eq_(app.etable.selected_indexes, [1])
    
    @with_app(do_setup)
    def test_not_modified(self, app):
        # Loading a file resets the modified flag.
        assert not app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_rename_account(self, app):
        # Renaming an account sets the modified flag.
        app.mainwindow.select_balance_sheet()
        app.bsheet.selected = app.bsheet.assets[0]
        app.bsheet.selected.name = 'some other name'
        app.bsheet.save_edits()
        assert app.doc.is_dirty()
    
    @with_app(do_setup)
    def test_save_edit_without_edit(self, app):
        # Calling save_entry() without having made changes doesn't set the modified flag.
        app.etable.save_edits()
        assert not app.doc.is_dirty()
    

class TestLoadTwice:
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2008, 2, 1))
        app.doc.load_from_xml(testdata.filepath('moneyguru', 'simple.moneyguru'))
        app.doc.load_from_xml(testdata.filepath('moneyguru', 'simple.moneyguru'))
        return app
    
    @with_app(do_setup)
    def test_save_load(self, app):
        # make sure that loading completely wipes out previous transactions (If it doesn't, old
        # transaction end up in the save file, making them being re-added to the account in the next
        # load).
        app.do_test_save_load()
    

class TestLoadMultiCurrency:
    def do_setup(self):
        # Loads 'multi_currency.moneyguru', a file with 2 accounts and a multi-currency transaction.
        app = TestApp()
        app.doc.date_range = MonthRange(date(2008, 2, 1))
        app.doc.load_from_xml(testdata.filepath('moneyguru', 'multi_currency.moneyguru'))
        app.mainwindow.select_balance_sheet()
        app.bsheet.selected = app.bsheet.assets[0]
        app.bsheet.show_selected_account()
        app.etable.select([0])
        return app
    
    @with_app(do_setup)
    def test_amounts(self, app):
        # The amounts are correctly loaded and the logical imbalance has been dealt with.
        eq_(app.etable[0].increase, '200.00')
        app.tpanel.load()
        eq_(len(app.stable), 4)
        eq_(app.stable[0].debit, '200.00')
        eq_(app.stable[1].debit, 'PLN 123.45')
        expected = set(['200.00', 'PLN 123.45'])
        assert app.stable[2].credit in expected
        assert app.stable[3].credit in expected
    

class TestLoadPayeeDescription:
    def do_setup(self):
        app = TestApp()
        app.doc.date_range = MonthRange(date(2008, 3, 1))
        app.doc.load_from_xml(testdata.filepath('moneyguru', 'payee_description.moneyguru'))
        app.mainwindow.select_transaction_table()
        return app
    
    @with_app(do_setup)
    def test_attributes(self, app):
        # description and payee attributes load correctly, even when some of them are missing.
        eq_(app.ttable[0].description, 'description')
        eq_(app.ttable[0].payee, 'payee')
        eq_(app.ttable[1].description, 'description')
        eq_(app.ttable[1].payee, '')
        eq_(app.ttable[2].description, '')
        eq_(app.ttable[2].payee, 'payee')
    

class TestTwoAccountTwoEntriesInEachWithNonAsciiStrings:
    def do_setup(self):
        # Two accounts, two entries in each. Descriptions, categories and account names contain
        # non-latin characters (a polish 'l'). currencies are set to non-default values. first account
        # is selected.
        app = TestApp()
        app.add_account('first_account\u0142', currency=PLN)
        app.mainwindow.show_account()
        app.add_entry('3/10/2007', 'first\u0142', transfer='other account', increase='1 usd')
        app.add_entry('4/10/2007', 'second\u0142', increase='2 usd') # Imbalance
        app.add_account('second_account\u0142', currency=CAD)
        app.mainwindow.show_account()
        app.add_entry('5/10/2007', 'third\u0142', transfer='first_account\u0142', decrease='1 usd')
        app.add_entry('6/10/2007', 'fourth\u0142', transfer='yet another account', decrease='2 usd')
        return app
    
    @with_app(do_setup)
    def test_save_load(self, app):
        # make sure all those values come back up alright
        app.do_test_save_load()
    
    @with_app(do_setup)
    def test_qif_export_import(self, app):
        app.do_test_qif_export_import()
    

class TestLoadInvalidAccountType:
    def do_setup(self):
        #Loads 'invalid_account_type.moneyguru' which contains a single account with an invalid type.
        app = TestApp()
        app.doc.load_from_xml(testdata.filepath('moneyguru', 'invalid_account_type.moneyguru'))
        return app
    
    @with_app(do_setup)
    def test_account_type(self, app):
        # The account with the invalid type is imported as an asset account.
        eq_(app.bsheet.assets.children_count, 3)
    

class TestLoadImportWithTransactionInTheFuture:
    def do_setup(self, monkeypatch):
        monkeypatch.patch_today(2008, 2, 1) # before any txn date
        app = TestApp()
        app.doc.parse_file_for_import(testdata.filepath('moneyguru', 'simple.moneyguru'))
        return app
    
    @with_app(do_setup)
    def test_transactions_show_up(self, app):
        # even when there are txns in the future, they show up in the import panel
        eq_(len(app.itable), 2)
    

class TestLoadWithReferences1:
    def do_setup(self, monkeypatch):
        # Loads 'with_references1.moneyguru' which also have boolean (y/n) reconciliation attributes.
        monkeypatch.patch_today(2008, 2, 1) # before any txn date
        app = TestApp()
        app.doc.load_from_xml(testdata.filepath('moneyguru', 'with_references1.moneyguru'))
        return app
    
    @with_app(do_setup)
    def test_reconciliation(self, app):
        # legacy boolean reconciliation was correctly loaded
        app.bsheet.selected = app.bsheet.assets[0] # Account 1
        app.mainwindow.show_account()
        # 2 entries, first is not reconciled, second is.
        assert not app.etable[0].reconciled
        assert app.etable[1].reconciled
    

#--- All app functions below are tested in the following test generators
def app_account_with_budget():
    app = TestApp()
    app.add_account('asset')
    app.add_account('income', account_type=AccountType.Income)
    app.add_budget('income', 'asset', '400')
    app.mainwindow.edit_item()
    app.bpanel.notes = 'foobar'
    app.bpanel.save()
    return app

def app_transaction_with_payee_and_checkno():
    app = TestApp()
    app.add_account('Checking')
    app.add_txn('10/10/2007', 'Deposit', payee='Payee', from_='Salary', to='Checking',
        amount='42.00', checkno='42')
    app.mainwindow.edit_item()
    app.tpanel.notes = 'foobar\nfoobaz'
    app.tpanel.save()
    return app

def app_entry_with_blank_description():
    app = TestApp()
    app.add_account()
    app.mw.show_account()
    app.add_entry('10/10/2007', description='', transfer='Salary', increase='42')
    return app

def app_account_in_group():
    app = TestApp()
    app.add_group('group')
    app.add_account(group_name='group')
    app.bsheet.selected = app.bsheet.assets[0][0] # the account in the group
    return app

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

def app_entry_in_liability():
    app = TestApp()
    app.add_account('Credit card', account_type=AccountType.Liability)
    app.mw.show_account()
    app.add_entry('1/1/2008', 'Payment', increase='10')
    return app

def app_split_with_null_amount():
    app = TestApp()
    app.add_account('foo')
    app.mw.show_account()
    app.add_entry(date='2/1/2007', description='Split', transfer='bar')
    app.tpanel.load()
    app.stable.add()
    row = app.stable.selected_row
    row.account = 'baz'
    app.stable.save_edits()
    app.tpanel.save()
    return app

def app_one_account_and_one_group():
    app = TestApp()
    app.add_account()
    app.add_group() # The group is selected
    return app

def app_one_account_in_one_group():
    app = TestApp()
    app.add_group('group')
    app.add_account(group_name='group')
    return app

def app_budget_with_all_fields_set():
    app = TestApp()
    app.add_account('income', account_type=AccountType.Income)
    app.add_budget('income', None, '100', start_date='01/01/2009', repeat_type_index=3,
        repeat_every=2, stop_date='01/01/2022')
    return app

def app_account_with_apanel_attrs():
    app = TestApp()
    app.add_account()
    app.mw.edit_item()
    app.apanel.account_number = '1234'
    app.apanel.notes = 'some\nnotes'
    app.apanel.save()
    return app

def app_one_schedule_and_one_normal_txn():
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('account')
    app.mw.show_account()
    app.add_entry('19/09/2008', description='bar', increase='2')
    app.add_schedule(start_date='13/09/2008', description='foo', account='account', amount='1',
        repeat_every=3)
    return app

def app_schedule_with_global_change(monkeypatch):
    monkeypatch.patch_today(2008, 9, 30)
    app = TestApp()
    app.add_schedule(start_date='13/09/2008', account='account', amount='1', repeat_every=3)
    app.mw.select_transaction_table()
    app.ttable.select([2])
    app.ttable[2].date = '17/09/2008'
    app.ttable[2].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    return app

def app_schedule_with_local_deletion(monkeypatch):
    monkeypatch.patch_today(2008, 9, 30)
    app = TestApp()
    app.add_schedule(start_date='13/09/2008', account='account', amount='1', repeat_every=3)
    app.mw.select_transaction_table()
    app.ttable.select([2])
    app.ttable.delete()
    return app

def app_schedule_made_from_txn():
    app = TestApp()
    app.add_txn('11/07/2008', 'description', 'payee', from_='first', to='second', amount='42')
    app.mw.make_schedule_from_selected()
    app.scpanel.save()
    return app

def app_account_and_group():
    app = TestApp()
    app.add_account()
    app.add_group()
    return app

def test_save_load(tmpdir, monkeypatch):
    # Some (if not all!) tests yielded here have no comments attached to it. This is, unfortunately
    # because, in the old TestCase based system, had mixed in the TestCase with the TestSaveLoadMixin
    # without commenting on why I was doing that. When nose-ifying, I didn't want to lose coverage
    # so I kept them, but I'm not sure what they're testing.
    def check(app):
        filepath = str(tmpdir.join('foo.xml'))
        app.doc.save_to_xml(filepath)
        app.doc.close()
        newapp = TestApp()
        newapp.doc.load_from_xml(filepath)
        newapp.doc.date_range = app.doc.date_range
        newapp.doc._cook()
        compare_apps(app.doc, newapp.doc)
    
    app = app_account_with_budget()
    check(app)
    
    app = app_transaction_with_payee_and_checkno()
    check(app)
    
    app = app_entry_with_blank_description()
    check(app)
    
    # make sure that groups are saved
    app = app_account_in_group()
    check(app)
    
    # Make sure memos are loaded/saved
    app = app_transaction_with_memos()
    check(app)
    
    # make sure that empty groups are kept when saving/loading
    app = app_one_account_and_one_group()
    check(app)
    
    # make sure that groups are saved
    app = app_one_account_in_one_group()
    check(app)
    
    # make sure that all budget fields are correctly saved
    app = app_budget_with_all_fields_set()
    check(app)
    
    # apanel attributes are saved/loaded
    app = app_account_with_apanel_attrs()
    check(app)
    
    # The native loader was loading the wrong split element into the Recurrence's
    # ref txn. So the recurrences were always getting splits from the last loaded normal txn
    app = app_one_schedule_and_one_normal_txn()
    check(app)
    
    app = app_schedule_with_global_change(monkeypatch)
    check(app)
    
    app = app_schedule_with_local_deletion(monkeypatch)
    check(app)
    
    # The first spawn (corresponding to the original txn) is still skipped when we save/load
    app_schedule_made_from_txn()
    check(app)
    
    # make sure that empty groups are kept when saving/loading
    app = app_account_and_group()
    check(app)

def test_save_load_qif(tmpdir):
    def check(app):
        filepath = str(tmpdir.join('foo.qif'))
        app.mw.export()
        app.expanel.export_path = filepath
        app.expanel.save()
        app.doc.close()
        newapp = TestApp()
        newapp.doc.parse_file_for_import(filepath)
        while newapp.iwin.panes:
            newapp.iwin.import_selected_pane()
        newapp.doc.date_range = app.doc.date_range
        newapp.doc._cook()
        compare_apps(app.doc, newapp.doc, qif_mode=True)
    
    app = app_transaction_with_payee_and_checkno()
    check(app)
    
    # Make sure memos are loaded/saved
    app = app_transaction_with_memos()
    check(app)
    
    # make sure liability accounts are exported/imported correctly.
    app = app_entry_in_liability()
    check(app)
    
    # Splits with null amount are saved/loaded
    app = app_split_with_null_amount()
    check(app)
