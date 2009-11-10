# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-10-31
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from moneyguru.document import Document as DocumentModel

class Document(object):
    def __init__(self, app):
        self.model = DocumentModel(view=self, app=app.model)
    
    # model --> view
    def query_for_schedule_scope(self):
        return False
    
