# Created By: Virgil Dupras
# Created On: 2009-11-08
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QPainter, QFont, QColor

from core.gui.pie_chart import FontID, ColorIndex
from .chart_view import ChartView

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
        
        self.titleFont = QFont(QApplication.font())
        self.titleFont.setPointSize(self.TITLE_FONT_SIZE)
        self.titleFont.setBold(True)
        self.legendFont = QFont(QApplication.font())
        self.legendFont.setPointSize(self.LEGEND_FONT_SIZE)
    
    #--- Override
    def fontForID(self, fontId):
        if fontId == FontID.Title:
            return self.titleFont
        else:
            return self.legendFont
    
    def colorForIndex(self, colorIndex):
        if colorIndex == ColorIndex.LegendBackground:
            return Qt.white
        else:
            return self.colors[colorIndex]
    
    def resizeEvent(self, event):
        self.dataSource.set_view_size(self.width(), self.height())
    
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
    
