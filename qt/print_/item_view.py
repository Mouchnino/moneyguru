# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-06
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from __future__ import division

from collections import namedtuple

from PyQt4.QtCore import Qt, QRect, QSize, QPoint, QModelIndex
from PyQt4.QtGui import QFont, QFontMetrics

from .layout import LayoutElement

CELL_MARGIN = 2

def applyMargin(rect, margin):
    result = QRect(rect)
    result.setLeft(result.left()+margin)
    result.setRight(result.right()-margin)
    result.setTop(result.top()+margin)
    result.setBottom(result.bottom()-margin)
    return result

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
        # We used to re-use table.view.itemDelegate() for cell drawing, but it turned out to me more
        # complex than anything (with margins being too wide and all...)
        painter.drawRect(self.rect)
        columnWidths = self.stats.columnWidths(self.rect.width())
        rowHeight = self.stats.rowHeight
        headerHeight = self.stats.headerHeight
        startRow = self.startRow
        left = self.rect.left()
        painter.save()
        painter.setFont(self.stats.headerFont)
        for col, colWidth in zip(self.stats.columns, columnWidths):
            title = col.title
            headerRect = QRect(left, self.rect.top(), colWidth, headerHeight)
            headerRect = applyMargin(headerRect, CELL_MARGIN)
            painter.drawText(headerRect, Qt.AlignLeft, title)
            left += colWidth
        painter.restore()
        painter.drawLine(self.rect.left(), self.rect.top()+headerHeight, self.rect.right(), self.rect.top()+headerHeight)
        painter.save()
        painter.setFont(self.stats.rowFont)
        rowFM = QFontMetrics(self.stats.rowFont)
        for rowIndex in xrange(startRow, self.endRow+1):
            top = self.rect.top() + rowHeight + ((rowIndex - startRow) * rowHeight)
            left = self.rect.left()
            for col, colWidth in zip(self.stats.columns, columnWidths):
                itemRect = QRect(left, top, colWidth, rowHeight)
                itemRect = applyMargin(itemRect, CELL_MARGIN)
                index = self.table.index(rowIndex, col.index)
                pixmap = self.table.data(index, Qt.DecorationRole)
                if pixmap:
                    painter.drawPixmap(itemRect.topLeft(), pixmap)
                else:
                    # we don't support drawing pixmap and text in the same cell (don't need it)
                    text = self.table.data(index, Qt.DisplayRole)
                    if text:
                        alignment = self.table.data(index, Qt.TextAlignmentRole)
                        if not alignment:
                            alignment = Qt.AlignLeft|Qt.AlignVCenter
                        # elidedText has a tendency to "over-elide" that's why we have "+1"
                        text = rowFM.elidedText(text, Qt.ElideRight, itemRect.width()+1)
                        painter.drawText(itemRect, alignment, text)
                left += colWidth
        painter.restore()
    

class TablePrintStats(object):
    def __init__(self, table):
        ColumnStats = namedtuple('ColumnStats', 'index title avgWidth maxWidth maxPixWidth headerWidth')
        self.rowFont = QFont(table.view.font())
        rowFM = QFontMetrics(self.rowFont)
        self.headerFont = QFont(self.rowFont)
        self.headerFont.setBold(True)
        headerFM = QFontMetrics(self.headerFont)
        self.rowCount = table.rowCount(QModelIndex())
        self.rowHeight = rowFM.height() + CELL_MARGIN * 2
        self.headerHeight = headerFM.height() + CELL_MARGIN * 2
        self.columns = []
        for column in table.COLUMNS:
            if table.view.horizontalHeader().isSectionHidden(column.index):
                continue
            colIndex = column.index
            sumWidth = 0
            maxWidth = 0
            maxPixWidth = 0
            headerWidth = headerFM.width(column.title) + CELL_MARGIN * 2
            for rowIndex in xrange(self.rowCount):
                index = table.index(rowIndex, colIndex)
                data = table.data(index, Qt.DisplayRole)
                if data:
                    width = rowFM.width(data) + CELL_MARGIN * 2
                    sumWidth += width
                    maxWidth = max(maxWidth, width)
                pixmap = table.data(index, Qt.DecorationRole)
                if pixmap is not None:
                    width = pixmap.width() + CELL_MARGIN * 2
                    maxPixWidth = max(maxPixWidth, width)
            avgWidth = sumWidth // self.rowCount
            maxWidth = max(maxWidth, maxPixWidth, headerWidth)
            cs = ColumnStats(column.index, column.title, avgWidth, maxWidth, maxPixWidth, headerWidth)
            self.columns.append(cs)
        self.maxWidth = sum(cs.maxWidth for cs in self.columns)
        # When pictures are involved, they get priority
        self.minWidth = sum(max(cs.headerWidth, cs.maxPixWidth) for cs in self.columns)
    
    def columnWidths(self, maxWidth):
        # Returns a list of recommended widths for columns if the table has `maxWidth` for
        # rendering. If it's possible to have maxWidth everywhere, each column will get it. If not,
        # We try to get at least `headerWidth` for each column. Then, the rest of the width is split
        # between the columns depending on the relative weight of avgWidth.
        if self.maxWidth <= maxWidth:
            return [cs.maxWidth for cs in self.columns]
        if self.minWidth <= maxWidth:
            leftOver = maxWidth - self.minWidth
        else:
            leftOver = 0 # Don't bother considering the headerWidths, we're screwed anyway
        baseWidths = [max(cs.headerWidth, cs.maxPixWidth) for cs in self.columns]
        sumAvgs = sum(cs.avgWidth for cs in self.columns)
        ratios = [(cs.avgWidth/sumAvgs) for cs in self.columns]
        extraWidths = [int(ratio*leftOver) for ratio in ratios[:-1]]
        # Last column gets the rounding error
        extraWidths.append(leftOver-sum(extraWidths))
        return [base+extra for base, extra in zip(baseWidths, extraWidths)]
    
