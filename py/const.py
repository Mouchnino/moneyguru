# Created By: Virgil Dupras
# Created On: 2008-09-14
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

NOEDIT = object()

REPEAT_NEVER = 'never'
REPEAT_DAILY = 'daily'
REPEAT_WEEKLY = 'weekly'
REPEAT_MONTHLY = 'monthly'
REPEAT_YEARLY = 'yearly'
REPEAT_WEEKDAY = 'weekday'
REPEAT_WEEKDAY_LAST = 'weekday_last'

# synced with the gui side, don't change the values
UNRECONCILIATION_ABORT = 0
UNRECONCILIATION_CONTINUE = 1
UNRECONCILIATION_CONTINUE_DONT_UNRECONCILE = 2