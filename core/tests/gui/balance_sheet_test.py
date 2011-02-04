# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.testutil import eq_, patch_today, Patcher
from hscommon.currency import Currency, USD, CAD

from ..base import DocumentGUI, ApplicationGUI, TestApp, with_app, TestData
from ...app import Application
from ...const import PaneType
from ...document import Document
from ...model.account import AccountType
from ...model.date import MonthRange

# IMPORTANT NOTE: Keep in mind that every node count check in these tests take the total node and the
# blank node into account. For example, the node acount of an empty ASSETS node is 2.

#--- Pristine app
@with_app(TestApp)
def test_add_account(app):
    # The default name for an account is 'New Account', and the selection goes from None to 0.
    # Then, on subsequent calls, a number is added next to 'New Account'.
    app.bsheet.add_account()
    eq_(app.account_names(), ['New account'])
    eq_(app.bsheet.selected, app.bsheet.assets[0])
    app.bsheet.add_account()
    eq_(app.account_names(), ['New account', 'New account 1'])
    eq_(app.bsheet.selected, app.bsheet.assets[1])
    app.bsheet.add_account()
    eq_(app.account_names(), ['New account', 'New account 1', 'New account 2'])
    eq_(app.bsheet.selected, app.bsheet.assets[2])

@with_app(TestApp)
def test_add_account_in_other_groups(app):
    # When groups other than Assets are selected, new accounts go underneath it.
    app.bsheet.selected = app.bsheet.liabilities
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.liabilities[0])
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.liabilities[1])
    app.bsheet.selected = app.bsheet.assets
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.assets[0])
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.assets[1])
    app.bsheet.selected = None
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.assets[2])

@with_app(TestApp)
def test_add_account_with_total_node_selected(app):
    # The added account will be of the type of the type node we're under
    app.bsheet.selected = app.bsheet.liabilities[0] # total node
    app.bsheet.add_account()
    eq_(app.bsheet.liabilities[0].name, 'New account')

@with_app(TestApp)
def test_add_group(app):
    # add_group() creates a new account group in the selected base group.
    app.bsheet.selected = app.bsheet.liabilities
    app.bsheet.add_account_group()
    eq_(app.bsheet.selected, app.bsheet.liabilities[0])
    eq_(app.bsheet.liabilities[0].name, 'New group')
    assert app.bsheet.liabilities[0].is_group
    assert app.doc.is_dirty()

@with_app(TestApp)
def test_add_group_with_total_node_selected(app):
    # The added group will be of the type of the type node we're under
    app.bsheet.selected = app.bsheet.liabilities[0] # total node
    app.bsheet.add_account_group()
    eq_(app.bsheet.liabilities[0].name, 'New group')

@with_app(TestApp)
def test_balance_sheet(app):
    # The balance sheet is empty
    eq_([x.name for x in app.bsheet], ['ASSETS',  'LIABILITIES',  'NET WORTH'])
    eq_(app.account_node_subaccount_count(app.bsheet.assets), 0)
    eq_(app.account_node_subaccount_count(app.bsheet.liabilities), 0)

@with_app(TestApp)
def test_can_delete(app):
    # can_delete doesn't crash when nothing is selected
    assert not app.bsheet.can_delete() # no crash

@with_app(TestApp)
def test_is_excluded_is_bool_for_empty_groups_and_type(app):
    # previously, empty lists would be returned, causing a crash in the gui
    assert isinstance(app.bsheet.assets.is_excluded, bool)
    app.bsheet.add_account_group()
    assert isinstance(app.bsheet.assets[0].is_excluded, bool)

@with_app(TestApp)
def test_root_nodes_initially_expanded(app):
    # When the preference doesn't say otherwise, root nodes are expanded.
    eq_(app.bsheet.expanded_paths, [(0, ), (1, )])

@with_app(TestApp)
def test_save_edits_doesnt_lead_to_infinite_loop(app):
    # in save_edits, self.edited must be put to None asap because changes in the document could
    # lead to refreshes in the views that would call save_edits again and create an infinite
    # loop
    app.bsheet.add_account()
    app.bsheet.assets[0].name = 'foo'
    def fake_refresh():
        assert app.bsheet.edited is None
    with Patcher() as p:
        p.patch(app.bsheet_gui, 'refresh', fake_refresh)
        app.bsheet.save_edits()

def test_refresh_on_connect():
    # the account tree refreshes itself and selects the first asset. It is important in case the
    # document is already loaded when we connect.
    mgapp = Application(ApplicationGUI())
    doc = Document(DocumentGUI(), mgapp)
    doc.date_range = MonthRange(date(2008, 2, 1))
    doc.load_from_xml(TestData.filepath('moneyguru', 'simple.moneyguru'))
    app = TestApp(app=mgapp, doc=doc)
    eq_(app.account_node_subaccount_count(app.bsheet.assets), 2)
    eq_(app.bsheet.selected, app.bsheet.assets[0])
    app.check_gui_calls(app.bsheet_gui, ['refresh'])

@with_app(TestApp)
def test_show_account_then_select_other_report(app):
    # If the shown account is not in the shown report, select the first account
    app.add_account('asset')
    app.add_account('income', account_type=AccountType.Income)
    app.mw.select_income_statement()
    app.istatement.selected = app.istatement.income[0]
    app.istatement.show_selected_account()
    app.mainwindow.select_balance_sheet()
    eq_(app.bsheet.selected, app.bsheet.assets[0])

@with_app(TestApp)
def test_delta_perc_with_negative_start(app):
    # When the balance at the start is negative, use the absolute starting value as a base to
    # compute the change %
    app.add_account('Loan', account_type=AccountType.Liability)
    app.mw.show_account()
    app.add_entry(date='31/12/2007', description='Starting balance', increase='1000')
    app.add_account('Checking')
    app.mw.show_account()
    app.add_entry(date='1/1/2008', description='Salary', increase='1500.00')
    app.mw.select_balance_sheet()
    eq_(app.bsheet.net_worth.delta_perc, '+150.0%')

#--- Account hierarchy
def app_account_hierarchy():
    app = TestApp()
    app.add_account('Asset 1', account_number='4242')
    app.add_group('Bank')
    app.add_account('Bank 1', group_name='Bank')
    app.add_account('Liability 1', account_type=AccountType.Liability)
    app.add_group('Loans', account_type=AccountType.Liability)
    app.add_account('Loan 1', account_type=AccountType.Liability, group_name='Loans')
    app.mw.select_balance_sheet()
    app.clear_gui_calls()
    return app

@with_app(app_account_hierarchy)
def test_balance_sheet_hierarchy(app):
    # The balance sheet shows the hierarchy correctly.
    eq_(app.bsheet.assets.account_number, '') # all nodes have an account_number property
    eq_(app.bsheet.net_worth.account_number, '')
    eq_(app.bsheet.assets[0].name, 'Bank')
    eq_(app.bsheet.assets[0][0].name, 'Bank 1')
    eq_(app.bsheet.assets[0][1].name, 'Total Bank')
    eq_(app.bsheet.assets[0][2].name, None)
    eq_(app.bsheet.assets[1].name, 'Asset 1')
    eq_(app.bsheet.assets[1].account_number, '4242')
    eq_(app.bsheet.assets[2].name, 'TOTAL ASSETS')
    eq_(app.bsheet.assets[3].name, None)
    eq_(app.bsheet.liabilities[0].name, 'Loans')
    eq_(app.bsheet.liabilities[0][0].name, 'Loan 1')
    eq_(app.bsheet.liabilities[1].name, 'Liability 1')

@with_app(app_account_hierarchy)
def test_can_show_selected_account(app):
    # Is the selected item is not an account, can_show_selected_account returns False
    app.bsheet.selected = app.bsheet.assets
    assert not app.bsheet.can_show_selected_account
    app.bsheet.selected = app.bsheet.assets[0] # the group
    assert not app.bsheet.can_show_selected_account
    app.bsheet.selected = app.bsheet.assets[0][0]
    assert app.bsheet.can_show_selected_account

@with_app(app_account_hierarchy)
def test_cancel_edits(app):
    # cancel_edits() reverts the node name to the old value.
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.selected.name = 'foobar'
    app.bsheet.cancel_edits()
    eq_(app.bsheet.selected.name, 'Asset 1')

@with_app(app_account_hierarchy)
def test_delete_account(app):
    # Removing an account refreshes the view and stops any edition that was going on (if edition
    # is not stopped, the current buffer will be applied to the node under the deleted account)
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.delete()
    app.check_gui_calls(app.bsheet_gui, ['refresh', 'stop_editing'])

@with_app(app_account_hierarchy)
def test_is_subtotal_in_hierarchy(app):
    # Node.is_subtotal is True when the node under it is a total node (is_total).
    assert not app.bsheet.assets.is_subtotal
    assert not app.bsheet.assets[0].is_subtotal
    assert app.bsheet.assets[0][0].is_subtotal
    assert not app.bsheet.assets[0][1].is_subtotal
    assert not app.bsheet.assets[0][2].is_subtotal
    assert not app.bsheet.liabilities.is_subtotal

@with_app(app_account_hierarchy)
def test_save_edits(app):
    # save_edits() refreshes the view.
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.selected.name = 'foobar'
    app.bsheet.save_edits()
    app.check_gui_calls(app.bsheet_gui, ['refresh'])

@with_app(app_account_hierarchy)
def test_show_selected_account(app):
    # show_selected_account() switches to the account view.
    app.bsheet.selected = app.bsheet.assets[0][0]
    app.clear_gui_calls()
    app.bsheet.show_selected_account()
    # no show_line_graph because it was already selected in the etable view before
    app.check_current_pane(PaneType.Account, account_name='Bank 1')

#--- One account
def app_one_account():
    app = TestApp()
    app.add_account('Checking')
    app.clear_gui_calls()
    return app

@with_app(app_one_account)
def test_add_accounts_after_current(app):
    # The selection follows the newly added account.
    app.bsheet.add_account()
    eq_(app.bsheet.selected, app.bsheet.assets[1])
    app.check_gui_calls(app.bsheet_gui, ['update_selection', 'start_editing', 'stop_editing', 'refresh'])

@with_app(app_one_account)
def test_duplicate_account_name(app):
    # when the user enters a duplicate account name, show a dialog.
    app.bsheet.add_account()
    app.bsheet.selected.name = 'checking' # fails
    app.bsheet.save_edits()
    eq_(app.bsheet.selected.name, 'New account')
    app.check_gui_calls_partial(app.mainwindow_gui, ['show_message'])
    assert app.bsheet.edited is None

@with_app(app_one_account)
def test_make_account_liability(app):
    # Making the account a liability account refreshes all views.
    app.bsheet.move(app.bsheet.get_path(app.bsheet.assets[0]), app.bsheet.get_path(app.bsheet.liabilities))
    app.check_gui_calls(app.nwgraph_gui, ['refresh'])

@with_app(app_one_account)
def test_selection_follows_account_after_editing(app):
    # After editing, selection follows the account that was edited. This is important to avoid
    # confusion when invoking the account panel when still editing the name.
    app.mw.new_item() # 'New Account', so it's after 'Checking'
    app.bsheet.selected.name = 'aaa' # will end up *before* 'Checking'
    app.mw.edit_item()
    eq_(app.bsheet.selected.name, 'aaa')

#--- Account in editing mode
def app_account_in_editing_mode():
    app = TestApp()
    app.bsheet.add_account()
    app.bsheet.selected.name = 'foo'
    return app

@with_app(app_account_in_editing_mode)
def test_add_account_while_editing(app):
    # What is in the edition buffer is saved before a new account is created
    app.bsheet.add_account()
    eq_(app.bsheet.assets[0].name, 'foo')
    # The new account name was determined after the save
    eq_(app.bsheet.assets[1].name, 'New account')

@with_app(app_account_in_editing_mode)
def test_add_group_while_editing(app):
    # What is in the edition buffer is saved before a new group is created
    app.bsheet.add_account_group()
    eq_(app.bsheet.assets[1].name, 'foo')

#--- With group
def app_with_group():
    app = TestApp()
    app.add_group('Group')
    app.clear_gui_calls()
    return app

@with_app(app_with_group)
def test_accounts_sorted_under_group(app):
    # Accounts inside a group are sorted alphabetically.
    app.add_account('Zorg', group_name='Group')
    app.add_account('Albany', group_name='Group')
    app.add_account('Réal', group_name='Group')
    app.add_account('Rex', group_name='Group')
    eq_([x.name for x in app.bsheet.assets[0][:4]], ['Albany', 'Réal', 'Rex', 'Zorg'])

@with_app(app_with_group)
def test_balance_sheet_with_group(app):
    eq_(app.bsheet.assets[0].name, 'Group')

@with_app(app_with_group)
def test_save_edits_on_group(app):
    # save_edits() on a group refreshes the view too.
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.selected.name = 'foobar'
    app.bsheet.save_edits()
    app.check_gui_calls(app.bsheet_gui, ['refresh'])

#--- Group in editing mode
def app_group_in_editing_mode():
    app = TestApp()
    app.bsheet.add_account_group()
    app.bsheet.selected.name = 'foo'
    return app

@with_app(app_group_in_editing_mode)
def test_add_account_while_editing_group(app):
    # What is in the edition buffer is saved before a new account is created
    app.bsheet.add_account()
    eq_(app.bsheet.assets[0].name, 'foo')

#--- Account beside group
def app_account_beside_group():
    app = TestApp()
    app.add_account()
    app.add_group()
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[0] # the group
    return app

@with_app(app_account_beside_group)
def test_add_account_when_a_group_is_selected(app):
    # New accounts are created under the selected user created group.
    app.bsheet.add_account()
    eq_(app.account_node_subaccount_count(app.bsheet.assets), 2)
    eq_(app.account_node_subaccount_count(app.bsheet.assets[0]), 1)

#--- Account in group
def app_account_in_group():
    app = TestApp()
    app.add_group('group')
    app.add_account(group_name='group')
    app.bsheet.selected = app.bsheet.assets[0][0] # the account in the group
    return app

@with_app(app_account_in_group)
def test_add_account_with_group_selected(app):
    # Adding an account when the selection is an account under a user created group creates
    # the new account under that same group.
    app.bsheet.add_account()
    eq_(app.account_node_subaccount_count(app.bsheet.assets[0]), 2)

@with_app(app_account_in_group)
def test_expanded_nodes(app):
    # the `expanded_paths` property returns nodes that are... exapnded!
    app.bsheet.expand_node(app.bsheet.assets[0])
    eq_(app.bsheet.expanded_paths, [(0, ), (1, ), (0, 0)])

@with_app(app_account_in_group)
def test_is_subtotal(app):
    # In case we only have a group node just before a total node, this not will be considered
    # a subtotal node *only* if it's collapsed (if it's expanded, it has a total node hierarchy
    # of its own).
    app.bsheet.expand_node(app.bsheet.assets[0])
    assert not app.bsheet.assets[0].is_subtotal
    app.bsheet.collapse_node(app.bsheet.assets[0])
    assert app.bsheet.assets[0].is_subtotal

#--- Accounts and entries (Re-used in sub-app funcs below)
def app_accounts_and_entries():
    app = TestApp()
    app.drsel.select_month_range()
    app.add_account('income', account_type=AccountType.Income)
    app.add_account('expense', account_type=AccountType.Expense)
    app.add_account('Account 1')
    app.mw.show_account()
    app.add_entry('10/01/2008', 'Entry 1', transfer='income', increase='100.00')
    app.add_entry('13/01/2008', 'Entry 2', transfer='income', increase='150.00')
    app.add_account('Account 2')
    app.mw.show_account()
    app.add_entry('11/12/2007', 'Entry 3', transfer='income', increase='100.00')
    app.add_entry('12/01/2008', 'Entry 4', transfer='expense', decrease='20.00')
    app.mw.select_balance_sheet()
    app.clear_gui_calls()
    return app

@with_app(app_accounts_and_entries)
def test_balance_sheet_with_entries(app):
    eq_(app.doc.date_range, MonthRange(date(2008, 1, 1)))
    eq_(app.bsheet.assets[0].name, 'Account 1')
    eq_(app.bsheet.assets[0].start, '0.00')
    eq_(app.bsheet.assets[0].delta, '250.00')
    eq_(app.bsheet.assets[0].delta_perc, '---')
    eq_(app.bsheet.assets[0].end, '250.00')
    eq_(app.bsheet.assets[1].name, 'Account 2')
    eq_(app.bsheet.assets[1].start, '100.00')
    eq_(app.bsheet.assets[1].delta, '-20.00')
    eq_(app.bsheet.assets[1].delta_perc, '-20.0%')
    eq_(app.bsheet.assets[1].end, '80.00')
    eq_(app.bsheet.assets.start, '100.00')
    eq_(app.bsheet.assets.delta, '230.00')
    eq_(app.bsheet.assets.delta_perc, '+230.0%')
    eq_(app.bsheet.assets.end, '330.00')
    eq_(app.bsheet.net_worth.start, '100.00')
    eq_(app.bsheet.net_worth.delta, '230.00')
    eq_(app.bsheet.net_worth.delta_perc, '+230.0%')
    eq_(app.bsheet.net_worth.end, '330.00')

@with_app(app_accounts_and_entries)
@patch_today(2008, 1, 15)
def test_budget(app):
    # Account 1 is the target of the expense budget, and Account 2 is the target of the income
    # Assign budgeted amounts to the appropriate accounts.
    app.add_budget('income', 'Account 2', '400') # + 150
    app.add_budget('expense', 'Account 1', '100') # + 80
    app.mw.select_balance_sheet()
    eq_(app.bsheet.assets[0].end, '250.00')
    eq_(app.bsheet.assets[0].budgeted, '-80.00')
    eq_(app.bsheet.assets[1].end, '80.00')
    eq_(app.bsheet.assets[1].budgeted, '150.00')
    eq_(app.bsheet.assets.end, '330.00')
    eq_(app.bsheet.assets.budgeted, '70.00')
    eq_(app.bsheet.net_worth.budgeted, '70.00')
    # When we go to the next date range, the "budgeted" value must be cumulated
    app.drsel.select_next_date_range()
    eq_(app.bsheet.assets[0].budgeted, '-180.00') # 80 + 100
    eq_(app.bsheet.assets[1].budgeted, '550.00') # 150 + 300
    eq_(app.bsheet.assets.budgeted, '370.00')

@with_app(app_accounts_and_entries)
@patch_today(2008, 1, 15)
def test_budget_multiple_currencies(app):
    # budgeted amounts must be correctly converted to the target's currency
    USD.set_CAD_value(0.8, date(2008, 1, 1))
    app.mw.select_income_statement()
    app.istatement.selected = app.istatement.income[0]
    app.mw.edit_item()
    app.apanel.currency_index = Currency.all.index(CAD)
    app.apanel.save()
    app.add_budget('income', 'Account 1', '400 cad')
    app.mw.select_balance_sheet()
    eq_(app.bsheet.assets[0].end, '250.00')
    eq_(app.bsheet.assets[0].budgeted, '250.00') # 400 / 2 / 0.8 = 250

@with_app(app_accounts_and_entries)
@patch_today(2008, 1, 15)
def test_budget_target_liability(app):
    # The budgeted amount must be normalized before being added to a liability amount
    app.add_account('foo', account_type=AccountType.Liability)
    app.add_budget('income', 'foo', '400')
    app.mainwindow.select_balance_sheet()
    eq_(app.bsheet.liabilities[0].end, '0.00')
    eq_(app.bsheet.liabilities[0].budgeted, '-150.00')

@with_app(app_accounts_and_entries)
@patch_today(2008, 1, 15)
def test_budget_without_target(app):
    # The Net Worth's "budgeted" column counts all budgets, including target-less ones
    app.add_budget('income', None, '400')
    app.mw.select_balance_sheet()
    eq_(app.bsheet.net_worth.budgeted, '150.00')

@with_app(app_accounts_and_entries)
def test_change_date_range(app):
    app.doc.date_range = app.doc.date_range.prev()
    eq_(app.bsheet.assets[0].end, '0.00')
    eq_(app.bsheet.assets[1].start, '0.00')
    eq_(app.bsheet.assets[1].end, '100.00')

@with_app(app_accounts_and_entries)
def test_exclude_total_node(app):
    # excluding a total node does nothing (no crash)
    app.bsheet.selected = app.bsheet.assets[2] # total node
    app.bsheet.toggle_excluded()
    assert not app.bsheet.assets[2].is_excluded

@with_app(app_accounts_and_entries)
def test_exclude_type(app):
    # Excluding a type toggles exclusion for all accounts of that type
    app.bsheet.selected = app.bsheet.assets
    app.bsheet.toggle_excluded()
    # The total line for an excluded node diseappears, leaving only the 2 account lines and the
    # blank node
    eq_(app.bsheet.assets.children_count, 3)
    assert app.bsheet.assets[2].is_blank
    eq_(app.bsheet.assets[0].start, '')
    eq_(app.bsheet.assets[0].end, '')
    eq_(app.bsheet.assets[0].delta, '')
    eq_(app.bsheet.assets[0].delta_perc, '')
    eq_(app.bsheet.assets[1].start, '')
    eq_(app.bsheet.assets[1].end, '')
    eq_(app.bsheet.assets[1].delta, '')
    eq_(app.bsheet.assets[1].delta_perc, '')
    assert app.bsheet.assets.is_excluded

@with_app(app_accounts_and_entries)
def test_show_account_and_come_back(app):
    # When going back to a report, the selected account in the document is also selected in the
    # report.
    app.bsheet.selected = app.bsheet.assets[1] # Account 2
    app.bsheet.show_selected_account()
    app.mw.navigate_back()
    eq_(app.bsheet.selected, app.bsheet.assets[1])

@with_app(app_accounts_and_entries)
def test_shown_account_is_sticky(app):
    # When calling show_selected_account, soming back in a report and selecting another account
    # does not change the account that will be shown is select_entry_table is called.
    app.bsheet.selected = app.bsheet.assets[0] # Account 1
    app.bsheet.show_selected_account()
    app.mw.select_balance_sheet()
    app.bsheet.selected = app.bsheet.assets[1] # Account 2
    app.mw.select_entry_table()
    eq_(app.balgraph.title, 'Account 1')
    eq_(app.etable[0].description, 'Entry 1')

#--- Multiple currencies
def app_multiple_currencies():
    app = TestApp(app=Application(ApplicationGUI(), default_currency=CAD))
    app.drsel.select_month_range()
    USD.set_CAD_value(0.8, date(2008, 1, 1))
    USD.set_CAD_value(0.9, date(2008, 1, 31))
    app.add_group('Group')
    app.add_account('USD account', currency=USD, group_name='Group')
    app.mw.show_account()
    app.add_entry('1/1/2007', 'USD entry', increase='50.00')
    app.add_entry('1/1/2008', 'USD entry', increase='80.00')
    app.add_entry('31/1/2008', 'USD entry', increase='20.00')
    app.add_account('CAD account', currency=CAD, group_name='Group')
    app.mw.show_account()
    app.add_entry('1/1/2008', 'USD entry', increase='100.00')
    app.mw.select_balance_sheet()
    return app

@with_app(app_multiple_currencies)
def test_balance_sheet_with_multiple_currencies(app):
    eq_(USD.value_in(CAD, date(2008, 2, 1)), 0.9)
    eq_(app.doc.date_range, MonthRange(date(2008, 1, 1)))
    eq_(app.bsheet.assets.start, '40.00')
    eq_(app.bsheet.assets.end, '235.00')
    eq_(app.bsheet.assets.delta, '195.00')
    eq_(app.bsheet.assets.delta_perc, '+487.5%')
    eq_(app.bsheet.assets[0].start, '40.00')
    eq_(app.bsheet.assets[0].end, '235.00')
    eq_(app.bsheet.assets[0].delta, '195.00')
    eq_(app.bsheet.assets[0].delta_perc, '+487.5%')

@with_app(app_multiple_currencies)
def test_delete_transaction(app):
    # Deleting a transaction correctly updates the balance sheet balances. Previously, the
    # cache in Account would not correctly be cleared on cook()
    app.mw.select_transaction_table()
    app.ttable.select([2]) # last entry, on the 31st
    app.ttable.delete()
    app.mw.select_balance_sheet()
    eq_(app.bsheet.assets.end, '217.00')

@with_app(app_multiple_currencies)
def test_exclude_group(app):
    # Excluding a group excludes all sub-accounts and removes the total node
    app.bsheet.selected = app.bsheet.assets[0] # Group
    app.bsheet.toggle_excluded()
    eq_(app.bsheet.assets[0].children_count, 3) # the 2 accounts and the blank node
    assert app.bsheet.assets[0][2].is_blank
    eq_(app.bsheet.assets[0][0].start, '')
    eq_(app.bsheet.assets[0][0].end, '')
    eq_(app.bsheet.assets[0][0].delta, '')
    eq_(app.bsheet.assets[0][0].delta_perc, '')
    eq_(app.bsheet.assets[0][1].start, '')
    eq_(app.bsheet.assets[0][1].end, '')
    eq_(app.bsheet.assets[0][1].delta, '')
    eq_(app.bsheet.assets[0][1].delta_perc, '')
    assert app.bsheet.assets[0].is_excluded

@with_app(app_multiple_currencies)
def test_exclude_group_with_one_child_excluded(app):
    # as soon as one child is excluded, the toggle_excluded action re-includes all children
    app.bsheet.selected = app.bsheet.assets[0][1]
    app.bsheet.toggle_excluded()
    app.bsheet.selected = app.bsheet.assets[0]
    app.bsheet.toggle_excluded() # excludes all
    assert app.bsheet.assets[0].is_excluded
    assert app.bsheet.assets[0][0].is_excluded
    assert app.bsheet.assets[0][1].is_excluded
    app.bsheet.toggle_excluded() # re-includes all
    assert not app.bsheet.assets[0].is_excluded
    eq_(app.bsheet.assets[0].children_count, 4) # all there
    assert not app.bsheet.assets[0][0].is_excluded
    assert not app.bsheet.assets[0][1].is_excluded

#--- With liabilities
def app_with_liabilities():
    app = TestApp()
    app.add_group('foo', account_type=AccountType.Liability)
    app.add_account('Credit card', account_type=AccountType.Liability, group_name='foo')
    app.mw.show_account()
    app.add_entry(date='31/12/2007', description='Starting balance', decrease='100.00')
    app.add_entry(date='1/1/2008', description='Expensive jewel', increase='1200.00')
    app.mw.select_balance_sheet()
    return app

@with_app(app_with_liabilities)
def test_balance_sheet_with_liabilies(app):
    # Liability amounts are shown in their normal form (credit is positive).
    eq_(app.bsheet.liabilities[0][0].name, 'Credit card')
    eq_(app.bsheet.liabilities[0][0].start, '-100.00')
    eq_(app.bsheet.liabilities[0][0].end, '1100.00')
    eq_(app.bsheet.liabilities[0].start, '-100.00')
    eq_(app.bsheet.liabilities[0].end, '1100.00')
    eq_(app.bsheet.liabilities.start, '-100.00')
    eq_(app.bsheet.liabilities.end, '1100.00')
    eq_(app.bsheet.net_worth.start, '100.00')
    eq_(app.bsheet.net_worth.end, '-1100.00')
    eq_(app.bsheet.net_worth.delta, '-1200.00')

#--- Excluded account
def app_excluded_account():
    app = app_accounts_and_entries()
    app.bsheet.selected = app.bsheet.assets[1]
    app.bsheet.toggle_excluded()
    return app

@with_app(app_excluded_account)
def test_gui_calls_upon_exclusion(app):
    # account exclusion refreshes the sheet
    app.check_gui_calls(app.bsheet_gui, ['refresh'])

@with_app(app_excluded_account)
def test_save_and_load_account_exclusion(app):
    # account exclusion is persistent
    newapp = app.save_and_load()
    assert newapp.bsheet.assets[1].is_excluded

@with_app(app_excluded_account)
def test_values_when_accounts_are_excluded(app):
    # Excluding an account removes its amount from the totals and blanks its own amounts
    eq_(app.bsheet.assets[1].start, '')
    eq_(app.bsheet.assets[1].end, '')
    eq_(app.bsheet.assets[1].delta, '')
    eq_(app.bsheet.assets[1].delta_perc, '')
    eq_(app.bsheet.assets.start, '0.00')
    eq_(app.bsheet.assets.end, '250.00')
    eq_(app.bsheet.assets.delta, '250.00')
    eq_(app.bsheet.assets.delta_perc, '---')
    assert app.bsheet.assets[1].is_excluded

