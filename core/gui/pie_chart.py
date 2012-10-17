# Created By: Virgil Dupras
# Created On: 2008-09-04
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from math import radians, sin
from itertools import combinations

from hscommon.trans import tr
from hscommon.geometry import Rect, Point
from hscommon.util import extract
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

def legends_intersect(legends):
    for legend1, legend2 in combinations(legends, 2):
        rect1, rect2 = legend1.label_rect, legend2.label_rect
        if rect1.intersects(rect2):
            return True
    return False

def spread_vertically(legends, circle_bounds):
    circle_size = min(circle_bounds.w, circle_bounds.h)
    legends.sort(key=lambda l: l.base_point.y)
    # It's possible that our pie chart is higher than wide, giving us a lot of screen estate
    # vertically. If we actually need it, great, use it. Otherwise, spread it over a height
    # equivalent to the circle's diameter (circle_size)
    # The "*1.2" part is to give us a little margin between legends
    needed_height = sum(l.label_rect.height for l in legends) * 1.2
    if circle_size > needed_height:
        # don't pack all labels in the center, use at least the circle's diameter.
        needed_height = circle_size
    interval = needed_height / len(legends)
    current_y = circle_bounds.center().y - (needed_height / 2) + (interval / 2)
    for legend in legends:
        # current_y represents where the label's center is supposed to be, that's why we
        # remove haslf the height
        legend.label_rect.y = current_y - (legend.label_rect.height / 2)
        current_y += interval

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
        # Returns a 2-sized tuple of list of {name: amount}
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
    
    def compute_pie_data(self, data):
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
            return None
        fmt = lambda name, amount: '%s %1.1f%%' % (name, amount / total * 100)
        return [(fmt(name, amount), amount, color) for name, amount, color in data]
    
    def compute(self):
        pie1, pie2 = self._get_data()
        self.pie1 = self.compute_pie_data(pie1)
        self.pie2 = self.compute_pie_data(pie2)
    
    def draw_pie(self, data, circle_bounds):
        if not data:
            return
        circle_size = min(circle_bounds.w, circle_bounds.h)
        radius = circle_size / 2
        center = circle_bounds.center()
        
        # draw pie
        total_amount = sum(amount for _, amount, _ in data)
        start_angle = 0
        legends = []
        for legend_text, amount, color_index in data:
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
        
        left, right = extract(lambda l: l.base_point.x < center.x, legends)
        # If any legend intersect, we start by sending everyone to their horizontal circle bounds.
        # Then, on each side, if anyone intersect, we go in "Spread mode", spreading all legends
        # vertically in a regular manner.
        if legends_intersect(legends):
            for legend in left:
                legend.label_rect.left = circle_bounds.left
            for legend in right:
                legend.label_rect.right = circle_bounds.right
        for side in (left, right):
            if legends_intersect(side):
                spread_vertically(side, circle_bounds)
        
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
    
    def draw_chart(self):
        view_rect = Rect(0, 0, *self.view_size)
        title = self.title
        _, title_height = self.view.text_size(title, 1)
        titley = view_rect.h - title_height - self.PADDING
        title_rect = (0, titley, view_rect.w, title_height)
        self.view.draw_text(title, title_rect, FontID.Title)
        
        if not hasattr(self, 'pie1'):
            return
        
        # circle coords
        # circle_bounds is the area in which the circle is allowed to be drawn (important for legend text)
        circle_bounds = view_rect.scaled_rect(-self.PADDING, -self.PADDING)
        circle_bounds.h -= title_height
        
        if circle_bounds.w > circle_bounds.h:
            circle_bounds.w = (circle_bounds.w - self.PADDING) / 2
            circle_bounds2 = Rect(circle_bounds.right + self.PADDING, circle_bounds.y,
                circle_bounds.w, circle_bounds.h)
        else:
            circle_bounds.h = (circle_bounds.h - self.PADDING) / 2
            # We want the first circle to be on top
            circle_bounds.y += circle_bounds.h + self.PADDING
            # hscommon.geometry has a top-left origin, we use "top" when we mean "bottom".
            circle_bounds2 = Rect(circle_bounds.x,
                circle_bounds.top - circle_bounds.h - self.PADDING, circle_bounds.w,
                circle_bounds.h)
        
        self.draw_pie(self.pie1, circle_bounds)
        self.draw_pie(self.pie2, circle_bounds2)
    
