# Created On: 2012-09-24
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from core.const import PaneArea

from .base_view import BaseView

class AccountSheetView(BaseView):
    # In sublasses' _setup(), set self.sheet, self.graph, self.piechart, self.splitterView and
    # self.subSplitterView
    #--- QWidget override
    def setFocus(self):
        self.sheet.view.setFocus()
    
    #--- Public
    def fitViewsForPrint(self, viewPrinter):
        hidden = self.model.mainwindow.hidden_areas
        viewPrinter.fitTree(self.sheet)
        if PaneArea.RightChart not in hidden:
            viewPrinter.fit(self.piechart.view, 150, 300, expandH=True)
        if PaneArea.BottomGraph not in hidden:
            viewPrinter.fit(self.graph.view, 300, 150, expandH=True, expandV=True)
    
    def restoreSubviewsSize(self):
        graphHeight = self.model.graph_height_to_restore
        if graphHeight:
            splitterHeight = self.splitterView.height()
            sizes = [splitterHeight-graphHeight, graphHeight]
            self.splitterView.setSizes(sizes)
        pieWidth = self.model.pie_width_to_restore
        if pieWidth:
            splitterWidth = self.subSplitterView.width()
            sizes = [splitterWidth-pieWidth, pieWidth]
            self.subSplitterView.setSizes(sizes)
    
    #--- model --> view
    def update_visibility(self):
        hidden = self.model.mainwindow.hidden_areas
        self.graph.view.setHidden(PaneArea.BottomGraph in hidden)
        self.piechart.view.setHidden(PaneArea.RightChart in hidden)
    
