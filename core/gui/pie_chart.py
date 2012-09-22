# Created By: Virgil Dupras
# Created On: 2008-09-04
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from math import radians, sin

from hscommon.trans import tr
from hscommon.geometry import Rect, Point
from .chart import Chart

# A pie chart's data is a list of (name, (float)amount). The name part is ready for display. It
# is exactly what should be in the legend of the pie chat (it has amount and %)

# Regardless of the view size, we always display this number of slices. If we have more, we group
# them under "Others"
MIN_SLICE_COUNT = 6
# This is the number of colors that our GUI layers must have. If we display more slices than we have
# colors, we cycle through them (except of the last color, which is always for the "Others" pie).
COLOR_COUNT = 6
MIN_VIEW_SIZE = 250 # Size at which we start counting for eventual extra slices
SIZE_COST_FOR_SLICE = 30 # Number of pixels we need to count an extra slice

def point_in_circle(center, radius, angle):
    # Returns the point at the edge of a circle with specified center/radius/angle
    # a/sin(A) = b/sin(B) = c/sin(C) = 2R
    # the start point is (center.x + radius, center.y) and goes counterclockwise
    angle = angle % 360
    C = radians(90)
    A = radians(angle % 90)
    B = C - A
    c = radius
    ratio = c / sin(C)
    b = ratio * sin(B)
    a = ratio * sin(A)
    if angle > 270:
        return Point(center.x + a, center.y - b)
    elif angle > 180:
        return Point(center.x - b, center.y - a)
    elif angle > 90:
        return Point(center.x - a, center.y + b)
    else:
        return Point(center.x + b, center.y + a)

def rect_from_center(center, size):
    # Returns a Rect centered on `center` with size `size`
    w, h = size
    x = center.x - w / 2
    y = center.y - h / 2
    return Rect(x, y, w, h)

def pull_rect_in(rect, container):
    # The top and bottom denomination are reversed (in hscommon.geometry, rect.top is rect.y and
    # in here, it's rect.y + rect.h) but it doesn't matter because the < and > comparison stay the
    # same. It's a bit of a mind bender, but it works.
    if container.contains_rect(rect):
        return
    if rect.top < container.top:
        rect.top = container.top
    elif rect.bottom > container.bottom:
        rect.bottom = container.bottom
    if rect.left < container.left:
        rect.left = container.left
    elif rect.right > container.right:
        rect.right = container.right

class FontID:
    Title = 1
    Legend = 2

class BrushID:
    # Indexes 0 to COLOR_COUNT-1 are for the different pie slices brush
    Legend = 10

class Legend:
    PADDING = 2 # the padding between legend text and the rectangle behind it
    
    def __init__(self, text, color, angle):
        self.text = text
        self.color = color
        self.angle = angle
        self.base_point = None
        self.text_rect = None
        self.label_rect = None
    
    def compute_label_rect(self):
        self.label_rect = self.text_rect.scaled_rect(self.PADDING, self.PADDING)
    
    def compute_text_rect(self):
        self.text_rect = self.label_rect.scaled_rect(-self.PADDING, -self.PADDING)
    
    def should_draw_line(self):
        return not self.label_rect.contains_point(self.base_point)
    

class PieChart(Chart):
    PADDING = 6
    
    def __init__(self, parent_view):
        Chart.__init__(self, parent_view)
        self.slice_count = MIN_SLICE_COUNT
    
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
        if slice_count != self.slice_count:
            self.slice_count = slice_count
            self._revalidate()
    
    def compute(self):
        self._data = []
        data = self._get_data()
        data = [(name, float(amount)) for name, amount in data.items() if amount > 0]
        data.sort(key=lambda t: t[1], reverse=True)
        data = [(name, amount, i % (COLOR_COUNT-1)) for i, (name, amount) in enumerate(data)]
        if len(data) > self.slice_count:
            others = data[self.slice_count-1:]
            others_total = sum(amount for _, amount, _ in others)
            del data[self.slice_count-1:]
            data.append((tr('Others'), others_total, COLOR_COUNT-1))
        total = sum(amount for _, amount, _ in data)
        if not total:
            return
        fmt = lambda name, amount: '%s %1.1f%%' % (name, amount / total * 100)
        self._data = [(fmt(name, amount), amount, color) for name, amount, color in data]
    
    def draw(self):
        view_rect = Rect(0, 0, *self.view_size)
        title = self.title
        _, title_height = self.view.text_size(title, 1)
        titley = view_rect.h - title_height - self.PADDING
        title_rect = (0, titley, view_rect.w, title_height)
        self.view.draw_text(title, title_rect, FontID.Title)
        
        if not hasattr(self, '_data'):
            return
        
        # circle coords
        # circle_bounds is the area in which the circle is allowed to be drawn (important for legend text)
        circle_bounds = view_rect.scaled_rect(-self.PADDING, -self.PADDING)
        circle_bounds.h -= title_height
        # circle_bounds = Rect(self.PADDING, self.PADDING + title_height, max_width, max_height)
        circle_size = min(circle_bounds.w, circle_bounds.h)
        radius = circle_size / 2
        center = circle_bounds.center()
        
        # draw pie
        total_amount = sum(amount for _, amount, _ in self.data)
        start_angle = 0
        legends = []
        for legend_text, amount, color_index in self.data:
            fraction = amount / total_amount
            angle = fraction * 360
            self.view.draw_pie(center, radius, start_angle, angle, color_index)
            legend_angle = start_angle + (angle / 2)
            legend = Legend(text=legend_text, color=color_index, angle=legend_angle)
            legends.append(legend)
            start_angle += angle
        
        # compute legend rects
        _, legend_height = self.view.text_size('', FontID.Legend)
        for legend in legends:
            legend.base_point = point_in_circle(center, radius, legend.angle)
            legend_width, _ = self.view.text_size(legend.text, FontID.Legend)
            legend.text_rect = rect_from_center(legend.base_point, (legend_width, legend_height))
            legend.compute_label_rect()
        
        # make sure they're inside circle_bounds
        for legend in legends:
            pull_rect_in(legend.label_rect, circle_bounds)
        
        # send to the sides of the chart
        for legend in legends:
            if legend.base_point.x < center.x:
                legend.label_rect.left = circle_bounds.left
            else:
                legend.label_rect.right = circle_bounds.right
        
        # Make sure the labels are not one over another
        for legend1, legend2 in zip(legends, legends[1:]):
            rect1, rect2 = legend1.label_rect, legend2.label_rect
            if not rect1.intersects(rect2):
                continue
            # Here, we use legend.base_point.y() rather than rect.top() to determine which rect is
            # the highest because rect1 might already have been pushed up earlier, and end up being
            # the highest, when in fact it's rect2 that "deserves" to be the highest.
            p1, p2 = legend1.base_point, legend2.base_point
            highest, lowest = (rect1, rect2) if p1.y < p2.y else (rect2, rect1)
            highest.bottom = lowest.top - 1
        
        # draw legends
        # draw lines before legends because we don't want them being drawn over other legends
        if len(legends) > 1:
            for legend in legends:
                if not legend.should_draw_line():
                    continue
                self.view.draw_line(legend.label_rect.center(), legend.base_point, legend.color)
        for legend in legends:
            self.view.draw_rect(legend.label_rect, legend.color, BrushID.Legend)
            legend.compute_text_rect()
            self.view.draw_text(legend.text, legend.text_rect, FontID.Legend)
    