# Created By: Virgil Dupras
# Created On: 2009-11-08
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QPainter, QFont, QColor, QBrush, QPen

from core.gui.pie_chart import FontID, BrushID
from .chart_view import ChartView, gradientFromColor

#0xrrggbb
COLORS = [
    0x5dbc56,
    0x3c5bce,
    0xb6181f,
    0xe99709,
    0x9521e9,
    0x808080, # Only for "Others"
]

class PieChartView(ChartView):
    TITLE_FONT_SIZE = 12
    LEGEND_FONT_SIZE = 8
    
    def __init__(self, parent):
        ChartView.__init__(self, parent)
        self.dataSource = None
        self.colors = [QColor(rgbInt) for rgbInt in COLORS]
    
    #--- Override
    def fontForID(self, fontId):
        result = QFont(QApplication.font())
        if fontId == FontID.Title:
            result.setPointSize(self.TITLE_FONT_SIZE)
            result.setBold(True)
        else:
            result.setPointSize(self.LEGEND_FONT_SIZE)
        return result
    
    def penForID(self, penId):
        color = self.colors[penId]
        pen = QPen(color)
        pen.setWidth(1)
        return pen
    
    def brushForID(self, brushId):
        if brushId == BrushID.Legend:
            return QBrush(Qt.white)
        else:
            color = self.colors[brushId]
            gradient = gradientFromColor(color)
            return QBrush(gradient)
    
    def paintEvent(self, event):
        ChartView.paintEvent(self, event)
        if self.dataSource is None:
            return
        ds = self.dataSource
        painter = QPainter(self)
        self.current_painter = painter
        painter.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing)
        painter.fillRect(self.rect(), Qt.white)
        ds.draw()
        del self.current_painter
    
