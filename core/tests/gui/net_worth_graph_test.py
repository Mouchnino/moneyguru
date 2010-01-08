# Created By: Virgil Dupras
# Created On: 2008-08-03
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from datetime import date

from hsutil.currency import CAD, USD

from ..base import TestCase, CommonSetup
from ...model.account import AccountType

class AssetsAndLiabilitiesInDifferentAccounts(TestCase, CommonSetup):
    def setUp(self):
        self.create_instances()
        self.setup_monthly_range()
        for i in range(1, 15):
            USD.set_CAD_value(1.42, date(2008, 7, i))
        for i in range(15, 32):
            USD.set_CAD_value(1.54, date(2008, 7, i))
        self.add_account_legacy('asset1')
        self.add_entry('12/6/2008', increase='10') # previous balance
        self.add_entry('3/7/2008', increase='50')
        self.add_entry('5/7/2008', increase='80')
        self.add_account_legacy('asset2')
        self.add_entry('1/7/2008', increase='32')
        self.add_entry('5/7/2008', increase='22')
        self.add_account_legacy('liability1', CAD, account_type=AccountType.Liability)
        self.add_entry('1/7/2008', increase='10')
        self.add_account_legacy('liability2', account_type=AccountType.Liability)
        self.add_entry('8/7/2008', increase='100')
        self.mainwindow.select_balance_sheet()
        self.clear_gui_calls()
    
    def test_add_group(self):
        # There was previously a bug where adding a group would empty the graph up.
        self.bsheet.add_account_group()
        self.bsheet.selected.name = 'foo'
        self.bsheet.save_edits()
        self.assertTrue(self.nw_graph_data())
    
    def test_budget(self):
        # when we add a budget, the balance graph will show a regular progression throughout date range
        self.mock_today(2008, 7, 27)
        self.add_account_legacy('income', account_type=AccountType.Income)
        self.add_account_legacy('expense', account_type=AccountType.Expense)
        self.add_budget('income', 'asset1', '300')
        self.add_budget('expense', 'asset1', '100')
        self.mainwindow.select_balance_sheet()
        # this means 200$ profit in 4 days
        self.mainwindow.select_balance_sheet()
        expected = [
            ('01/07/2008', '10.00'),
            ('02/07/2008', '34.96'), # 32 - 10 * 1.42 (the mock xchange rate)
            ('03/07/2008', '34.96'),
            ('04/07/2008', '84.96'), # + 50
            ('05/07/2008', '84.96'),
            ('06/07/2008', '186.96'), # + 80 + 22
            ('08/07/2008', '186.96'),
            ('09/07/2008', '86.96'), # - 100
            ('15/07/2008', '86.96'),
            ('16/07/2008', '87.51'), # currency value change
            ('28/07/2008', '87.51'),
            ('01/08/2008', '287.51'),
        ]
        self.assertEqual(self.nw_graph_data(), expected)
    
    def test_budget_target_excluded(self):
        # when the budget target is excluded, don't show it's budgeted data
        self.mock_today(2008, 7, 27)
        self.mainwindow.select_income_statement() # refresh graph
        self.mainwindow.select_balance_sheet() # refresh graph
        without_budget = self.nw_graph_data()
        self.add_account_legacy('asset3')
        self.add_account_legacy('income', account_type=AccountType.Income)
        self.add_budget('income', 'asset3', '300')
        self.mainwindow.select_balance_sheet()
        self.bsheet.selected = self.bsheet.assets[2] # asset3
        self.bsheet.toggle_excluded()
        self.assertEqual(self.nw_graph_data(), without_budget)
    
    def test_exclude_account(self):
        # excluding an account removes it from the net worth graph
        self.bsheet.selected = self.bsheet.liabilities[0] # that CAD account
        self.bsheet.toggle_excluded()
        expected = [
            ('01/07/2008', '10.00'),
            ('02/07/2008', '42.00'),
            ('03/07/2008', '42.00'),
            ('04/07/2008', '92.00'), # + 50
            ('05/07/2008', '92.00'),
            ('06/07/2008', '194.00'), # + 80 + 22
            ('08/07/2008', '194.00'),
            ('09/07/2008', '94.00'), # - 100
            ('01/08/2008', '94.00'),
        ]
        self.assertEqual(self.nw_graph_data(), expected)
        self.check_gui_calls(self.nwgraph_gui, ['refresh'])
    
    def test_net_worth_graph(self):
        # One interesting thing about this graph is that on the 14th of july, the CAD value changes,
        # so even if there is no entry on that day, the net worth changes anyway.
        expected = [
            ('01/07/2008', '10.00'),
            ('02/07/2008', '34.96'), # 32 - 10 * 1.42 (the mock xchange rate)
            ('03/07/2008', '34.96'),
            ('04/07/2008', '84.96'), # + 50
            ('05/07/2008', '84.96'),
            ('06/07/2008', '186.96'), # + 80 + 22
            ('08/07/2008', '186.96'),
            ('09/07/2008', '86.96'), # - 100
            ('15/07/2008', '86.96'),
            ('16/07/2008', '87.51'), # currency value change
            ('01/08/2008', '87.51'),
        ]
        self.assertEqual(self.nw_graph_data(), expected)
        self.assertEqual(self.nwgraph.title, 'Net Worth')
        self.assertEqual(self.nwgraph.currency, USD)
    
    def test_refresh_account_deleted(self):
        # When an account is deleted, charts are refreshed
        self.bsheet.selected = self.bsheet.assets[0]
        self.bsheet.delete()
        self.arpanel.ok() # continue deletion
        self.assertNotEqual(self.nw_graph_data()[0], ('01/07/2008', '10.00'))
        self.check_gui_calls(self.nwgraph_gui, ['refresh'])
    
    def test_refresh_on_import(self):
        # When entries are imported, charts are refreshed
        self.document.parse_file_for_import(self.filepath('qif', 'checkbook.qif'))
        self.iwin.import_selected_pane()
        # For the data itself, we just have to test that it changed. the QIF has data in 02/2008
        self.assertNotEqual(self.nw_graph_data()[0], ('01/07/2008', '10.00'))
        self.check_gui_calls(self.nwgraph_gui, ['refresh'])
    
