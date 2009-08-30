# Created By: Virgil Dupras
# Created On: 2008-07-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from hsutil.currency import USD

from ..base import TestCase

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
    
    def test_attrs(self):
        # No crash occur when trying to access atrtibutes while the panel is not loaded
        self.tpanel.date
    
    def test_can_load(self):
        """When there is no selection, can_load() is False"""
        self.assertFalse(self.tpanel.can_load())
    

class OneEntry(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42')
    
    def test_add_cancel_then_load(self):
        # when loading the tpanel right after cancelling a txn addition, the wrong txn is loaded
        self.etable.add()
        self.etable.cancel_edits()
        self.tpanel.load()
        self.assertEqual(self.tpanel.description, 'description')
    
    def test_buffer(self):
        """tpanel's edition is buffered"""
        self.tpanel.load()
        self.tpanel.date = '07/07/2008'
        self.tpanel.description = 'foo'
        self.tpanel.payee = 'bar'
        self.tpanel.checkno = 'baz'
        self.tpanel.load()
        self.assertEqual(self.tpanel.date, '06/07/2008')
        self.assertEqual(self.tpanel.description, 'description')
        self.assertEqual(self.tpanel.payee, 'payee')
        self.assertEqual(self.tpanel.checkno, '42')
    
    def test_can_load_selected_transaction(self):
        """can_load is based on the last selection of either the etable ot the ttable"""
        self.etable.select([])
        self.mainwindow.select_transaction_table()
        self.ttable.select([0])
        self.assertTrue(self.tpanel.can_load())
    
    def test_completion(self):
        """Here, we just want to make sure that complete() responds. We don't want to re-test 
        completion, we just want to make sure that the transaction panel is of the right subclass"""
        self.add_account() # the tpanel's completion must not be ependant on the selected account (like entries)
        self.assertEqual(self.tpanel.complete('d', 'description'), 'description')
    
    def test_load_refreshes_mct_button(self):
        # loading the panel refreshes the mct button
        self.tpanel.load()
        self.check_gui_calls_partial(self.tpanel_gui, refresh_mct_button=1)
    
    def test_load_while_etable_is_editing(self):
        """loading the tpanel while etable is editing saves the edits and stops editing mode"""
        self.etable.add()
        row = self.etable.edited
        row.date = '07/07/2008'
        self.clear_gui_calls()
        self.tpanel.load()
        self.assertTrue(self.etable.edited is None)
        self.assertEqual(len(self.etable), 2)
        self.check_gui_calls(self.etable_gui, refresh=1, show_selected_row=1, stop_editing=1)
    
    def test_load_while_ttable_is_editing(self):
        """loading the tpanel while ttable is editing saves the edits and stops editing mode"""
        self.mainwindow.select_transaction_table()
        self.ttable.add()
        row = self.ttable.edited
        row.date = '07/07/2008'
        self.clear_gui_calls()
        self.tpanel.load()
        self.assertTrue(self.ttable.edited is None)
        self.assertEqual(len(self.ttable), 2)
        self.check_gui_calls(self.ttable_gui, refresh=1, show_selected_row=1, stop_editing=1)
    
    def test_values(self):
        """The values of the panel are correct"""
        self.assertTrue(self.tpanel.can_load())
        self.tpanel.load()
        self.assertEqual(self.tpanel.date, '06/07/2008')
        self.assertEqual(self.tpanel.description, 'description')
        self.assertEqual(self.tpanel.payee, 'payee')
        self.assertEqual(self.tpanel.checkno, '42')
    
    def test_values_after_deselect(self):
        """When there is no selection, can_load() is False"""
        self.etable.select([])
        self.assertFalse(self.tpanel.can_load())
    

class OneAmountlessEntryPanelLoaded(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry(date='06/07/2008', description='description', payee='payee', checkno='42')
        self.mainwindow.select_transaction_table()
        self.ttable.select([0])
        self.tpanel.load()
        self.clear_gui_calls()
    
    def test_can_do_mct_balance(self):
        # doesn't crash if there is no split with amounts
        self.assertFalse(self.tpanel.can_do_mct_balance)
    

class OneEntryPanelLoaded(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry(date='06/07/2008', description='description', increase='42')
        self.mainwindow.select_transaction_table()
        self.ttable.select([0])
        self.tpanel.load()
        self.clear_gui_calls()
    
    def test_can_do_mct_balance(self):
        # the mct balance button is enabled if the txn is a MCT
        self.assertFalse(self.tpanel.can_do_mct_balance)
    
    def test_change_date(self):
        # Changing the date no longer calls refresh_repeat_options() on the view (this stuff is now
        # in schedules)
        self.tpanel.date = '17/07/2008'
        self.check_gui_calls(self.tpanel_gui, refresh_repeat_options=0)
    

class TwoAmountlessEntries(TestCase):
    def setUp(self):
        self.create_instances()
        self.add_account()
        self.add_entry(date='06/07/2008', description='desc1', payee='payee1', checkno='42')
        self.add_entry(date='07/07/2008', description='desc2', payee='payee2', checkno='43')
    
    def test_can_load_with_multiple_selection(self):
        """can_load() returns False if there is nore than one txn selected"""
        self.etable.select([0, 1])
        self.assertFalse(self.tpanel.can_load())
    
    def test_loads_last_selected_transaction(self):
        """the tpanel also works with the ttable. If the ttable is the last to have had a selection,
        tpanel loads this one."""
        self.mainwindow.select_transaction_table()
        self.ttable.select([0]) # etable has index 1 selected
        self.tpanel.load()
        self.assertEqual(self.tpanel.description, 'desc1')
    
    def test_set_values(self):
        """the load/save mechanism works for all attributes"""
        # The reason why we select another entry is to make sure that the value we're testing isn't
        # simply a buffer in the gui layer.
        def set_and_test(attrname, newvalue, othervalue):
            self.tpanel.load()
            setattr(self.tpanel, attrname, newvalue)
            self.tpanel.save()
            self.etable.select([0])
            self.tpanel.load()
            self.assertEqual(getattr(self.tpanel, attrname), othervalue)
            self.etable.select([1])
            self.tpanel.load()
            self.assertEqual(getattr(self.tpanel, attrname), newvalue)
        
        set_and_test('date', '08/07/2008', '06/07/2008')
        set_and_test('description', 'new', 'desc1')
        set_and_test('payee', 'new', 'payee1')
        set_and_test('checkno', '44', '42')
    

class MultiCurrencyTransaction(TestCase):
    def setUp(self):
        self.create_instances()
        USD.set_CAD_value(0.8, date(2008, 1, 1))
        self.mainwindow.select_transaction_table()
        self.ttable.add()
        self.tpanel.load()
        self.stable[0].account = 'first'
        self.stable[0].credit = '44 usd'
        self.stable.save_edits()
        self.stable.select([1])
        self.stable[1].account = 'second'
        self.stable[1].debit = '42 cad'
        self.stable.save_edits()
        self.clear_gui_calls()
    
    def test_can_do_mct_balance(self):
        # the mct balance button is enabled if the txn is a MCT
        self.assertTrue(self.tpanel.can_do_mct_balance)
    
    def test_mct_balance(self):
        # a mct balance takes the "lowest side" of the transaction and adds a split with the
        # difference on that side. For this example, the usd side is the weakest side (if they were
        # equal, it would be 52.50 usd).
        self.tpanel.mct_balance()
        self.assertEqual(len(self.stable), 3)
        self.assertEqual(self.stable[2].credit, 'CAD 6.80') # the selected split is the 2nd one
        self.check_gui_calls_partial(self.stable_gui, refresh=1, stop_editing=1)
    
    def test_mct_balance_select_null_split(self):
        # if the selected split has no amount, use the default currency
        self.stable.add()
        self.tpanel.mct_balance()
        self.assertEqual(self.stable[3].credit, '8.50') # the new split is the 4th!
    
    def test_mct_balance_select_usd_split(self):
        # the currency of the new split is the currency of the selected split
        self.stable.select([0])
        self.tpanel.mct_balance()
        self.assertEqual(self.stable[2].credit, '8.50')
    
    def test_mct_balance_twice(self):
        # if there is nothing to balance, don't add anything.
        self.tpanel.mct_balance()
        self.tpanel.mct_balance()
        self.assertEqual(len(self.stable), 3)
    
    def test_stop_edition_on_mct_balance(self):
        # edition must stop before mct balance or else we end up with a crash
        self.stable[1].account = 'foo'
        self.tpanel.mct_balance()
        self.check_gui_calls_partial(self.stable_gui, stop_editing=1)
    
