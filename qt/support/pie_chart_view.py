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

from PyQt4.QtCore import Qt, QPointF, QRectF
from PyQt4.QtGui import QWidget, QPainter, QFont, QFontMetrics, QPen, QColor, QBrush, QLinearGradient

class PieChartView(QWidget):
    PADDING = 16
    
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
    
    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        if self.dataSource is None:
            return
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        painter.fillRect(self.rect(), Qt.white)
        ds = self.dataSource
        
        viewWidth = self.width()
        viewHeight = self.height()
        maxWidth = viewWidth - (self.PADDING * 2)
        maxHeight = viewHeight - (self.PADDING * 2)
        circleSize = min(maxWidth, maxHeight)
        radius = circleSize / 2
        centerX = viewWidth / 2 
        centerY = viewHeight / 2
        circleRect = QRectF(centerX - radius, centerY - radius, circleSize, circleSize)
        
        # pie
        totalAmount = sum(amount for _, amount in ds.data)
        startAngle = 0
        for (_, amount), gradient in zip(ds.data, self.gradients):
            fraction = amount / totalAmount
            angle = fraction * 360
            painter.setBrush(QBrush(gradient))
            # pie slices have to be drawn with 1/16th of an angle as argument
            painter.drawPie(circleRect, startAngle*16, angle*16)
            startAngle += angle
    
