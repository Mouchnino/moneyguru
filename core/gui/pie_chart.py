# Created By: Virgil Dupras
# Created On: 2008-09-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

from .chart import Chart

# A pie chart's data is a list of (name, (float)amount). The name part is ready for display. It
# is exactly what should be in the legend of the pie chat (it has amount and %)

SLICE_COUNT = 6 # If there is more than SLICE_COUNT items, the last item will group all the rest.

class PieChart(Chart):
    #--- Virtual
    def _get_data(self):
        # Returns a list of {name: amount}
        raise NotImplementedError()
    
    #--- Override
    def compute(self):
        self._data = []
        data = self._get_data()
        data = [(name, float(amount)) for name, amount in data.items() if amount > 0]
        data.sort(key=lambda t: t[1], reverse=True)
        if len(data) > SLICE_COUNT:
            others = data[SLICE_COUNT - 1:]
            others_total = sum(amount for name, amount in others)
            del data[SLICE_COUNT - 1:]
            data.append(('Others', others_total))
        total = sum(amount for name, amount in data)
        if not total:
            return
        fmt = lambda name, amount: '%s %1.1f%%' % (name, amount / total * 100)
        self._data = [(fmt(name, amount), amount) for name, amount in data]
    
