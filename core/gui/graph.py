# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

from datetime import date
from math import ceil, floor, log10

from ..model.date import inc_month, inc_year, strftime
from .chart import Chart

# A graph is a chart or drawing that shows the relationship between changing things.
# For the code, a Graph is a Chart with x and y axis.

class Graph(Chart):
    #--- Public    
    def compute_x_axis(self):
        date_range = self.document.date_range
        self._xmin = date_range.start.toordinal()
        self._xmax = date_range.end.toordinal() + 1
        tick = date_range.start
        self._xtickmarks = [tick.toordinal()]
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
            tick_pos = tick.toordinal() + (newtick - tick).days / 2
            self._xlabels.append(dict(text=strftime(tick_format, tick), pos=tick_pos))
            tick = newtick
            self._xtickmarks.append(tick.toordinal())

    def compute_y_axis(self):
        ymin, ymax = self.yrange()
        ydelta = float(ymax - ymin)
        yfactor = 10 ** int(log10(ydelta))
        ymin = int(yfactor * floor(float(ymin) / yfactor))
        ymax = int(yfactor * ceil(float(ymax) / yfactor))
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
        self._ytickmarks = range(ymin, ymax + 1, ystep)
        self._ylabels = [dict(text=str(x), pos=x) for x in self.ytickmarks]

    def compute(self):
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
    
