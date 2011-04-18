# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.gui.net_worth_graph import NetWorthGraph as NetWorthGraphModel

from ..chart import Chart

class NetWorthGraph(Chart):
    CHART_MODEL_CLASS = NetWorthGraphModel
