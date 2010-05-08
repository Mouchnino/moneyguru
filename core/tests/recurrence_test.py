# Created By: Virgil Dupras
# Created On: 2008-09-12
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from nose.tools import eq_
from hsutil.testutil import Patcher

from ..const import PaneType
from ..document import ScheduleScope
from .base import TestCase, TestSaveLoadMixin, CommonSetup, TestApp, with_app

#--- One transaction
def app_one_transaction():
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('first')
    app.mw.show_account()
    app.add_entry('11/07/2008', 'description', 'payee', transfer='second', decrease='42', checkno='24')
    app.mw.select_transaction_table()
    app.clear_gui_calls()
    return app

@with_app(app_one_transaction)
def test_make_schedule_from_selected(app):
    # make_schedule_from_selected takes the selected transaction, create a monthly schedule out
    # of it, selects the schedule table, and pops the edition panel for it.
    app.mw.make_schedule_from_selected()
    app.check_current_pane(PaneType.Schedule)
    app.check_gui_calls_partial(app.scpanel_gui, ['pre_load', 'post_load'])
    eq_(len(app.sctable), 0) # It's a *new* schedule, only added if we press save
    eq_(app.scpanel.start_date, '11/07/2008')
    eq_(app.scpanel.description, 'description')
    eq_(app.scpanel.repeat_type_index, 2) # monthly
    eq_(app.scpanel.repeat_every, 1)
    app.scpanel.save()
    eq_(len(app.sctable), 1) # now we have it
    # When creating the schedule, we must delete the first occurrence because it overlapse with
    # the base transaction
    app.mw.select_transaction_table()
    eq_(app.ttable.row_count, 1)

#--- Daily schedule
def app_daily_schedule():
    p = Patcher()
    p.patch_today(2008, 9, 13)
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('account')
    app.add_schedule(start_date='13/09/2008', description='foobar', account='account',  amount='1',
        repeat_every=3)
    app.mainwindow.select_transaction_table()
    app.clear_gui_calls()
    return app, p

@with_app(app_daily_schedule)
def test_change_schedule_transaction(app):
    # when modifying a schedule's transaction through the scpanel, make sure that this change
    # is reflected among all spawns (in other words, reset spawn cache).
    app.mainwindow.select_schedule_table()
    app.sctable.select([0])
    app.scpanel.load()
    app.scpanel.description = 'foobaz'
    app.scpanel.save()
    app.mainwindow.select_transaction_table()
    eq_(app.ttable[1].description, 'foobaz')

@with_app(app_daily_schedule)
def test_change_spawn(app):
    # changing a spawn adds an exception to the recurrence (even if the date is changed)
    app.ttable.select([1])
    app.ttable[1].date = '17/09/2008'
    app.ttable[1].description = 'changed'
    app.ttable.save_edits()
    eq_(app.ttable.row_count, 6) # the spawn wasn't added to the tlist as a normal txn
    assert app.ttable[1].recurrent
    eq_(app.ttable[1].date, '17/09/2008')
    eq_(app.ttable[1].description, 'changed')
    # change again
    app.ttable[1].date = '20/09/2008'
    app.ttable.save_edits()
    eq_(app.ttable[1].date, '19/09/2008')
    eq_(app.ttable[2].date, '20/09/2008')
    eq_(app.ttable[2].description, 'changed')

@with_app(app_daily_schedule)
def test_change_spawn_cancel(app):
    # When cancelling a spawn change, nothing happens
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Cancel
    app.ttable.select([1])
    app.ttable[1].description = 'changed'
    app.ttable.save_edits()
    eq_(app.ttable[1].description, 'foobar')
    # The schedule scoping logic used to take place after the under had recorded. What we're
    # testing here is that the undoer, due to the cancellation, has *not* recorded anything
    app.doc.undo()
    eq_(app.ttable.row_count, 0) # the schedule creation has been undone

@with_app(app_daily_schedule)
def test_change_spawn_then_delete_it(app):
    # The correct spawn is deleted when a changed spawn is deleted
    app.ttable.select([1])
    app.ttable[1].date = '17/09/2008'
    app.ttable.save_edits()
    app.ttable.delete()
    eq_(app.ttable.row_count, 5)
    eq_(app.ttable[1].date, '19/09/2008')

@with_app(app_daily_schedule)
def test_change_spawn_through_etable(app):
    # Changing a spawn through etable queries for a scope.
    app.show_account('account')
    app.etable[1].description = 'changed'
    app.etable.save_edits()
    app.check_gui_calls(app.doc_gui, ['query_for_schedule_scope'])

@with_app(app_daily_schedule)
def test_change_spawn_through_etable_globally(app):
    # When the user selects a global change through the etable, we listen
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.show_account('account')
    app.etable[1].description = 'changed'
    app.etable.save_edits()
    eq_(app.etable[2].description, 'changed')

@with_app(app_daily_schedule)
def test_change_spawn_through_tpanel(app):
    # Previously, each edition of a spawn through tpanel would result in a new schedule being
    # added even if the recurrence itself didn't change
    app.ttable.select([1])
    app.tpanel.load()
    app.tpanel.description = 'changed'
    app.tpanel.save()
    eq_(app.ttable[1].description, 'changed')
    eq_(app.ttable[2].description, 'foobar')
    eq_(app.ttable[3].description, 'foobar')
    # We were queried for a scope
    app.check_gui_calls(app.doc_gui, ['query_for_schedule_scope'])

@with_app(app_daily_schedule)
def test_change_spawn_with_global_scope(app):
    # changing a spawn with a global scope makes every following spawn like it.
    # The date progression, however, continues as it was
    app.ttable.select([2])
    app.ttable[2].date = '17/09/2008'
    app.ttable[2].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    # the explcitely changed one, however, keeps its date
    eq_(app.ttable[2].date, '17/09/2008')
    eq_(app.ttable[3].date, '22/09/2008')
    eq_(app.ttable[3].description, 'changed')
    eq_(app.ttable[4].date, '25/09/2008')
    eq_(app.ttable[4].description, 'changed')

@with_app(app_daily_schedule)
def test_change_spawn_with_global_scope_then_with_local_scope(app):
    # Previously, the same instance was used in the previous recurrence exception as well as
    # the new occurence base, making the second change, which is local, global.
    app.ttable.select([2])
    app.ttable[2].date = '17/09/2008'
    app.ttable[2].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    app.ttable[2].description = 'changed again'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Local
    app.ttable.save_edits()
    eq_(app.ttable[3].description, 'changed')

@with_app(app_daily_schedule)
def test_change_spawn_with_global_scope_twice(app):
    # Previously, the second change would result in schedule duplicating
    app.ttable.select([2])
    app.ttable[2].date = '17/09/2008'
    app.ttable[2].description = 'changed'
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.save_edits()
    app.ttable[2].description = 'changed again'
    app.ttable.save_edits()
    eq_(app.ttable[3].date, '22/09/2008')
    eq_(app.ttable[3].description, 'changed again')

@with_app(app_daily_schedule)
def test_delete_account(app):
    # Deleting an account affecting a schedule properly update that schedule
    app.mainwindow.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.delete()
    app.arpanel.save()
    app.mainwindow.select_schedule_table()
    eq_(app.sctable[0].to, '')

@with_app(app_daily_schedule)
def test_delete_spawn(app):
    # deleting a spawn only deletes this instance
    app.ttable.select([1])
    app.ttable.delete()
    eq_(app.ttable.row_count, 5)
    eq_(app.ttable[1].date, '19/09/2008')

@with_app(app_daily_schedule)
def test_delete_spawn_cancel(app):
    # When the user cancels a spawn deletion, nothing happens
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Cancel
    app.ttable.select([1])
    app.ttable.delete()
    eq_(app.ttable.row_count, 6)

@with_app(app_daily_schedule)
def test_delete_spawn_with_global_scope(app):
    # when deleting a spawn and query_for_global_scope returns True, we stop the recurrence 
    # right there
    app.ttable.select([2])
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.delete()
    eq_(app.ttable.row_count, 2)
    eq_(app.ttable[1].date, '16/09/2008')

@with_app(app_daily_schedule)
def test_delete_spawn_with_global_scope_after_change(app):
    # A bug would cause the stop_date to be ineffective if a change had been made at a later date
    app.ttable.select([3])
    app.ttable[3].description = 'changed'
    app.ttable.save_edits()
    app.ttable.select([2])
    app.doc_gui.query_for_schedule_scope_result = ScheduleScope.Global
    app.ttable.delete()
    eq_(app.ttable.row_count, 2)

@with_app(app_daily_schedule)
def test_etable_attrs(app):
    app.show_account('account')
    eq_(app.etable_count(), 6) # same thing in etable
    assert app.etable[0].recurrent
    eq_(app.ttable[0].date, '13/09/2008')
    assert app.ttable[5].recurrent
    eq_(app.ttable[5].date, '28/09/2008')

@with_app(app_daily_schedule)
def test_exceptions_are_always_spawned(app):
    # When an exception has a smaller date than the "spawn date", enough to be in another range,
    # when reloading the document, this exception would not be spawn until the date range
    # reached the "spawn date" rather than the exception date.
    app.drsel.select_next_date_range()
    app.ttable.select([0])
    app.ttable[0].date = '30/09/2008'
    app.ttable.save_edits() # date range now on 09/2008
    app.doc._cook() # little hack to invalidate previously spawned txns
    app.ttable.refresh() # a manual refresh is required
    eq_(app.ttable.row_count, 7) # The changed spawn must be there.

@with_app(app_daily_schedule)
def test_filter(app):
    # scheduled transactions are included in the filters
    app.sfield.query = 'foobar'
    eq_(app.ttable.row_count, 6)

@with_app(app_daily_schedule)
def test_mass_edition(app):
    # When a mass edition has a spawn in it, don't ask for scope, just perform the change in the
    # local scope
    app.ttable.select([1, 2])
    app.mepanel.load()
    app.mepanel.description = 'changed'
    app.mepanel.save()
    eq_(app.ttable[3].description, 'foobar')
    app.check_gui_calls_partial(app.doc_gui, not_expected=['query_for_schedule_scope'])

@with_app(app_daily_schedule)
def test_ttable_attrs(app):
    eq_(app.ttable.row_count, 6) # this txn happens 6 times this month
    assert app.ttable[0].recurrent # original is not recurrent
    eq_(app.ttable[0].date, '13/09/2008')
    assert app.ttable[1].recurrent
    eq_(app.ttable[1].date, '16/09/2008')
    assert app.ttable[2].recurrent
    eq_(app.ttable[2].date, '19/09/2008')
    assert app.ttable[3].recurrent
    eq_(app.ttable[3].date, '22/09/2008')
    assert app.ttable[4].recurrent
    eq_(app.ttable[4].date, '25/09/2008')
    assert app.ttable[5].recurrent
    eq_(app.ttable[5].date, '28/09/2008')
    # Also test amount. Previously, the spawns would have their amount attributes stuck at 0.
    eq_(app.ttable[0].amount, '1.00')

class OneDailyRecurrentTransactionWithAnotherOne(TestCase, CommonSetup, TestSaveLoadMixin):
    # TestSaveLoadMixin: The native loader was loading the wrong split element into the Recurrence's
    # ref txn. So the recurrences were always getting splits from the last loaded normal txn
    def setUp(self):
        self.create_instances()
        self.drsel.select_month_range()
        self.add_account_legacy('account')
        self.add_entry('19/09/2008', description='bar', increase='2')
        self.setup_scheduled_transaction(description='foo', account='account', debit='1', repeat_every=3)
    
    def test_ttable_attrs(self):
        self.assertEqual(self.ttable.row_count, 7)
        self.assertEqual(self.ttable[2].date, '19/09/2008')
        self.assertEqual(self.ttable[2].description, 'bar')
        self.assertEqual(self.ttable[3].date, '19/09/2008')
        self.assertEqual(self.ttable[3].description, 'foo')
        self.assertEqual(self.ttable[3].to, 'account')
    
    def test_etable_attrs(self):
        self.mainwindow.select_entry_table()
        self.assertEqual(self.ta.etable_count(), 7)
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
        self.document_gui.query_for_schedule_scope_result = ScheduleScope.Global
        self.ttable.save_edits()
    
    def test_perform_another_global_change_before(self):
        # Previously, the second global change would not override the first
        self.ttable.select([1])
        self.ttable[1].description = 'changed again'
        self.document_gui.query_for_schedule_scope_result = ScheduleScope.Global
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
        self.document_gui.query_for_schedule_scope_result = ScheduleScope.Global
        self.ttable.save_edits()
        self.assertEqual(self.ttable[2].date, '22/09/2008')
    

class OneDailyRecurrentTransactionWithStopDate(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(repeat_every=3)
        self.ttable.select([3])
        self.document_gui.query_for_schedule_scope_result = ScheduleScope.Global
        self.ttable.delete()
    
    def test_perform_global_change(self):
        # Previously, the stop date on the new scheduled txn wouldn't be set
        self.ttable.select([1])
        self.ttable[1].description = 'changed'
        self.ttable.save_edits()
        self.assertEqual(self.ttable.row_count, 3)
    

class OneWeeklyRecurrentTransaction(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(repeat_type_index=1, repeat_every=2) # weekly
    
    def test_next_date_range(self):
        # The next date range also has the correct recurrent txns
        self.drsel.select_next_date_range()
        self.assertEqual(self.ttable.row_count, 2)
        self.assertEqual(self.ttable[0].date, '11/10/2008')
        self.assertEqual(self.ttable[1].date, '25/10/2008')
    
    def test_ttable_attrs(self):
        self.assertEqual(self.ttable.row_count, 2)
        self.assertEqual(self.ttable[0].date, '13/09/2008')
        self.assertEqual(self.ttable[1].date, '27/09/2008')
    

class OneMonthlyRecurrentTransactionOnThirtyFirst(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date='31/08/2008', repeat_type_index=2) # monthly
    
    def test_use_last_day_in_invalid_months(self):
        self.drsel.select_next_date_range() # sept
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].date, '30/09/2008') # can't use 31, so it uses 30
        # however, revert to 31st on the next month
        self.drsel.select_next_date_range() # oct
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].date, '31/10/2008')
    

class OneYearlyRecurrentTransactionOnTwentyNinth(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date='29/02/2008', repeat_type_index=3) # yearly
    
    def test_use_last_day_in_invalid_months(self):
        self.drsel.select_year_range()
        self.drsel.select_next_date_range() # 2009
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].date, '28/02/2009') # can't use 29, so it uses 28
        # however, revert to 29 4 years later
        self.drsel.select_next_date_range() # 2010
        self.drsel.select_next_date_range() # 2011
        self.drsel.select_next_date_range() # 2012
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].date, '29/02/2012')
    

class TransactionRecurringOnThirdMondayOfTheMonth(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date='15/09/2008', repeat_type_index=4) # week no in month
    
    def test_year_range(self):
        # The next date range also has the correct recurrent txns
        self.drsel.select_year_range()
        self.assertEqual(self.ttable.row_count, 4)
        self.assertEqual(self.ttable[0].date, '15/09/2008')
        self.assertEqual(self.ttable[1].date, '20/10/2008')
        self.assertEqual(self.ttable[2].date, '17/11/2008')
        self.assertEqual(self.ttable[3].date, '15/12/2008')
    

class TransactionRecurringOnFifthTuesdayOfTheMonth(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date='30/09/2008', repeat_type_index=4) # week no in month
    
    def test_next_date_range(self):
        # There's not a month with a fifth tuesday until december
        self.drsel.select_next_date_range() # oct
        self.assertEqual(self.ttable.row_count, 0)
        self.drsel.select_next_date_range() # nov
        self.assertEqual(self.ttable.row_count, 0)
        self.drsel.select_next_date_range() # dec
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].date, '30/12/2008')
    

class TransactionRecurringOnLastTuesdayOfTheMonth(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_scheduled_transaction(start_date='30/09/2008', repeat_type_index=5) # last week in month
    
    def test_next_date_range(self):
        # next month has no 5th tuesday, so use the last one
        self.drsel.select_next_date_range() # oct
        self.assertEqual(self.ttable.row_count, 1)
        self.assertEqual(self.ttable[0].date, '28/10/2008')
    

class TwoDailyRecurrentTransaction(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('account')
        self.setup_scheduled_transaction(description='foo')
        self.setup_scheduled_transaction(description='bar')
    
    def test_can_order_sheduled_transaction(self):
        # scheduled transactions can't be re-ordered
        self.assertFalse(self.ttable.can_move([3], 2))
    

class DailyScheduleWithOneSpawnReconciled(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.add_account_legacy('account')
        self.setup_scheduled_transaction(account='account', debit='1', repeat_every=3)
        self.mainwindow.select_entry_table()
        self.etable.select([1]) # This one is the spawn on 16/09/2008
        self.aview.toggle_reconciliation_mode()
        self.etable.selected_row.toggle_reconciled()
        self.aview.toggle_reconciliation_mode()
    
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
        eq_(self.ttable.row_count, 19)
    
    def test_spawn_was_materialized(self):
        # reconciling a scheduled transaction "materializes" it
        self.assertTrue(self.etable[1].reconciled)
        self.assertFalse(self.etable[1].recurrent)
    
