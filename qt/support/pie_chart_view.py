# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-08
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

from math import radians, sin

from PyQt4.QtCore import Qt, QPointF, QRectF, QSizeF
from PyQt4.QtGui import QWidget, QPainter, QFont, QPen, QColor, QBrush, QLinearGradient

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

class PieChartView(QWidget):
    PADDING = 4
    TITLE_FONT_FAMILY = "Lucida Grande"
    TITLE_FONT_SIZE = 15
    LEGEND_FONT_FAMILY = "Lucida Grande"
    LEGEND_FONT_SIZE = 11
    LEGEND_PADDING = 2 # the padding between legend text and the rectangle behind it
    LINE_WIDTH = 1
    
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        self.dataSource = None
        COLORS = [
            (93, 188, 86),
            (60, 91, 206),
            (182, 24, 31),
            (233, 151, 9),
            (149, 33, 233),
            (128, 128, 128),
        ]
        
        gradients = []
        for r, g, b in COLORS:
            gradient = QLinearGradient(0, 0, 0, 1)
            gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
            color = QColor(r, g, b)
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, color.lighter())
            gradients.append(gradient)
        self.gradients = gradients
        
        self.titleFont = QFont(self.TITLE_FONT_FAMILY, self.TITLE_FONT_SIZE, QFont.Bold)
        self.legendFont = QFont(self.LEGEND_FONT_FAMILY, self.LEGEND_FONT_SIZE, QFont.Normal)
    
    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        if self.dataSource is None:
            return
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        painter.fillRect(self.rect(), Qt.white)
        ds = self.dataSource
        
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
        totalAmount = sum(amount for _, amount in ds.data)
        startAngle = 0
        legendAngles = []
        for (_, amount), gradient in zip(ds.data, self.gradients):
            fraction = amount / totalAmount
            angle = fraction * 360
            painter.setBrush(QBrush(gradient))
            # pie slices have to be drawn with 1/16th of an angle as argument
            painter.drawPie(circleRect, startAngle*16, angle*16)
            legendAngles.append(startAngle + (angle / 2))
            startAngle += angle
        
        # draw legends
        painter.setFont(self.legendFont)
        painter.setBrush(QBrush(Qt.white))
        fm = painter.fontMetrics()
        legendHeight = fm.height()
        legendPadding = self.LEGEND_PADDING
        for (text, _), angle, gradient in zip(ds.data, legendAngles, self.gradients):
            point = pointInCircle(center, radius, angle)
            # stops is a QVector<QPair<qreal, QColor>>. We chose the dark color of the gardient.
            legendColor = gradient.stops()[0][1]
            legendWidth = fm.width(text)
            legendRect = rectFromCenter(point, QSizeF(legendWidth, legendHeight))
            labelRect = legendRect.adjusted(-legendPadding, -legendPadding, legendPadding*2, legendPadding*2)
            pen = QPen(legendColor)
            pen.setWidth(self.LINE_WIDTH)
            painter.setPen(pen)
            painter.drawRect(labelRect) # The label behind the text
            painter.setPen(QPen(Qt.black))
            painter.drawText(legendRect, 0, text) # the text
    
