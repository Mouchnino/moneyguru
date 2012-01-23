# Created By: Virgil Dupras
# Created On: 2008-09-14
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

NOEDIT = object()
DATE_FORMAT_FOR_PREFERENCES = '%d/%m/%Y'

# These constants are in sync with the GUI
class PaneType:
    NetWorth = 0
    Profit = 1
    Transaction = 2
    Account = 3
    Schedule = 4
    Budget = 5
    Cashculator = 6
    GeneralLedger = 7
    DocProps = 8
    Empty = 100

# These constants are in sync with the GUI
class PaneArea:
    Main = 1
    BottomGraph = 2
    RightChart = 3
