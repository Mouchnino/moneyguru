# Created By: Virgil Dupras
# Created On: 2009-12-06
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from itertools import combinations

from PyQt4.QtCore import Qt, QRect, QSize, QPoint
from PyQt4.QtGui import QPixmap, QPainter, QApplication, QFont, QFontMetrics

from hscommon.util import first

class LayoutElement:
    def __init__(self, rect):
        self.rect = rect
    
    def render(self, painter):
        raise NotImplementedError()
    
    def placed(self):
        # Called after the element has been placed on a page layout
        pass
    

class LayoutViewElement(LayoutElement):
    def __init__(self, view, rect):
        LayoutElement.__init__(self, rect)
        self.view = view
    
    def render(self, painter):
        pixmap = QPixmap(self.view.size())
        pixPainter = QPainter()
        pixPainter.begin(pixmap)
        self.view.render(pixPainter)
        pixPainter.end()
        scaledPixmap = pixmap.scaled(self.rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        drawRect = QRect(self.rect.topLeft(), scaledPixmap.size())
        painter.drawPixmap(drawRect, scaledPixmap)
    

class LayoutTitleElement(LayoutElement):
    def __init__(self, page):
        font = QFont(QApplication.font())
        font.setBold(True)
        fm = QFontMetrics(font)
        titleBase = page.viewPrinter.title
        titleLineCount = len(titleBase.split('\n'))
        titleHeight = fm.height() * titleLineCount
        rect = QRect(page.pageRect.topLeft(), QSize(page.pageRect.width(), titleHeight))
        LayoutElement.__init__(self, rect)
        self.page = page
        self.font = font
    
    def render(self, painter):
        text = self.page.title
        painter.save()
        painter.setFont(self.font)
        painter.drawText(self.rect, Qt.AlignCenter, text)
        painter.restore()
    

class LayoutPage(object):
    def __init__(self, viewPrinter):
        self.viewPrinter = viewPrinter
        self.pageRect = QRect(QPoint(0, 0), viewPrinter.pageSize)
        self.elements = []
        self.availableRects = [self.pageRect]
        self.fit(LayoutTitleElement(self))
    
    def _computeAvailableRects(self):
        # For each element, we end up with potentially 2 available rects: 
        # 1. QRect(e.right(), e.top(), page.right()-e.right(), page.bottom()-e.top())
        # 2. QRect(e.left(), e.bottom(), page.right()-e.left(), page.bottom()-e.bottom())
        # However, for each *other* element besides the first one, we have to shrink previous
        # available rects and create new, smaller ones. For simplicity, we only go "downward-right"
        # We're not bothering ourselves with space that might still be free up or at the left of the
        # elements.
        availableRects = [self.pageRect]
        for element in self.elements:
            rect = element.rect
            newAvailableRects = []
            for previous in availableRects:
                if rect.contains(previous):
                    continue # This available rect has been entirely eaten up
                inter = rect & previous
                if inter:
                    if inter.right() < previous.right():
                        # We still have some space left next to the element
                        available = QRect(inter.right()+1, previous.top(), 
                            previous.right()-inter.right()-1, previous.height())
                        newAvailableRects.append(available)
                    if inter.bottom() < previous.bottom():
                        # We still have some space left under the element
                        available = QRect(previous.left(), inter.bottom()+1, previous.width(), 
                            previous.bottom()-inter.bottom()-1)
                        newAvailableRects.append(available)
                else:
                    newAvailableRects.append(previous)
            # At this point, we might have "duplicate" available rects (some rects are contained
            # in others). We want to eliminate them.
            # We use a list instead of a set because QRect is unhashable. Screw performance!
            duplicates = [r1 for r1, r2 in combinations(newAvailableRects, 2) if r2.contains(r1)]
            availableRects = [r for r in newAvailableRects if r not in duplicates]
        self.availableRects = availableRects
    
    def fit(self, element, expandH=False, expandV=False):
        # Go through all available rects and take the first one that fits.
        fits = lambda rect: rect.width() >= element.rect.width() and rect.height() >= element.rect.height()
        fittingRect = first(r for r in self.availableRects if fits(r))
        if fittingRect is None:
            return False
        element.rect.moveTopLeft(fittingRect.topLeft())
        if expandH:
            element.rect.setWidth(fittingRect.width())
        if expandV:
            element.rect.setHeight(fittingRect.height())
        self.elements.append(element)
        element.placed()
        self._computeAvailableRects()
        return True
    
    def render(self, painter):
        for element in self.elements:
            element.render(painter)
    
    @property
    def maxAvailableWidth(self):
        return max(rect.width() for rect in self.availableRects)
    
    @property
    def title(self):
        pageNumber = self.viewPrinter.layoutPages.index(self) + 1
        pageCount = len(self.viewPrinter.layoutPages)
        title = self.viewPrinter.title
        return "{title} (Page {pageNumber} of {pageCount})".format(**locals())
    
