# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-07
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
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
        
        # close the polygon and fill it.
        firstPoint = points[0]
        lastPoint = points[-1]
        points.append(QPointF(lastPoint.x(), 0))
        points.append(QPointF(firstPoint.x(), 0))
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(self.graphBrush)
        painter.drawPolygon(*points)
    
