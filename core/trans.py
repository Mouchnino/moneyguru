# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-06-23
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

# Doing i18n with GNU gettext for the core text gets complicated, so what I do is that I make the
# GUI layer responsible for supplying a tr() function.

_trfunc = None

def tr(s):
    # We use this double call so that we can do "from trans import tr" and still change the tr func
    # afterwards (otherwise, modules that imported the tr func are stuck with the old one)
    if _trfunc is None:
        return s
    else:
        return _trfunc(s)

def set_tr(new_tr):
    global _trfunc
    _trfunc = new_tr
