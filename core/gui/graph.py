# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date
from math import ceil, floor, log10

from hscommon.geometry import Point, Rect

from ..model.date import inc_month, inc_year
from .chart import Chart

# A graph is a chart or drawing that shows the relationship between changing things.
# For the code, a Graph is a Chart with x and y axis.

class FontID:
    Title = 1
    AxisLabel = 2

class PenID:
    Axis = 1
    AxisOverlay = 2

class GraphContext:
    def __init__(self, xfactor, yfactor, xoffset, yoffset):
        self.xfactor = xfactor
        self.yfactor = yfactor
        self.xoffset = xoffset
        self.yoffset = yoffset
    
    def trpoint(self, p):
        x, y = p
        x += self.xoffset
        y += self.yoffset
        return Point(x, y)
    
    def trpoints(self, pts):
        return [self.trpoint(p) for p in pts]
    
    def trrect(self, r):
        x, y, w, h = r
        x += self.xoffset
        y += self.yoffset
        return Rect(x, y, w, h)
    

class Graph(Chart):
    PADDING = 16
    TITLE_PADDING = 4
    TICKMARKS_LENGTH = 5
    XLABELS_PADDING = 3
    YLABELS_PADDING = 8
    
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
    
    def draw_graph(self, context):
        pass
    
    def draw_graph_after_axis(self, context):
        pass
    
    def draw(self):
        view_rect = Rect(0, 0, *self.view_size)
        data_width = self.xmax - self.xmin
        data_height = self.ymax - self.ymin
        y_labels_width = max(self.view.text_size(label['text'], FontID.AxisLabel)[0] for label in self.ylabels)
        labels_height = self.view.text_size('', FontID.AxisLabel)[1]
        graph_width = view_rect.w - y_labels_width - (self.PADDING * 2)
        graph_height = view_rect.h - labels_height - (self.PADDING * 2)
        graphx = y_labels_width + self.PADDING
        graphy = labels_height + self.PADDING
        graph_rect = Rect(graphx, graphy, graph_width, graph_height)
        xfactor = graph_width / data_width
        yfactor = graph_height / data_height
        graph_left = round(self.xmin * xfactor)
        graph_bottom = round(self.ymin * yfactor)
        graph_top = round(self.ymax * yfactor)
        xoffset = graph_rect.left
        # yoffset = graph_rect.y + graph_bottom
        yoffset = -(graph_bottom - graph_rect.y)
        context = GraphContext(xfactor, yfactor, xoffset, yoffset)
        
        self.draw_graph(context)
        
        # X/Y axis
        p1 = context.trpoint(Point(0, graph_bottom))
        p2 = context.trpoint(Point(graph_width, graph_bottom))
        p3 = context.trpoint(Point(0, graph_top))
        self.view.draw_line(p1, p2, PenID.Axis)
        self.view.draw_line(p1, p3, PenID.Axis)
        if graph_bottom < 0:
            p1 = context.trpoint(Point(0, 0))
            p2 = context.trpoint(Point(graph_width, 0))
            self.view.draw_line(p1, p2, PenID.Axis)
        
        # X tickmarks
        tickBottomY = graph_bottom - self.TICKMARKS_LENGTH
        for tickPos in self.xtickmarks:
            tickX = tickPos * xfactor
            p1 = context.trpoint(Point(tickX, graph_bottom))
            p2 = context.trpoint(Point(tickX, tickBottomY))
            self.view.draw_line(p1, p2, PenID.Axis)
        
        # Y tickmarks
        tickLeftX = graph_left - self.TICKMARKS_LENGTH
        for tickPos in self.ytickmarks:
            tickY = tickPos * yfactor
            p1 = context.trpoint(Point(graph_left, tickY))
            p2 = context.trpoint(Point(tickLeftX, tickY))
            self.view.draw_line(p1, p2, PenID.Axis)
        
        # X Labels
        labelY = graph_bottom - labels_height - self.XLABELS_PADDING
        for label in self.xlabels:
            labelText = label['text']
            labelWidth = self.view.text_size(labelText, FontID.AxisLabel)[0]
            labelX = (label['pos'] * xfactor) - (labelWidth / 2)
            text_rect = context.trrect(Rect(labelX, labelY, labelWidth, labels_height))
            self.view.draw_text(labelText, text_rect, FontID.AxisLabel)
        
        # Y Labels
        for label in self.ylabels:
            labelText = label['text']
            labelWidth = self.view.text_size(labelText, FontID.AxisLabel)[0]
            labelX = graph_left - self.YLABELS_PADDING - labelWidth
            labelY = (label['pos'] * yfactor) - (labels_height / 2)
            text_rect = context.trrect(Rect(labelX, labelY, labelWidth, labels_height))
            self.view.draw_text(labelText, text_rect, FontID.AxisLabel)
        
        # Graph title
        title = "{} ({})".format(self.title, self.currency.code)
        title_width, title_height = self.view.text_size(title, FontID.Title)
        titley = view_rect.h - self.TITLE_PADDING - title_height
        self.view.draw_text(title, Rect(0, titley, view_rect.w, title_height), FontID.Title)
        
        self.draw_graph_after_axis(context)
    
    def draw_axis_overlay_x(self, context):
        graphBottom = round(self.ymin * context.yfactor)
        # XXX Translate that one everything has been pushed to core
        # if graphBottom < 0:
        #     # We have a graph with negative values and we need some extra space to draw the lowest values
        #     graphBottom -= 2 * self.LINE_WIDTH
        graphTop = round(self.ymax * context.yfactor)
        for tickPos in self.xtickmarks[:-1]:
            tickX = tickPos * context.xfactor
            p1 = context.trpoint(Point(tickX, graphBottom))
            p2 = context.trpoint(Point(tickX, graphTop))
            self.view.draw_line(p1, p2, PenID.AxisOverlay)
    
    def draw_axis_overlay_y(self, context):
        graphLeft = round(self.xmin * context.xfactor)
        graphRight = round(self.xmax * context.xfactor)
        for tickPos in self.ytickmarks[:-1]:
            tickY = tickPos * context.yfactor
            p1 = context.trpoint(Point(graphLeft, tickY))
            p2 = context.trpoint(Point(graphRight, tickY))
            self.view.draw_line(p1, p2, PenID.AxisOverlay)
    
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
    
