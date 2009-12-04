# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import Qt, QRect, QPoint
from PyQt4.QtGui import QPixmap, QPainter

from hsutil.misc import first

# The PDF preview is all blurry, I don't know how it looks on a real printer. This guy seems to have
# the same problem:
#http://lists.trolltech.com/pipermail/qt-interest/2009-November/015375.html

class LayoutElement(object):
    def __init__(self, page, rect):
        self.page = page
        self.rect = rect
    

class LayoutViewElement(LayoutElement):
    def __init__(self, view, page, rect):
        LayoutElement.__init__(self, page, rect)
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
    

class LayoutPage(object):
    def __init__(self, size):
        self.size = size
        self.pageRect = QRect(QPoint(0, 0), size)
        self.elements = []
        self.availableRects = [self.pageRect]
    
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
                    if inter.bottom() < previous.bottom():
                        # We still have some space left under the element
                        available = QRect(previous.left(), inter.bottom(), previous.width(), 
                            previous.bottom()-inter.bottom())
                        newAvailableRects.append(available)
                    if inter.right() < previous.right():
                        # We still have some space left next to the element
                        available = QRect(inter.right(), previous.top(), 
                            previous.right()-inter.right(), previous.height())
                        newAvailableRects.append(available)
                else:
                    newAvailableRects.append(previous)
            availableRects = newAvailableRects
        self.availableRects = availableRects
    
    def fit(self, view, minSize, expandH=False, expandV=False):
        # Go through all available rects and take the first one that fits.
        fits = lambda rect: rect.width() >= minSize.width() and rect.height() >= minSize.height()
        fittingRect = first(r for r in self.availableRects if fits(r))
        if fittingRect is None:
            return False
        rect = QRect(fittingRect.topLeft(), minSize)
        if expandH:
            rect.setWidth(fittingRect.width())
        if expandV:
            rect.setHeight(fittingRect.height())
        self.elements.append(LayoutViewElement(view, self, rect))
        self._computeAvailableRects()
        return True
    
    def render(self, painter):
        for element in self.elements:
            element.render(painter)
    

class ViewPrinter(object):
    def __init__(self, printer, painter):
        self.printer = printer
        self.painter = painter
        self.layoutPages = [LayoutPage(printer.pageRect().size())]
    
    def fit(self, view, minSize, expandH=False, expandV=False):
        for page in self.layoutPages:
            if page.fit(view, minSize, expandH, expandV):
                break
        else:
            self.layoutPages.append(LayoutPage(self.printer.pageRect().size()))
    
    def render(self):
        for page in self.layoutPages[:-1]:
            page.render(self.painter)
            self.printer.newPage()
        self.layoutPages[-1].render(self.painter)
    
