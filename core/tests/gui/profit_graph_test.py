# Created By: Virgil Dupras
# Created On: 2008-08-20
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license


from datetime import date

from hscommon.currency import USD

from ..base import TestCase

class Pristine(TestCase):
    def setUp(self):
        self.create_instances()
        self.drsel.select_month_range()
    
    def test_cook_bar_overflow(self):
        # When some data is included in a bar that overflows, we must not forget to ensure cooking
        # until the end of the *overflow*, not the end of the date range.
        self.add_account_legacy('Checking')
        self.add_entry('01/11/2008', transfer='Income', increase='42') #sunday
        self.drsel.select_prev_date_range() # oct 2008
        self.add_entry('31/10/2008', transfer='Income', increase='42')
        self.mainwindow.select_income_statement()
        # now, the creation of the txn forced a recook. what we want to make sure is that both 
        # entries will be in the bar
        self.assertEqual(self.pgraph.data[0][2], 84)
    
    
class IncomesAndExpensesInDifferentAccounts(TestCase):
    def setUp(self):
        self.create_instances()
        self.drsel.select_month_range()
        USD.set_CAD_value(1.42, date(2008, 7, 1))
        # in july 2008, the first mondy is the 7th
        self.add_account_legacy('asset')
        self.add_entry('12/6/2008', transfer='income1', increase='10') # will be ignored
        self.add_entry('3/7/2008', transfer='income1', increase='50') # 1st week
        self.add_entry('5/7/2008', transfer='income1', increase='80')
        self.add_entry('7/7/2008', transfer='income1', increase='90') # 2nd week
        self.add_entry('1/7/2008', transfer='income2', increase='32') # 1st week
        self.add_entry('5/7/2008', transfer='income2', increase='22')
        self.add_entry('15/7/2008', transfer='income2', increase='54') # 3rd week
        self.add_entry('1/7/2008', transfer='expense1', decrease='10 cad')
        self.add_entry('8/7/2008', transfer='expense2', decrease='100') # 2nd week
        self.mainwindow.select_income_statement()
        self.clear_gui_calls()
    
    def test_budget(self):
        # budgets are counted in the pgraph
        self.mock_today(2008, 7, 18)
        self.add_budget('income1', 'asset', '400') # +180
        self.mainwindow.select_income_statement()
        amounts = [data[2:] for data in self.pgraph.data]
        first_week = 50 + 80 + 32 + 22 - 7.04
        second_week = 90 - 100
        third_week = 54
        # now for the budget. 13 days in the future, 2 in the 3rd week, 7 in the 4th and 4 in the 5th
        third_week_future = 27.69 # 180 / 13 * 2
        fourth_week_future = 96.92 # 180 / 13 * 7
        fifth_week_future = 55.38 + 38.71 # (180 / 13 * 4) + (400 / 31 * 3)
        expected = [(first_week, 0), (second_week, 0), (third_week, third_week_future), 
            (0, fourth_week_future), (0, fifth_week_future)]
        self.assertEqual(amounts, expected)
    
    def test_budget_and_exclusion(self):
        # when an account is excluded, it's budget is not counted
        self.mock_today(2008, 7, 18)
        self.add_budget('income1', 'asset', '400') # +180
        self.mainwindow.select_income_statement()
        self.istatement.toggle_excluded()
        # same as test_exclude_account
        amounts = [data[2] for data in self.pgraph.data]
        expected = [32 + 22 - 7.04, -100, 54]
        self.assertEqual(amounts, expected)
    
    def test_exclude_account(self):
        # excluding an account removes it from the net worth graph
        self.istatement.selected = self.istatement.income[0]
        self.istatement.toggle_excluded()
        # We don't want to test the padding, so we only go for the amounts here
        amounts = [data[2] for data in self.pgraph.data]
        # the mock conversion system is rather hard to predict, but the converted amount for 10 CAD
        # on 1/7/2008 is 7.04 USD
        expected = [32 + 22 - 7.04, -100, 54]
        self.assertEqual(amounts, expected)
        self.check_gui_calls(self.pgraph_gui, ['refresh'])
    
    def test_profit_graph(self):
        # We don't want to test the padding, so we only go for the amounts here
        amounts = [data[2] for data in self.pgraph.data]
        # the mock conversion system is rather hard to predict, but the converted amount for 10 CAD
        # on 1/7/2008 is 7.04 USD
        expected = [50 + 80 + 32 + 22 - 7.04, 90 - 100, 54]
        self.assertEqual(amounts, expected)
        self.assertEqual(self.pgraph.title, 'Profit & Loss')
        self.assertEqual(self.pgraph.currency, USD)
    
