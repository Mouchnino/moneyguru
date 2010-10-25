# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-12-06
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from collections import namedtuple

from PyQt4.QtCore import Qt, QRect, QSize, QPoint, QModelIndex
from PyQt4.QtGui import QFont, QFontMetrics

from hsutil.misc import nonone

from ..const import (INDENTATION_OFFSET_ROLE, EXTRA_ROLE, EXTRA_UNDERLINED, EXTRA_UNDERLINED_DOUBLE,
    EXTRA_SPAN_ALL_COLUMNS)
from .layout import LayoutElement

CELL_MARGIN = 2

def applyMargin(rect, margin):
    result = QRect(rect)
    result.setLeft(result.left()+margin)
    result.setRight(result.right()-margin)
    result.setTop(result.top()+margin)
    result.setBottom(result.bottom()-margin)
    return result

class ItemPrintDatasource(object):
    # If we want to print tables and trees with a good code re-use, we've got to abstract away the
    # fact that trees have nodes and stuff and start treating it as rows and columns, with some
    # cells having more indentation than others. That's what this class is about.:
    def columnCount(self):
        """Returns the number of columns *to print*."""
        raise NotImplementedError()
    
    def rowCount(self):
        """Returns the number of rows *to print*."""
        raise NotImplementedError()
    
    def data(self, rowIndex, colIndex, role):
        """Returns model data for the index at the *printable* (rowIndex, colIndex) cell."""
        raise NotImplementedError()
    
    def columnAtIndex(self, colIndex):
        """Returns the Column instance at index `colIndex`"""
        raise NotImplementedError()
    
    def indentation(self, rowIndex, colIndex):
        """Returns the indentation pixels for the (rowIndex, colIndex)."""
        return 0
    
    def rowFont(self):
        raise NotImplementedError()
    
    def headerFont(self):
        raise NotImplementedError()
    

class TablePrintDatasource(ItemPrintDatasource):
    def __init__(self, table):
        ItemPrintDatasource.__init__(self)
        self.table = table
        h = table.view.horizontalHeader()
        self.columns = [col for col in table.COLUMNS if not h.isSectionHidden(col.index)]
        self.columns.sort(key=lambda c: h.visualIndex(c.index))
        self._rowFont = QFont(table.view.font())
        self._headerFont = QFont(self._rowFont)
        self._headerFont.setBold(True)
    
    def columnCount(self):
        return len(self.columns)
    
    def rowCount(self):
        return self.table.rowCount(QModelIndex())
    
    def data(self, rowIndex, colIndex, role):
        index = self.table.index(rowIndex, self.columns[colIndex].index)
        return self.table.data(index, role)
    
    def columnAtIndex(self, colIndex):
        return self.columns[colIndex]
    
    def rowFont(self):
        return self._rowFont
    
    def headerFont(self):
        return self._headerFont
    

class TreePrintDatasource(ItemPrintDatasource):
    def __init__(self, tree):
        ItemPrintDatasource.__init__(self)
        self.tree = tree
        h = tree.view.header()
        self.columns = [col for col in tree.COLUMNS if not h.isSectionHidden(col.index)]
        self.columns.sort(key=lambda c: h.visualIndex(c.index))
        self._rowFont = QFont(tree.view.font())
        self._headerFont = QFont(self._rowFont)
        self._headerFont.setBold(True)
        
        self._mapRows()
    
    def _getIndex(self, rowIndex, colIndex):
        index = self.rows[rowIndex]
        # `index` is for the column 0 of the row, now we have to get the correct cell
        index = index.sibling(index.row(), self.columns[colIndex].index)
        return index
    
    def _mapRows(self):
        self.rows = []
        index = self.tree.index(0, 0, QModelIndex())
        while index.isValid():
            self.rows.append(index)
            index = self.tree.view.indexBelow(index)
    
    def columnCount(self):
        return len(self.columns)
    
    def rowCount(self):
        return len(self.rows)
    
    def data(self, rowIndex, colIndex, role):
        index = self._getIndex(rowIndex, colIndex)
        return self.tree.data(index, role)
    
    def columnAtIndex(self, colIndex):
        return self.columns[colIndex]
    
    def indentation(self, rowIndex, colIndex):
        if colIndex != 0:
            return 0
        index = self._getIndex(rowIndex, colIndex)
        indentationOffset = self.tree.data(index, INDENTATION_OFFSET_ROLE)
        result = 0
        while index.parent().isValid():
            result += self.tree.view.indentation()
            index = index.parent()
        if indentationOffset:
            result += indentationOffset
        return result
    
    def rowFont(self):
        return self._rowFont
    
    def headerFont(self):
        return self._headerFont
    

class ItemViewLayoutElement(LayoutElement):
    def __init__(self, ds, stats, width, startRow):
        # We start with a minimal rect (`width` and enough height to fit the header and 1 row),
        # and then we let the element be placed. Afterwards, we can know what will be the endRow
        # value (so that the ViewPrinter can know if we need another page).
        height = stats.headerHeight + stats.rowHeight
        rect = QRect(QPoint(), QSize(width, height)) 
        LayoutElement.__init__(self, rect)
        self.ds = ds
        self.stats = stats
        self.startRow = startRow
        self.endRow = startRow
    
    def placed(self):
        height = self.rect.height()
        height -= self.stats.headerHeight
        rowToFit = height // self.stats.rowHeight
        self.endRow = min(self.startRow+rowToFit-1, self.ds.rowCount()-1)
        rowCount = self.endRow - self.startRow + 1
        # If it's the last page, we want to adjust the height of the rect so it's possible to fit
        # stuff under it.
        self.rect.setHeight(self.stats.headerHeight+(self.stats.rowHeight*rowCount))
    
    def renderCell(self, painter, rowIndex, colIndex, itemRect):
        extraFlags = nonone(self.ds.data(rowIndex, colIndex, EXTRA_ROLE), 0)
        pixmap = self.ds.data(rowIndex, colIndex, Qt.DecorationRole)
        if pixmap:
            painter.drawPixmap(itemRect.topLeft(), pixmap)
        else:
            # we don't support drawing pixmap and text in the same cell (don't need it)
            bgbrush = self.ds.data(rowIndex, colIndex, Qt.BackgroundRole)
            if bgbrush is not None:
                painter.fillRect(itemRect, bgbrush)
            text = self.ds.data(rowIndex, colIndex, Qt.DisplayRole)
            if text:
                alignment = self.ds.data(rowIndex, colIndex, Qt.TextAlignmentRole)
                if not alignment:
                    alignment = Qt.AlignLeft|Qt.AlignVCenter
                font = self.ds.data(rowIndex, colIndex, Qt.FontRole)
                if font is None:
                    font = self.ds.rowFont()
                fm = QFontMetrics(font)
                # elidedText has a tendency to "over-elide" that's why we have "+1"
                text = fm.elidedText(text, Qt.ElideRight, itemRect.width()+1)
                painter.save()
                painter.setFont(font)
                painter.drawText(itemRect, alignment, text)
                painter.restore()
        if extraFlags & (EXTRA_UNDERLINED | EXTRA_UNDERLINED_DOUBLE):
            p1 = itemRect.bottomLeft()
            p2 = itemRect.bottomRight()
            # Things get crowded with double lines and we have to cheat a little bit on 
            # item rects.
            p1.setY(p1.y()+2)
            p2.setY(p2.y()+2)
            painter.drawLine(p1, p2)
            if extraFlags & EXTRA_UNDERLINED_DOUBLE:
                p1.setY(p1.y()-3)
                p2.setY(p2.y()-3)
                painter.drawLine(p1, p2)
    
    def render(self, painter):
        # We used to re-use itemDelegate() for cell drawing, but it turned out to me more
        # complex than anything (with margins being too wide and all...)
        columnWidths = self.stats.columnWidths(self.rect.width())
        rowHeight = self.stats.rowHeight
        headerHeight = self.stats.headerHeight
        startRow = self.startRow
        left = self.rect.left()
        painter.save()
        painter.setFont(self.ds.headerFont())
        for colStats, colWidth in zip(self.stats.columns, columnWidths):
            col = colStats.col
            headerRect = QRect(left, self.rect.top(), colWidth, headerHeight)
            headerRect = applyMargin(headerRect, CELL_MARGIN)
            painter.drawText(headerRect, col.alignment, col.title)
            left += colWidth
        painter.restore()
        painter.drawLine(self.rect.left(), self.rect.top()+headerHeight, self.rect.right(), self.rect.top()+headerHeight)
        painter.save()
        painter.setFont(self.ds.rowFont())
        for rowIndex in range(startRow, self.endRow+1):
            top = self.rect.top() + rowHeight + ((rowIndex - startRow) * rowHeight)
            left = self.rect.left()
            extraRole = nonone(self.ds.data(rowIndex, 0, EXTRA_ROLE), 0)
            rowIsSpanning = extraRole & EXTRA_SPAN_ALL_COLUMNS
            if rowIsSpanning:
                itemRect = QRect(left, top, self.rect.width(), rowHeight)
                self.renderCell(painter, rowIndex, 0, itemRect)
            else:
                for colIndex, colWidth in enumerate(columnWidths):
                    indentation = self.ds.indentation(rowIndex, colIndex)
                    itemRect = QRect(left+indentation, top, colWidth, rowHeight)
                    itemRect = applyMargin(itemRect, CELL_MARGIN)
                    self.renderCell(painter, rowIndex, colIndex, itemRect)
                    left += colWidth
        painter.restore()
    

class ItemViewPrintStats(object):
    def __init__(self, ds):
        ColumnStats = namedtuple('ColumnStats', 'index col avgWidth maxWidth minWidth')
        rowFM = QFontMetrics(ds.rowFont())
        headerFM = QFontMetrics(ds.headerFont())
        self.rowHeight = rowFM.height() + CELL_MARGIN * 2
        self.headerHeight = headerFM.height() + CELL_MARGIN * 2
        spannedRowIndexes = set()
        for rowIndex in range(ds.rowCount()):
            extraRole = nonone(ds.data(rowIndex, 0, EXTRA_ROLE), 0)
            if extraRole & EXTRA_SPAN_ALL_COLUMNS:
                spannedRowIndexes.add(rowIndex)
        self.columns = []
        for colIndex in range(ds.columnCount()):
            col = ds.columnAtIndex(colIndex)
            sumWidth = 0
            maxWidth = 0
            # We need to have *at least* the width of the header.
            minWidth = headerFM.width(col.title) + CELL_MARGIN * 2
            for rowIndex in range(ds.rowCount()):
                if rowIndex in spannedRowIndexes:
                    continue
                data = ds.data(rowIndex, colIndex, Qt.DisplayRole)
                if data:
                    font = ds.data(rowIndex, colIndex, Qt.FontRole)
                    fm = QFontMetrics(font) if font is not None else rowFM
                    width = fm.width(data) + CELL_MARGIN * 2
                    width += ds.indentation(rowIndex, colIndex)
                    sumWidth += width
                    maxWidth = max(maxWidth, width)
                pixmap = ds.data(rowIndex, colIndex, Qt.DecorationRole)
                if pixmap is not None:
                    width = pixmap.width() + CELL_MARGIN * 2
                    maxWidth = max(maxWidth, width)
            avgWidth = sumWidth // ds.rowCount()
            maxWidth = max(maxWidth, minWidth)
            if col.cantTruncate: # if it's a "can't truncate" column, we make no concession
                minWidth = maxWidth
            cs = ColumnStats(colIndex, col, avgWidth, maxWidth, minWidth)
            self.columns.append(cs)
        self.maxWidth = sum(cs.maxWidth for cs in self.columns)
        self.minWidth = sum(cs.minWidth for cs in self.columns)
    
    def columnWidths(self, maxWidth):
        # Returns a list of recommended widths for columns if the table has `maxWidth` for
        # rendering. If it's possible to have maxWidth everywhere, each column will get it. If not,
        # We try to get at least `minWidth` for each column. Then, the rest of the width is split
        # between the columns depending on the relative weight of avgWidth.
        if self.maxWidth <= maxWidth:
            return [cs.maxWidth for cs in self.columns]
        if self.minWidth <= maxWidth:
            leftOver = maxWidth - self.minWidth
        else:
            leftOver = 0 # Don't bother considering the minWidths, we're screwed anyway
        baseWidths = [cs.minWidth for cs in self.columns]
        sumAvgs = sum(cs.avgWidth for cs in self.columns)
        ratios = [(cs.avgWidth/sumAvgs) for cs in self.columns]
        extraWidths = [int(ratio*leftOver) for ratio in ratios[:-1]]
        # Last column gets the rounding error
        extraWidths.append(leftOver-sum(extraWidths))
        return [base+extra for base, extra in zip(baseWidths, extraWidths)]
    
