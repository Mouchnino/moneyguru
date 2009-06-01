# Unit Name: moneyguru.exception
# Created By: Virgil Dupras
# Created On: 2008-02-15
# $Id$
# Copyright 2009 Hardcoded Software (http://www.hardcoded.net)

class FileFormatError(Exception):
    pass

class FileLoadError(Exception):
    pass

class DuplicateAccountNameError(Exception):
    pass

class OperationAborted(Exception):
    pass