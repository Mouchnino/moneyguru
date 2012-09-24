# Created On: 2012-09-18
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QRectF, QPointF
from PyQt4.QtGui import QWidget, QPen, QLinearGradient, QPainter

# Used by subclasses for brush creation
def gradientFromColor(color):
    gradient = QLinearGradient(0, 0, 0, 1)
    gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
    gradient.setColorAt(0, color)
    gradient.setColorAt(1, color.lighter())
    return gradient

class ChartView(QWidget):
    #--- Virtual
    def fontForID(self, fontId):
        # Return a QFont instance that is represented by fontId
        pass
    
    def penForID(self, penId):
        pass
    
    def brushForID(self, brushId):
        pass
    
    #--- Override
    def resizeEvent(self, event):
        if self.dataSource is not None:
            self.dataSource.set_view_size(self.width(), self.height())
    
    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        if self.dataSource is None:
            return
        painter = QPainter(self)
        self.current_painter = painter
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        painter.fillRect(self.rect(), Qt.white)
        self.dataSource.draw()
        del self.current_painter
    
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
    def draw_line(self, p1, p2, pen):
        painter = self.current_painter
        painter.setPen(pen)
        painter.drawLine(QPointF(*self.flipPoint(p1)), QPointF(*self.flipPoint(p2)))
    
    def draw_rect(self, rect, pen, brush):
        painter = self.current_painter
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(QRectF(*self.flipRect(rect)))
    
    def draw_pie(self, center, radius, start_angle, span_angle, brush):
        center = self.flipPoint(center)
        centerX, centerY = center
        painter = self.current_painter
        painter.setPen(QPen())
        painter.setBrush(brush)
        diameter = radius * 2
        # circleRect is the area that the pie drawing use for bounds
        circleRect = QRectF(centerX - radius, centerY - radius, diameter, diameter)
        # pie slices have to be drawn with 1/16th of an angle as argument
        painter.drawPie(circleRect, start_angle*16, span_angle*16)
    
    def draw_polygon(self, points, pen, brush):
        points = [QPointF(*self.flipPoint(p)) for p in points]
        painter = self.current_painter
        painter.setPen(pen)
        painter.setBrush(brush)
        if brush.style() == Qt.NoBrush:
            painter.drawPolyline(*points)
        else:
            painter.drawPolygon(*points)
    
    def draw_text(self, text, rect, font):
        rect = QRectF(*self.flipRect(rect))
        painter = self.current_painter
        painter.save()
        painter.setFont(font)
        painter.setPen(QPen(Qt.black))
        painter.drawText(rect, Qt.AlignHCenter|Qt.AlignVCenter, text)
        painter.restore()
