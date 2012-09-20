# Created On: 2012-09-18
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QRectF, QPointF
from PyQt4.QtGui import QWidget, QBrush, QPen
    
class ChartView(QWidget):
    #--- Virtual
    def fontForID(self, fontId):
        # Return a QFont instance that is represented by fontId
        pass
    
    def colorForIndex(self, colorIndex):
        pass
    
    #--- Public
    def flipRect(self, rect):
        # Coordinates from the core are based on the origin being at the *lower* left corner. In
        # Qt, it's at the upper left corner. We have to flip that.
        x, y, w, h = rect
        y = self.height() - y - h
        return (x, y, w, h)
    
    def flipPoint(self, point):
        x, y = point
        y = self.height() - y
        return (x, y)
    
    #--- model --> view
    def draw_line(self, p1, p2, color):
        pen = QPen(color)
        pen.setWidth(1)
        painter = self.current_painter
        painter.setPen(pen)
        painter.drawLine(QPointF(*self.flipPoint(p1)), QPointF(*self.flipPoint(p2)))
    
    def draw_rect(self, rect, line_color, bg_color):
        pen = QPen(line_color)
        pen.setWidth(1)
        painter = self.current_painter
        painter.setPen(pen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRect(QRectF(*self.flipRect(rect)))
    
    def draw_pie(self, center, radius, start_angle, span_angle, gradient):
        center = self.flipPoint(center)
        centerX, centerY = center
        painter = self.current_painter
        painter.setBrush(QBrush(gradient))
        diameter = radius * 2
        # circleRect is the area that the pie drawing use for bounds
        circleRect = QRectF(centerX - radius, centerY - radius, diameter, diameter)
        # pie slices have to be drawn with 1/16th of an angle as argument
        painter.drawPie(circleRect, start_angle*16, span_angle*16)
    
    def draw_text(self, text, rect, font):
        rect = QRectF(*self.flipRect(rect))
        painter = self.current_painter
        painter.save()
        painter.setFont(font)
        painter.setPen(QPen(Qt.black))
        painter.drawText(rect, Qt.AlignHCenter|Qt.AlignVCenter, text)
        painter.restore()
