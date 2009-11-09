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
    PADDING = 4
    TITLE_FONT_FAMILY = "Lucida Grande"
    TITLE_FONT_SIZE = 15
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
        titleText = ds.title
        painter.setFont(self.titleFont)
        fm = painter.fontMetrics()
        titleHeight = fm.height()
        titleAscent = fm.ascent()
        titleWidth = fm.width(titleText)
        
        # circle coords
        maxWidth = viewWidth - (self.PADDING * 2)
        maxHeight = viewHeight - titleHeight - (self.PADDING * 2)
        circleSize = min(maxWidth, maxHeight)
        radius = circleSize / 2
        centerX = viewWidth / 2 
        centerY = ((viewHeight - titleHeight) / 2) + titleHeight
        circleRect = QRectF(centerX - radius, centerY - radius, circleSize, circleSize)
        
        # draw title
        painter.setFont(self.titleFont)
        titleX = (viewWidth - titleWidth) / 2
        titleY = self.PADDING + titleAscent
        painter.drawText(QPointF(titleX, titleY), titleText)
        
        # draw pie
        totalAmount = sum(amount for _, amount in ds.data)
        startAngle = 0
        for (_, amount), gradient in zip(ds.data, self.gradients):
            fraction = amount / totalAmount
            angle = fraction * 360
            painter.setBrush(QBrush(gradient))
            # pie slices have to be drawn with 1/16th of an angle as argument
            painter.drawPie(circleRect, startAngle*16, angle*16)
            startAngle += angle
    
