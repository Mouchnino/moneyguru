# -*- coding: utf-8 -*-
# Created By: Virgil Dupras
# Created On: 2010-06-22
# Copyright 2010 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "HS" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/hs_license

import os
import os.path as op
import shutil

SOURCE_LPROJ = 'en'
TARGET_LPROJS = ['fr']

def main():
    source_folder = '%s.lproj' % SOURCE_LPROJ
    for target_lproj in TARGET_LPROJS:
        target_folder = '%s.lproj' % target_lproj
        sourcefiles = os.listdir(source_folder)
        xibs = [fn for fn in sourcefiles if fn.endswith('.xib')]
        for xib in xibs:
            basename = xib[:-4]
            source_xib = op.join(source_folder, xib)
            target_xib = op.join(target_folder, xib)
            target_strings = op.join(target_folder, '%s.strings' % basename)
            if op.exists(target_strings):
                cmd = 'ibtool --strings-file %s --write %s %s' % (target_strings, target_xib, source_xib)
                print "Localizing %s from %s to %s" % (xib, SOURCE_LPROJ, target_lproj)
                os.system(cmd)
            else:
                # no translation to be done, just copy the thing
                print "Copying %s to %s" % (source_xib, target_xib)
                shutil.copy(source_xib, target_xib)

if __name__ == '__main__':
    main()
