# Created By: Virgil Dupras
# Created On: 2008-09-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from nose.tools import eq_

from .base import TestCase, TestSaveLoadMixin, CommonSetup

class OneDailyRecurrentTransaction(TestCase, CommonSetup, TestSaveLoadMixin):
    def setUp(self):
        self.create_instances()
        self.add_account('account')
        self.setup_scheduled_transaction(account='account', debit='1', repeat_every=3)
    
    def test_change_schedule_transaction(self):
        # when modifying a schedule's transaction through the scpanel, make sure that this change
        # is reflected among all spawns (in other words, reset spawn cache).
        self.mainwindow.select_schedule_table()
        self.sctable.select([0])
        self.scpanel.load()
        self.scpanel.description = 'foobaz'
        self.scpanel.save()
        self.mainwindow.select_transaction_table()
        eq_(self.ttable[1].description, 'foobaz')
    
    def test_change_spawn(self):
        # changing a spawn adds an exception to the recurrence (even if the date is changed)
        self.ttable.select([1])
        self.ttable[1].date = '17/09/2008'
        self.ttable[1].description = 'changed'
        self.ttable.save_edits()
        self.assertEqual(len(self.ttable), 6) # the spawn wasn't added to the tlist as a normal txn
        self.assertTrue(self.ttable[1].recurrent)
        self.assertEqual(self.ttable[1].date, '17/09/2008')
        self.assertEqual(self.ttable[1].description, 'changed')
        # change again
        self.ttable[1].date = '20/09/2008'
        self.ttable.save_edits()
        self.assertEqual(self.ttable[1].date, '19/09/2008')
        self.assertEqual(self.ttable[2].date, '20/09/2008')
        self.assertEqual(self.ttable[2].description, 'changed')
    
    def test_change_spawn_then_delete_it(self):
        # The correct spawn is deleted when a changed spawn is deleted
        self.ttable.select([1])
        self.ttable[1].date = '17/09/2008'
        self.ttable.save_edits()
        self.ttable.delete()
        self.assertEqual(len(self.ttable), 5)
        self.assertEqual(self.ttable[1].date, '19/09/2008')
    
    def test_change_spawn_through_tpanel(self):
        # Previously, each edition of a spawn through tpanel would result in a new schedule being
        # added even if the recurrence itself didn't change
        self.ttable.select([1])
        self.tpanel.load()
        self.tpanel.description = 'changed'
        self.tpanel.save()
        self.assertEqual(self.ttable[1].description, 'changed')
        self.assertEqual(self.ttable[2].description, 'foobar')
        self.assertEqual(self.ttable[3].description, 'foobar')
    
    def test_change_spawn_with_global_scope(self):
        # changing a spawn with a global scope makes every following spawn like it.
        # The date progression, however, continues as it was
        self.ttable.select([2])
        self.ttable[2].date = '17/09/2008'
        self.ttable[2].description = 'changed'
        self.document_gui.query_for_schedule_scope_result = True
        self.ttable.save_edits()
        # the explcitely changed one, however, keeps its date
        self.assertEqual(self.ttable[2].date, '17/09/2008')
        self.assertEqual(self.ttable[3].date, '22/09/2008')
        self.assertEqual(self.ttable[3].description, 'changed')
        self.assertEqual(self.ttable[4].date, '25/09/2008')
        self.assertEqual(self.ttable[4].description, 'changed')
    
    def test_change_spawn_with_global_scope_then_with_local_scope(self):
        # Previously, the same instance was used in the previous recurrence exception as well as
        # the new occurence base, making the second change, which is local, global.
        self.ttable.select([2])
        self.ttable[2].date = '17/09/2008'
        self.ttable[2].description = 'changed'
        self.document_gui.query_for_schedule_scope_result = True
        self.ttable.save_edits()
        self.ttable[2].description = 'changed again'
        self.document_gui.query_for_schedule_scope_result = False
        self.ttable.save_edits()
        self.assertEqual(self.ttable[3].description, 'changed')
    
    def test_change_spawn_with_global_scope_twice(self):
        # Previously, the second change would result in schedule duplicating
        self.ttable.select([2])
        self.ttable[2].date = '17/09/2008'
        self.ttable[2].description = 'changed'
        self.document_gui.query_for_schedule_scope_result = True
        self.ttable.save_edits()
        self.ttable[2].description = 'changed again'
        self.ttable.save_edits()
        self.assertEqual(self.ttable[3].date, '22/09/2008')
        self.assertEqual(self.ttable[3].description, 'changed again')
    
    def test_delete_spawn(self):
        # deleting a spawn only deletes this instance
        self.ttable.select([1])
        self.ttable.delete()
        self.assertEqual(len(self.ttable), 5)
        self.assertEqual(self.ttable[1].date, '19/09/2008')
    
    def test_delete_spawn_with_global_scope(self):
        # when deleting a spawn and query_for_global_scope returns True, we stop the recurrence 
        # right there
        self.ttable.select([2])
        self.document_gui.query_for_schedule_scope_result = True
        self.ttable.delete()
        self.assertEqual(len(self.ttable), 2)
        self.assertEqual(self.ttable[1].date, '16/09/2008')
    
    def test_delete_spawn_with_global_scope_after_change(self):
        # A bug would cause the stop_date to be ineffective if a change had been made at a later date
        self.ttable.select([3])
        self.ttable[3].description = 'changed'
        self.ttable.save_edits()
        self.ttable.select([2])
        self.document_gui.query_for_schedule_scope_result = True
        self.ttable.delete()
        self.assertEqual(len(self.ttable), 2)
    
    def test_etable_attrs(self):
        self.mainwindow.select_entry_table()
        self.assertEqual(len(self.etable), 6) # same thing in etable
        self.assertTrue(self.etable[0].recurrent)
        self.assertEqual(self.ttable[0].date, '13/09/2008')
        self.assertTrue(self.ttable[5].recurrent)
        self.assertEqual(self.ttable[5].date, '28/09/2008')
    
    def test_exceptions_are_always_spawned(self):
        # When an exception has a smaller date than the "spawn date", enough to be in another range,
        # when reloading the document, this exception would not be spawn until the date range
        # reached the "spawn date" rather than the exception date.
        self.document.select_next_date_range()
        self.ttable.select([0])
        self.ttable[0].date = '30/09/2008'
        self.ttable.save_edits() # date range now on 09/2008
        self.document._cook() # little hack to invalidate previously spawned txns
        self.ttable.refresh() # a manual refresh is required
        self.assertEqual(len(self.ttable), 7) # The changed spawn must be there.
    
    def test_filter(self):
        # scheduled transactions are included in the filters
        self.sfield.query = 'foobar'
        self.assertEqual(len(self.ttable), 6)
    
    def test_mass_edition(self):
        # When a mass edition has a spawn in it, don't ask for scope, just perform the change in the
        # local scope
        self.ttable.select([1, 2])
        self.mepanel.load()
        self.mepanel.description = 'changed'
        self.mepanel.save()
        self.assertEqual(self.ttable[3].description, 'foobar')
        self.assertEqual(self.document_gui.calls, {}) # no query_for_schedule_scope calls
    
    def test_ttable_attrs(self):
        self.assertEqual(len(self.ttable), 6) # this txn happens 6 times this month
        self.assertTrue(self.ttable[0].recurrent) # original is not recurrent
        self.assertEqual(self.ttable[0].date, '13/09/2008')
        self.assertTrue(self.ttable[1].recurrent)
        self.assertEqual(self.ttable[1].date, '16/09/2008')
        self.assertTrue(self.ttable[2].recurrent)
        self.assertEqual(self.ttable[2].date, '19/09/2008')
        self.assertTrue(self.ttable[3].recurrent)
        self.assertEqual(self.ttable[3].date, '22/09/2008')
        self.assertTrue(self.ttable[4].recurrent)
        self.assertEqual(self.ttable[4].date, '25/09/2008')
        self.assertTrue(self.ttable[5].recurrent)
        self.assertEqual(self.ttable[5].date, '28/09/2008')
    

class OneDailyRecurrentTransactionWithAnotherOne(TestCase, CommonSetup, TestSaveLoadMixin):
    # TestSaveLoadMixin: The native loader was loading the wrong split element into the Recurrence's
    # ref txn. So the recurrences were always getting splits from the last loaded normal txn
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        self.add_account('account')
        self.add_entry('19/09/2008', description='bar', increase='2')
        self.setup_scheduled_transaction(description='foo', account='account', debit='1', repeat_every=3)
    
    def test_ttable_attrs(self):
        self.assertEqual(len(self.ttable), 7)
        self.assertEqual(self.ttable[2].date, '19/09/2008')
        self.assertEqual(self.ttable[2].description, 'bar')
        self.assertEqual(self.ttable[3].date, '19/09/2008')
        self.assertEqual(self.ttable[3].description, 'foo')
        self.assertEqual(self.ttable[3].to, 'account')
    
    def test_etable_attrs(self):
        self.mainwindow.select_entry_table()
        self.assertEqual(len(self.etable), 7)
        self.assertEqual(self.etable[2].date, '19/09/2008')
        self.assertEqual(self.etable[2].description, 'bar')
        self.assertEqual(self.etable[3].date, '19/09/2008')
        self.assertEqual(self.etable[3].description, 'foo')
    

class OneDailyRecurrentTransactionWithLocalChange(TestCase, CommonSetup):
    def setUp(self):
        self.mock_today(2008, 9, 30)
        self.create_instances()
        self.setup_scheduled_transaction(account='account', debit='1', repeat_every=3)
        self.ttable.select([2])
        self.ttable[2].date = '17/09/2008'
        self.ttable[2].description = 'changed'
        self.ttable.save_edits()
    
    def test_exceptions_still_hold_the_correct_recurrent_date_after_load(self):
        # Previously, reloading an exception would result in recurrent_date being the same as date
        self.document = self.save_and_load()
        self.create_instances()
        self.mainwindow.select_schedule_table()
        self.mainwindow.select_transaction_table()
        self.ttable.select([2])
        self.ttable.delete()
        self.assertEqual(self.ttable[2].date, '22/09/2008')
    
    def test_save_load(self):
        # Previously, exceptions would lose their recurrent status after a reload
        # Also, later, local changes would be lost at reload
        self.document = self.save_and_load()
        self.create_instances()
        self.mainwindow.select_transaction_table()
        self.assertTrue(self.ttable[2].recurrent)
        self.assertEqual(self.ttable[2].description, 'changed')
    

class OneDailyRecurrentTransactionWithGlobalChange(TestCase, CommonSetup, TestSaveLoadMixin):
    def setUp(self):
        self.mock_today(2008, 9, 30)
        self.create_instances()
        self.setup_scheduled_transaction(account='account', debit='1', repeat_every=3)
        self.ttable.select([2])
        self.ttable[2].date = '17/09/2008'
        self.ttable[2].description = 'changed'
        self.document_gui.query_for_schedule_scope_result = True
        self.ttable.save_edits()
    
    def test_perform_another_global_change_before(self):
        # Previously, the second global change would not override the first
        self.ttable.select([1])
        self.ttable[1].description = 'changed again'
        self.document_gui.query_for_schedule_scope_result = True
        self.ttable.save_edits()
        self.assertEqual(self.ttable[2].description, 'changed again')
    

class OneDailyRecurrentTransactionWithLocalDeletion(TestCase, CommonSetup, TestSaveLoadMixin):
    def setUp(self):
        self.mock_today(2008, 9, 30)
        self.create_instances()
        self.setup_scheduled_transaction(account='account', debit='1', repeat_every=3)
        self.ttable.select([2])
        self.ttable.delete()
    
    def test_perform_another_global_change_before(self):
        # Don't remove the local deletion
        self.ttable.select([1])
        self.ttable[1].description = 'changed'
        self.document_gui.query_for_schedule_scope_result = True
        self.ttable.save_edits()
        self.assertEqual(self.ttable[2].date, '22/09/2008')
    

class OneDailyRecurrentTransactionWithStopDate(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(repeat_every=3)
        self.ttable.select([3])
        self.document_gui.query_for_schedule_scope_result = True
        self.ttable.delete()
    
    def test_perform_global_change(self):
        # Previously, the stop date on the new scheduled txn wouldn't be set
        self.ttable.select([1])
        self.ttable[1].description = 'changed'
        self.ttable.save_edits()
        self.assertEqual(len(self.ttable), 3)
    

class OneWeeklyRecurrentTransaction(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(repeat_type_index=1, repeat_every=2) # weekly
    
    def test_next_date_range(self):
        # The next date range also has the correct recurrent txns
        self.document.select_next_date_range()
        self.assertEqual(len(self.ttable), 2)
        self.assertEqual(self.ttable[0].date, '11/10/2008')
        self.assertEqual(self.ttable[1].date, '25/10/2008')
    
    def test_ttable_attrs(self):
        self.assertEqual(len(self.ttable), 2)
        self.assertEqual(self.ttable[0].date, '13/09/2008')
        self.assertEqual(self.ttable[1].date, '27/09/2008')
    

class OneMonthlyRecurrentTransactionOnThirtyFirst(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date=date(2008, 8, 31), repeat_type_index=2) # monthly
    
    def test_use_last_day_in_invalid_months(self):
        self.document.select_next_date_range() # sept
        self.assertEqual(len(self.ttable), 1)
        self.assertEqual(self.ttable[0].date, '30/09/2008') # can't use 31, so it uses 30
        # however, revert to 31st on the next month
        self.document.select_next_date_range() # oct
        self.assertEqual(len(self.ttable), 1)
        self.assertEqual(self.ttable[0].date, '31/10/2008')
    

class OneYearlyRecurrentTransactionOnTwentyNinth(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date=date(2008, 2, 29), repeat_type_index=3) # yearly
    
    def test_use_last_day_in_invalid_months(self):
        self.document.select_year_range()
        self.document.select_next_date_range() # 2009
        self.assertEqual(len(self.ttable), 1)
        self.assertEqual(self.ttable[0].date, '28/02/2009') # can't use 29, so it uses 28
        # however, revert to 29 4 years later
        self.document.select_next_date_range() # 2010
        self.document.select_next_date_range() # 2011
        self.document.select_next_date_range() # 2012
        self.assertEqual(len(self.ttable), 1)
        self.assertEqual(self.ttable[0].date, '29/02/2012')
    

class TransactionRecurringOnThirdMondayOfTheMonth(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date=date(2008, 9, 15), repeat_type_index=4) # week no in month
    
    def test_year_range(self):
        # The next date range also has the correct recurrent txns
        self.document.select_year_range()
        self.assertEqual(len(self.ttable), 4)
        self.assertEqual(self.ttable[0].date, '15/09/2008')
        self.assertEqual(self.ttable[1].date, '20/10/2008')
        self.assertEqual(self.ttable[2].date, '17/11/2008')
        self.assertEqual(self.ttable[3].date, '15/12/2008')
    

class TransactionRecurringOnFifthTuesdayOfTheMonth(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date=date(2008, 9, 30), repeat_type_index=4) # week no in month
    
    def test_next_date_range(self):
        # There's not a month with a fifth tuesday until december
        self.document.select_next_date_range() # oct
        self.assertEqual(len(self.ttable), 0)
        self.document.select_next_date_range() # nov
        self.assertEqual(len(self.ttable), 0)
        self.document.select_next_date_range() # dec
        self.assertEqual(len(self.ttable), 1)
        self.assertEqual(self.ttable[0].date, '30/12/2008')
    

class TransactionRecurringOnLastTuesdayOfTheMonth(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date=date(2008, 9, 30), repeat_type_index=5) # last week in month
    
    def test_next_date_range(self):
        # next month has no 5th tuesday, so use the last one
        self.document.select_next_date_range() # oct
        self.assertEqual(len(self.ttable), 1)
        self.assertEqual(self.ttable[0].date, '28/10/2008')
    

# XXX This test will be re-enabled when I introduce "Make schedule from selected transaction"
# class OneReconciledEntry(TestCase):
#     def setUp(self):
#         self.create_instances()
#         self.add_account()
#         self.add_entry('1/1/2008')
#         self.etable.select([0])
#         self.document.toggle_reconciliation_mode()
#         row = self.etable.selected_row
#         row.toggle_reconciled()
#         self.document.toggle_reconciliation_mode() # commit
#     
#     def test_make_recurrent(self):
#         # A reconciled entry made recurrent does not result in reconciled scheduled entries
#         self.tpanel.load()
#         self.tpanel.repeat_index = 1 # daily
#         self.tpanel.save()
#         self.assertFalse(self.etable[1].reconciled)
#     

class TwoDailyRecurrentTransaction(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.add_account('account')
        self.setup_scheduled_transaction(description='foo')
        self.setup_scheduled_transaction(description='bar')
    
    def test_can_order_sheduled_transaction(self):
        # scheduled transactions can't be re-ordered
        self.assertFalse(self.ttable.can_move([3], 2))
    

class DailyScheduleWithOneSpawnReconciled(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.add_account('account')
        self.setup_scheduled_transaction(account='account', debit='1', repeat_every=3)
        self.mainwindow.select_entry_table()
        self.etable.select([1]) # This one is the spawn on 16/09/2008
        self.document.toggle_reconciliation_mode()
        self.etable.selected_row.toggle_reconciled()
        self.document.toggle_reconciliation_mode()
    
    def test_dont_spawn_before_last_materialization_on_change(self):
        # One tricky problem was that if a schedule was changed to a more frequent one. When it happens,
        # exceptions start to be all out of sync with the recurrence, and trying to figure out which
        # ones should be kept is a nightmare. Thus, when a recurrence's start_date, repeat_type or
        # repeat_every is changed, its exceptions are simply reset.
        self.mainwindow.select_schedule_table()
        self.sctable.select([0])
        self.scpanel.load()
        self.scpanel.repeat_every = 1
        self.scpanel.save()
        self.mainwindow.select_transaction_table()
        # spawns start from the 13th, *not* the 13th, which means 18 spawn. If we add the reconciled
        # spawn which have been materialized, we have 19
        eq_(len(self.ttable), 19)
    
    def test_spawn_was_materialized(self):
        # reconciling a scheduled transaction "materializes" it
        self.assertTrue(self.etable[1].reconciled)
        self.assertFalse(self.etable[1].recurrent)
    
