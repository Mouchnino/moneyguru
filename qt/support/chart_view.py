# Created On: 2012-09-18
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QRectF
from PyQt4.QtGui import QWidget, QBrush

class ChartView(QWidget):
    #--- Virtual
    def fontForID(self, fontId):
        # Return a QFont instance that is represented by fontId
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
    def draw_pie(self, center, radius, start_angle, span_angle, color_index):
        center = self.flipPoint(center)
        centerX, centerY = center
        painter = self.current_painter
        gradient = self.gradients[color_index]
        painter.setBrush(QBrush(gradient))
        diameter = radius * 2
        # circleRect is the area that the pie drawing use for bounds
        circleRect = QRectF(centerX - radius, centerY - radius, diameter, diameter)
        # pie slices have to be drawn with 1/16th of an angle as argument
        painter.drawPie(circleRect, start_angle*16, span_angle*16)
    
    def draw_text(self, text, rect, font):
        rect = QRectF(*rect)
        painter = self.current_painter
        painter.save()
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignHCenter|Qt.AlignVCenter, text)
        painter.restore()
