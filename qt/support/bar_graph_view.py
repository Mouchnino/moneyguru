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

class BarGraphView(GraphView):
    def _drawGraph(self, painter, xFactor, yFactor):
        ds = self.dataSource
        for x1, x2, h1, h2 in ds.data:
            x1 *= xFactor
            x2 *= xFactor
            h1 *= yFactor
            h2 *= yFactor
            
            # draw the line
            points = [QPointF(x1, 0), QPointF(x1, h1), QPointF(x2, h1), QPointF(x2, 0)]
            painter.setPen(self.linePen)
            painter.drawPolyline(*points)
            
            # fill it.
            painter.setPen(QPen(Qt.NoPen))
            painter.setBrush(self.graphBrush)
            painter.drawPolygon(*points)
    
