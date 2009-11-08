# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-08
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

class Chart(object):
    CHART_MODEL_CLASS = None
    
    def __init__(self, doc, view):
        self.doc = doc
        self.view = view
        self.model = self.CHART_MODEL_CLASS(document=doc.model, view=self)
        self.view.dataSource = self.model
    
    #--- model --> view
    def refresh(self):
        self.view.update()