# Created By: Virgil Dupras
# Created On: 2009-11-08
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

class Chart:
    CHART_MODEL_CLASS = None
    
    def __init__(self, parent_or_model, view):
        self.view = view
        if self.CHART_MODEL_CLASS is not None:
            self.model = self.CHART_MODEL_CLASS(self, parent_or_model.model)
        else:
            self.model = parent_or_model
            self.model.view = self
        self.view.dataSource = self.model
    
    #--- model --> view
    def refresh(self):
        self.view.update()