# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-04
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

from collections import namedtuple
from itertools import combinations

from PyQt4.QtCore import Qt, QRect, QSize, QPoint, QModelIndex
from PyQt4.QtGui import QPixmap, QPainter, QApplication, QFont, QFontMetrics

from hsutil.misc import first

from moneyguru.gui.print_view import PrintView as PrintViewModel

# The PDF preview is all blurry, I don't know how it looks on a real printer. This guy seems to have
# the same problem:
#http://lists.trolltech.com/pipermail/qt-interest/2009-November/015375.html

class LayoutElement(object):
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
        rect = QRect(page.pageRect.topLeft(), QSize(page.pageRect.width(), fm.height()))
        LayoutElement.__init__(self, rect)
        self.page = page
        self.font = font
    
    def render(self, painter):
        text = self.page.title
        painter.save()
        painter.setFont(self.font)
        painter.drawText(self.rect, Qt.AlignCenter, text)
        painter.restore()
    

class LayoutTableElement(LayoutElement):
    def __init__(self, table, stats, width, startRow):
        # We start with a minimal rect (`width` and enough height to fit the header and 1 row),
        # and then we let the element be placed. Afterwards, we can know what will be the endRow
        # value (so that the ViewPrinter can know if we need another page).
        height = stats.headerHeight + stats.rowHeight
        rect = QRect(QPoint(), QSize(width, height)) 
        LayoutElement.__init__(self, rect)
        self.table = table
        self.stats = stats
        self.startRow = startRow
        self.endRow = startRow
    
    def placed(self):
        height = self.rect.height()
        height -= self.stats.headerHeight
        rowToFit = height // self.stats.rowHeight
        self.endRow = min(self.startRow+rowToFit-1, self.stats.rowCount-1)
    
    def render(self, painter):
        painter.drawRect(self.rect)
        delegate = self.table.view.itemDelegate()
        options = self.table.view.viewOptions()
        columnWidths = self.stats.columnWidths(self.rect.width())
        rowHeight = self.stats.rowHeight
        headerHeight = self.stats.headerHeight
        startRow = self.startRow
        left = self.rect.left()
        for colIndex, colWidth in enumerate(columnWidths):
            title = self.stats.columns[colIndex].title
            headerRect = QRect(left, self.rect.top(), colWidth, headerHeight)
            painter.drawText(headerRect, Qt.AlignLeft|Qt.AlignTop, title)
            left += colWidth
        painter.drawLine(self.rect.left(), self.rect.top()+headerHeight, self.rect.right(), self.rect.top()+headerHeight)
        for rowIndex in xrange(startRow, self.endRow+1):
            top = self.rect.top() + rowHeight + ((rowIndex - startRow) * rowHeight)
            left = self.rect.left()
            for colIndex, colWidth in enumerate(columnWidths):
                index = self.table.index(rowIndex, colIndex)
                itemRect = QRect(left, top, colWidth, rowHeight)
                options.rect = itemRect
                delegate.paint(painter, options, index)
                left += colWidth
    

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
            duplicates = set(r1 for r1, r2 in combinations(newAvailableRects, 2) if r2.contains(r1))
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
    

class TablePrintStats(object):
    def __init__(self, table):
        ColumnStats = namedtuple('ColumnStats', 'title avgWidth maxWidth headerWidth')
        self.rowFont = QFont(table.view.font())
        rowFM = QFontMetrics(self.rowFont)
        self.headerFont = QFont(self.rowFont)
        self.headerFont.setBold(True)
        headerFM = QFontMetrics(self.headerFont)
        self.rowCount = table.rowCount(QModelIndex())
        self.rowHeight = rowFM.height() + 2
        self.headerHeight = self.rowHeight + 4
        self.columns = []
        for column in table.COLUMNS:
            colIndex = column.index
            sumWidth = 0
            maxWidth = 0
            headerWidth = headerFM.width(column.title)
            for rowIndex in xrange(self.rowCount):
                index = table.index(rowIndex, colIndex)
                data = table.data(index, Qt.DisplayRole)
                if data:
                    width = rowFM.width(data)
                    sumWidth += width
                    maxWidth = max(maxWidth, width)
            avgWidth = sumWidth // self.rowCount
            self.columns.append(ColumnStats(column.title, avgWidth, maxWidth, headerWidth))
        self.maxWidth = sum(cs.maxWidth for cs in self.columns)
        self.headersWidth = sum(cs.headerWidth for cs in self.columns)
    
    def columnWidths(self, maxWidth):
        # Returns a list of recommended widths for columns if the table has `maxWidth` for
        # rendering. If it's possible to have maxWidth everywhere, each column will get it. If not,
        # We try to get at least `headerWidth` for each column. Then, the rest of the width is split
        # between the columns depending on the relative weight of avgWidth.
        if self.maxWidth <= maxWidth:
            return [cs.maxWidth for cs in self.columns]
        sumAvgs = sum(cs.avgWidth for cs in self.columns)
        ratios = [(cs.avgWidth/sumAvgs) for cs in self.columns]
        if self.headersWidth <= maxWidth:
            leftOver = maxWidth - self.headersWidth
        else:
            leftOver = 0 # Don't bother considering the headerWidths, we're screwed anyway
        toAdd = [int(ratio*leftOver) for ratio in ratios[:-1]]
        # Last column gets the rounding error
        toAdd.append(leftOver-sum(toAdd))
        return [col.headerWidth+width for col, width in zip(self.columns, toAdd)]
    

class ViewPrinter(object):
    def __init__(self, printer, document, titleFormat):
        # title format has 2 placeholders, {startDate} and {endDate}
        # hack, see moneyguru.gui.print_view
        self.document = document.model
        self.app = document.app.model
        self.model = PrintViewModel(self)
        self.title = titleFormat.format(startDate=self.model.start_date, endDate=self.model.end_date)
        self.printer = printer
        self.pageSize = printer.pageRect().size()
        self.layoutPages = [LayoutPage(self)]
    
    def fit(self, view, minWidth, minHeight, expandH=False, expandV=False):
        rect = QRect(0, 0, minWidth, minHeight)
        element = LayoutViewElement(view, rect)
        for page in self.layoutPages:
            if page.fit(element, expandH, expandV):
                break
        else:
            page = LayoutPage(self)
            page.fit(element, expandH, expandV)
            self.layoutPages.append(page)
    
    def fitTable(self, table):
        # It is currently assumed that the current page's width availability is going to be the same
        # as possible additonnal pages (in other words, place it first).
        stats = TablePrintStats(table)
        page = self.layoutPages[-1]
        currentRow = 0
        while True:
            maxPageWidth = page.maxAvailableWidth
            elementWidth = min(maxPageWidth, stats.maxWidth)
            element = LayoutTableElement(table, stats, elementWidth, currentRow)
            page.fit(element, expandV=True)
            currentRow = element.endRow+1
            if currentRow >= stats.rowCount:
                break
            page = LayoutPage(self)
            self.layoutPages.append(page)
    
    def render(self):
        painter = QPainter()
        painter.begin(self.printer)
        for page in self.layoutPages[:-1]:
            page.render(painter)
            self.printer.newPage()
        self.layoutPages[-1].render(painter)
        painter.end()
    
