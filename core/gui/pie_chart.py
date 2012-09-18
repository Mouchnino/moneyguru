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

# Regardless of the view size, we always display this number of slices. If we have more, we group
# them under "Others"
MIN_SLICE_COUNT = 6
MIN_VIEW_SIZE = 250 # Size at which we start counting for eventual extra slices
SIZE_COST_FOR_SLICE = 30 # Number of pixels we need to count an extra slice
CHART_PADDING = 6

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
    def __init__(self, parent_view):
        Chart.__init__(self, parent_view)
        self._slice_count = MIN_SLICE_COUNT
    
    #--- Virtual
    def _get_data(self):
        # Returns a list of {name: amount}
        raise NotImplementedError()
    
    #--- Override
    def set_view_size(self, width, height):
        Chart.set_view_size(self, width, height)
        size = min(width, height)
        slice_count = MIN_SLICE_COUNT
        if size > MIN_VIEW_SIZE:
            slice_count += (size - MIN_VIEW_SIZE) // SIZE_COST_FOR_SLICE
        if slice_count != self._slice_count:
            self._slice_count = slice_count
            self._revalidate()
    
    def compute(self):
        self._data = []
        data = self._get_data()
        data = [(name, float(amount)) for name, amount in data.items() if amount > 0]
        data.sort(key=lambda t: t[1], reverse=True)
        data = [(name, amount, i % (len(COLORS)-1)) for i, (name, amount) in enumerate(data)]
        if len(data) > self.slice_count():
            others = data[self.slice_count()-1:]
            others_total = sum(amount for _, amount, _ in others)
            del data[self.slice_count()-1:]
            data.append((tr('Others'), others_total, len(COLORS)-1))
        total = sum(amount for _, amount, _ in data)
        if not total:
            return
        fmt = lambda name, amount: '%s %1.1f%%' % (name, amount / total * 100)
        self._data = [(fmt(name, amount), amount, color) for name, amount, color in data]
    
    def draw(self):
        vieww, viewh = self.view_size
        title = self.title
        titlew, titleh = self.view.text_size(title, 1)
        titley = viewh - titleh - CHART_PADDING
        title_rect = (0, titley, vieww, titleh)
        self.view.draw_text(title, title_rect, 1)
    
    #--- Public
    def colors(self):
        return COLORS
    
    def slice_count(self):
        return self._slice_count
