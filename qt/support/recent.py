# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2009-11-12
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

from PyQt4.QtCore import SIGNAL, QObject, QSettings
from PyQt4.QtGui import QAction

from qtlib.preferences import variant_to_py

class Recent(QObject):
    def __init__(self, menu, settingName, maxItemCount=10, filterFunc=None):
        QObject.__init__(self)
        self._menu = menu
        self._settingName = settingName
        self._maxItemCount = maxItemCount
        self._filterFunc = filterFunc
        self._items = []
        self._loadFromSettings()
        self._refreshMenu()
    
    #--- Private
    def _loadFromSettings(self):
        settings = QSettings()
        if not settings.contains(self._settingName):
            return
        items = variant_to_py(settings.value(self._settingName))
        assert isinstance(items, list)
        if self._filterFunc is not None:
            items = filter(self._filterFunc, items)
        self._items = items
    
    def _refreshMenu(self):
        menu = self._menu
        menu.clear()
        for item in self._items:
            action = QAction(item, menu)
            action.setData(item)
            action.triggered.connect(self.menuItemWasClicked)
            menu.addAction(action)
    
    def _saveToSettings(self):
        settings = QSettings()
        settings.setValue(self._settingName, self._items)
    
    #--- Public
    def itemWasOpened(self, item):
        self._items = ([item] + self._items)[:self._maxItemCount]
        self._refreshMenu()
        self._saveToSettings()
    
    #--- Event Handlers
    def menuItemWasClicked(self):
        action = self.sender()
        if action is not None:
            item = action.data().toString()
            self.emit(SIGNAL('mustOpenItem(QString)'), item)
            self._items.remove(item)
            self._items.insert(0, item)
            self._refreshMenu()
    

    