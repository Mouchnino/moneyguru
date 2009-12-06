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

from PyQt4.QtCore import QRect
from PyQt4.QtGui import QPainter

from moneyguru.gui.print_view import PrintView as PrintViewModel
from .layout import LayoutPage, LayoutViewElement
from .item_view import LayoutTableElement, TablePrintStats, TablePrintDatasource

# Yes, this unit is messy, but then again, so is printing. Maybe it's my lack of Qt knowledge, but
# writing this unit felt like fighting against the Qt framework.

# XXX I think it might be possible to push down some of the layout logic to the model part of the 
# app so that it can be re-used on the Cocoa side (this code is messy too).

# The PDF preview is all blurry, I don't know how it looks on a real printer. This guy seems to have
# the same problem:
#http://lists.trolltech.com/pipermail/qt-interest/2009-November/015375.html

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
        ds = TablePrintDatasource(table)
        stats = TablePrintStats(ds)
        page = self.layoutPages[-1]
        currentRow = 0
        while True:
            maxPageWidth = page.maxAvailableWidth
            elementWidth = min(maxPageWidth, stats.maxWidth)
            element = LayoutTableElement(ds, stats, elementWidth, currentRow)
            page.fit(element, expandV=True)
            currentRow = element.endRow+1
            if currentRow >= ds.rowCount():
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
    
