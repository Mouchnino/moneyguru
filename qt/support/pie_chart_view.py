# Created By: Virgil Dupras
# Created On: 2009-11-08
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from math import radians, sin

from PyQt4.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt4.QtGui import (QApplication, QWidget, QPainter, QFont, QPen, QColor, QBrush,
    QLinearGradient)

def pointInCircle(center, radius, angle):
    # Returns the point at the edge of a circle with specified center/radius/angle
    # a/sin(A) = b/sin(B) = c/sin(C) = 2R
    # the start point is (center.x + radius, center.y) and goes counterclockwise
    # (this was based on the objc implementation, but since the Ys are upside down in Qt, we have
    # to switch the Ys here as well)
    angle = angle % 360
    C = radians(90)
    A = radians(angle % 90)
    B = C - A
    c = radius
    ratio = c / sin(C)
    b = ratio * sin(B)
    a = ratio * sin(A)
    if angle > 270:
        return QPointF(center.x() + a, center.y() + b)
    elif angle > 180:
        return QPointF(center.x() - b, center.y() + a)
    elif angle > 90:
        return QPointF(center.x() - a, center.y() - b)
    else:
        return QPointF(center.x() + b, center.y() - a)

def rectFromCenter(center, size):
    # Returns a QRectF centered on `center` with size `size`
    x = center.x() - size.width() / 2
    y = center.y() - size.height() / 2
    return QRectF(QPointF(x, y), size)

def pullRectIn(rect, container):
    if container.contains(rect):
        return
    if rect.top() < container.top():
        rect.moveTop(container.top())
    elif rect.bottom() > container.bottom():
        rect.moveBottom(container.bottom())
    if rect.left() < container.left():
        rect.moveLeft(container.left())
    elif rect.right() > container.right():
        rect.moveRight(container.right())

class Legend:
    PADDING = 2 # the padding between legend text and the rectangle behind it
    
    def __init__(self, text, color, angle):
        self.text = text
        self.color = color
        self.angle = angle
        self.basePoint = None
        self.textRect = None
        self.labelRect = None
    
    def computeLabelRect(self):
        padding = self.PADDING
        self.labelRect = self.textRect.adjusted(-padding, -padding, padding*2, padding*2)
    
    def computeTextRect(self):
        padding = self.PADDING
        self.textRect = self.labelRect.adjusted(padding, padding, -padding*2, -padding*2)
    
    def shouldDrawLine(self):
        return not self.labelRect.contains(self.basePoint)
    

class PieChartView(QWidget):
    PADDING = 4
    TITLE_FONT_SIZE = 12
    LEGEND_FONT_SIZE = 8
    LINE_WIDTH = 1
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.dataSource = None
        self.gradients = None
        
        self.titleFont = QFont(QApplication.font())
        self.titleFont.setPointSize(self.TITLE_FONT_SIZE)
        self.titleFont.setBold(True)
        self.legendFont = QFont(QApplication.font())
        self.legendFont.setPointSize(self.LEGEND_FONT_SIZE)
    
    def _gradientsFromColors(self, colors):
        gradients = []
        for rgbInt in colors:
            gradient = QLinearGradient(0, 0, 0, 1)
            gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
            color = QColor(rgbInt)
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, color.lighter())
            gradients.append(gradient)
        return gradients
    
    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        if self.dataSource is None:
            return
        ds = self.dataSource
        if self.gradients is None:
            self.gradients = self._gradientsFromColors(ds.colors())
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        painter.fillRect(self.rect(), Qt.white)
        
        # view dimensions
        viewWidth = self.width()
        viewHeight = self.height()
        
        # title dimensions
        painter.setFont(self.titleFont)
        fm = painter.fontMetrics()
        titleText = ds.title
        titleHeight = fm.height()
        titleAscent = fm.ascent()
        titleWidth = fm.width(titleText)
        
        # circle coords
        maxWidth = viewWidth - (self.PADDING * 2)
        maxHeight = viewHeight - titleHeight - (self.PADDING * 2)
        # circleBounds is the area in which the circle is allwed to be drawn (important for legend text)
        circleBounds = QRectF(self.PADDING, self.PADDING + titleHeight, maxWidth, maxHeight)
        circleSize = min(maxWidth, maxHeight)
        radius = circleSize / 2
        center = circleBounds.center()
        # cirectRect is the area that the pie drawing use for bounds
        circleRect = QRectF(center.x() - radius, center.y() - radius, circleSize, circleSize)
        
        # draw title
        painter.setFont(self.titleFont)
        titleX = (viewWidth - titleWidth) / 2
        titleY = self.PADDING + titleAscent
        painter.drawText(QPointF(titleX, titleY), titleText)
        
        # draw pie
        totalAmount = sum(amount for _, amount, _ in ds.data)
        startAngle = 0
        legends = []
        for (legendText, amount, colorIndex) in ds.data:
            gradient = self.gradients[colorIndex]
            fraction = amount / totalAmount
            angle = fraction * 360
            painter.setBrush(QBrush(gradient))
            # pie slices have to be drawn with 1/16th of an angle as argument
            painter.drawPie(circleRect, startAngle*16, angle*16)
            # stops is a QVector<QPair<qreal, QColor>>. We chose the dark color of the gardient.
            legendColor = gradient.stops()[0][1]
            legendAngle = startAngle + (angle / 2)
            legend = Legend(text=legendText, color=legendColor, angle=legendAngle)
            legends.append(legend)
            startAngle += angle
        
        # compute legend rects
        painter.setFont(self.legendFont)
        fm = painter.fontMetrics()
        legendHeight = fm.height()
        
        # base rects
        for legend in legends:
            legend.basePoint = pointInCircle(center, radius, legend.angle)
            legendWidth = fm.width(legend.text)
            legend.textRect = rectFromCenter(legend.basePoint, QSizeF(legendWidth, legendHeight))
            legend.computeLabelRect()
        
        # make sure they're inside circleBounds
        for legend in legends:
            pullRectIn(legend.labelRect, circleBounds)
        
        # send to the sides of the chart
        for legend in legends:
            if legend.basePoint.x() < center.x():
                legend.labelRect.moveLeft(self.PADDING)
            else:
                legend.labelRect.moveRight(self.PADDING + maxWidth)
        
        # Make sure the labels are not one over another
        for legend1, legend2 in zip(legends, legends[1:]):
            rect1, rect2 = legend1.labelRect, legend2.labelRect
            if not rect1.intersects(rect2):
                continue
            # Here, we use legend.basePoint.y() rather than rect.top() to determine which rect is
            # the highest because rect1 might already have been pushed up earlier, and end up being
            # the highest, when in fact it's rect2 that "deserves" to be the highest.
            p1, p2 = legend1.basePoint, legend2.basePoint
            highest, lowest = (rect1, rect2) if p1.y() < p2.y() else (rect2, rect1)
            highest.moveBottom(lowest.top()-1)
        
        # draw legends
        painter.setBrush(QBrush(Qt.white))
        # draw lines before legends because we don't want them being drawn over other legends
        if len(legends) > 1:
            for legend in legends:
                if not legend.shouldDrawLine():
                    continue
                pen = QPen(legend.color)
                pen.setWidth(self.LINE_WIDTH)
                painter.setPen(pen)
                painter.drawLine(legend.labelRect.center(), legend.basePoint)
        for legend in legends:
            pen = QPen(legend.color)
            pen.setWidth(self.LINE_WIDTH)
            painter.setPen(pen)
            painter.drawRect(legend.labelRect) # The label behind the text
            painter.setPen(QPen(Qt.black))
            legend.computeTextRect()
            painter.drawText(legend.textRect, 0, legend.text) # the text
    
