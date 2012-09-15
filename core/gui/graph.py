# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license



from datetime import date
from math import ceil, floor, log10

from ..model.date import inc_month, inc_year
from .chart import Chart

# A graph is a chart or drawing that shows the relationship between changing things.
# For the code, a Graph is a Chart with x and y axis.

class Graph(Chart):
    #--- Private
    def _offset_xpos(self, xpos):
        return xpos - self._xoffset
    
    #--- Public    
    def compute_x_axis(self):
        date_range = self.document.date_range
        self._xmin = self._offset_xpos(date_range.start.toordinal())
        self._xmax = self._offset_xpos(date_range.end.toordinal() + 1)
        tick = date_range.start
        self._xtickmarks = [self._offset_xpos(tick.toordinal())]
        self._xlabels = []
        days = date_range.days
        if days > 366:
            tick_format = '%Y'
            inc_func = inc_year
            tick = date(tick.year, 1, 1)
        else:
            inc_func = inc_month
            tick = date(tick.year, tick.month, 1)
            tick_format = '%b' if days > 150 else '%B'
        while tick < date_range.end:
            newtick = inc_func(tick, 1)
            # 'tick' might be lower than xmin. ensure that it's not (for label pos)
            tick = tick if tick > date_range.start else date_range.start
            tick_pos = self._offset_xpos(tick.toordinal()) + (newtick - tick).days / 2
            self._xlabels.append(dict(text=tick.strftime(tick_format), pos=tick_pos))
            tick = newtick
            self._xtickmarks.append(self._offset_xpos(tick.toordinal()))

    def compute_y_axis(self):
        ymin, ymax = self.yrange()
        if ymin >= ymax: # max must always be higher than min
            ymax = ymin + 1
        ydelta = float(ymax - ymin)
        # our minimum yfactor is 100 or else the graphs are too squeezed with low datapoints
        yfactor = max(100, 10 ** int(log10(ydelta)))
        # We add/remove 0.05 so that datapoints being exactly on yfactors get some wiggle room.
        def adjust(amount, by):
            if amount == 0:
                return 0
            result = amount + by
            return result if (amount > 0) == (result > 0) else 0
        ymin = int(yfactor * floor(adjust(ymin/yfactor, -0.05)))
        ymax = int(yfactor * ceil(adjust(ymax/yfactor, 0.05)))
        ydelta = ymax - ymin
        ydelta_msd = ydelta // yfactor
        if ydelta_msd == 1:
            ystep = yfactor // 5
        elif ydelta_msd < 5:
            ystep = yfactor // 2
        else:
            ystep = yfactor
        self._ymin = ymin
        self._ymax = ymax
        self._ytickmarks = list(range(ymin, ymax + 1, ystep))
        self._ylabels = [dict(text=str(x), pos=x) for x in self.ytickmarks]

    def compute(self):
        # Our X data is based on ordinal date values, which can be quite big. On Qt, we get some
        # weird overflow problem when translating our painter by this large offset. Therefore, it's
        # better to offset this X value in the model.
        self._xoffset = self.document.date_range.start.toordinal()
        self.compute_data()
        self.compute_x_axis()
        self.compute_y_axis()
    
    #--- Properties
    
    @property
    def xmin(self):
        return self._xmin
    
    @property
    def xmax(self):
        return self._xmax
    
    @property
    def xlabels(self):
        return self._xlabels
    
    @property
    def xtickmarks(self):
        return self._xtickmarks
    
    @property
    def ymin(self):
        return self._ymin
    
    @property
    def ymax(self):
        return self._ymax
    
    @property
    def ylabels(self):
        return self._ylabels
    
    @property
    def ytickmarks(self):
        return self._ytickmarks
    
