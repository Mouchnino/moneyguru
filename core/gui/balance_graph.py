# Created By: Virgil Dupras
# Created On: 2008-07-06
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from datetime import date

from hscommon.geometry import Point

from ..model.date import ONE_DAY
from .graph import Graph, PenID as PenIDBase

class PenID(PenIDBase):
    Graph = 3
    TodayLine = 4

class BrushID:
    GraphNormal = 1
    GraphFuture = 2

class BalanceGraph(Graph):
    # BalanceGraph's data point is (float x, float y)
    #--- Virtual
    def _balance_for_date(self, date):
        return 0
    
    def _budget_for_date(self, date):
        return 0
    
    #--- Override
    # Computation Notes: When the balance in the graph changes, we have to create a flat line until
    # one day prior to the change. However, when budgets are involved, the line is *not* flattened.
    # To save some calculations (in a year range, those take a lot of time if they're made every day), 
    # rather than calculating the budget every day, they are only calculated when the balance without
    # budget changes. this is what the algorithm below reflects.
    def compute_data(self):
        date_range = self.document.date_range
        TODAY = date.today()
        date2value = {}
        last_balance = self._balance_for_date(date_range.start - ONE_DAY)
        if last_balance:
            date2value[date_range.start] = last_balance
        for date_point in date_range:
            balance = self._balance_for_date(date_point)
            if (balance != last_balance) or (date_point == TODAY) or (date_point == date_range.end):
                if date2value and last_balance != balance:
                    # create a "step"
                    date2value[date_point] = last_balance
                date2value[date_point + ONE_DAY] = balance
                last_balance = balance
        for date_point, value in list(date2value.items()):
            if date_point <= TODAY:
                continue
            budget = self._budget_for_date(date_point - ONE_DAY)
            if budget:
                date2value[date_point] += budget
        if date_range.start not in date2value and date_range.start > TODAY:
            budget = self._budget_for_date(date_range.start - ONE_DAY)
            date2value[date_range.start] = budget
        self._data = []
        # if there's only zeroes, keep the data empty
        if any(date2value.values()):
            for date_point, value in sorted(date2value.items()):
                pos = self._offset_xpos(date_point.toordinal())
                self._data.append((pos, float(value)))
    
    def yrange(self):
        if self._data:
            ymin = min(point[1] for point in self._data)
            ymax = max(point[1] for point in self._data)
            return (ymin, ymax)
        else:
            return (0, 1)
    
    def draw(self, xfactor, yfactor):
        if len(self.data) < 2:
            return
        
        points = [Point(x*xfactor, y*yfactor) for x, y in self.data]
        
        # close the polygons and fill them.
        # The closing point depends if we have a positive graph, a negative one or a mixed up
        if self.ymin >= 0: # positive
            yClose = round(self.ymin * yfactor)
        elif self.ymax < 0: # negative
            yClose = round(self.ymax * yfactor)
        else: # mixed up
            yClose = 0
        # painter.setPen(QPen(Qt.NoPen))
        xTodayfactored = self.xtoday * xfactor;
        pastPoints = [p for p in points if p.x <= xTodayfactored]
        futurePoints = [p for p in points if p.x > xTodayfactored]
        if pastPoints and futurePoints:
            meetingPoint = Point(xTodayfactored, pastPoints[-1].y)
            pastPoints.append(meetingPoint)
            futurePoints.insert(0, meetingPoint)
        else:
            meetingPoint = None
        # start with past
        if pastPoints:
            firstPoint = pastPoints[0]
            lastPoint = pastPoints[-1]
            pastPoints.append(Point(lastPoint.x, yClose))
            pastPoints.append(Point(firstPoint.x, yClose))
            self.view.draw_polygon(pastPoints, None, BrushID.GraphNormal)
        if futurePoints:
            firstPoint = futurePoints[0]
            lastPoint = futurePoints[-1]
            futurePoints.append(Point(lastPoint.x, yClose))
            futurePoints.append(Point(firstPoint.x, yClose))
            self.view.draw_polygon(futurePoints, None, BrushID.GraphFuture)
        if meetingPoint is not None:
            self.view.draw_line(Point(xTodayfactored, yClose), meetingPoint, PenID.TodayLine)
        
        self.draw_axis_overlay_y(xfactor, yfactor)
        self.draw_axis_overlay_x(xfactor, yfactor)
        
        # draw the main graph line. It looks better when that line is drawn after the overlay.
        self.view.draw_polygon(points, PenID.Graph, None)
    
    @property
    def title(self):
        return ''
    
    @property
    def currency(self):
        return None
    
    @property
    def xtoday(self):
        """The X value representing today"""
        return self._offset_xpos(date.today().toordinal() + 1)
    
