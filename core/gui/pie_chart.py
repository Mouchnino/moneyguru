# Created By: Virgil Dupras
# Created On: 2008-09-04
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from hscommon.trans import tr
from .chart import Chart

# A pie chart's data is a list of (name, (float)amount). The name part is ready for display. It
# is exactly what should be in the legend of the pie chat (it has amount and %)

SLICE_COUNT = 6 # If there is more than SLICE_COUNT items, the last item will group all the rest.

#0xrrggbb
COLORS = [
    0x5dbc56,
    0x3c5bce,
    0xb6181f,
    0xe99709,
    0x9521e9,
    0x808080, # Only for "Others"
]

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
        data = [(name, amount, i % (len(COLORS)-1)) for i, (name, amount) in enumerate(data)]
        if len(data) > SLICE_COUNT:
            others = data[SLICE_COUNT - 1:]
            others_total = sum(amount for _, amount, _ in others)
            del data[SLICE_COUNT - 1:]
            data.append((tr('Others'), others_total, len(COLORS)-1))
        total = sum(amount for _, amount, _ in data)
        if not total:
            return
        fmt = lambda name, amount: '%s %1.1f%%' % (name, amount / total * 100)
        self._data = [(fmt(name, amount), amount, color) for name, amount, color in data]
    
    #--- Public
    def colors(self):
        return COLORS
    
