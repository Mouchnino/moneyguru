# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-09-09
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from ..const import PaneType
from .base import BaseView, MESSAGES_DOCUMENT_CHANGED

class GeneralLedgerView(BaseView):
    VIEW_TYPE = PaneType.GeneralLedger
    
    #--- Overrides
    def set_children(self, children):
        [self.gltable] = children
        BaseView.set_children(self, children)
    
