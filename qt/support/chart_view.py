# Created On: 2012-09-18
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt, QRectF
from PyQt4.QtGui import QWidget

class ChartView(QWidget):
    #--- Virtual
    def fontForID(self, fontId):
        # Return a QFont instance that is represented by fontId
        pass
    
    #--- Public
    def flipRect(self, rect):
        # Coordinates from the core are based on the origin being at the *lower* left corner. In
        # Qt, it's at the upper left corner. We have to flip that.
        x, y, w, h = rect
        y = self.height() - y - h
        return (x, y, w, h)
    
    #--- model --> view
    def draw_text(self, text, rect, font):
        rect = QRectF(*rect)
        painter = self.current_painter
        painter.save()
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignHCenter|Qt.AlignVCenter, text)
        painter.restore()
