# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-08
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

class Chart(object):
    CHART_MODEL_CLASS = None
    
    def __init__(self, parent, view):
        self.doc = parent.doc
        self.view = view
        self.model = self.CHART_MODEL_CLASS(self, parent.model)
        self.view.dataSource = self.model
    
    #--- model --> view
    def refresh(self):
        self.view.update()