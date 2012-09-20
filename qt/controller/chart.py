# Created By: Virgil Dupras
# Created On: 2009-11-08
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4.QtGui import QFontMetrics, QLinearGradient

def gradientFromColor(color):
    gradient = QLinearGradient(0, 0, 0, 1)
    gradient.setCoordinateMode(QLinearGradient.ObjectBoundingMode)
    gradient.setColorAt(0, color)
    gradient.setColorAt(1, color.lighter())
    return gradient

class Chart:
    CHART_MODEL_CLASS = None
    
    def __init__(self, parent_or_model, view):
        self.view = view
        # Drawing related methods are called very, very often. I don't know how expensive to create
        # gradients and fonts are, but it's probably more expensive than a dictionary lookup, so
        # there, we cache fonts and gradients.
        self.id2font = {}
        self.index2gradient = {}
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
    
    def gradientForColorIndex(self, colorIndex):
        try:
            result = self.index2gradient[colorIndex]
        except KeyError:
            color = self.view.colorForIndex(colorIndex)
            result = gradientFromColor(color)
            self.index2gradient[colorIndex] = result
        return result
    
    #--- model --> view
    def refresh(self):
        self.view.update()
    
    def draw_line(self, p1, p2, color_index):
        color = self.view.colorForIndex(color_index)
        self.view.draw_line(p1, p2, color)
    
    def draw_rect(self, rect, line_color_index, bg_color_index):
        line_color = self.view.colorForIndex(line_color_index)
        bg_color = self.view.colorForIndex(bg_color_index)
        self.view.draw_rect(rect, line_color, bg_color)
    
    def draw_pie(self, center, radius, start_angle, span_angle, color_index):
        gradient = self.gradientForColorIndex(color_index)
        self.view.draw_pie(center, radius, start_angle, span_angle, gradient)
    
    def draw_text(self, text, rect, font_id):
        font = self.fontForID(font_id)
        self.view.draw_text(text, rect, font)
    
    def text_size(self, text, font_id):
        font = self.view.fontForID(font_id)
        fm = QFontMetrics(font)
        return (fm.width(text), fm.height())
    
