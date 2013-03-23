# Created By: Virgil Dupras
# Created On: 2009-11-08
# Copyright 2013 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFontMetrics, QPen, QBrush

class Chart:
    CHART_MODEL_CLASS = None
    
    def __init__(self, parent_or_model, view):
        self.view = view
        # Drawing related methods are called very, very often. I don't know how expensive to create
        # pen, brushes and fonts are, but it's probably more expensive than a dictionary lookup, so
        # there, we cache them.
        self.id2font = {}
        self.index2pen = {}
        self.index2brush = {}
        self.noPen = QPen(Qt.NoPen)
        self.noBrush = QBrush(Qt.NoBrush)
        if self.CHART_MODEL_CLASS is not None:
            self.model = self.CHART_MODEL_CLASS(self, parent_or_model.model)
        else:
            self.model = parent_or_model
            self.model.view = self
        self.view.dataSource = self.model
    
    def fontForID(self, fontId):
        try:
            result = self.id2font[fontId]
        except KeyError:
            result = self.view.fontForID(fontId)
            self.id2font[fontId] = result
        return result
    
    def penForID(self, penID):
        if penID is None:
            return self.noPen
        try:
            result = self.index2pen[penID]
        except KeyError:
            result = self.view.penForID(penID)
            self.index2pen[penID] = result
        return result
    
    def brushForID(self, brushID):
        if brushID is None:
            return self.noBrush
        try:
            result = self.index2brush[brushID]
        except KeyError:
            result = self.view.brushForID(brushID)
            self.index2brush[brushID] = result
        return result
    
    #--- model --> view
    def refresh(self):
        self.view.update()
    
    def draw_line(self, p1, p2, pen_id):
        pen = self.penForID(pen_id)
        self.view.draw_line(p1, p2, pen)
    
    def draw_rect(self, rect, pen_id, brush_id):
        pen = self.penForID(pen_id)
        brush = self.brushForID(brush_id)
        self.view.draw_rect(rect, pen, brush)
    
    def draw_pie(self, center, radius, start_angle, span_angle, brush_id):
        brush = self.brushForID(brush_id)
        self.view.draw_pie(center, radius, start_angle, span_angle, brush)
    
    def draw_polygon(self, points, pen_id, brush_id):
        pen = self.penForID(pen_id)
        brush = self.brushForID(brush_id)
        self.view.draw_polygon(points, pen, brush)
    
    def draw_text(self, text, rect, font_id):
        font = self.fontForID(font_id)
        self.view.draw_text(text, rect, font)
    
    def text_size(self, text, font_id):
        font = self.view.fontForID(font_id)
        fm = QFontMetrics(font)
        return (fm.width(text), fm.height())
    
