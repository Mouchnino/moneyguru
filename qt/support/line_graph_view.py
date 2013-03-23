# Created By: Virgil Dupras
# Created On: 2009-11-07
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QPen

from core.gui.balance_graph import PenID, BrushID
from .graph_view import GraphView

class LineGraphView(GraphView):
    def penForID(self, penId):
        if penId == PenID.Graph:
            return self.linePen
        elif penId == PenID.TodayLine:
            pen = QPen(self.linePen)
            pen.setColor(Qt.red)
            return pen
        else:
            return GraphView.penForID(self, penId)
    
    def brushForID(self, brushId):
        if brushId == BrushID.GraphNormal:
            return self.graphBrush
        elif brushId == BrushID.GraphFuture:
            return self.graphFutureBrush
    
