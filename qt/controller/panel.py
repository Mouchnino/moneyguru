# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-10
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtGui import QDialog

class Panel(QDialog):
    def __init__(self):
        QDialog.__init__(self, None)
    
    def _loadFields(self):
        raise NotImplementedError()
    
    def _saveFields(self):
        raise NotImplementedError()
    
    def accept(self):
        self.model.save()
        QDialog.accept(self)
    
    #--- model --> view
    def pre_load(self):
        pass
    
    def pre_save(self):
        self._saveFields()
    
    def post_load(self):
        self._loadFields()
        self.show()
    
