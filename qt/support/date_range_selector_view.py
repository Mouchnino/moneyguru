# Created By: Virgil Dupras
# Created On: 2010-03-16
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QWidget

class DateRangeSelectorView(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self._setupUi()
    
    def _setupUi(self):
        self.resize(259, 32)
        self.horizontalLayout = QtGui.QHBoxLayout(self)
        self.horizontalLayout.setMargin(0)
        self.prevButton = QtGui.QPushButton(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/nav_left_9"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.prevButton.setIcon(icon)
        self.horizontalLayout.addWidget(self.prevButton)
        self.typeButton = QtGui.QPushButton("<date range>")
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.typeButton.sizePolicy().hasHeightForWidth())
        self.typeButton.setSizePolicy(sizePolicy)
        self.typeButton.setMinimumSize(QtCore.QSize(0, 0))
        self.typeButton.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.typeButton.setIconSize(QtCore.QSize(6, 6))
        self.horizontalLayout.addWidget(self.typeButton)
        self.nextButton = QtGui.QPushButton(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/nav_right_9"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.nextButton.setIcon(icon1)
        self.horizontalLayout.addWidget(self.nextButton)
        self.horizontalLayout.setStretch(1, 1)

