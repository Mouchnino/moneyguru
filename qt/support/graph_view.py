# Created By: Virgil Dupras
# Created On: 2009-11-06
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFont, QPen, QColor, QBrush, QLinearGradient, QApplication

from core.gui.graph import PenID, FontID
from .chart_view import ChartView

class GraphView(ChartView):
    LINE_WIDTH = 2
    OVERLAY_AXIS_WIDTH = 0.2
    LABEL_FONT_SIZE = 8
    TITLE_FONT_SIZE = 12
    
    def __init__(self, parent=None):
        ChartView.__init__(self, parent)
        self.dataSource = None
        pen = QPen()
        pen.setColor(QColor(20, 158, 11))
        pen.setWidthF(self.LINE_WIDTH)
        self.linePen = pen
        
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QColor(93, 188, 86)) # dark green
        gradient.setColorAt(1, QColor(164, 216, 158)) # light green
        self.graphBrush = QBrush(gradient)
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
        gradient.setColorAt(0, Qt.darkGray)
        gradient.setColorAt(1, Qt.lightGray)
        self.graphFutureBrush = QBrush(gradient)
    
    def fontForID(self, fontId):
        result = QFont(QApplication.font())
        if fontId == FontID.Title:
            result.setPointSize(self.TITLE_FONT_SIZE)
            result.setBold(True)
        elif fontId == FontID.AxisLabel:
            result.setPointSize(self.LABEL_FONT_SIZE)
        return result
    
    def penForID(self, penId):
        pen = QPen()
        if penId == PenID.Axis:
            pen.setColor(Qt.darkGray)
            pen.setWidthF(self.LINE_WIDTH)
        elif penId == PenID.AxisOverlay:
            pen.setColor(Qt.darkGray)
            pen.setWidthF(self.OVERLAY_AXIS_WIDTH)
        return pen
    
