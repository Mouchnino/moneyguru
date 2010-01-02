# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-08
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from core.gui.account_pie_chart import ExpensesPieChart as ExpensesPieChartModel

from ..chart import Chart

class ExpensePieChart(Chart):
    CHART_MODEL_CLASS = ExpensesPieChartModel
