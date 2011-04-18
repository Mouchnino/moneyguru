# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-07
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QPointF, QRectF
from PyQt4.QtGui import QPen

from .graph_view import GraphView

class BarGraphView(GraphView):
    DRAW_XAXIS_OVERLAY = False
    
    def _drawGraph(self, painter, xFactor, yFactor):
        ds = self.dataSource
        for x1, x2, h1, h2 in ds.data:
            x1 *= xFactor
            x2 *= xFactor
            h1 *= yFactor
            h2 *= yFactor
            
            differentSide = (h1 >= 0) != (h2 >= 0)
            pastRect = QRectF(x1, 0, x2-x1, abs(h1))
            if h2:
                futureHeight = abs(h2 if differentSide else h2-h1)
            else:
                futureHeight = 0
            futureRect = QRectF(x1, 0, x2-x1, futureHeight)
            # WARNING. This part here is confusing. We're in an inverted scale, so the QRect's
            # bottom/top are also inverted.
            if h1 >= 0:
                pastRect.moveBottom(h1)
            else:
                pastRect.moveTop(h1)
            if h2 >= 0:
                futureRect.moveBottom(h2)
            else:
                futureRect.moveTop(h2)
            union = pastRect.united(futureRect)
            
            # draw the line
            painter.setPen(self.linePen)
            if (union.top() < 0) and (union.bottom() > 0): # we draw 4 sides instead of 3
                painter.drawRect(union)
            else:
                # One of bottom and top is 0. Use the other one. We're working with floats here,
                # comparison with 0 are hazardous, so I'm avoiding them.
                h = union.top() if abs(union.top()) >= abs(union.bottom()) else union.bottom()
                points = [QPointF(x1, 0), QPointF(x1, h), QPointF(x2, h), QPointF(x2, 0)]
                painter.drawPolyline(*points)
            
            # fill it.
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(self.graphBrush)
            painter.drawRect(pastRect)
            painter.setBrush(self.graphFutureBrush)
            painter.drawRect(futureRect)
            
            # draw red line
            if (h1 != 0) and (h2 != 0):
                lineY = 0 if differentSide else h1
                pen = QPen(self.linePen)
                pen.setColor(Qt.red)
                painter.setPen(pen)
                painter.drawLine(x1, lineY, x2, lineY)
    
