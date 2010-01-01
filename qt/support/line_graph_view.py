# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-07
# $Id$
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

from PyQt4.QtCore import Qt, QPointF
from PyQt4.QtGui import QPen

from .graph_view import GraphView

class LineGraphView(GraphView):
    def _drawGraph(self, painter, xFactor, yFactor):
        ds = self.dataSource
        if len(ds.data) < 2:
            return
            
        # draw the line
        points = [QPointF(x*xFactor, y*yFactor) for x, y in ds.data]
        painter.setPen(self.linePen)
        painter.drawPolyline(*points)
        
        # close the polygons and fill them.
        painter.setPen(QPen(Qt.NoPen))
        xTodayFactored = ds.xtoday * xFactor;
        pastPoints = [p for p in points if p.x() <= xTodayFactored]
        futurePoints = [p for p in points if p.x() > xTodayFactored]
        if pastPoints and futurePoints:
            meetingPoint = QPointF(xTodayFactored, pastPoints[-1].y())
            pastPoints.append(meetingPoint)
            futurePoints.insert(0, meetingPoint)
        else:
            meetingPoint = None
        # start with past
        if pastPoints:
            firstPoint = pastPoints[0]
            lastPoint = pastPoints[-1]
            pastPoints.append(QPointF(lastPoint.x(), 0))
            pastPoints.append(QPointF(firstPoint.x(), 0))
            painter.setBrush(self.graphBrush)
            painter.drawPolygon(*pastPoints)
        if futurePoints:
            firstPoint = futurePoints[0]
            lastPoint = futurePoints[-1]
            futurePoints.append(QPointF(lastPoint.x(), 0))
            futurePoints.append(QPointF(firstPoint.x(), 0))
            painter.setBrush(self.graphFutureBrush)
            painter.drawPolygon(*futurePoints)
        if meetingPoint is not None:
            pen = QPen(self.linePen)
            pen.setColor(Qt.red)
            painter.setPen(pen)
            painter.drawLine(QPointF(xTodayFactored, 0), meetingPoint)
    
